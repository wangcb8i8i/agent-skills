# 高性能队列——Disruptor

作者：宫铭（美团技术团队）
日期：2016-11-18
来源：https://tech.meituan.com/2016/11/18/disruptor.html

## 背景

Disruptor是英国外汇交易公司LMAX开发的一个高性能队列，研发的初衷是解决内存队列的延迟问题（在性能测试中发现竟然与I/O操作处于同样的数量级）。基于Disruptor开发的系统单线程能支撑每秒600万订单，2010年在QCon演讲后，获得了业界关注。2011年，企业应用软件专家Martin Fowler专门撰写长文介绍。同年它还获得了Oracle官方的Duke大奖。

目前，包括Apache Storm、Camel、Log4j 2在内的很多知名项目都应用了Disruptor以获取高性能。在美团技术团队它也有不少应用，有的项目架构借鉴了它的设计机制。本文从实战角度剖析了Disruptor的实现原理。

需要特别指出的是，这里所说的队列是系统内部的内存队列，而不是Kafka这样的分布式队列。另外，本文所描述的Disruptor特性限于3.3.4。

## Java内置队列

介绍Disruptor之前，我们先来看一看常用的线程安全的内置队列有什么问题。Java的内置队列如下表所示。

| 队列 | 有界性 | 锁 | 数据结构 |
|------|--------|-----|----------|
| ArrayBlockingQueue | bounded | 加锁 | arraylist |
| LinkedBlockingQueue | optionally-bounded | 加锁 | linkedlist |
| ConcurrentLinkedQueue | unbounded | 无锁 | linkedlist |
| LinkedTransferQueue | unbounded | 无锁 | linkedlist |
| PriorityBlockingQueue | unbounded | 加锁 | heap |
| DelayQueue | unbounded | 加锁 | heap |

队列的底层一般分成三种：数组、链表和堆。其中，堆一般情况下是为了实现带有优先级特性的队列，暂且不考虑。

我们就从数组和链表两种数据结构来看，基于数组线程安全的队列，比较典型的是ArrayBlockingQueue，它主要通过加锁的方式来保证线程安全；基于链表的线程安全队列分成LinkedBlockingQueue和ConcurrentLinkedQueue两大类，前者也通过锁的方式来实现线程安全，而后者以及上面表格中的LinkedTransferQueue都是通过原子变量compare and swap（以下简称"CAS"）这种不加锁的方式来实现的。

通过不加锁的方式实现的队列都是无界的（无法保证队列的长度在确定的范围内）；而加锁的方式，可以实现有界队列。在稳定性要求特别高的系统中，为了防止生产者速度过快，导致内存溢出，只能选择有界队列；同时，为了减少Java的垃圾回收对系统性能的影响，会尽量选择array/heap格式的数据结构。这样筛选下来，符合条件的队列就只有ArrayBlockingQueue。

## ArrayBlockingQueue的问题

ArrayBlockingQueue在实际使用过程中，会因为加锁和伪共享等出现严重的性能问题，我们下面来分析一下。

### 加锁

现实编程过程中，加锁通常会严重地影响性能。线程会因为竞争不到锁而被挂起，等锁被释放的时候，线程又会被恢复，这个过程中存在着很大的开销，并且通常会有较长时间的中断，因为当一个线程正在等待锁时，它不能做任何其他事情。如果一个线程在持有锁的情况下被延迟执行，例如发生了缺页错误、调度延迟或者其它类似情况，那么所有需要这个锁的线程都无法执行下去。如果被阻塞线程的优先级较高，而持有锁的线程优先级较低，就会发生优先级反转。

Disruptor论文中讲述了一个实验：测试程序调用了一个函数，该函数会对一个64位的计数器循环自增5亿次。机器环境：2.4G 6核。

| Method | Time (ms) |
|--------|-----------|
| Single thread | 300 |
| Single thread with CAS | 5,700 |
| Single thread with lock | 10,000 |
| Single thread with volatile write | 4,700 |
| Two threads with CAS | 30,000 |
| Two threads with lock | 224,000 |

CAS操作比单线程无锁慢了1个数量级；有锁且多线程并发的情况下，速度比单线程无锁慢3个数量级。可见无锁速度最快。单线程情况下，不加锁的性能 > CAS操作的性能 > 加锁的性能。在多线程情况下，为了保证线程安全，必须使用CAS或锁，这种情况下，CAS的性能超过锁的性能，前者大约是后者的8倍。综上可知，加锁的性能是最差的。

**关于锁和CAS**

保证线程安全一般分成两种方式：锁和原子变量。

采取加锁的方式，默认线程会冲突，访问数据时，先加上锁再访问，访问之后再解锁。通过锁界定一个临界区，同时只有一个线程进入。

下面是ArrayBlockingQueue通过加锁的方式实现的offer方法，保证线程安全。

```java
public boolean offer(E e) {
    checkNotNull(e);
    final ReentrantLock lock = this.lock;
    lock.lock();
    try {
        if (count == items.length)
            return false;
        else {
            insert(e);
            return true;
        }
    } finally {
        lock.unlock();
    }
}
```

原子变量能够保证原子性的操作，意思是某个任务在执行过程中，要么全部成功，要么全部失败回滚，恢复到执行之前的初态，不存在初态和成功之间的中间状态。例如CAS操作，要么比较并交换成功，要么比较并交换失败。由CPU保证原子性。

通过原子变量可以实现线程安全。执行某个任务的时候，先假定不会有冲突，若不发生冲突，则直接执行成功；当发生冲突的时候，则执行失败，回滚再重新操作，直到不发生冲突。

CAS会先把Entry现在的value跟线程当初读出的值相比较，若相同，则赋值；若不相同，则赋值执行失败。一般会通过while/for循环来重新执行，直到赋值成功。

```java
public final int getAndAdd(int delta) {
    for (;;) {
        int current = get();
        int next = current + delta;
        if (compareAndSet(current, next))
            return current;
    }
}
```

在高度竞争的情况下，锁的性能将超过原子变量的性能，但是更真实的竞争情况下，原子变量的性能将超过锁的性能。同时原子变量不会有死锁等活跃性问题。

### 伪共享

**什么是共享**

下图是计算的基本结构。L1、L2、L3分别表示一级缓存、二级缓存、三级缓存，越靠近CPU的缓存，速度越快，容量也越小。当CPU执行运算的时候，它先去L1查找所需的数据、再去L2、然后是L3，如果最后这些缓存中都没有，所需的数据就要去主内存拿。走得越远，运算耗费的时间就越长。所以如果你在做一些很频繁的事，你要尽量确保数据在L1缓存中。

从CPU访问不同层级数据的时间概念：主存约60-80ns、L3 cache约15ns、L2 cache约3ns、L1 cache约1ns。可见CPU读取主存中的数据会比从L1中读取慢了近2个数量级。

**缓存行**

Cache是由很多个cache line组成的。每个cache line通常是64字节，并且它有效地引用主内存中的一块儿地址。一个Java的long类型变量是8字节，因此在一个缓存行中可以存8个long类型的变量。

CPU每次从主存中拉取数据时，会把相邻的数据也存入同一个cache line。在访问一个long数组的时候，如果数组中的一个值被加载到缓存中，它会自动加载另外7个。因此你能非常快速的遍历这个数组。

**什么是伪共享**

ArrayBlockingQueue有三个成员变量：takeIndex（需要被取走的元素下标）、putIndex（可被元素插入的位置的下标）、count（队列中元素的数量）。这三个变量很容易放到一个缓存行中，但是之间修改没有太多的关联。所以每次修改，都会使之前缓存的数据失效，从而不能完全达到共享的效果。

当生产者线程put一个元素到ArrayBlockingQueue时，putIndex会修改，从而导致消费者线程的缓存中的缓存行无效，需要从主存中重新读取。这种无法充分使用缓存行特性的现象，称为伪共享。

对于伪共享，一般的解决方案是，增大数组元素的间隔使得由不同线程存取的元素位于不同的缓存行上，以空间换时间。在2G Hz，2核，8G内存的运行环境下，使用了共享机制比没有使用共享机制，速度快了4倍左右。在jdk1.8中，有专门的注解@Contended来避免伪共享，更优雅地解决问题。

## Disruptor的设计方案

Disruptor通过以下设计来解决队列速度慢的问题：

**环形数组结构**：为了避免垃圾回收，采用数组而非链表。同时，数组对处理器的缓存机制更加友好。

**元素位置定位**：数组长度2^n，通过位运算，加快定位的速度。下标采取递增的形式。不用担心index溢出的问题。index是long类型，即使100万QPS的处理速度，也需要30万年才能用完。

**无锁设计**：每个生产者或者消费者线程，会先申请可以操作的元素在数组中的位置，申请到之后，直接在该位置写入或者读取数据。整个过程通过原子变量CAS，保证操作的线程安全。

### 一个生产者

生产者单线程写数据的流程比较简单：
1. 申请写入m个元素；
2. 若是有m个元素可以入，则返回最大的序列号。这儿主要判断是否会覆盖未读的元素；
3. 若是返回的正确，则生产者开始写入元素。

### 多个生产者

多个生产者的情况下，会遇到"如何防止多个线程重复写同一个元素"的问题。Disruptor的解决方法是，每个线程获取不同的一段数组空间进行操作。这个通过CAS很容易达到。只需要在分配元素的时候，通过CAS判断一下这段空间是否已经分配出去即可。

但是会遇到一个新问题：如何防止读取的时候，读到还未写的元素。Disruptor在多个生产者的情况下，引入了一个与Ring Buffer大小相同的buffer：available Buffer。当某个位置写入成功的时候，便把availble Buffer相应的位置置位，标记为写入成功。读取的时候，会遍历available Buffer，来判断元素是否已经就绪。

**读数据**：生产者多线程写入的情况会复杂很多。读线程读到下标为2的元素，三个线程Writer1/Writer2/Writer3正在向RingBuffer相应位置写数据，写线程被分配到的最大元素下标是11。读线程申请读取到下标从3到11的元素，判断writer cursor>=11。然后开始读取availableBuffer，从3开始，往后读取，发现下标为7的元素没有生产成功，于是WaitFor(11)返回6。然后，消费者读取下标从3到6共计4个元素。

**写数据**：多个生产者写入时，申请写入m个元素；若是有m个元素可以写入，则返回最大的序列号。每个生产者会被分配一段独享的空间；生产者写入元素，写入元素的同时设置available Buffer里面相应的位置，以标记自己哪些位置是已经写入成功的。

防止不同生产者对同一段空间写入的代码：

```java
public long tryNext(int n) throws InsufficientCapacityException {
    if (n < 1) {
        throw new IllegalArgumentException("n must be > 0");
    }
    long current;
    long next;
    do {
        current = cursor.get();
        next = current + n;
        if (!hasAvailableCapacity(gatingSequences, n, current)) {
            throw InsufficientCapacityException.INSTANCE;
        }
    } while (!cursor.compareAndSet(current, next));
    return next;
}
```

通过do/while循环的条件cursor.compareAndSet(current, next)，来判断每次申请的空间是否已经被其他生产者占据。假如已经被占据，该函数会返回失败，While循环重新执行，申请写入空间。

## 总结

Disruptor通过精巧的无锁设计实现了在高并发情形下的高性能。在美团内部，很多高并发场景借鉴了Disruptor的设计，减少竞争的强度。其设计思想可以扩展到分布式场景，通过无锁设计，来提升服务性能。

## 性能

依据并发竞争的激烈程度的不同，Disruptor比ArrayBlockingQueue吞吐量快4~7倍。按照Pipeline: 1P–3C的连接模式测试延迟，平均延迟差了3个数量级（ArrayBlockingQueue约32,757ns vs Disruptor约52ns）。

## 等待策略

生产者的等待策略：暂时只有休眠1ns（LockSupport.parkNanos(1)）。

消费者的等待策略：

| 名称 | 措施 | 适用场景 |
|------|------|----------|
| BlockingWaitStrategy | 加锁 | CPU资源紧缺，吞吐量和延迟并不重要的场景 |
| BusySpinWaitStrategy | 自旋 | 通过不断重试减少系统调用延迟，推荐在线程绑定到固定CPU的场景下使用 |
| PhasedBackoffWaitStrategy | 自旋 + yield + 自定义策略 | CPU资源紧缺，吞吐量和延迟并不重要的场景 |
| SleepingWaitStrategy | 自旋 + yield + sleep | 性能和CPU资源之间有很好的折中，延迟不均匀 |
| TimeoutBlockingWaitStrategy | 加锁，有超时限制 | CPU资源紧缺，吞吐量和延迟并不重要的场景 |
| YieldingWaitStrategy | 自旋 + yield + 自旋 | 性能和CPU资源之间有很好的折中，延迟比较均匀 |

## Log4j 2应用场景

Log4j 2相对于Log4j 1最大的优势在于多线程并发场景下性能更优。该特性源自于Log4j 2的异步模式采用了Disruptor来处理。在Log4j 2的配置文件中可以配置WaitStrategy，默认是Timeout策略。

loggers all async采用的是Disruptor，而Async Appender采用的是ArrayBlockingQueue队列。单线程情况下，两者吞吐量相差不大，但是在64个线程的时候，loggers all async的吞吐量比Async Appender增加了12倍，是Sync模式的68倍。

美团在公司内部统一推行日志接入规范，要求必须使用Log4j 2，使普通单机QPS的上限不再只停留在几千，极高地提升了服务性能。

## 参考文档

1. http://brokendreams.iteye.com/blog/2255720
2. http://ifeve.com/dissecting-disruptor-whats-so-special/
3. https://github.com/LMAX-Exchange/disruptor/wiki/Performance-Results
4. https://lmax-exchange.github.io/disruptor/
5. https://logging.apache.org/log4j/2.x/manual/async.html

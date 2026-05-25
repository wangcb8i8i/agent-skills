---
name: research-report
description: 自动化的深度研究引擎。给方向，拿结论——Scope 确认后全自动执行，只在起点和终点需要你。
version: 2.0.0
---

<objective>
把「一个问题」变成「一份可拍板的结论」，全程无需用户介入中间过程。不是协作式研究助手——是委托式研究引擎：你定方向，我做研究，你拿结果。
</objective>

<triggers>
  <trigger>用户显式调用 /research [主题]</trigger>
  <never>绝不自动触发。用户不召唤则不出场。</never>
</triggers>

<llm critical="true">
  <mandate>SCOPE 阶段确认后，自动进入研究执行，不再询问用户确认</mandate>
  <mandate>研究执行期间，每完成一个内部阶段给出 1 句话进度更新（非中断式）</mandate>
  <mandate>所有事实性主张必须标注来源，无法确认的明确标注「假设」</mandate>
  <mandate>不伪造信息。不确定就是不确定。</mandate>
  <mandate>分析保持中立。有反对证据就呈现反对证据。</mandate>
  <mandate>输出语言与用户输入语言一致（中文输入→中文输出）</mandate>
</llm>

<flow>
  <!-- ==================== PHASE 1: SCOPE ==================== -->
  <phase id="scope" title="SCOPE — 定方向">

    <goal>把用户的研究兴趣转化为有明确边界的研究任务。这是唯一需要用户深度参与的阶段。</goal>

    <step n="1" name="问题澄清">
      <action>如果用户输入是短语（如"AI 应用落地场景"），引导明确：
        - 想问的具体是什么？（市场格局？投资机会？技术成熟度？）
        - 从哪个视角？（创业者/投资人/企业采购？）
      </action>
      <action>如果用户输入已经具体，确认即可，不强行追问</action>
      <action>识别研究类型（投资判断/技术趋势/产品决策/行业调研/生活经验），后续流程据此自适应</action>
    </step>

    <step n="2" name="锚定点确认">
      <principle>锚定点是用户约束研究方向的唯一机制——中间不再有机会调整。</principle>
      <action>确认用户的锚定点——即：有什么具体要求、关注角度、排除项？</action>
      <examples>
        - "重点关注中美对比"
        - "只考虑 2025 年以后的数据"
        - "不看以太坊生态"
        - "从开发者体验角度切入"
        - "帮我对标这几个竞品：X, Y, Z"
      </examples>
      <action>锚定点不足时，引导补充以下边界：
        - 时间范围（近 1 年/近 3 年/不限）
        - 地域范围（全球/中国/特定市场）
        - 排除项（哪些子话题不需要涉及）
      </action>
    </step>

    <step n="3" name="已有知识注入" optional="true">
      <action>用户可在此提供已掌握的信息或材料——跳过不提供不影响流程。</action>
      <options>
        - 已了解的关键信息或事实
        - 已读过的研究、报道、分析
        - 偏好的信息源（特定媒体/作者/数据库）
        - 需要参考的原始材料（文档、数据、链接）
      </options>
      <principle>如用户提供了原始材料，SCAN Lens 自动激活，在所有 Lens 之前首先执行，在用户材料中定位相关段落。</principle>
      <principle>如用户提供了已知信息，研究应聚焦于补充未知部分，不重复已知内容。</principle>
    </step>

    <step n="4" name="深度设定">
      <question>需要多深？</question>
      <levels>
        <level id="1">快速扫描（~30 min）—— 关键事实 + 1-2 个核心判断</level>
        <level id="2">标准简报（~2h）—— 完整 Lens 分析 + 结论 + 来源</level>
        <level id="3">深度报告（~半天）—— 全部 Lens + 交叉验证 + 多假设推演</level>
      </levels>
      <default>Level 2</default>
    </step>

    <step n="5" name="格式选择">
      <principle>产出格式在 Scope 阶段决定，避免研究完成后再让用户做选择。</principle>
      <question>需要什么格式？</question>
      <options>
        <option id="full">Full Report —— 完整报告，含分析过程（默认）</option>
        <option id="brief">Executive Brief —— 1 页简报，核心结论 + 建议</option>
        <option id="slides">Slide Deck —— 逐页要点，Mermaid 提纲</option>
        <option id="mindmap">Mind Map —— Mermaid 思维导图</option>
      </options>
      <default>Full Report</default>
    </step>

    <step n="6" name="Scope 确认">
      <output>
        ## 研究任务确认

        **研究问题**: {一句话核心问题}
        **研究类型**: {投资判断/技术趋势/产品决策/行业调研/生活经验/知识储备}
        **锚定点**: {用户指定的约束条件}
        **范围**: 时间={} / 地域={} / 排除={}
        **深度**: Level {}
        **格式**: {Full Report / Executive Brief / Slide Deck / Mind Map}
        **已有材料**: {有，共 N 份 / 无}

        确认以上方向无误？确认后我将自动执行研究，完成后给你完整报告。
      </output>
    </step>
  </phase>

  <!-- ==================== PHASE 2: AUTO-RESEARCH ==================== -->
  <phase id="auto-research" title="AUTO-RESEARCH — 自动研究执行">
    <goal>用户确认 Scope 后，全自动完成信息检索、筛选、分析与综合。无需用户介入。</goal>

    <principle>
      <mandate>中间不询问用户意见。遇到缺口、矛盾、不确定，自主决策并记录，在报告中呈现。</mandate>
      <mandate>每完成一个内部步骤，用 1 句话非中断式更新进度（如「正在分析信息…」）。</mandate>
      <mandate>如果搜索结果为 0 或信息严重不足，继续往下做——在报告中标注信息缺口，而不是卡住问用户。</mandate>
      <mandate>锚定点是硬约束——搜索、筛选、分析、建议的全过程都受锚定点限制，不得偏离。</mandate>
      <mandate>根据深度级别调整执行量：Level 1 快速收敛，Level 2 正常展开，Level 3 穷尽覆盖。</mandate>
    </principle>

    <!-- 1. 搜索 -->
    <subphase id="auto-search" title="搜索">
      <action>根据核心问题和锚定点，生成多组搜索关键词覆盖不同角度（Level 1: 2-3 组 / Level 2: 3-5 组 / Level 3: 5+ 组）</action>
      <action>锚定点直接映射为搜索约束——时间锚定→过滤年份，地域锚定→限定市场，排除项→剔除关键词</action>
      <action>确保信源多元化：行业报告 + 一手信息 + 新闻报道 + 社区讨论 + 学术/技术文献，至少覆盖 3 类</action>
      <action>去重后保留核心材料（Level 1: 3-5 篇 / Level 2: 5-15 篇 / Level 3: 15+ 篇），每份生成 passport（标题/来源/日期/标签/摘要/可信度初评）</action>
      <action>主动检查信息缺口——对照锚定点的每个维度，如果某个关键角度没有覆盖到，补搜</action>
    </subphase>

    <!-- 2. 筛选 -->
    <subphase id="auto-filter" title="筛选">
      <action>对每份材料做相关性分级：★★★ 直接相关 / ★★ 间接相关 / ★ 弱相关</action>
      <action>锚定点作为相关性判断的加权条件——满足锚定点约束的材料提升优先级</action>
      <action>对 ★★★ 和 ★★ 材料做四维可信度评估：来源权威性 / 数据可验证性 / 时效性 / 潜在偏见</action>
      <action>标注来源间的矛盾点，留到分析阶段处理</action>
    </subphase>

    <!-- 3. 分析 -->
    <subphase id="auto-analyze" title="分析">
      <principle>根据研究类型自动选择 Lens 组合，锚定点调整 Lens 优先级和侧重。</principle>

      <step name="Lens 自适应选择">
        <action>基于研究类型选择核心 Lens（Level 1: 2-3 个 / Level 2: 3-5 个 / Level 3: 5-7 个）：</action>
        <mapping>
          <type name="投资判断">/DEEP → /ANGLE → /HYP → /CHALLENGE → /ACTION</type>
          <type name="行业调研">/DEEP → /ANGLE → /TIMELINE → /VOICES → /HYP → /CHALLENGE → /ACTION</type>
          <type name="技术趋势">/DEEP → /TIMELINE → /VOICES → /HYP → /MIX → /CHALLENGE</type>
          <type name="产品决策">/VOICES → /DEEP → /ANGLE → /CHALLENGE → /FIRST-PRINCIPLES → /ACTION</type>
          <type name="生活经验">/VOICES → /ANGLE → /DEEP → /CHALLENGE → /ACTION</type>
          <type name="知识储备">/DEEP → /ANGLE → /TIMELINE → /VOICES → /MIX → /CHALLENGE</type>
        </mapping>
        <action>根据锚定点调整 Lens 组合——「对比」→ 强化 /ANGLE，「风险」→ 强化 /CHALLENGE，「怎么做」→ 强化 /ACTION，「为什么」→ 强化 /DEEP</action>
        <action>对于 Level 1，从完整序列中取前 N 个最核心的 Lens</action>
      </step>

      <step name="Lens 逐个执行">
        <action>按选定顺序逐个执行 Lens，每个 Lens 的输出标注信息来源</action>
        <action>每个 Lens 执行时，以锚定点为分析边界——只关注锚定点范围内的发现</action>
      </step>
    </subphase>

    <!-- 4. 综合 -->
    <subphase id="auto-synthesize" title="综合">
      <action>汇总所有 Lens 核心发现，每条标注：来源 + Lens + 置信度</action>
      <action>交叉验证：多来源确认 → 升级置信度；单来源 → 标注待验证；矛盾 → 分析原因</action>
      <action>对矛盾点给出裁决或保留双方立场</action>
      <action>按「置信度 × 影响力」矩阵排序所有发现，锚定点指向的维度给予更高影响力权重</action>
      <action>生成可执行建议（Level 1: 1-3 条 / Level 2: 3-5 条 / Level 3: 5-8 条），每条含：行动 + 预期效果 + 主要风险 + 前置条件</action>
      <action>建议必须回应用户的锚定点——每条建议标注回应了哪个锚定约束</action>
    </subphase>

    <!-- 5. 异常降级 -->
    <subphase id="auto-degradation" title="异常降级">
      <principle>遇到信息障碍时不卡住、不硬推、不伪造。按场景执行对应降级策略，所有异常状态带入报告。</principle>

      <scenario id="no-results" name="搜索无结果或信息严重不足">
        <trigger>某关键词搜索返回 <3 条有效结果，或整体材料池 < 最低门槛（L1: 2 篇 / L2: 3 篇 / L3: 5 篇）</trigger>
        <degradation>
          <step>放宽搜索约束：去掉时间/地域限制 → 扩展同义词 → 上探一级话题（如「XX 赛道竞争格局」→「XX 行业概况」）</step>
          <step>切换信源类型：学术无结果 → 搜行业媒体、社区讨论；英文无结果 → 搜中文，反之亦然</step>
          <step>若仍不足，启动「类比外推」：找相邻领域的类似模式作为参考（标注为「类比推断，非直接证据」）</step>
          <step>最终仍不足 → 报告标注「信息缺口：{具体缺什么}」，跳过该维度的结论，不强行给出判断</step>
        </degradation>
      </scenario>

      <scenario id="contradiction" name="来源信息矛盾">
        <trigger>同一事实维度上 ≥2 个来源给出了冲突的信息或判断</trigger>
        <degradation>
          <step>定位矛盾点：具体是数据冲突、方向判断冲突、还是归因冲突？</step>
          <step>来源可信度加权对比：权威性高、时效性新、有原始数据的来源优先</step>
          <step>检查时间差：矛盾是否来自不同时间点的快照（如 2023 的数据 vs 2025 的数据），如果是，以最新为准并标注变化趋势</step>
          <step>无法裁决 → 保留双方立场，标注「来源分歧」，降级该结论的置信度</step>
        </degradation>
      </scenario>

      <scenario id="low-quality" name="来源质量偏低">
        <trigger>★★★ 材料中 >50% 可信度评分 < 3/5，或主要来源为自媒体、匿名社区帖、无数据支撑的观点文</trigger>
        <degradation>
          <step>降级标注：所有来自低质量源的结论标注「低置信度：来源为{类型}，未经独立验证」</step>
          <step>三角定位：用 2+ 个独立低质量源交叉印证同一事实，提升为「中等置信度：多源交叉一致」</step>
          <step>补充搜索：针对性搜索高质量源（行业报告、学术论文、一手数据）验证关键主张</step>
          <step>报告中诚实呈现：「本话题可获取的高质量信息有限，以下结论基于{来源类型}，建议以{具体方式}进一步验证」</step>
        </degradation>
      </scenario>

      <scenario id="language-gap" name="语言壁垒">
        <trigger>关键市场的信息主要存在于模型无法直接检索的语言中（如仅中文/仅英文/仅小语种）</trigger>
        <degradation>
          <step>切换搜索语言重试</step>
          <step>仍无法获取 → 标注「语言壁垒：{语言}信息未充分覆盖」，不影响已有语言的结论质量</step>
        </degradation>
      </scenario>
    </subphase>
  </phase>

  <!-- ==================== PHASE 3: REPORT ==================== -->
  <phase id="report" title="REPORT — 输出结论">

    <goal>产出可直接用于决策的研究报告。格式已在 Scope 阶段确定。</goal>

    <step n="1" name="自适应报告生成">
      <principle>报告结构根据研究类型和深度级别自适应，不是固定模板。</principle>

      <common-sections>
        <section id="executive_summary">
          <name>执行摘要</name>
          <content>核心发现（1-2 句）+ 最强推荐（1 句）+ 关键风险（1 句）</content>
        </section>
        <section id="key_findings">
          <name>核心发现</name>
          <content>3-5 条，按「置信度 × 影响力」排序</content>
        </section>
        <section id="analysis">
          <name>分析过程</name>
          <content>按使用的 Lens 组织，每条结论可追溯至来源</content>
        </section>
        <section id="action_section" conditional="true">
          <name>行动章节（根据研究类型选择）</name>
          <principle>不是所有研究都需要行动建议。根据类型选择合适的收尾板块。</principle>
          <mapping>
            <type name="投资判断">行动建议 — 3-5 条，格式：行动 / 预期效果 / 风险 / 前置条件</type>
            <type name="产品决策">行动建议 — 3-5 条，格式：行动 / 预期效果 / 风险 / 前置条件</type>
            <type name="生活经验">行动建议 — 3-5 条，格式：行动 / 预期效果 / 风险 / 前置条件</type>
            <type name="行业调研">战略含义 — 对行业格局意味着什么，对不同类型的参与者有何影响</type>
            <type name="技术趋势">关键信号 — 需要持续关注的先行指标 + 入场时机的判断框架</type>
            <type name="知识储备">推荐学习路径 — 从哪里开始、进阶路线、核心资源索引</type>
          </mapping>
        </section>
        <section id="uncertainties">
          <name>不确定性与反论</name>
          <content>关键不确定性 + 可能改变结论的条件 + 反面观点</content>
        </section>
        <section id="sources">
          <name>来源</name>
          <content>主要来源列表 + 整体置信度评估</content>
        </section>
      </common-sections>

      <type-adaptations>
        <type name="投资判断">强化「风险矩阵」和「情景分析」部分；增加「如果判断错误，可能漏掉什么」</type>
        <type name="技术趋势">强化「时间线」和「成熟度评估」；增加「采用曲线位置判断」</type>
        <type name="行业调研">强化「产业链图谱」和「竞争格局」；增加「政策/监管环境」</type>
        <type name="产品决策">强化「竞品对比」和「用户需求映射」；增加「实施路线图建议」</type>
        <type name="生活经验">强化「实操建议」和「成本/收益分析」；精简理论分析</type>
        <type name="知识储备">强化「概念体系」和「知识全景」</type>
      </type-adaptations>

      <depth-adaptations>
        <level id="1">仅执行摘要 + 核心发现 + 行动章节，不展开分析过程</level>
        <level id="2">完整报告，含分析过程引用</level>
        <level id="3">完整报告 + 附录（详细 Lens 输出 + 来源全文摘要 + 假设推演场景）</level>
      </depth-adaptations>
    </step>

    <step n="2" name="追问入口">
      <principle>报告输出后默认自动保存。用户可对任意发现聚焦深挖，无需重新发起完整研究。</principle>
      <action>报告末尾附提示：「报告已保存。如需深挖某个发现，回复"追问 + 问题"即可。」</action>
      <mechanism>
        <step>基于已有研究上下文，生成 2-3 组定向搜索关键词</step>
        <step>仅执行 /DEEP + 一个上下文匹配的 Lens（对比→/ANGLE，风险→/CHALLENGE，怎么做→/ACTION）</step>
        <step>增量输出至已有报告末尾，不覆盖原文</step>
      </mechanism>
    </step>
  </phase>
</flow>

<lens_catalog>
  <description>分析视角工具箱。每个 Lens 是一种特定的问题拆解方式。系统根据研究类型自动选择 3-5 个。</description>

  <lens id="deep" name="/DEEP" title="深度事实挖掘">
    <goal>穿透表象，理解本质。对一个主题进行分层深挖。</goal>
    <method>
      <step>第一层：What —— 事实是什么？（数据、事件、时间线）</step>
      <step>第二层：How —— 怎么运作的？（机制、流程、因果关系）</step>
      <step>第三层：Why —— 为什么会这样？（驱动力、结构因素、历史脉络）</step>
    </method>
    <output>主题的完整画像：事实层 + 机制层 + 动因层</output>
  </lens>

  <lens id="angle" name="/ANGLE" title="多角度对比">
    <goal>通过对比暴露差异，发现被单一视角掩盖的信息。</goal>
    <method>
      <step>选取 2-4 个对比维度（竞品之间 / 不同地区 / 不同时期 / 行业 vs 学术视角）</step>
      <step>逐维度列出相同点和不同点</step>
      <step>差异背后的原因分析</step>
    </method>
    <output>对比矩阵 + 关键差异解读</output>
  </lens>

  <lens id="hyp" name="/HYP" title="假设推演">
    <goal>不满足于描述现状，推演可能的未来。</goal>
    <method>
      <step>基于现有信息，生成 2-3 个合理假设（6-12 个月内的可能变化）</step>
      <step>每个假设标注：触发条件 + 概率评估 + 影响程度</step>
      <step>识别早期信号指标——什么发生时说明该假设正在成真</step>
    </method>
    <output>假设清单，附触发条件和早期信号</output>
  </lens>

  <lens id="challenge" name="/CHALLENGE" title="挑战与反面证据">
    <goal>主动寻找反面证据和逻辑漏洞。对抗确认偏误。</goal>
    <method>
      <step n="1" name="定位核心主张">
        <action>从已有分析中提取 3-5 个最强的结论性主张（「X 是 Y」「A 导致 B」「C 赛道最有前景」）</action>
        <action>每个主张标注其依赖的关键前提——如果前提不成立，结论就不成立</action>
      </step>
      <step n="2" name="反向搜索">
        <action>针对每个主张，用否定句式构造搜索词：「X 失败案例」「X 的局限性」「为什么 X 不行」「X 的批评」「X 过时」</action>
        <action>专门搜索持反对立场的信息源（做空报告、批评文章、竞对分析、学术 rebuttal）</action>
        <action>找 1-2 个该主张被证伪的真实案例（如「看好 XX 赛道的投资后来为什么亏了」「某技术被替代的时间线」）</action>
      </step>
      <step n="3" name="压力测试">
        <action>数据层：数据来源是否可复现？样本是否代表总体？统计口径是否一致？是否存在幸存者偏差？</action>
        <action>逻辑层：相关关系是否被当作因果关系？是否存在遗漏变量？结论是否过度外推？</action>
        <action>假设层：结论依赖的假设如果反转（如「监管政策不变」→「监管突然收紧」），结论还成立吗？</action>
      </step>
      <step n="4" name="立场审计">
        <action>逐一标注每个主要来源的立场和潜在利益：卖方报告→做多倾向，被投企业 PR→美化倾向，学术论文→发表偏误（positive results 更易发表）</action>
        <action>检查：如果我方结论被这些偏见系统性影响，最可能的偏误方向是什么？（过度乐观/过度悲观/忽略尾部风险）</action>
      </step>
    </method>
    <output>主张瓦解清单（每条含：主张 / 反面证据 / 逻辑漏洞 / 偏误方向 / 幸存置信度）</output>
  </lens>

  <lens id="action" name="/ACTION" title="行动转化">
    <goal>把分析变成决策。发现如果不转化为行动，等于没有发现。</goal>
    <method>
      <step>基于当前结论，可以做什么？</step>
      <step>每项行动的约束条件是什么？（资源/时间/能力）</step>
      <step>成功的定义是什么？如何验证？</step>
    </method>
    <output>可执行行动清单，每条附约束条件和成功标准</output>
  </lens>

  <lens id="first-principles" name="/FIRST-PRINCIPLES" title="第一性原理">
    <goal>抛开现有方案和行业惯例，从最基础的真理重新拆解问题。</goal>
    <method>
      <step>这个问题的最底层元素是什么？</step>
      <step>抛开现有解决方案，如果从零开始会怎么做？</step>
      <step>哪些"常识"其实是未经检验的假设？</step>
    </method>
    <output>重新定义的问题框架 + 被打破的假设 + 可能的替代方案</output>
  </lens>

  <lens id="voices" name="/VOICES" title="利益相关方映射">
    <goal>理解不同参与者的立场、动机和信息差。</goal>
    <method>
      <step>列出所有关键利益相关方</step>
      <step>每方：他们知道什么？想要什么？怕什么？</step>
      <step>各方之间的利益一致/冲突关系</step>
    </method>
    <output>利益相关方地图 + 张力点标注</output>
  </lens>

  <lens id="timeline" name="/TIMELINE" title="演化追踪">
    <goal>通过时间线发现模式：趋势、拐点、周期性。</goal>
    <method>
      <step>按时间排列关键事件</step>
      <step>标注加速/减速期、拐点</step>
      <step>识别驱动阶段变化的关键因素</step>
    </method>
    <output>时间线 + 阶段划分 + 关键拐点标注</output>
  </lens>

  <lens id="mix" name="/MIX" title="跨界连接">
    <goal>发现非显然的跨领域/跨主题关联。</goal>
    <method>
      <step>当前话题与哪些看似不相关的领域有结构相似性？</step>
      <step>其他行业/领域有没有可类比的模式或教训？</step>
      <step>有没有"奇怪"的数据点可能暗含重要信号？</step>
    </method>
    <output>跨界关联清单 + 可迁移洞察</output>
  </lens>

  <lens id="scan" name="/SCAN" title="快速语义扫描">
    <goal>快速定位语料库中与特定查询相关的段落，用于定向查找。</goal>
    <method>
      <step>指定查询词或概念</step>
      <step>扫描所有材料中相关段落</step>
      <step>汇总 + 标注出处</step>
    </method>
    <output>精确引用 + 段落摘要</output>
    <note>条件 Lens：仅在用户于 Scope 阶段提供了原始材料时激活。在所有 Lens 之前首先执行，在用户提供的材料中快速定位相关段落。无用户材料时不出现在 Lens 序列中。</note>
  </lens>
</lens_catalog>

<quality_gates>
  <gate phase="scope">
    <check>核心问题可操作（不是兴趣短语，而是可回答的问题）</check>
    <check>锚定点明确（知道查什么，也知道不查什么）</check>
    <check>研究类型已识别，Lens 组合可确定</check>
  </gate>

  <gate phase="report">
    <check>所有事实性主张有来源标注</check>
    <check>结论有置信度标注</check>
    <check>建议可执行（不是「要关注 XX」而是「做 XX，因为 YY，风险是 ZZ」）</check>
    <check>信息缺口已诚实标注</check>
  </gate>
</quality_gates>

<output_artifacts>
  <artifact>
    <path>docs/research/{topic-slug}-{date}.md</path>
    <description>研究报告，格式根据研究类型和深度级别自适应</description>
  </artifact>
</output_artifacts>

<operating_rules>
  <rule id="1" name="委托模式">
    Scope 确认后即进入自动模式。用户如果想中途介入，可以打断，但系统默认不等待用户确认。
  </rule>
  <rule id="2" name="来源必追溯">
    每个关键主张（非常识）标注出处。无法确认的标「假设」或「待验证」。
  </rule>
  <rule id="3" name="不确定就说">
    不确定的数据、矛盾的来源、推断的局限——诚实呈现。比假装确定更有价值。
  </rule>
  <rule id="4" name="自适应深度">
    Level 1 → 关键事实 + 1-2 判断，不展开全部 Lens
    Level 2 → 完整流程，3-5 Lens
    Level 3 → 全 Lens + 深度交叉验证 + 附录
  </rule>
  <rule id="5" name="输出语言">
    用户用中文提问 → 中文输出。用户用英文提问 → 英文输出。
  </rule>
  <rule id="6" name="缺省不补搜">
    除非信息严重不足以致无法形成任何结论，否则不自动发起第二轮搜索。缺口在报告中标注，而不是无限迭代。
  </rule>
</operating_rules>

<success_criteria>
  <criterion>Scope 确认后，用户不再需要参与中间过程</criterion>
  <criterion>结论有置信度标注和来源追溯</criterion>
  <criterion>建议具体可执行</criterion>
  <criterion>研究类型自适应生效——不同话题的报告结构不同</criterion>
</success_criteria>

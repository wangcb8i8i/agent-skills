---
name: research-report
description: 自动化的深度研究引擎。给方向，拿结论——Scope 确认后全自动执行，只在起点和终点需要你。
version: 3.0.0
---

<objective>
把「一个问题」变成「一份可拍板的结论」——不只是描述事实，而是穿透到因果层、支撑具体决策。全程无需用户介入中间过程。不是协作式研究助手——是委托式研究引擎：你定方向，我做研究，你拿结果。
</objective>

<root_value>
  这技能存在的唯一理由是：让用户拿到报告后能直接做决策——不管是「投」还是「不投」还是「再等一个信号」。
  所有内部设计决策，当两条原则冲突时，由这条裁决：哪条让最终决策更可靠？
</root_value>

<triggers>
  <trigger>用户显式调用 /research [主题]（默认 Single Pass 模式）</trigger>
  <trigger>用户显式调用 /research --deep [主题]（强制 Deep 模式）</trigger>
  <trigger>用户说「深入调研/深入研究/深度分析/搞透 [主题]」时，自动选择 Deep 模式</trigger>
  <never>绝不自动触发。用户不召唤则不出场。</never>
</triggers>

<llm critical="true">
  <mandate>SCOPE 阶段确认后，自动进入研究执行，不再询问用户确认</mandate>
  <mandate>研究执行期间，每完成一个内部阶段给出 1 句话进度更新（非中断式）</mandate>
  <mandate>所有事实性主张必须标注来源。无法确认的明确标注「假设」或「待验证」。</mandate>
  <mandate>不伪造信息。不确定就是不确定。</mandate>
  <mandate>分析保持中立。有反对证据就呈现反对证据。</mandate>
  <mandate>因果链追问贯穿始终：每个关键发现追问 Why 直到触及结构动因或底层约束。</mandate>
  <mandate>每个关键发现同时回答：这个发现如果为真/为假，改变什么决策？</mandate>
  <mandate>用分析原则引导判断，而非步骤清单约束——理解为什么做，不只是做什么。</mandate>
  <mandate>输出语言与用户输入语言一致（中文输入→中文输出）</mandate>
  <mandate>如果某维度的置信度不足以支撑决策且无法补搜 → 输出「无法形成可行动结论」并列出什么信息能翻盘，不凑一份报告</mandate>
</llm>

<flow>
  <!-- ==================== PHASE 1: SCOPE ==================== -->
  <phase id="scope" title="SCOPE — 定方向">

    <goal>把用户的研究兴趣转化为有明确边界的研究任务。这是唯一需要用户深度参与的阶段。</goal>
    
    <step n="1" name="问题澄清">
      <principle>用户的输入就是起点，不强行追问。根据输入的具体程度做适应性引导，核心是搞清「想知道什么」和「从什么视角」。</principle>
      <action>如果用户输入是短语（如"AI 应用落地场景"），引导明确：
        - 想问的具体是什么？（市场格局？投资机会？技术成熟度？）
        - 从哪个视角？（创业者/投资人/企业采购/研究者？）
        - 这个研究最终要支持什么决策？（选型决策 A vs B / 判断决策 做不做 / 理解决策 了解全景 / 监控决策 关注什么信号）
      </action>
      <action>如果用户输入已经具体，确认即可，不强行追问</action>
      <action>识别研究类型（投资判断/技术趋势/产品决策/行业调研/生活经验/知识储备），后续流程据此自适应</action>
      <action condition="mode-not-yet-decided">检测用户语言中的深度信号：
        - 包含「深入调研」「深入研究」「深度分析」「搞透」等 → 自动选择 Deep 模式
        - 显式使用 `/research --deep` → 强制 Deep 模式
        - 其余 → 默认 Single Pass，在 Step 4.5 让用户选择
      </action>
    </step>
    
    <step n="2" name="锚定点确认">
      <principle>锚定点是用户约束研究方向的唯一机制——中间不再有机会调整。锚定点应该具体到能过滤信息，而不是泛泛的方向。</principle>
      <action>确认用户的锚定点——有什么具体要求、关注角度、排除项？</action>
      <examples>
        - "重点关注中美对比"
        - "只考虑 2025 年以后的数据"
        - "不看以太坊生态"
        - "从开发者体验角度切入"
        - "帮我对标这几个竞品：X, Y, Z"
      </examples>
      <action>锚定点不足时，引导补充边界：
        - 时间范围（近 1 年/近 3 年/不限）
        - 地域范围（全球/中国/特定市场）
        - 排除项（哪些子话题不需要涉及）
      </action>
      <action>确认决策约束条件：
        - 什么时间窗口内需要做这个决策？（紧迫性影响搜索深度）
        - 做错和被误导相比，哪种代价更高？（决定置信度门槛）
      </action>
    </step>
    
    <step n="3" name="已有知识注入" optional="true">
      <principle>用户已有的信息是研究的跳板——不要重复已知，聚焦补充未知。</principle>
      <action>用户可在此提供已掌握的信息或材料——跳过不提供不影响流程。</action>
      <options>
        - 已了解的关键信息或事实
        - 已读过的研究、报道、分析
        - 偏好的信息源（特定媒体/作者/数据库）
        - 需要参考的原始材料（文档、数据、链接）
      </options>
      <principle>如用户提供了原始材料，在常规研究之前首先扫描这些材料，定位相关段落作为背景锚点。</principle>
    </step>
    
    <step n="4" name="格式选择">
      <principle>产出格式在 Scope 阶段决定，统一决策节奏。</principle>
      <question>需要什么格式？</question>
      <options>
        <option id="full">Full Report —— 完整报告（默认）</option>
        <option id="brief">Executive Brief —— 1 页简报（核心结论 + 建议）</option>
        <option id="slides">Slide Deck —— 逐页要点（Mermaid 提纲）</option>
        <option id="mindmap">Mind Map —— Mermaid 思维导图</option>
        <option id="decision-memo">Decision Memo —— 1 页，含：推荐结论 / 关键证据（3条） / 关键不确定性 / 什么新信息会反转本推荐</option>
      </options>
      <default>Full Report</default>
      <principle>格式反映决策场景差异，反向影响研究侧重。Decision Memo → 优先确认 3 条关键证据的置信度；Slide Deck → 优先确保 5-7 个核心 claim 个个站得住；Executive Brief → 深度优先于广度，聚焦 1 个核心判断。</principle>
    </step>
    
    <step n="4.5" name="模式选择" condition="deep-not-auto-triggered">
      <principle>研究模式决定搜索是单次完成还是多轮递归收敛。Deep 模式适合边界模糊、需要层层深入的议题。</principle>
      <question>研究模式偏好？</question>
      <options>
        <option id="single">Single Pass（默认）—— 单次搜索+综合，信息缺口在报告中标注。适合边界清晰的决策问题，追求速度。</option>
        <option id="deep">Deep —— 多轮递归搜索（默认最多 3 轮），直到信息饱和或达到轮次上限。适合开放式深层问题，追求完整度。</option>
      </options>
      <default>Single Pass</default>
    </step>

    <step n="5" name="Scope 确认">
      <output>
        ## 研究任务确认
    
        **研究问题**: {一句话核心问题}
        **研究类型**: {投资判断/技术趋势/产品决策/行业调研/生活经验/知识储备}
        **决策类型**: {选型/判断/理解/监控}
        **决策约束**: {时间窗口 / 错误代价方向 / 排除决策}
        **锚定点**: {用户指定的约束条件}
        **范围**: 时间={} / 地域={} / 排除={}
        **格式**: {Full Report / Executive Brief / Slide Deck / Mind Map}
        **模式**: {Single Pass / Deep (最多 3 轮)}
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
      <mandate>每完成一个内部步骤，用 1 句话非中断式更新进度（如「正在搜索…」「正在分析信息…」）。</mandate>
      <mandate>信息不足时先尝试降级策略补搜。严重不足且无法补搜 → 区分场景：核心决策维度缺信息 → 输出「无法形成结论」；次要维度缺信息 → 继续，标注缺口。</mandate>
      <mandate>锚定点是硬约束——搜索、筛选、分析、建议的全过程都受锚定点限制，不得偏离。</mandate>
      <mandate>因果链追问不是单独的步骤，而是贯穿每个分析环节的思维习惯——每看到一个事实，问「为什么」直到触及结构动因或底层约束。</mandate>
      <mandate>研究不追求速度，追求每层结论的可靠性。搜索覆盖不足就补搜，分析不够深就继续挖。</mandate>
    </principle>
    
    <!-- 1. 搜索 -->
    <subphase id="auto-search" title="搜索">
      <principle>搜索的目的是覆盖核心问题的所有关键角度，而不是凑够数量。锚定点直接映射为搜索约束。</principle>
      <action>根据核心问题和锚定点，生成多组搜索关键词，确保每个锚定维度至少被一组关键词覆盖</action>
      <action>确保信源多元化：行业报告 + 一手信息 + 新闻报道 + 社区讨论 + 学术/技术文献，至少覆盖 3 类</action>
      <action>对每个搜索维度标注"对最终决策的影响程度"：高/中/低。影响程度高的维度优先搜索、优先分配搜索预算（关键词数量和尝试次数）</action>
      <action>去重后保留核心材料（至少 5 篇以上优质材料），每份生成 passport（标题/来源/日期/标签/摘要/可信度初评）</action>
      <action>主动检查信息缺口——对照锚定点的每个维度，如果某个关键角度没有覆盖到，补搜</action>
    </subphase>
    
    <!-- 2. 筛选 -->
    <subphase id="auto-filter" title="筛选">
      <principle>信息质量比数量重要。筛选的核心是回答「这个信息值得信任吗？」「和我的核心问题有关吗？」「它会改变决策吗？」</principle>
      <action>对每份材料做二维评分：
        - 相关度：★★★ 直接相关 / ★★ 间接相关 / ★ 弱相关
        - 决策影响力：◉ 会改变推荐 / ◎ 支撑现有推荐 / ○ 不改变推荐
      </action>
      <action>双高材料（★★★ + ◉）是核心——优先深度阅读。高相关低影响力 → 摘要即可。</action>
      <action>锚定点作为相关性判断的加权条件——满足锚定点约束的材料提升优先级</action>
      <action>对 ★★★ 和 ★★ 材料做四维可信度评估：来源权威性 / 数据可验证性 / 时效性 / 潜在偏见</action>
      <action>标注来源间的矛盾点，留到分析阶段处理</action>
    </subphase>
    
    <!-- 3. 分析 -->
    <subphase id="auto-analyze" title="分析">
      <principle>研究类型决定了分析框架的自然结构——不是套模板，而是从问题本质推导出最适用的拆解方式。下面的 Lens catalog 是分析视角的参考工具箱：如果现有 Lens 能覆盖核心问题的各面，就用它们；如果议题需要独特的拆解方式，自由创建新的 Lens。关键在于覆盖问题的所有关键维度，不在于用了几个 Lens。</principle>

      <step name="建立分析框架">
        <action>先想清楚：这个问题的本质是什么？需要从哪几个角度才能把它说透？</action>
        <action>参考 Lens catalog（见下方），但不受限于它——现有 Lens 是常见分析模式的总结，不是必须遵循的清单</action>
        <action>根据研究类型确定分析重心：
          <mapping>
            <type name="投资判断">多情景对比 + 风险/收益矩阵 + 不对称机会识别</type>
            <type name="行业调研">产业链关系 + 竞争格局 + 结构性变化驱动力</type>
            <type name="技术趋势">成熟度评估 + 演化阶段 + 替代/颠覆可能性</type>
            <type name="产品决策">用户真实需求 + 竞品差异 + 实施可行性</type>
            <type name="生活经验">成本/收益 + 实操条件 + 主要风险</type>
            <type name="知识储备">全景地图 + 核心脉络 + 进阶路径</type>
          </mapping>
        </action>
        <action>锚定点调整分析侧重——「对比」→ 强化多维度对比如 ANGLE，「风险」→ 强化挑战与反面证据，「怎么做」→ 强化行动转化，「为什么」→ 强化因果链深挖</action>
        <action>/CHALLENGE（挑战与反面证据）自动激活——无论选择哪些其他 Lens，对顶部 3 个核心主张执行压力测试：定位主张 → 反向搜索 → 压力测试 → 立场审计</action>
      </step>
    
      <step name="逐角度分析">
        <principle>每个分析角度独立执行，输出标注信息来源。每个角度执行时，以锚定点为分析边界。</principle>
        <principle>因果链是贯穿所有角度的红线——无论从哪个角度切入，遇到关键事实都追问 Why。不是说一次「因为…」就停，而是递归追问直到触及无法继续分解的底层动因或结构约束。</principle>
        <principle>区分近因（proximate cause）和根因（root cause）。某公司裁员是因为收入下降（近因），收入下降是因为核心市场份额被侵蚀（中游），市场被侵蚀是因为技术代际切换没有跟上（根因）。报告呈现要传递这个因果深度，而不只是第一层解释。</principle>
      </step>
    </subphase>
    
    <!-- 4. 综合 -->
    <subphase id="auto-synthesize" title="综合">
      <principle>综合不是罗列发现，而是提炼出最有决策价值的结论。排序标准：「对决策的影响」×「结论的置信度」。</principle>
      <action>汇总所有分析角度的核心发现，每条标注来源和置信度</action>
      <action>交叉验证：多来源确认 → 升级置信度；单来源 → 标注待验证；矛盾 → 分析原因</action>
      <action>对矛盾点给出裁决或保留双方立场</action>
      <action>按「置信度 × 对决策的影响力」排序所有发现，锚定点指向的维度给予更高权重</action>
      <action>生成可执行建议（3-8 条），每条包含：行动 + 预期效果 + 主要风险 + 前置条件</action>
      <action>每条建议标注「反转条件」——什么新发现会让本推荐不成立（1-2 句）</action>
      <action>每条建议标注回应了哪个锚定约束</action>
    </subphase>
    
    <!-- 5. 异常降级 -->
    <subphase id="auto-degradation" title="异常降级">
      <principle>遇到信息障碍时不卡住、不硬推、不伪造。诚实呈现信息状态比假装确定更有价值。</principle>
    
      <scenario id="no-results" name="搜索无结果或信息严重不足">
        <trigger>某关键词搜索返回 <3 条有效结果，或整体材料池 < 5 篇且质量不足</trigger>
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
        <trigger>主要来源为自媒体、匿名社区帖、无数据支撑的观点文</trigger>
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

      <scenario id="decision-gate" name="无法形成可行动结论">
        <trigger>核心决策维度经过降级策略后，置信度仍 < 50%</trigger>
        <degradation>
          <step>输出不是报告，而是「针对你的问题，现有信息不足以形成可行动结论」</step>
          <step>附上如果能获取以下信息可以翻盘：
            - 具体缺什么信息
            - 什么渠道可能找到
            - 找到后预期会如何影响决策</step>
          <step>建议用户决定：继续等 / 换角度 / 基于现有信息但接受更高不确定性</step>
        </degradation>
      </scenario>
    </subphase>

    <!-- 6. 递归循环（仅 Deep 模式） -->
    <subphase id="recursive-loop" title="递归循环">
      <condition>仅 Deep 模式激活。Single Pass 模式跳过此阶段，直接进入 Phase 3。</condition>
      <principle>单次模式到此结束。Deep 模式继续评估覆盖度，未饱和则自动发起补搜，递归收敛至信息饱和或达到轮次上限。</principle>

      <step n="1" name="覆盖度评估">
        <action>对照锚定点的每个维度，评估覆盖度：全面 / 部分 / 空白</action>
        <action>识别置信度偏低（< 70%）的核心主张清单</action>
        <action>计算饱和度指标：本轮新增核心发现数 / 累计总核心发现数 × 100%</action>
        <action>记录当前递归轮次 N</action>
      </step>

      <step n="2" name="关闭标准检查">
        <principle>同时满足 C1~C3 则正常关闭。触发 C4 则强制关闭并在报告中标注缺口。</principle>
        <criterion id="c1">C1: 所有决策关键维度至少「部分覆盖」（非决策关键维度允许空白）</criterion>
        <criterion id="c2">C2: 顶部 3 个决策因子的置信度 ≥ 70%</criterion>
        <criterion id="c3">C3: 连续 2 轮未改变推荐结论</criterion>
        <criterion id="c4">C4: 已达最大轮次上限（默认 3）</criterion>
        <decision>
          C1 + C2 + C3 满足 → 进入 Phase 3 REPORT
          C4 满足 → 进入 Phase 3，报告标注「已达最大轮次，以下维度未充分覆盖」
          否则 → 进入 Step 3
        </decision>
      </step>

      <step n="3" name="生成补搜策略">
        <principle>补搜不重新展开全部分析维度，只针对缺口做定向窄化深挖。</principle>
        <action>空白维度 → 生成 2-3 组扩展搜索词（放宽时间/地域约束、同义扩展、上探一级概念）</action>
        <action>置信度不足的主张 → 搜索验证性或反驳性证据</action>
        <action>未裁决的矛盾点 → 搜索能裁决矛盾的第三方信源（学术文献、官方数据）</action>
        <action>跨维度关联 → 如发现多维度间有因果关联，生成综合搜索词一次覆盖</action>
      </step>

      <step n="4" name="执行补搜">
        <action>将补搜策略送入 Subphase 1（搜索），搜索范围限定为补搜项，不重新展开全部分析维度</action>
        <action>Subphase 1→2→3 窄化执行 → 增量合并到已有发现池，不覆盖原内容</action>
        <action>重新执行 Subphase 4（综合）的交叉验证和建议生成，基于增量后的完整发现池</action>
        <action>回到 Step 1 重新评估覆盖度</action>
      </step>
    </subphase>
  </phase>

  <!-- ==================== PHASE 3: REPORT ==================== -->
  <phase id="report" title="REPORT — 输出结论">

    <goal>产出可直接用于决策的研究报告。格式已在 Scope 阶段确定。报告结构不是固定模板——由研究类型、用户角色、问题粒度共同决定叙事方式。</goal>
    
    <step n="1" name="确定叙事结构">
      <principle>报告结构由核心问题的本质决定，不是套用模板。以下原则指导结构设计，不是章节清单。</principle>

      <principle name="类型驱动主线">
        研究类型决定了报告的「主干逻辑」：
        - 投资判断 → 多情景对比 → 风险矩阵 → 不对称机会 → 行动建议
        - 技术趋势 → 现状与阶段 → 成熟度评估 → 关键信号 → 趋势判断
        - 行业调研 → 产业链条 → 竞争格局 → 驱动/抑制因素 → 战略含义
        - 产品决策 → 用户需求 → 竞品分析 → 选项对比 → 行动路线
        - 生活经验 → 背景全景 → 核心选择 → 实操条件 → 成本收益
        - 知识储备 → 领域地图 → 核心概念 → 脉络关系 → 进阶路径
      </principle>

      <principle name="角色决定视角侧重">
        用户角色影响哪些内容应该前置、哪些应该详述：
        - 创业者/产品人 → 行动路线、可行性、资源条件前置
        - 投资人 → 风险矩阵、回报率、竞争壁垒前置
        - 研究者 → 方法论、数据完整性、信息缺口前置
        - 技术决策者 → 技术对比、迁移路径、兼容性前置
      </principle>

      <principle name="问题粒度决定展开度">
        问题的宽窄决定了报告的深度和广度配比：
        - 宽泛问题（如「SaaS 行业趋势」）→ 全景概览 + 2-3 个深挖点
        - 中等问题（如「中国 CRM 市场竞争格局」）→ 维度展开充分
        - 聚焦问题（如「HubSpot 和 Salesforce 在小企业市场的差异」）→ 单点深挖，不留宽泛章节
      </principle>

      <principle name="叙事递进通用模式">
        无论哪种结构，内容递进应遵循读者认知的自然顺序：背景/现状 → 核心发现 → 深层分析 → 含义/行动。但不作为固定模板——根据研究的具体内容决定最自然的叙事顺序。
      </principle>

      <principle name="决策类型驱动终端结构">
        研究收尾方式由决策类型决定：
        - 选型决策 → 前置对比框架 + 推荐 + 为什么不选其他选项
        - 判断决策 → 前置阈值 + 证据 + 置信度
        - 理解决策 → 全景 → 关键脉络 → 路标（下一步关注什么）
        - 监控决策 → 信号清单 + 阈值 + 响应策略
      </principle>

      <principle name="分析方法不暴露">
        所有内部方法、分析框架、工具代号（如 /DEEP、/ANGLE）一律不出现报告中。读者只看到结论性内容，不需要知道分析过程的方法论。</principle>
    </step>

    <step n="2" name="撰写报告章节">
      <principle>以下章节是报告的常用组件，但不是必须全部使用——根据叙事结构选择最合适的组合。</principle>

      <section id="decision_summary" recommended="always">
        <name>决策摘要</name>
        <content>
          - 推荐结论（1 句）
          - 支撑推荐的关键证据（3 条以内，每条标注置信度和来源）
          - 如果只能记得一件事——the one thing that should influence the decision
          - 主要逆转条件——什么新信息会推翻推荐
        </content>
      </section>

      <section id="body" recommended="always">
        <name>正文</name>
        <principle>正文的章节结构由 Step 1 确定的叙事结构决定。不使用固定模板。</principle>
        <principle>每个主题节的标题以读者最关心的维度命名（如「竞争格局」「技术成熟度评估」「情景分析」），而非分析方法名称。</principle>
        <principle>每个关键结论同时呈现因果链——不只说「X 在增长」，还要说「因为 Y，所以 X 在增长；而 Y 又受 Z 驱动」。</principle>
        <principle>遇到反面证据或争议点，主动呈现，不回避。</principle>
      </section>

      <section id="action_section" conditional="true">
        <principle>不是所有研究都需要行动建议。根据类型选择合适的收尾板块。章节标题直接用下表对应的名字。</principle>
        <mapping>
          <type name="投资判断">行动建议 — 3-5 条，包含退出条件</type>
          <type name="产品决策">行动建议 — 3-5 条，包含实施路线图</type>
          <type name="生活经验">行动建议 — 3-5 条，附成本/收益</type>
          <type name="行业调研">战略含义 — 对行业格局意味着什么，对不同类型的参与者有何影响</type>
          <type name="技术趋势">趋势判断与信号 — 关键先行指标 + 入场时机的判断框架</type>
          <type name="知识储备">知识体系梳理 — 从哪里开始、进阶路线、核心资源索引</type>
        </mapping>
      </section>

      <section id="uncertainties" recommended="always">
        <name>不确定性评估</name>
        <content>
          - 关键不确定性清单
          - 每条标注：如果这个不确定性被消除，是否改变推荐？
            - 会改变 → 高优先级（建议用户优先查证）
            - 不会改变 → 低优先级（可以接受存在）
        </content>
      </section>

      <section id="sources" recommended="always">
        <name>参考来源</name>
        <content>来源列表，按贡献度或主题组织</content>
      </section>
    </step>
    
    <step n="3" name="追问入口">
      <principle>报告输出后默认自动保存。用户可对任意发现聚焦深挖，无需重新发起完整研究。</principle>
      <mechanism>
        <step>基于已有研究上下文，生成 2-3 组定向搜索关键词</step>
        <step>优先搜索可能证明被追问发现错误的证据（决策反转搜索）</step>
        <step>仅对追问点做窄化深挖，不展开全部分析维度</step>
        <step>增量输出至已有报告末尾，不覆盖原文</step>
      </mechanism>
    </step>
  </phase>
</flow>

<lens_catalog>
  <description>分析视角工具箱。每个 Lens 是一种特定的问题拆解方式。这份目录是参考而非约束——它是常见分析模式的总结，但议题需要特定拆解方式时，自由创建新的 Lens。关键是覆盖核心问题的各个关键维度，不在于用了几个 Lens。
  
  /CHALLENGE 在每次研究中对顶部 3 个核心主张自动激活（在分析阶段由流程强制执行），不视为可选 Lens。其余 Lens 按需选择。</description>

  <lens id="deep" name="/DEEP" title="深度因果挖掘">
    <goal>穿透表象，理解本质。对一个主题进行分层深挖，每一层追问 Why 直到触及结构动因或底层约束。</goal>
    <method>
      <step>第一层：What —— 事实是什么？（数据、事件、时间线）</step>
      <step>第二层：How —— 怎么运作的？（机制、流程、因果关系）</step>
      <step>第三层：Why —— 为什么会这样？（驱动力、结构因素、历史脉络）</step>
    </method>
    <principle>关键技巧是「递归追问」——对每个关键发现，追问 2-3 层 Why。不是一次「因为…」就停，而是直到回答触及无法继续分解的底层动因。例如：市场下滑（事实）→ 因为头部客户流失（近因）→ 因为产品代际差距（中游）→ 因为研发投入连续 3 年低于行业均值（根因）。</principle>
    <principle>区分近因（proximate cause）和根因（root cause）。报告呈现必须至少传递两层深度，不能只停留在第一层解释。</principle>
    <output>主题的完整画像：事实层 + 机制层 + 动因层，每层之间标注因果连接</output>
  </lens>

  <lens id="angle" name="/ANGLE" title="多角度对比">
    <goal>通过对比暴露差异，发现被单一视角掩盖的信息。</goal>
    <method>
      <step>选取 2-4 个对比维度（竞品之间 / 不同地区 / 不同时期 / 行业 vs 学术视角）</step>
      <step>逐维度列出相同点和不同点</step>
      <step>差异背后的原因分析——为什么有差异？这说明了什么？</step>
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
        <action>从已有分析中提取 3-5 个最强的结论性主张</action>
        <action>每个主张标注其依赖的关键前提——如果前提不成立，结论就不成立</action>
      </step>
      <step n="2" name="反向搜索">
        <action>针对每个主张，构造否定句式搜索：「X 失败案例」「X 的局限性」「为什么 X 不行」「X 的批评」</action>
        <action>专门搜索持反对立场的信息源（做空报告、批评文章、竞对分析）</action>
      </step>
      <step n="3" name="压力测试">
        <action>数据层：数据来源是否可复现？样本是否代表总体？是否存在幸存者偏差？</action>
        <action>逻辑层：相关关系是否被当作因果关系？是否存在遗漏变量？结论是否过度外推？</action>
        <action>假设层：结论依赖的假设如果反转，结论还成立吗？</action>
      </step>
      <step n="4" name="立场审计">
        <action>逐一标注每个主要来源的立场和潜在利益</action>
        <action>检查：如果我方结论被这些偏见系统性影响，最可能的偏误方向是什么？</action>
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
    <check>核心问题可操作——不是兴趣短语，而是可回答的问题</check>
    <check>锚定点明确——知道查什么，也知道不查什么</check>
    <check>研究类型已识别，分析框架可确定</check>
    <check>决策类型已识别（选型/判断/理解/监控）</check>
    <check>用户知道"得到答案后要做什么"</check>
  </gate>

  <gate phase="report">
    <check>所有事实性主张有来源标注</check>
    <check>结论有置信度标注</check>
    <check>因果链有传递深度——不只是第一层解释</check>
    <check>建议可执行——不是「要关注 XX」而是「做 XX，因为 YY，风险是 ZZ」</check>
    <check>每条关键推荐标注了反转条件</check>
    <check>不确定性章节区分了「值得查证」和「可以接受」</check>
    <check>信息缺口已诚实标注</check>
    <check>报告结构由问题本质驱动，而非固定模板</check>
  </gate>

  <gate phase="recursive" condition="deep-mode">
    <check>所有决策关键维度已覆盖（无空白）或已标注未覆盖原因</check>
    <check>饱和度指标已记录在案</check>
    <check>关闭标准（C1~C4）评估过程可追溯</check>
    <check>递归轮次已达关闭条件，非人为中断</check>
  </gate>
</quality_gates>

<output_artifacts>
  <artifact>
    <path>docs/research/{topic-slug}-{date}.md</path>
    <description>研究报告。受众多为决策者或需要了解该主题的人——只呈现分析结论，不暴露研究方法、分析框架、内部流程。</description>
  </artifact>
</output_artifacts>

<operating_principles>
  <principle id="1" name="委托模式">
    Scope 确认后即进入自动模式。用户如果想中途介入，可以打断，但系统默认不等待用户确认。
  </principle>
  <principle id="2" name="来源必追溯">
    每个关键主张（非常识）标注出处。无法确认的标「假设」或「待验证」。
  </principle>
  <principle id="3" name="不确定就说，且标注决策影响">
    不确定的数据、矛盾的来源、推断的局限——诚实呈现。比假装确定更有价值。
    同时标注：这个不确定如果被消除，是否会改变推荐结论。
  </principle>
  <principle id="4" name="因果链必追问">
    每个关键发现至少追问两层 Why。区分近因和根因，在报告中呈现因果深度，而非停留在表面解释。
  </principle>
  <principle id="5" name="结构由问题驱动">
    不套用固定模板。报告结构由研究类型、用户角色和问题粒度共同决定。
  </principle>
  <principle id="6" name="输出语言">
    用户用中文提问 → 中文输出。用户用英文提问 → 英文输出。
  </principle>
  <principle id="7" name="模式决定搜索策略">
    根据研究模式决定搜索深度。Single Pass：除非信息严重不足以致无法形成结论，否则不自动发起第二轮搜索。Single Pass 模式下如果核心决策维度置信度 < 50%，自动升至 Deep 模式。Deep：递归搜索直到信息饱和或达到轮次上限，缺口在报告中标注。
  </principle>
</operating_principles>

<success_criteria>
  <criterion>Scope 确认后，用户不再需要参与中间过程</criterion>
  <criterion>结论有置信度标注和来源追溯</criterion>
  <criterion>因果链清晰传递——读者能理解「为什么」，不只知道「是什么」</criterion>
  <criterion>建议具体可执行，且回应了锚定约束</criterion>
  <criterion>每条关键推荐标注了反转条件——用户知道什么情况下本推荐应被推翻</criterion>
  <criterion>不确定性评估不是陈列——而是告诉用户哪些不确定性值得跟进</criterion>
  <criterion>用户拿到报告后能直接做出一个决策（哪怕决策是"再等一个信号"）</criterion>
  <criterion>不同类型研究的报告结构差异明显——不是同一模板换标题</criterion>
  <criterion>信息缺口已诚实标注，不假装确定</criterion>
  <criterion condition="deep-mode">递归过程自动收敛（C1~C3满足或C4触发），无需用户判定"够不够深"</criterion>
</success_criteria>

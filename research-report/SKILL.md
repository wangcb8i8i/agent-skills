---
name: research-report
description: 系统化深度研究框架。覆盖问题定义→信息检索→筛选评估→多Lens分析→结论综合→决策级报告全流程。适用于投资研究、行业调研、信息洞察等场景。
version: 1.0.0
---

<objective>
将研究问题转化为决策级研究报告的系统化方法论。不是信息摘要，不是搜索辅助——是从「一个问题」到「一份可拍板的结论」的完整流水线。每一步用户都知道在做什么、为什么这么做。
</objective>

<triggers>
  <trigger>用户显式调用 /research [主题]</trigger>
  <never>绝不自动触发。用户不召唤则不出场。</never>
</triggers>

<llm critical="true">
  <mandate>严格按 Phase 顺序推进，不跳步，不并步</mandate>
  <mandate>每个 Phase 输出完成后，简要告知用户本 Phase 完成，确认后进入下一 Phase</mandate>
  <mandate>所有事实性主张必须标注来源，无法确认的明确标注「假设」</mandate>
  <mandate>不伪造信息。不确定就是不确定。</mandate>
  <mandate>分析保持中立。有反对证据就呈现反对证据。</mandate>
  <mandate>输出语言与用户输入语言一致（中文输入→中文输出）</mandate>
</llm>

<flow>
  <phase id="scope" title="SCOPE — 问题定义与边界">
    <goal>将模糊的研究兴趣转化为可操作的研究问题，设定范围和深度。</goal>

    <step n="1" name="问题澄清">
      <action>如果用户输入是一个短语（如"AI 应用落地场景"），引导用户明确：
        - 想问的具体是什么？（市场格局？投资机会？技术成熟度？）
        - 从哪个视角？（创业者/投资人/企业采购？）
      </action>
      <action>如果用户输入已经具体，确认即可，不强行追问</action>
      <output>1 句话核心研究问题</output>
    </step>
    
    <step n="2" name="范围约束">
      <action>与用户确认三个边界，不明确的主动询问：
        - 时间范围（近 1 年/近 3 年/不限）
        - 地域范围（全球/中国/特定市场）
        - 排除项（哪些子话题不需要涉及）
      </action>
      <output>明确的 in-scope 和 out-of-scope</output>
    </step>
    
    <step n="3" name="用途校准">
      <question>这份研究最终用来做什么？</question>
      <options>投资决策 / 战略规划 / 产品立项 / 知识储备 / 向上汇报 / 对外发表</options>
      <principle>用途决定后续各 Phase 的侧重——投资决策偏风险评估，战略规划偏竞争格局，知识储备偏广度</principle>
    </step>
    
    <step n="4" name="深度设定">
      <question>需要多深？</question>
      <levels>
        <level id="1">快速扫描（30 min 级）—— 关键事实 + 1-2 个核心判断</level>
        <level id="2">标准简报（2h 级）—— 完整 Lens 分析 + 结论 + 来源</level>
        <level id="3">深度报告（半天级）—— 全部 Lens + 交叉验证 + 多假设推演</level>
      </levels>
      <default>Level 2</default>
    </step>
    
    <exit_criteria>
      <required>1 句话核心问题已确认</required>
      <required>时间/地域/排除项已明确</required>
      <required>最终用途已知</required>
      <required>深度级别已设定</required>
    </exit_criteria>
    
    <transition to="search">用户确认 Scope 输出无误后进入 SEARCH</transition>
  </phase>

  <phase id="search" title="SEARCH — 系统化信息检索">
    <goal>围绕核心问题，系统性地从多类信源收集信息，建立初始语料库。</goal>

    <step n="1" name="搜索策略">
      <action>围绕核心问题，生成 3-5 组搜索关键词，覆盖不同角度</action>
      <action>明确信源类型组合（至少 3 类）：
        - 行业报告（券商/咨询/第三方）
        - 一手信息（公司官网/财报/专利/招聘）
        - 新闻报道（科技媒体/财经媒体）
        - 学术/技术文献
        - 社区讨论（Reddit/HN/知乎/专业论坛）
        - 竞品/对标产品
      </action>
      <output>关键词矩阵 + 信源计划</output>
    </step>
    
    <step n="2" name="并行检索">
      <action>按关键词 × 信源类型并行搜索</action>
      <action>去重，保留最相关的 5-15 篇核心材料</action>
      <mandate>优先使用最新、最权威的信息源</mandate>
    </step>
    
    <step n="3" name="Corpus 建档">
      <action>为每份核心材料生成 passport：
        - 标题 + 来源 + 日期
        - 3-5 个关键主题标签
        - 100-200 字核心内容摘要
        - 可信度初评（High/Medium/Low + 简短理由）
      </action>
      <output>语料库总览（列表形式，不超过 1 屏）</output>
    </step>
    
    <step n="4" name="缺口检查">
      <question>有没有应该覆盖但尚未覆盖的角度或信源类型？</question>
      <action>用户指出缺口 → 补充检索 → 更新 Corpus</action>
    </step>
    
    <exit_criteria>
      <required>Corpus 包含 5-15 篇核心材料，每份有 passport</required>
      <required>至少覆盖 3 类信源</required>
      <required>用户确认无重大缺口</required>
    </exit_criteria>
    
    <transition to="filter">Corpus 就绪后进入 FILTER</transition>
  </phase>

  <phase id="filter" title="FILTER — 信息筛选与可信度评估">
    <goal>从语料库中筛出真正可用的信息，评估每份材料的质量，识别信息缺口。</goal>

    <step n="1" name="相关性分级">
      <action>对每份材料标定与核心问题的直接相关度：
        - ★★★ 直接相关 —— 直接回答或覆盖核心问题
        - ★★ 间接相关 —— 提供背景、对比或部分覆盖
        - ★ 弱相关 —— 仅供参考，不作为分析基础
      </action>
      <action>★ 材料进入备用区，不作为主分析输入</action>
    </step>
    
    <step n="2" name="可信度四维评估">
      <dimensions>
        <dim name="来源权威性">谁发布的？该领域公认的信源吗？</dim>
        <dim name="数据可验证性">关键数据能否通过其他来源交叉验证？</dim>
        <dim name="时效性">信息发布时间？是否仍有效？</dim>
        <dim name="潜在偏见">发布方是否有利益相关？是否存在选择性呈现？</dim>
      </dimensions>
      <output>每份 ★★★/★★ 材料的四维评估摘要</output>
    </step>
    
    <step n="3" name="矛盾标注">
      <action>如果不同来源对同一事实给出矛盾信息，显式标注</action>
      <action>不强行裁决，留到 ANALYZE 阶段处理</action>
    </step>
    
    <step n="4" name="缺口识别">
      <action>对照核心问题，识别信息覆盖不足的维度</action>
      <action>缺口严重时，回到 SEARCH 阶段补充检索</action>
    </step>
    
    <exit_criteria>
      <required>★★★ 和 ★★ 材料已完成相关性分级和可信度评估</required>
      <required>矛盾点已标注</required>
      <required>信息缺口已识别（如有）</required>
    </exit_criteria>
    
    <transition to="analyze">筛选完成，确认后进入 ANALYZE</transition>
  </phase>

  <phase id="analyze" title="ANALYZE — Multi-Lens 多维度分析">
    <goal>用多种分析视角拆解信息，从不同维度逼近真相。这是框架的核心。</goal>

    <principle>
      <mandate>不是所有 Lens 每次都用。根据研究问题的性质选择 3-5 个最相关的 Lens。</mandate>
      <mandate>每个 Lens 分析必须标注信息来自 Corpus 中哪些材料</mandate>
      <mandate>Lens 之间允许结论不同甚至矛盾——这是信号，不是问题</mandate>
    </principle>
    
    <step n="1" name="Lens 选择">
      <action>根据研究问题的性质，从 Lens Catalog 中选择 3-5 个</action>
      <default_set>
        <scenario>投资研究</scenario>
        <lenses>/DEEP → /ANGLE → /HYP → /CHALLENGE → /ACTION</lenses>
      </default_set>
      <default_set>
        <scenario>行业调研</scenario>
        <lenses>/DEEP → /ANGLE → /TIMELINE → /VOICES → /ACTION</lenses>
      </default_set>
      <default_set>
        <scenario>信息洞察</scenario>
        <lenses>/DEEP → /MIX → /CHALLENGE → /FIRST-PRINCIPLES → /HYP</lenses>
      </default_set>
    </step>
    
    <step n="2" name="Lens 逐个执行">
      <action>按选定顺序逐个执行 Lens</action>
    
      <!-- Lens 定义见下方 Lens Catalog -->
    </step>
    
    <exit_criteria>
      <required>选定的 3-5 个 Lens 全部完成</required>
      <required>每个 Lens 输出标注了信息来源</required>
      <required>Lens 间的矛盾点已记录</required>
    </exit_criteria>
    
    <transition to="synthesize">分析完成，确认后进入 SYNTHESIZE</transition>
  </phase>

  <phase id="synthesize" title="SYNTHESIZE — 综合与验证">
    <goal>将各 Lens 的独立发现整合为统一结论，交叉验证，识别高置信度判断。</goal>

    <step n="1" name="发现汇总">
      <action>将所有 Lens 的核心发现汇总成清单</action>
      <action>每条发现标注：来源材料 + 产生该发现的 Lens + 置信度（High/Medium/Low）</action>
    </step>
    
    <step n="2" name="交叉验证">
      <action>同一发现被多个独立来源确认 → 置信度升级</action>
      <action>仅单一来源 → 标注「待验证」</action>
      <action>来源间矛盾 → 呈现双方，分析可能原因，给出倾向性判断</action>
    </step>
    
    <step n="3" name="矛盾裁决">
      <action>对 FILTER 阶段标注的矛盾点进行处理：
        - 能裁决的 → 给出判断 + 依据
        - 不能裁决的 → 保留双方立场，说明需要什么额外信息才能裁决
      </action>
      <principle>不做伪调和。诚实比整洁更重要。</principle>
    </step>
    
    <step n="4" name="结论排序">
      <action>按「置信度 × 影响力」矩阵排序所有发现</action>
      <matrix>
        <quadrant>高置信 × 高影响 → 核心结论</quadrant>
        <quadrant>高置信 × 低影响 → 背景事实</quadrant>
        <quadrant>低置信 × 高影响 → 关键不确定性（重点标注）</quadrant>
        <quadrant>低置信 × 低影响 → 附录或舍弃</quadrant>
      </matrix>
    </step>
    
    <step n="5" name="建议生成">
      <action>基于核心结论，生成 3-5 条具体可执行建议</action>
      <format>每条建议：行动是什么 + 预期效果 + 主要风险 + 所需资源/前置条件</format>
    </step>
    
    <exit_criteria>
      <required>核心结论 3-5 条，每条有置信度标注</required>
      <required>矛盾点已处理（裁决或保留）</required>
      <required>建议 3-5 条，格式完整</required>
    </exit_criteria>
    
    <transition to="report">综合完成，确认后进入 REPORT</transition>
  </phase>

  <phase id="report" title="REPORT — 生成决策级研究报告">
    <goal>将研究发现转化为结构清晰、有说服力的研究报告。</goal>

    <step n="1" name="格式选择">
      <question>需要什么形式的输出？</question>
      <options>
        <option id="brief">Executive Brief —— 1 页简报，核心结论 + 建议（适合发高管）</option>
        <option id="full">Full Report —— 完整报告，含全部 Lens 分析过程（适合深度参考）</option>
        <option id="slides">Slide Deck —— 逐页要点，适合汇报演示（提供 Markdown 提纲）</option>
        <option id="mindmap">Mind Map —— Mermaid 格式思维导图，适合理清逻辑</option>
      </options>
      <default>Executive Brief</default>
    </step>
    
    <step n="2" name="报告生成">
      <mandatory_sections>
        <section id="executive_summary">
          <name>Executive Summary</name>
          <content>200-300 字：核心发现（1-2 句）+ 最强推荐（1 句）+ 关键风险（1 句）</content>
        </section>
        <section id="scope_method">
          <name>研究范围与方法</name>
          <content>核心问题 + 范围约束 + 深度级别 + 主要信源类型</content>
          <note>不超过 5 行，读者 10 秒内理解研究边界</note>
        </section>
        <section id="key_findings">
          <name>核心发现</name>
          <content>3-5 条核心发现，按「置信度 × 影响力」排序。每条标注所用 Lens</content>
        </section>
        <section id="recommendations">
          <name>行动建议</name>
          <content>3-5 条，格式：行动 / 预期效果 / 风险 / 前置条件</content>
        </section>
        <section id="uncertainties">
          <name>不确定性与反论</name>
          <content>关键不确定性 + 可能改变结论的条件 + 主要反面观点</content>
        </section>
        <section id="sources">
          <name>来源与置信度</name>
          <content>主要来源列表 + 整体报告置信度（High/Medium/Low + 理由）</content>
        </section>
      </mandatory_sections>
    </step>
    
    <exit_criteria>
      <required>报告包含全部 6 个必要章节</required>
      <required>主张有来源，假设有标注</required>
      <required>结论可追溯至具体 Lens 和 Corpus 材料</required>
    </exit_criteria>
  </phase>
</flow>

<lens_catalog>
  <description>分析视角工具箱。每个 Lens 是一种特定的问题拆解方式。不是全部使用——根据研究场景选择 3-5 个。</description>

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
      <step>当前主流观点或自身初步判断是什么？</step>
      <step>有什么证据与之矛盾？有什么案例不支持它？</step>
      <step>我们可能在哪出错了？数据、逻辑、还是假设？</step>
      <step>利益相关方有哪些偏见可能影响信息？</step>
    </method>
    <output>反面证据清单 + 潜在偏差列表</output>
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
    <note>轻量 Lens，适合在 DEEP 之前做快速定位，或验证某个具体细节</note>
  </lens>
</lens_catalog>

<quality_gates>
  <description>每个 Phase 结束后，必须满足对应条件才能推进。这是铁律，不是建议。</description>

  <gate phase="scope">
    <check>核心问题可操作（不是兴趣短语，而是可回答的问题）</check>
    <check>边界明确（知道查什么，也知道不查什么）</check>
  </gate>

  <gate phase="search">
    <check>Corpus 多元（至少 3 类信源）且充足（5-15 篇核心材料）</check>
    <check>每份材料有 passport</check>
  </gate>

  <gate phase="filter">
    <check>材料已分级（★★★/★★/★）</check>
    <check>核心材料（★★★）已完成四维可信度评估</check>
    <check>矛盾点已标注</check>
  </gate>

  <gate phase="analyze">
    <check>3-5 个 Lens 全部完成，输出可追溯至 Corpus</check>
  </gate>

  <gate phase="synthesize">
    <check>结论有置信度标注，矛盾已处理</check>
    <check>建议可执行（不是"要关注XX"而是"做XX，因为YY，风险是ZZ"）</check>
  </gate>

  <gate phase="report">
    <check>6 个必要章节齐全</check>
    <check>主张可追溯至来源</check>
  </gate>
</quality_gates>

<output_artifacts>
  <artifact>
    <path>docs/research/{topic-slug}-brief.md</path>
    <description>Executive Brief 格式——1 页简报，核心结论 + 建议</description>
  </artifact>
  <artifact>
    <path>docs/research/{topic-slug}-full.md</path>
    <description>Full Report 格式——完整报告，含全部 Lens 分析过程</description>
  </artifact>
</output_artifacts>

<operating_rules>
  <rule id="1" name="不跳步">
    Phase 按顺序执行。如果用户说「直接给我结论」，提醒每个 Phase 对结论质量的保障作用，但不强行违抗用户意愿。
  </rule>
  <rule id="2" name="来源必追溯">
    每个关键主张（非常识）标注出处。无法确认的标「假设」或「待验证」。
  </rule>
  <rule id="3" name="不确定就说">
    不确定的数据、矛盾的来源、推断的局限——诚实呈现。比假装确定更有价值。
  </rule>
  <rule id="4" name="深度配速">
    Level 1（30min）→ 关键事实 + 1-2 判断，不展开全部 Lens
    Level 2（2h）→ 完整流程，3-5 Lens
    Level 3（半天）→ 全 Lens + 深度交叉验证
  </rule>
  <rule id="5" name="输出语言">
    用户用中文提问 → 中文输出。用户用英文提问 → 英文输出。
  </rule>
</operating_rules>

<success_criteria>
  <criterion>6 个 Phase 全部通过 Quality Gate</criterion>
  <criterion>结论有置信度标注和来源追溯</criterion>
  <criterion>建议具体可执行（非泛泛建议）</criterion>
  <criterion>报告包含全部必要章节，可直接用于决策或汇报</criterion>
</success_criteria>

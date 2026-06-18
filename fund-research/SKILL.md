---
name: fund-research
description: 公募基金/ETF/FOF 调查研究。用户手动调用：/research-fund [基金名称/代码]
disable-model-invocation: true
---

<objective>
围绕一个裁决（买/卖/持有/对比）搜索证据、做出判断。输出一份让用户直接能做决定的报告。
</objective>

<leading_word>
基金裁决 — 每个分析维度是呈堂证据，你是法官。核心追问只有三句：
1. 这个证据让你对判断改变多少？
2. 你有多确信？
3. 什么能翻案？

**重要**：这个 leading word 只用于你的分析过程。报告里不出现"裁决""判决""呈堂证据"等词汇。
</leading_word>

<flow>

<phase id="scope" title="定焦">
  <goal>确认基金 + 案由，然后自动开始。用户不需要懂参数。</goal>

  <step n="1" name="确定基金">
    <action>用户输入基金名称或代码。不完整时做模糊匹配引导确认。</action>
    <completion>单一基金已确认。对比案由 → 两到三只基金已确认。</completion>
  </step>

  <step n="2" name="确定案由">
    <principle>案由决定研究重心。用户不知道选什么时，用一句话解释差异后建议一个。</principle>
    <options>
      <option id="buy">买入 — 该不该买？什么时机合适？</option>
      <option id="hold">持有 — 继续持有还是卖出？</option>
      <option id="monitor">监控 — 持续跟踪哪些信号？</option>
      <option id="compare">对比 — A vs B（vs C），选哪个？</option>
    </options>
    <completion>案由已确定。</completion>
  </step>

  <step n="3" name="Scope 确认">
    <principle>管辖范围（时间跨度/比较基准）全部由 agent 默认推理，不询问用户。用户如果明确给出，则使用用户提供的。</principle>
    <action>默认值：
      - 时间跨度：近 1 年（除非历史数据有强信号需要更长窗口）
      - 比较基准：同类均值（股票型/混合型等根据基金类型自动匹配）
      - 排除项：无
    </action>
    <action>输出简短确认：「基金+案由+基准摘要」核对，然后问"开始？"</action>
    <completion>用户确认「开始」或「是」。</completion>
  </step>
</phase>

<phase id="auto-evidence" title="取证">
  <goal>全自动搜索、筛选、分析 10 个维度。中间不询问用户。</goal>

  <principle>
    <mandate>每完成一个维度用 1 句非中断式更新进度。</mandate>
    <mandate>每个关键事实追问 Why 直到触及根因。</mandate>
    <mandate>所有事实性主张标注来源。无法确认的标「待验证」。</mandate>
    <mandate>每个维度同时回答：这个发现如果为真/为假，改变什么结论？</mandate>
  </principle>

  <step name="搜索">
    <action>优先级搜索专业数据源：天天基金 / 晨星 / Choice / 基金年报原文</action>
    <action>每维度至少 1 组定向搜索关键词。决策影响度高的维度优先。</action>
    <action>信息不足时降级：放宽时间 → 扩展同义词 → 上探一级话题。</action>
    <note name="工具约束">
      WebSearch 可能无法直接获取部分专业数据（Brinson 归因、内部持仓穿透等）。
      搜索降级链：
      1. WebSearch 基金名称 + 指标关键词（如"收益率 排名"）
      2. WebFetch 天天基金/晨星公开页面中的可读数据
      3. 仍无法获取 → 标注「数据受限，无法分析」，不在报告中编造数据
    </note>
    <completion>
      每个高影响维度至少有 2 份可引用材料，或已标注「信息有限」。
      整体材料 ≥ 5 篇，或已启动降级路径。
    </completion>
  </step>

  <step name="筛选">
    <action>每份材料二维评分：相关度（★★★/★★/★）和 决策影响力（◉ / ◎ / ○）。</action>
    <action>四维可信度评估：来源权威性 / 数据可验证性 / 时效性 / 潜在偏见。</action>
  </step>

  <step name="10 维分析">
    <action>加载 references/evidence-rules.md 获取各维度指标库和解读方法。</action>
    <action>按决策影响度从高到低执行。每维输出：
      维度名 | 核心指标 | 置信度 | 决策影响度 | 关键证据摘要 | 信息缺口</action>
    <action>对顶部 3 个最影响结论的主张执行反向搜索 + 压力测试。</action>
    <action if="案由为对比">对每只基金独立执行本流程。所有基金取证完毕后，额外构建差异矩阵：关键分歧点 → 推荐方向。</action>
    <completion>10 个维度全部覆盖。高影响维度置信度有明确标注。</completion>
  </step>

  <step name="证据汇总">
    <action>汇总所有维度，按「置信度 × 决策影响力」排序。</action>
    <action>识别 3 条最影响结论的关键证据。</action>
    <action>如果核心维度置信度 < 50% → 输出「信息不足」报告，附翻盘所需信息。</action>
    <completion>3 条关键证据已识别。或已判定证据不足。</completion>
  </step>
</phase>

<phase id="report" title="输出">
  <goal>输出一份用户第一眼就知道该怎么做的报告。格式固定，不询问。</goal>

  <principle>
    <mandate>报告第一条就是结论。用户不应该需要翻页才能知道答案。</mandate>
    <mandate>结论包含「买/不买/持有/卖出/等信号」一词 + 可信度 + 预期收益</mandate>
    <mandate>用户只看到结论和证据，不看到分析方法论。</mandate>
    <mandate>不足 10 行内让用户回答三个问题：怎么做？为什么？多可信？</mandate>
    <mandate>翻案条件和信息缺口已标注</mandate>
    <mandate>不出现"裁决""判决""呈堂证据"等 internal 词汇</mandate>
  </principle>

  <step name="撰写报告">
    <action>报告标题用「{基金名称} — {案由}研究简报」。</action>
    <action>加载 references/verdict-templates.md，使用对应案由的模板填充报告。</action>
    <completion>报告完成。结论以加粗单词开头（买/不买/持有/卖出/等信号）。</completion>
  </step>

  <step name="输出">
    <principle>首次输出直接显示在对话中，用户看完即可决定。文件同时保存到磁盘。</principle>
    <action>输出到对话 + 保存到 docs/research/fund/{基金代码}-{案由}-{日期}.md</action>
  </step>
</phase>

</flow>

<quality_gates>
  <gate phase="scope">
    <check>案由已确定</check>
    <check>基金已确认</check>
    <check>用户只回答了一两个简单问题——没被要求指定技术参数</check>
  </gate>

  <gate phase="evidence">
    <check>10 个维度全部覆盖，未跳过</check>
    <check>高影响维度置信度已显式标注</check>
    <check>反向搜索 + 压力测试已对 top 3 主张执行</check>
    <check>如证据不足 → 已输出「信息不足」报告而非伪造结论</check>
  </gate>

  <gate phase="report">
    <check>报告前 3 行直接给出结论</check>
    <check>结论包含「买/不买/持有/卖出/等信号」一词 + 可信度 + 预期收益</check>
    <check>没有「判决书」「裁决」「呈堂证据」等 internal 词汇</check>
    <check>不讨论分析方法——只呈现结论和证据</check>
    <check>翻案条件已标注</check>
    <check>信息缺口已标注</check>
  </gate>
</quality_gates>

<output>
  <path>docs/research/fund/{基金代码}-{案由}-{日期}.md</path>
  <description>研究报告。受众为需要做投资决策的人。</description>
</output>

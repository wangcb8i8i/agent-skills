---
name: intent-capture
description: Capture user intent through guided conversation when the user is starting something new, expressing ideas incompletely, or says they want to optimize/improve something but cannot yet define the problem clearly.
version: 3.0.0
---

<objective>
Capture, clarify, and confirm the user's real intent through guided conversation when their expression is incomplete, mixed, or still forming.
</objective>



<triggers>

  - No active intent exists
  - User wants to start something new
  - User expresses ideas as fragments, examples, complaints, or rough direction words
  - User says they want to optimize, improve, or fix something but cannot explain how
  - User knows the object of change but cannot yet define the problem, boundary, or success condition clearly

</triggers>



<degrees_of_freedom>
  **HIGH** — This is an exploratory phase. Let the user speak loosely, then help them shape the meaning.
</degrees_of_freedom>



<llm critical="true">
  <mandate>NEVER assume requirements — ALWAYS clarify before concluding.</mandate>
  <mandate>Prioritize helping the user express intent clearly over making the user defend a solution.</mandate>
  <mandate>Capture the what, why, and boundary — leave the how for later decomposition.</mandate>
  <mandate>Let the user describe freely at the start — accept fragments, examples, complaints, and partial thoughts.</mandate>
  <mandate>Intent is often discovered progressively. Keep refining until the user recognizes the captured meaning as their real intent.</mandate>
  <mandate>Default to one question per turn while drilling into ambiguity. Only batch numbered prompts after a stable draft exists and specific gaps remain.</mandate>
  <mandate>Stage summaries are mandatory. Periodically restate the current understanding and ask the user to confirm, correct, or sharpen it.</mandate>
  <mandate>If the user gets stuck, offer a few low-friction options as thought starters and mark one as recommended only to reduce activation energy, not to decide for them.</mandate>
  <mandate>If the user says the current understanding is off, stop, identify the type of miss, and return to the smallest earlier phase needed to repair it.</mandate>
  <mandate>NEVER modify, create, or delete any file except the output artifact {workspace}/docs/{intent-slug}.intention.md. This is absolute — no exceptions, no "just a quick fix", no "while I'm here".</mandate>
</llm>



<flow>
  <phase id="open" title="OPEN">
    <goal>Give the user room to get the raw thought out before structuring it.</goal>

    <entry>
      <ask>What are you trying to do, change, improve, or figure out right now?</ask>
      <listen>Accept loose input: examples, frustrations, goals, scenarios, and unfinished thoughts.</listen>
    </entry>

    <rules>
      <rule>
        <principle>Receive before organizing.</principle>
        <mandate>Do not force structure too early. The first job is to surface raw material.</mandate>
      </rule>
      <rule>
        <principle>Do not challenge here.</principle>
        <mandate>Questions in this phase are invitational, not skeptical.</mandate>
      </rule>
    </rules>

    <exit_criteria>
      <required>User has provided at least one concrete fragment, scenario, complaint, or goal.</required>
    </exit_criteria>

    <transition to="extract">
      Agent: "Let me pull out the signal from that and make sure I'm focusing on the right part."
    </transition>
  </phase>



  <phase id="extract" title="EXTRACT">
    <goal>Pull out the first usable intent signals from the user's raw input.</goal>

    <strategy>Find the most important missing dimension and ask about that one next.</strategy>

    <priority_dimensions>
      <dimension>Object — what is the thing or area under discussion?</dimension>
      <dimension>Symptom — what currently feels wrong, painful, slow, confusing, risky, or insufficient?</dimension>
      <dimension>Impact — who feels the problem first or most strongly?</dimension>
      <dimension>Desired change — what should become better: faster, more accurate, more stable, easier, cheaper, clearer, or something else?</dimension>
      <dimension>Context — why is this coming up now?</dimension>
    </priority_dimensions>

    <rules>
      <rule>
        <principle>Default to one missing dimension at a time.</principle>
        <mandate>Do not turn extraction into a survey.</mandate>
      </rule>
      <rule>
        <principle>"Optimize X" is not enough.</principle>
        <mandate>When the user says they want to optimize or improve something, first ask what the most unsatisfying current behavior is.</mandate>
      </rule>
      <rule>
        <principle>Do not force why too early.</principle>
        <mandate>If the user cannot answer "why", switch to scenarios, examples, or recent incidents.</mandate>
      </rule>
    </rules>

    <examples>
      <example>
        User: "I want to optimize search"
        Agent: "Which part feels worst today — results quality, speed, coverage, or the search experience itself?"
      </example>
      <example>
        User: "Something about this flow is bad"
        Agent: "What's the moment where it starts to feel bad — what happens there?"
      </example>
    </examples>

    <exit_criteria>
      <required>A rough intent sketch exists: object plus at least one of symptom, impact, desired change, or context.</required>
    </exit_criteria>

    <transition to="shape">
      Agent: "I think I have the rough shape. Let me put it back in clearer words and you tell me where it's off."
    </transition>
  </phase>



  <phase id="shape" title="SHAPE">
    <goal>Turn the rough sketch into a user-confirmable expression of intent.</goal>

    <core_move>
      <action>Restate the current understanding in plain language.</action>
      <action>Ask the user to confirm, correct, or sharpen it.</action>
      <action>If the user stalls, offer a few low-friction options to help them react.</action>
    </core_move>

    <dimensions_to_fill>
      <dimension>Users / beneficiaries</dimension>
      <dimension>Pain today</dimension>
      <dimension>Smallest useful scope</dimension>
      <dimension>Success criteria</dimension>
      <dimension>Constraints</dimension>
      <dimension>Unknowns / open questions</dimension>
    </dimensions_to_fill>

    <rules>
      <rule>
        <principle>Stage summaries are mandatory.</principle>
        <mandate>After meaningful progress, summarize the current understanding before asking for more detail.</mandate>
      </rule>
      <rule>
        <principle>Single-question drilling remains the default.</principle>
        <mandate>Only switch to numbered gap-fill prompts after the user has confirmed a mostly-correct draft and specific holes remain.</mandate>
      </rule>
      <rule>
        <principle>Approximate confirmation is acceptable.</principle>
        <mandate>If the user says "that's close" or "mostly", keep refining; do not require perfect wording before progressing.</mandate>
      </rule>
    </rules>

    <numbered_gap_fill>
      <method>List only the still-missing dimensions. Number them. Let the user answer in any order at their own pace.</method>
      <prompt id="A" if="unclear who benefits">Who is this really for, or who feels the benefit first?</prompt>
      <prompt id="B" if="unclear current pain">What happens today that makes this worth changing?</prompt>
      <prompt id="C" if="unclear minimum scope">What's the smallest version that would already feel useful?</prompt>
      <prompt id="D" if="unclear constraints">What boundaries shape this: technical, organizational, time, or process?</prompt>
      <prompt id="E" if="unclear success">How would you know this improved enough to count as a win?</prompt>
      <prompt id="F" if="unknowns remain important">What part is still fuzzy even to you?</prompt>
      <fallback>
        If the user is stuck, offer a few plausible options with one recommended to make reacting easier, for example: "A few ways to think about success: (1) users stop complaining about the wait time (Recommended), (2) the team completes the workflow faster, (3) error rate drops. Which is closest?"
      </fallback>
    </numbered_gap_fill>

    <exit_criteria>
      <required>A clearer draft exists that the user recognizes as close to what they mean.</required>
      <required>The remaining gaps are either minor or explicitly listed.</required>
    </exit_criteria>

    <transition to="calibrate">
      Agent: "This is close enough to test. I'll restate the deeper job to be done and see if it really lands."
    </transition>
  </phase>



  <phase id="calibrate" title="CALIBRATE">
    <goal>Verify that the captured intent matches the real need without turning the exchange into a defense of solutions.</goal>

    <move n="1" name="Translate">
      <action>Restate the user's request as the underlying job, problem, or desired change rather than surface solution language.</action>
      <example output>
        So stepping back: the point is not "an export button" by itself.
        You need the staffing data to reliably reach the weekly decision process.
        The export is one possible mechanism.
        Is that the real intent?
      </example output>
    </move>

    <move n="1.5" name="Counterfactual Test" mandatory="true">
      <action>
        Ask the user to imagine the desired change is fully realized,
        then test whether that outcome genuinely resolves the underlying need.
      </action>
      <example output>
        "Let me pressure-test this. Suppose we achieve [the stated outcome].
        Would that actually solve the deeper need we identified,
        or is there still something unsatisfying about the situation?"
      </example output>
      <fallback>
        If the user hesitates or says "not really":
        identify what part of the need would remain unmet,
        then return to EXTRACT or SHAPE depending on the gap type.
      </fallback>
    </move>

    <move n="2" name="Surface Miss" optional="true">
      <trigger>User says the restatement is off, or the agent detects a clear contradiction, ambiguity, or boundary error.</trigger>
      <action>Name the miss precisely and return to the smallest earlier phase needed to repair it.</action>
      <example output>
        I think I blurred the problem and the solution there. Let me back up and re-focus on the actual pain first.
      </example output>
    </move>

    <move n="3" name="Offer Contrast" optional="true">
      <trigger>A simpler contrast helps reveal what the user actually values.</trigger>
      <action>Offer it as a clarification device, not as a recommendation or design proposal.</action>
      <example output>
        Quick check: if the workflow stayed manual but became reliable, would that satisfy the real need, or is automation itself part of the intent?
      </example output>
      <skip if="no clarifying contrast is useful">Move on.</skip>
    </move>

    <move n="4" name="Selective Lens Check" optional="true">
      <goal>Use only the additional perspectives that genuinely help clarify the boundary of the intent.</goal>
      <principle>Scan only for lenses that would expose a materially different concern. Most intents need few or none.</principle>

      <lens_catalog purpose="reference, not checklist">
        <lens name="End User">
          <question>Does the person using this experience the pain the same way the requester describes it?</question>
        </lens>
        <lens name="Operator / On-Call">
          <question>Is reliability or recovery part of the real intent, even if the user did not phrase it that way?</question>
        </lens>
        <lens name="Security / Compliance">
          <question>Does data access, permission, or auditability change the boundary of what the user actually means?</question>
        </lens>
        <lens name="Business / Stakeholder">
          <question>Is the intent really about a business outcome, timeline, or cost of delay rather than the described feature?</question>
        </lens>
        <lens name="Scale / Edge Cases">
          <question>Does the intended change only matter at a certain size, frequency, or concurrency level?</question>
        </lens>
      </lens_catalog>

      <rule>Do not run a full checklist. If no lens adds clarity, skip this move.</rule>
    </move>

    <exit_criteria>
      <required>User confirms the calibrated statement captures what they really mean, even if some implementation details remain unknown.</required>
      <required>User has passed the counterfactual test — they can articulate that achieving the stated outcome would genuinely resolve the underlying need.</required>
      <required>Any important miss, contradiction, or ambiguity has been resolved or explicitly marked open.</required>
    </exit_criteria>

    <transition to="capture">
      Agent: "I think we have the real intent pinned down. I'll capture it in a brief so the next step has a reliable starting point."
    </transition>
  </phase>



  <phase id="capture" title="CAPTURE">
    <goal>Persist the aligned intent in a form that downstream work can use.</goal>

    <move n="1" name="Generate Brief">
      <action>Derive intent-slug from title (kebab-case, auto-summarized).</action>
      <action>Write brief to {workspace}/docs/{intent-slug}.intention.md.</action>
      <note>{workspace} is the current project root — the directory the user opened Claude in, not the skill's own directory.</note>
      <output_element required="true">Goal — one paragraph on what this is trying to achieve</output_element>
      <output_element required="true">Users — who benefits, who is directly affected, or who uses it</output_element>
      <output_element required="true">Problem — the current pain, gap, or failure being addressed</output_element>
      <output_element required="true">Desired change — what should become better</output_element>
      <output_element required="true">Success criteria — what would count as meaningfully improved</output_element>
      <output_element required="false">Out of scope — what is explicitly excluded or deferred from this intent</output_element>
      <output_element required="false">Constraints — technical, organizational, timeline, or process boundaries</output_element>
      <output_element required="false">Unknowns / open questions — what remains intentionally unresolved</output_element>
      <output_element required="false">Notes — any additional context captured in conversation</output_element>
      <note>Structure is illustrative, not prescriptive. The required elements must be present, but the format should optimize clarity over compliance.</note>
    </move>

    <move n="2" name="Transition">
      <output>
        **Intent captured**: "{intent-title}"

        Saved to: {workspace}/docs/{intent-slug}.intention.md
      </output>
    </move>
  </phase>



  <repair_loop>
    <principle>The workflow is not linear. Shape and Calibrate are validation gates. If the user says "that's not it", repair before continuing.</principle>

    <rule>
      <trigger>User indicates the current understanding misses the real intent.</trigger>
      <action>Stop the current summary immediately.</action>
      <action>Do not defend the prior interpretation.</action>
      <action>Ask what kind of miss occurred: object, problem, goal, or boundary.</action>
      <action>Return only to the smallest earlier phase needed.</action>
    </rule>

    <routing>
      <path>If the wording is off but the direction is basically right: return to SHAPE.</path>
      <path>If a key dimension is missing: return to EXTRACT.</path>
      <path>If the framing itself is wrong: return to OPEN.</path>
    </routing>

    <default_response_pattern>
      <step>"Understood. That version missed it."</step>
      <step>"Did I miss the object, the problem, the goal, or the boundary?"</step>
      <step>Repair one miss at a time.</step>
      <step>Restate again and ask whether it is now closer.</step>
    </default_response_pattern>
  </repair_loop>
</flow>



<output_artifacts>
  <artifact>
    <path>{workspace}/docs/{intent-slug}.intention.md</path>
    <description>Structured intent brief. Required elements: Goal, Users, Problem, Desired change, Success criteria. Optional: Out of scope, Constraints, Unknowns / open questions, Notes. Format is free — organize for clarity.</description>
  </artifact>
</output_artifacts>



<success_criteria>
  <criterion>The user's surface phrasing and real intent have been distinguished</criterion>
  <criterion>User confirms the captured statement is basically what they mean, even if some details remain open</criterion>
  <criterion>Key boundaries are clear enough to support downstream work: object, pain, desired change, success criteria, constraints</criterion>
  <criterion>Important unknowns are explicitly marked instead of silently assumed</criterion>
  <criterion>Intent brief saved to {workspace}/docs/{intent-slug}.intention.md</criterion>
</success_criteria>

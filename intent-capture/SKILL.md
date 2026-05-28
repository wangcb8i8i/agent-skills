---
name: intent-capture
description: Capture user intent through guided conversation. Exploratory phase with high degrees of freedom.
version: 2.0.0
---

<objective>
Capture user intent through guided conversation — not just what users say they want, but the real need beneath it.
</objective>



<triggers>

  - No active intent exists
  - User wants to start something new

</triggers>



<degrees_of_freedom>
  **HIGH** — This is a creative, exploratory phase. Ask open-ended questions. Don't constrain prematurely.
</degrees_of_freedom>



<llm critical="true">
  <mandate>NEVER assume requirements — ALWAYS ask clarifying questions</mandate>
  <mandate>Capture the "what" and "why" — leave the "how" for decomposition</mandate>
  <mandate>Let user describe freely — don't interrupt</mandate>
  <mandate>Intent is discovered, not stated. Keep digging until you reach the root motivation.</mandate>
  <mandate>NEVER ask multiple questions in a single turn during depth drilling. One question per turn — the user's answer determines the next direction.</mandate>
  <mandate>NEVER modify, create, or delete any file except the output artifact {workspace}/docs/{intent-slug}.intention.md. This is absolute — no exceptions, no "just a quick fix", no "while I'm here".</mandate>
</llm>



<flow>
  <phase id="explore" title="EXPLORE">
    <goal>Understand the real intent beneath the surface request.</goal>
    <strategy>Start with "why?", drill deep, then cover gaps.</strategy>
    

    <entry>
      <ask>What do you want to build? or What's the problem?</ask>
      <listen>Let user describe freely. Don't interrupt.</listen>
    </entry>
    
    <rules priority_order="strict">
      <rule priority="1">
        <principle>Always accept first, then probe</principle>
        <mandate>Never challenge in this phase. Questions must be open, curious, exploring — not skeptical.</mandate>
      </rule>
      <rule priority="2">
        <name>Depth Drill</name>
        <trigger>After every substantive user answer</trigger>
        <method>Ask "why" — drive toward the underlying motivation.</method>
        <depth>Not a fixed count. Stop when the user reaches a root need or repeats.</depth>
        <anti_pattern>Asking two or more questions at once (e.g. "why do you need that and what format?"). This collapses the drill into a survey, losing the chain.</anti_pattern>
        <anti_pattern>Pre-answering your own question or listing options alongside it. Let the user's answer stand alone.</anti_pattern>
        <example>
          User: "I want an export button"
          Agent: "That makes sense. Help me understand — once the data is exported, what do you do with it?"
          User: "Import it into my analytics tool for weekly reports"
          Agent: "Got it. And those weekly reports — what decisions do they drive?"
          User: "We adjust staffing for the following week"
          Agent: "So the real need is having data flow into your decision loop on a weekly cadence — the export button is just the means."
        </example>
      </rule>
      <rule priority="3">
        <name>Gap Fill</name>
        <trigger>After depth drilling has reached a natural stopping point</trigger>
        <method>Check for uncovered dimensions using the conditional prompts below.</method>
      </rule>
    </rules>
    
    <conditional_prompts>
      <prompt if="unclear who benefits">Who is this for? Who will use it?</prompt>
      <prompt if="unclear what painful now">What happens today without this? How do people cope?</prompt>
      <prompt if="unclear scope">What's the smallest version that would be useful? What can wait?</prompt>
      <prompt if="unclear constraints">Any boundaries — technical, organizational, timeline — that shape what's possible?</prompt>
      <prompt if="unclear success">When this works, what changes? How would you measure that?</prompt>
    </conditional_prompts>
    
    <loop allowed="true">
      Depth drill and gap fill may alternate until all dimensions are covered and motivation is at root level.
    </loop>
    
    <exit_criteria>
      <required>Root motivation understood (not just surface request)</required>
      <required>All five dimensions probed at least once: users, pain-today, scope, constraints, success</required>
      <required>No obvious contradiction or ambiguity detected (these go to CHALLENGE)</required>
    </exit_criteria>
    
    <transition to="challenge">
      Agent: "I think I understand the real need here. Let me reflect that back and test it."
    </transition>
  </phase>



  <phase id="challenge" title="CHALLENGE">
    <goal>Test the understanding. Make sure we're solving the right problem.</goal>

    <move n="1" name="Translate">
      <action>Restate the user's request as a problem statement, not a feature ask.</action>
      <principle>If the user said "I need X", reframe as "You're trying to achieve Y". Strip the solution-language.</principle>
      <example output>
        So if I step back: the export button isn't the point.
        You need weekly staffing data flowing into your decision loop.
        The export is one way to make that happen.
        Is that the real job to be done?
      </example>
    </move>
    
    <move n="2" name="Surface Tension" optional="true">
      <trigger>Agent detects any of: conflicting goals, mutually exclusive constraints, unstated tradeoffs, logical gaps.</trigger>
      <action>Name the tension directly. Don't resolve it — let the user react.</action>
      <example output>
        One thing I'm noticing: you want this to be fast, and you also want it to
        cover every edge case. Those pull in opposite directions.
        Which matters more for the first version?
      </example>
      <example output>
        You mentioned "for the whole team" but the pain you described only affects
        the ops lead. Is this actually a single-person workflow?
      </example>
      <skip if="no tension detected">Nothing to surface — move on.</skip>
    </move>
    
    <move n="3" name="Offer Alternatives" optional="true">
      <trigger>Agent can think of a meaningfully simpler way to meet the same root need.</trigger>
      <action>Offer it as a thought experiment — not a recommendation.</action>
      <principle>If the user rejects it, that's useful signal about what actually matters.</principle>
      <example output>
        One thought: instead of building a full export feature with filters and
        scheduling, would giving the ops lead a read-only SQL client solve the
        immediate problem with 10% of the work?
      </example>
      <skip if="no simpler alternative comes to mind">Nothing useful to offer — move on.</skip>
    </move>
    
    <move n="4" name="Multi-Lens Check">
      <goal>Don't stop at one perspective. Scan for other role viewpoints that would surface different concerns — 1 to N lenses, driven by the intent, not a template.</goal>
      
      <principle>After the first round of challenge (translate, tension, alternatives), pause and ask: "Who else has skin in this game?" The first lens the conversation naturally fell into might not be the only one that matters.</principle>
      
      <anti_pattern>
        <bad>Mechanically running through all 8 lenses every time. Most intents only need 1-3.</bad>
        <bad>Forcing a lens that has nothing to say. If the lens question is already answered by what the user said, skip it.</bad>
        <bad>Treating this as a checklist to complete before moving on. The goal is surfacing blind spots, not filling a quota.</bad>
      </anti_pattern>
      
      <step n="1" name="Judge Applicability">
        <action>Given this specific intent, which roles or stakeholders would have a genuinely different take? Scan the reference catalog below — not as a checklist, but as a prompt to think.</action>
        <rule>If only one lens applies (the one the conversation already used), acknowledge it and move on. Don't invent perspectives.</rule>
        <rule>If 0 additional lenses apply, skip the move entirely.</rule>
      </step>
      
      <lens_catalog purpose="reference, not checklist">
        <lens name="End User">
          <question>Will the person actually using this understand it? Is it discoverable? Does it match their mental model?</question>
          <applies_when>There's a UI, a workflow, or a human-in-the-loop action.</applies_when>
        </lens>
        <lens name="Operator / On-Call">
          <question>What breaks at 3am? How do you know it's broken? What's the recovery path?</question>
          <applies_when>Anything that runs in production, has dependencies, or changes state.</applies_when>
        </lens>
        <lens name="Security / Compliance">
          <question>Who can do what? What data moves where? What audit trail exists?</question>
          <applies_when>The intent touches auth, data access, PII, external integrations, or permissions.</applies_when>
        </lens>
        <lens name="Maintainer / Future Team">
          <question>Will someone inheriting this 6 months from now understand why it exists and how it works?</question>
          <applies_when>The intent involves custom logic, configuration, or non-obvious design choices.</applies_when>
        </lens>
        <lens name="Business / Stakeholder">
          <question>Does this move a metric that matters? What's the cost of being wrong? What's the opportunity cost?</question>
          <applies_when>The intent has a business goal, a budget, or a timeline.</applies_when>
        </lens>
        <lens name="Data / Analytics">
          <question>What does success look like in data? What events or metrics would prove this worked?</question>
          <applies_when>The intent involves user behavior, business outcomes, or anything that should be measured.</applies_when>
        </lens>
        <lens name="Newcomer / Onboarding">
          <question>Does this assume knowledge a new user or team member wouldn't have?</question>
          <applies_when>The intent creates a new surface, API, workflow, or convention.</applies_when>
        </lens>
        <lens name="Scale / Edge Cases">
          <question>What happens at 10x? 0 items? 10,000 items? Concurrent users? Retry storms?</question>
          <applies_when>The intent involves data processing, queues, lists, or multi-user scenarios.</applies_when>
        </lens>
      </lens_catalog>
      
      <step n="2" name="Present">
        <action>State which lenses you're checking, then ask the key question for each — all together, not one-by-one waiting for confirmation. Keep each lens to 1-2 sentences.</action>
        <rule>Don't narrate the lens name unless it adds clarity. The user cares about the insight, not the taxonomy.</rule>
        <format>
          <example output>
            Before we lock this down, a couple other angles:
            
            From an on-call perspective — if this export fails silently at 3am Sunday, does anyone notice before Monday's staffing meeting?
            
            And at scale — "all projects" is 10 or 10,000? The shape of the solution changes a lot at different orders of magnitude.
          </example>
        </format>
      </step>
      
      <step n="3" name="Resolve">
        <action>Let the user respond to the set. They may dismiss some lenses, dig into others, or adjust the intent.</action>
        <action>Each lens is resolved when the user confirms, defers, or the concern proves irrelevant.</action>
      </step>
    </move>
    
    <exit_criteria>
      <required>User confirmed the translation accurately captures the real need</required>
      <required>Any surfaced tension has been resolved or explicitly deferred by the user</required>
      <required>Any offered alternative has been accepted or explicitly rejected by the user</required>
      <required>Applicable lenses have been scanned — at least one, at most as many as the intent genuinely calls for</required>
    </exit_criteria>
    
    <transition to="capture">
      Agent: "Are we aligned? Does this all feel right?" — User confirms without reservation.
    </transition>
    
    <transition to="explore" trigger="challenge-revealed-gap">
      Challenge exposed a missing dimension or a flawed premise. Go back and re-explore that specific gap, then return to CHALLENGE.
    </transition>
  </phase>



  <phase id="capture" title="CAPTURE">
    <goal>Write the brief and hand off.</goal>

	<move n="1" name="Generate Brief">
	  <action>Derive intent-slug from title (kebab-case, auto-summarized)</action>
	  <action>Write brief to {workspace}/docs/{intent-slug}.intention.md</action>
      <note>{workspace} is the current project root — the directory the user opened Claude in, not the skill's own directory.</note>
	  <output_element required="true">Goal — one paragraph on what this achieves</output_element>
	  <output_element required="true">Users — who benefits, who uses it</output_element>
	  <output_element required="true">Problem — the pain or gap being addressed</output_element>
	  <output_element required="true">Success criteria — how you'll know it's working</output_element>
	  <output_element required="false">Constraints — technical, organizational, or timeline boundaries</output_element>
	  <output_element required="false">Notes — any additional context captured in conversation</output_element>
	  <note>Structure is illustrative, not prescriptive. Use whatever format best communicates the intent clearly. The required elements must be present; how they're organized is up to the writer.</note>
	</move>
	
	<move n="2" name="Transition">
	  <output>
	    **Intent captured**: "{intent-title}"
	
	    Saved to: {workspace}/docs/{intent-slug}.intention.md
	
	  </output>
	</move>
  </phase>
</flow>



<output_artifacts>
  <artifact>
    <path>{workspace}/docs/{intent-slug}.intention.md</path>
    <description>Structured intent brief. Required elements: Goal, Users, Problem, Success criteria. Optional: Constraints, Notes. Format is free — organize for clarity, not compliance.</description>
  </artifact>
</output_artifacts>



<success_criteria>
  <criterion>Root motivation reached — not just surface request captured</criterion>
  <criterion>Understanding tested via translation, tension, and alternatives before capture</criterion>
  <criterion>User confirmed alignment without reservation</criterion>
  <criterion>Intent brief saved to {workspace}/docs/{intent-slug}.intention.md</criterion>
</success_criteria>


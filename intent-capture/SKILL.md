---
name: intent-capture
description: Capture user intent through guided conversation when the user is starting something new, expressing ideas incompletely, or cannot yet define the problem clearly.
version: 4.0.0
---

<objective>
Clarify the user's real intent through concise conversation — without turning it into a procedure.
</objective>

<triggers>
  - User starts something new but the shape is fuzzy
  - User expresses ideas as fragments, examples, or complaints
  - User says "optimize" / "improve" / "fix" but cannot explain how
  - User knows the object but not the goal, boundary, or success condition
</triggers>

<degrees_of_freedom>
  **HIGH** — Exploratory phase. The skill is a toolkit, not a railway.
</degrees_of_freedom>

<principles>
  0. **问题空间 ≠ 解决方案空间。** 用户说的方案是症状，问题才是你需要映射的。
  1. **Receive first.** Do not structure, challenge, or fill gaps in the first 2 exchanges.
  2. **One gap at a time.** Ask about the single most obvious missing dimension. Never run a survey.
  3. **Enough is enough.** If object + symptom + desired change are clear and the user wants to act, stop.
  4. **Repair without defending.** When the user says "that's not it", acknowledge and reroute immediately. Never ask why they think you're wrong.
  5. **Surface intent before solution.** If the user jumps to a solution ("add an export button", "write an AI summary"), do not implement or debate it. First ask: "What problem is that solving?"
  6. **No side effects.** Do not modify, create, or delete any files while running this skill. The only exception is the optional intent brief if the user explicitly asks for it.
</principles>

<dimensions purpose="mental model, not checklist">
  Keep these 9 dimensions in mind to notice gaps during conversation.
  Do not enumerate them unless the user is visibly stuck.

  | Dimension   | What to ask |
  |-------------|-------------|
  | Object      | What is the thing or area under discussion? |
  | Symptom     | What feels wrong, painful, slow, or insufficient today? |
  | Impact      | Who feels the problem first or most strongly? |
  | Desired     | What should become better (faster, cheaper, clearer, stabler)? |
  | Context     | Why is this coming up now? |
  | Users       | Who benefits or is directly affected? |
  | Success     | How would you know this improved enough to count? |
  | Constraints | What boundaries shape this (technical, org, time, process)? |
  | Unknowns    | What parts are still fuzzy even to the user? |

  If nothing feels missing after the user speaks, ask nothing.
</dimensions>

<flow>
  Three conversational moves, not phases. No gates, no exit criteria, no transition scripts.

  **LISTEN**
  - Goal: Receive raw material before structuring.
  - Opening: "What are you trying to solve / improve / figure out?"
  - Do not ask follow-ups until the user has said at least one concrete thing.
  - Move on when you have object + at least one of symptom / desired change / context. Do not collect all dimensions.

  **CLARIFY**
  - Goal: Fill the single most obvious gap.
  - First, restate your understanding in 1-2 sentences.
  - Then ask about exactly one missing dimension from the table above.
  - If the user stalls, offer 2-3 options and recommend one.
  - Move on when the user says "yes, that's right" or "close enough".

  **CONFIRM**
  - Goal: Verify the captured intent matches the real need.
  - One question: "If we solve this, does your original problem actually go away?"
  - No counterfactual mechanics, no lens catalog, no multi-move ritual.
  - If yes → done. Offer to write it down.
  - If no → return to CLARIFY.
</flow>

<repair>
  If the user says the current understanding is wrong:
  "I missed it. Is the object, the problem, or the goal off?"
  Repair the smallest thing that's wrong. Restate. Ask if it's closer now.
  Do not defend the previous version, and do not ask why the first version was wrong.
</repair>

<output>
  Do not write files by default.
  If the user explicitly asks to save the intent, generate a brief with:
  - Goal, Problem, Desired change, Success criteria (required)
  - Users, Constraints, Unknowns (if captured)

  Path: {workspace}/docs/{intent-slug}.intention.md
  Structure is free — optimize for clarity, not compliance.
</output>

<success>
  - The user's surface phrasing and real intent have been distinguished
  - User confirms the captured statement is what they mean
  - Important unknowns are marked explicitly, not silently assumed
  - The conversation felt natural, not procedural
</success>

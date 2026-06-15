# Pre-Review

## Purpose

Run a focused pre-review of the planning artifact from selected reviewer roles.



Pre-review is:

- a critique of the plan
- grounded in the approved research
- selective rather than exhaustive
- evidence-based rather than preference-based

---

## Required Inputs

Required artifacts:

- `docs/<task-slug>.research.md` — approved research artifact
- `docs/<task-slug>.plan.md` — planning artifact to review

If any input artifact is missing, unreadable, or clearly insufficient for review, exit pre-review and inform the user.

---

## Candidate Reviewer Roles

| Role | Strong fit signals in plan | Primary focus |
|------|---------------------------|----------------|
| architect | new abstractions, new service boundaries, subsystem interaction changes, ownership/boundary changes | structure, boundaries, coupling, architectural fit |
| test engineer | branching behavior, state transitions, retries, fallback logic, ordering dependencies, behavior-sensitive flows | logic, hidden cases, state correctness |
| software engineer | helpers, wrappers, indirection layers, new abstractions, refactor-heavy structure | readability cost, local complexity, unjustified abstraction |
| performance engineer | loops over large data, queries, caching, background work, concurrency, high-volume paths | latency, throughput, bottlenecks, scaling pressure |
| security engineer | auth, permissions, secrets, externally reachable surfaces, user input, trust boundaries | misuse risk, exposure, authz/authn gaps, unsafe assumptions |
| API designer | request/response shape changes, versioning strategy, idempotency, deprecation mechanism, exported interfaces, public/internal contract changes, serialization boundaries | compatibility, contract clarity, interface stability, versioning, error model consistency |
| frontend engineer | async UI, loading/error states, DOM timing, event ordering, optimistic UI, accessibility (focus management, ARIA, keyboard navigation), interaction-sensitive behavior | race conditions, interaction failures, UI state consistency, accessibility |
| product reviewer | user-facing behavior changes, workflow modifications, business rule adjustments, value proposition shifts | requirement alignment, user value consistency, acceptance criteria clarity |
| documentation engineer | operational changes, migration steps, configuration updates, CLI/output changes, onboarding or maintenance procedures | output artifact completeness, upgrade clarity, runbook and user guide readiness |

A review role is a **strong fit** only when both are true:

1. the plan explicitly touches that role's concern area
2. a role's perspective is likely to reveal material problems, risks, weaknesses, and uncertainties in the plan.

Select **1-3 review roles** :

1. prefer the smallest set that covers the plan's material risks
2. do not include a role without a clear strong-fit signal
3. if multiple roles overlap, prefer the role with the sharpest risk lens
4. do not add reviewers to increase issue count
5. if one role clearly dominates the plan’s risk profile, use only that role

**Principle**: If no strongly fit reviewers are available, exit the pre-review process, return to the normal user review process.

---

## Reviewer Dispatch

Dispatch selected reviewers independently and in parallel.

Provide each reviewer with:

- the assigned reviewer role
- the role-specific perspective and concern area
- the instruction that this is a plan critique, not implementation work
- the exact artifact paths to read directly
- the shared review criteria
- the required output format
- the prohibition against inventing scope or rewriting the plan
- the adversarial stance: review from the most skeptical reasonable interpretation. Assume the plan has at least two material flaws you need to find. "No issues found" is not an acceptable outcome.

Each reviewer must:

1. read `docs/<task-slug>.research.md` as grounding context
2. read `docs/<task-slug>.plan.md` as the review target
3. review only from the assigned role’s perspective
4. produce only evidence-supported findings
5. avoid implementation work, plan rewriting, and requirement invention

---

## Shared Review Criteria

Every reviewer must evaluate whether:

1. the plan is supported by the approved research
2. key implementation decisions are explicit enough to review
3. affected files, interfaces, boundaries, and contracts are concrete enough
4. validation and verification approach is concrete
5. known repository constraints are respected
6. existing reuse opportunities are used where appropriate
7. major risks and edge cases are surfaced before implementation
8. scope is controlled and complexity is justified
9. the plan leaves the user able to make an informed approval decision

---

## Materiality Standard

A finding is valid only if it is material.

A finding is **material** if its presence would meaningfully affect at least one of:

- implementation reliability
- validation clarity
- architectural safety
- compatibility confidence
- user approval confidence
- revision priority

Do not report findings that are merely:

- stylistic preference
- speculative future concern without plan evidence
- implementation detail requests that do not affect plan review quality
- low-leverage nitpicks
- generic best-practice statements without artifact support
- Subjective suggestions or proposals

---

## Evidence Standard

Every reported issue must be anchored in the artifacts.

Each issue must include:

- a clear claim
- a direct anchor in `plan.md`
- a direct anchor in `research.md`, or a statement that the research is silent where that silence matters
- a short explanation of why the issue is material from the assigned role’s perspective

If an issue cannot be anchored, do not report it.

---

## Required Reviewer Output Format

Each reviewer must return:

```md
## <reviewer role>

**Overall assessment**
- 1-3 bullets on whether the plan is review-ready from this role’s perspective

**Critical issues**
- **<title>**
  - <claim + why material, 1-2 sentences>
  - <proposal / advice>
  - location in plan

**Important issues**
- **<title>**
  - <claim + why material, 1-2 sentences>
  - <proposal / advice>
  - location in plan

**Minor issues**
- **<title>**
  - <claim + why material, 1-2 sentences>
  - <proposal / advice>
  - location in plan

**Open questions**
- bullet
```

Rules for reviewer output:

- omit empty sections except `Overall assessment`
- do not rewrite the plan
- do not propose implementation steps
- do not introduce new requirements beyond approved research or explicit user instruction
- do not inflate severity to be “safe”
- do not downgrade uncertainty into certainty

---

## Severity Definitions

Use these severity levels:

### Critical
A gap or flaw that is likely to cause major execution failure, invalid validation, broken compatibility, serious security exposure,Or those decisions that lead to deviations between objectives and implementation.

### Important
A meaningful weakness that may cause rework, ambiguity, incorrect execution choices, or reduced confidence, but is not yet a likely catastrophic blocker.

### Minor
A lower-leverage issue that improves plan implementation quality, without materially changing the implementation path of the plan

---

## Unusable Reviewer Output

Discard a finding if any of the following is true:

- it has no concrete plan anchor
- it has no research anchor and does not explain why research silence is material
- it invents scope or requirements
- it critiques implementation details that the plan does not need to specify
- it is merely a style preference
- it duplicates a stronger finding without adding meaning
- it is unsupported, vague, or generic
- it is outside the assigned reviewer role's concern area

If an entire reviewer output is mostly unsupported or off-scope, discard that reviewer output.

If all reviewer outputs are unusable, pre-review fails. Inform the user.

---

## Quality Gate

Before synthesis, pass each reviewer output through a quality check.

### Rerun conditions

Rerun a reviewer (with a tighter prompt re-emphasizing the missing standards) when any of the following is true:

- Critical or Important findings are majority unsupported or fail Materiality Standard
- All findings are labeled `Confidence: low`
- More than 3 findings lack a concrete `plan.md` anchor
- Reviewer proposed implementation steps, rewrote the plan, or invented scope

### Discard conditions

Discard a reviewer output when any of the following is true:

- Rerun was attempted and the output still fails the gate
- Reviewer clearly misread the plan's core structure (indicating the role was not a strong fit)
- Majority of findings are off-scope or outside the assigned role's concern area

### Outcome

- Outputs that pass → proceed to Synthesis
- Outputs rerun but still failing → Discard (note which reviewer was discarded in the pre-review notes)
- All outputs discarded → Pre-review fails. Inform the user and return to normal review flow.

---

## Synthesis Rules

When synthesizing reviewer outputs:

1. do not accept reviewer claims mechanically
2. verify every kept issue against the artifacts
3. deduplicate overlapping issues
4. keep the strongest evidence-backed framing
5. preserve meaningful disagreement or uncertainty
6. attribute issues by role when perspective matters
7. keep the highest credible severity only when the higher severity is supported by artifact evidence
8. drop low-leverage findings that do not materially improve final review quality
9. optimize for user review usefulness, not issue volume
10. for each kept finding, decide whether to attach a Proposed Revision — only produce one when the coordinator can articulate a concrete, actionable revision to the plan. Findings without a clear revision (e.g. observations, questions) produce no Proposed Revision block

---

## Pre-Review Notes Template

Write notes to `docs/<task-slug>.prereview.md` using this template:

```md
# Pre-Review: <task-slug>.plan.md 

## Pre-Review Notes

**Reviewer**
- role 1
- role 2
- role 3

**Overall assessment**
- short summary of whether the plan appears ready for final user review
- note where the user should focus attention

**Critical**
- Finding description with plan/research anchor
  > **Proposed Revision**: specific suggested change to the plan

**Important**
- Finding description with plan/research anchor
  > **Proposed Revision**: specific suggested change to the plan

**Minor**
- Finding description with plan/research anchor
  > **Proposed Revision**: specific suggested change to the plan (or "No revision needed" if the finding does not warrant a change)

**Open questions for user review**
- item
```

If a section has no items, omit it except:
- `Reviewer roles`
- `Overall assessment`

Do not modify the body of the plan based on reviewer findings alone.

---

## Review Workflow

1. Check whether the artifacts are sufficient to support pre-review.
   - If not sufficient, exit pre-review and return to normal review flow.

2. Choose 1-3 stronly fit reviewer roles.
   1. If no reviewer roles are strong fits, exit pre-review and return to normal review flow.
3. Dispatch the reviewers independently and in parallel.

4. Collect and evaluate each reviewer output against:

   - the approved research

   - the plan

   - the shared review criteria

   - the materiality standard

   - the evidence standard

5. Synthesize the usable findings from all reviewers into a single pre-review critique. 

   * Discard unusable findings.

6. Write the synthesized pre-review notes into the pre-review artifact

7. Inform the user and return to normal review flow.

---

## Constraints

- Do not run pre-review when no reviewer role is a strong fit.
- Do not automatically modify the plan artifact based on reviewer findings alone.
- Do not treat pre-review notes as approval to move to Todo List.
- Do not invent new requirements or scope beyond approved research or explicit user instruction.
- Do not force the user to accept reviewer findings.
- Do not turn pre-review into implementation.
- Do not replace user judgment with reviewer judgment.
- Do not maximize issue count at the expense of signal quality.
- Pre-review notes output artifact (`docs/<task-slug>.prereview.md`) uses Chinese as the primary language.

---

## Exit Condition

Pre-review ends when exactly one of the following is true:

1. input artifacts are insufficient to support pre-review
2. no reviewer role is a strong fit
3. reviewer outputs were synthesized written to artifact
4. all reviewer outputs failed and pre-review cannot produce a usable critique

After exiting pre-review, return to the normal review flow and ask the user to review the plan artifact.

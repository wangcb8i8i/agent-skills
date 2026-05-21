# Verification & Feedback

## Purpose

Audit the implementation's **TODO fidelity**: whether every file change or operation in the implementation phase matches its corresponding TODO item — no false positives (marked done but not done), no false negatives (done but not marked), and no unexpected changes outside the approved list.

This is a **fidelity audit**, not a functional or quality validation. It answers one question: *did we do what we said we would, and only what we said we would?*

## What to do

### Forward verification (catch false positives)

Check each TODO item against the actual implementation:

1. For each `[x]` item, verify: does the claimed deliverable actually exist?
2. For each `[x]` item, verify: does the implementation match the description in the plan?
3. Flag any `[x]` item where the work is incomplete, incorrect, or absent.

### Reverse verification (catch false negatives)

Cross-check the actual code changes against the TODO list, looking for work done but not listed:

1. Read the set of files created or modified during implementation.
2. For each change, ask: "Which TODO item does this serve?"
3. If a change cannot be mapped to any TODO item (and is not trivial supporting code such as imports, scaffolding, or whitespace), it is a **potentially unexpected change** that requires explicit disclosure.
4. If a change clearly implements a TODO item that has `[ ]` (not checked off), mark it as **missed check-off**.

Classification rules for step 3:

| Change type | Classification |
|---|---|
| Matches a specific TODO item | Expected |
| Trivial support code (imports, function signatures called by TODO code, error handling) | Acceptable supporting change |
| Changes behavior/functionality outside all TODO scope | **Unexpected change — report** |
| Structures code differently than plan described (e.g., split a function when plan said one file) | **Potential scope drift — decide** |

### Consistency check

1. Verify that the set of files changed matches the set of files the plan said would change.
2. If the plan listed files to create but some were not created, flag them.
3. If files were created that the plan did not mention, assess whether they are supporting files or scope creep.

## Report

After completing forward verification, reverse verification, and consistency check, produce a single fidelity report covering all findings.

### Drift classification

If drift is found, classify it with evidence in the report:

| Drift type | Example | Report label |
|---|---|---|
| Implementation-level: work done but doesn't match TODO | Script exists but outputs wrong column order | `implementation mismatch` |
| Plan-level: TODO list insufficient | TODO missed creating a ZIP step | `plan gap` |
| Research-level: plan was correct but research was wrong | Research claimed 4 interfaces but there are 5 | `research error` |

### Fidelity report template

```
## Fidelity Report
A sentence or two summary
###Issues###
[none / itemized list with evidence and drift type]
```

Then ask: does the user want follow-up refinement?

## What aspects should be verified

- `[x]` items: work actually exists and matches the TODO description
- `[ ]` items: none left that should have been implemented (talk-through check)
- Forward mapping: TODO → implementation — all accounted for
- Reverse mapping: implementation → TODO — no orphan changes
- Changed files: does the set match the plan's stated scope?
- Any mismatches or unexpected changes explicitly disclosed

## What is not sufficient verification

A verification pass is not sufficient when any of the following is true:
- only forward verification was performed (false negatives uncaught)
- the implementer's summary was taken at face value without independent cross-check against actual files on disk
- reverse mapping was attempted but code was too complex to reason about — ambiguity must be surfaced, not skipped
- drift is discovered but not traced back to the phase where the drift was introduced

## Constraints

- This phase verifies and reports. It does not modify any files, artifacts, or system state.
- Do not reopen design decisions, hide discrepancies, or imply fidelity when mismatches exist.
- Do not execute any command or operation that produces side effects. Read-only analysis only.
- If the user accepts work with known drift, point out the mismatch rather than silently agreeing.

## Completion criteria

This phase is complete when:

- forward verification performed: every `[x]` item checked against actual implementation
- reverse verification performed: every implementation change traced to a TODO item or surfaced as unexpected
- any drift or mismatch has been explicitly surfaced in the fidelity report
- the fidelity report has been presented per the template

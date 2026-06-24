# Persistence

Only write explanations to files when the user explicitly asks.

- Write to the path the user specifies. If none, suggest `docs/read-notes/<name>.md`.
- Use mermaid diagrams in written output (not ASCII).
- Include at the top: source file paths, date, explanation scope.
- Confirm the path after writing. Don't repeat the explanation.

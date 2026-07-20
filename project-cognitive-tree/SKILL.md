---
name: project-cognitive-tree
description: Guide a user to build and persist a cognitive tree of an unfamiliar project — root to leaf, top-down, user chooses the path. User-invoked only.
---

Guide through a **cognitive tree** — nodes and the edges between them. The tree grows where the user looks.
Code is evidence, not the story. Establish what before how. All files live under `.cognitive-tree/` —
INDEX.md as the ascii tree, `.md` files for node content. The tree body is
the archive of progress.

INDEX.md exists → show the tree first, ask what to do next. Doesn't exist →
discover the project, write a root node, graft it, show the tree. Ask: dig
deeper?
At each node, grow the tree to where the user's understanding needs to go.

Write for a Chinese reader.
A node fails if reading it requires opening the source. Write so someone new to the project walks away understanding this piece — fill in whatever domain or context is needed.

---
layout: converter-docs
title: "Design decisions"
permalink: /converter/docs/decisions/
sitemap: false
noindex: true
---
{% raw %}

Open design questions of the converter, one per session (user, 2026-10-24). Each entry: the question,
what is known, the options, status. When decided, the decision goes where it belongs (CLAUDE.md,
PLANNED.md, the docs of the format) and the entry says where.

## Criteria for a decision (draft, 2026-10-24; to discuss in a session of its own)

The user asked for words to judge whether a decision makes the converter better, more efficient, or too
rigid to develop. Draft list, each as a question:
- Simplicity: does it remove code, parameters, special cases, or add them?
- Locality (coupling): does a change stay in one module, or do other rules depend on it?
- Reversibility: can it be undone later without remaking files or breaking what users made with it?
- Idempotence (stability): applied twice, is the result the same as once? (No drift over round trips.)
- Fidelity: does what the user drew survive the conversion, and is every change said in the messages?
- Predictability: can a user tell what the output will be from the input and the rule?
- Evolvability (extensibility): does a new target, a new map or a new rule fit without changing this one?
- Robustness: does it hold on maps not seen yet, and on files edited afterwards in the other program?
- Lock-in: does it tie the converter to one program's behaviour, or to one map?
- Cost of being wrong: if it proves wrong, how much is lost (files, user's edits) and how is it found?

## Points to discuss, one per session

Settled 2026-10-24 (user): 1. the tidy module removed, 2. the process glyph by hidden edit points,
over 3 px, 3. no node moved, multimers as dimers with N:x, 4. a hidden point under the node, 5. no
default left to choose ([D14](/converter/docs/design/#d14-no-node-moved-the-process-glyph-and-ports-by-hidden-edit-points),
[D15](/converter/docs/design/#d15-multimers-drawn-as-dimers-the-count-as-a-unit)).

6. Complex name room (PLANNED.md): grow the complex, or move its members.

7. Species on a compartment's edge (2026-10-28, ExposomeMap-PM; ISSUES.md, Known faults). CellDesigner draws a
   membrane protein across its compartment's border, a member of the compartment; yEd draws a group round all its
   members, and the GraphML check refuses a member outside its group, so the trip CellDesigner > GraphML >
   CellDesigner loses it and its reactions. Options: (a) the check accepts a member whose box overlaps its
   compartment (on the membrane), yEd's group grows a little on opening; (b) CellDesigner to GraphML makes such a
   species a top-level node and keeps the compartment as a node property, read back to CellDesigner; (c) the
   species moved inside, against "no node moved". Proposed: (a), the smallest; it keeps membership and
   position, and the growth is the known fault already listed.

{% endraw %}

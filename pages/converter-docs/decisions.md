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

1. Tidy module: what stays in the CellDesigner adapter, what goes into the tidy module, and whether the
   tidy is for CellDesigner only or generic (the straightening could also go to human-like-layout's
   `standardise.py`, in the source map). Split agreed (PLANNED.md, "Conversion translates").
2. Process glyph by hidden edit points (advanced only; agreed in principle): when to add them (a
   threshold, so reactions are not shifted 1-2 px with extra points), how many reactions per Atlas map
   would get them, and the test in CellDesigner (drag a reactant). In the straight layout the process
   stays midway and nothing is moved for a modifier: its arc may slant.
3. Adapters never move a node's centre (agreed): wording. Multimers grow from the top left in
   CellDesigner (the front shape stays, the centre moves 3 px per unit over 2), so the rule is about
   where the target draws the node's main shape. The exceptions (complex name room, Newt's padding).
4. The centre-line move: a line yEd draws level from an off-centre port of a large node; CellDesigner
   draws from the centre or one of 16 anchors, so the converter moves the other end (iNOS CaM 25 px).
   Options: keep the move (tidy), an anchor, a hidden point under the node, or the slanted line reported.
5. The tidy default (on or off).
6. Complex name room (PLANNED.md): grow the complex, or move its members.

{% endraw %}

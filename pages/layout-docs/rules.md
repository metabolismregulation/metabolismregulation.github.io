---
layout: layout-docs
title: "Drawing rules"
permalink: /human-like-layout/documentation/rules/
sitemap: false
noindex: true
---
{% raw %}

The rules a layout follows, from the curator's edits of the Atlas maps. Strict rules hold on every map drawn
with the tool. Preferences hold where nothing stronger stands against them. Options are used where they fit. On
a map drawn by someone else the rules apply as far as room allows, and the drawer's geometry is kept.

When two rules collide, the higher one wins:

1. Content unchanged.
2. The curator's own geometry on this map: no pass undoes what they drew.
3. The story reads: the main story and its substories straight and regular.
4. No overlap, no arc through a node.
5. No crossing, on our own blocks and maps up to about 30 processes. On large maps and maps drawn by someone
   else crossings are counted, at 90 degrees where they stay. A short diagonal beats a crossing.
6. Room: 8 px between shapes, 30 px between lines and at arrowheads. Room is made, never squeezed.
7. Compact: no more room than that, and a corridor where a line must pass.
8. Regular elsewhere: equal steps, processes midway, aligned lines, grid.
9. Preferences: ports at node centres, soft bends, orthogonal segments, few bends.
10. Standards a script applies: icons, complex packing, compartment distances.

A lower rule is not traded against a higher one, and is not worked on while a higher one fails. Work stops when
the check shows nothing new on levels 3 to 6; levels 8 to 10 are left to the scripts.

## Sizes

| Glyph | Size |
|---|---|
| Macromolecule (protein) | 80 x 40, wider only when the name does not fit |
| Simple chemical (metabolite) | a 40 x 40 circle, a long name runs past it |
| Process | 18 x 18 |
| Logic operator | 30 x 30 |
| State variable | one or two letters (P, Ub, Ac) or none: a circle of 18 x 18. Three or more (Glut, active): a capsule 18 px tall, as wide as its text |
| Unit of information | 16 px tall, as wide as its text |

A node's footprint is its shapes: a metabolite's circle as a circle, any other node as its box, each icon and a
name running past the node as a box. Two nodes are too close when any of their shapes come closer than 8 px.

## Processes and arcs (strict)

- **Two antennas, for a reversible process only**: its two ends attach on opposite sides and modulation arcs on the
  other two, since arrows at both ends do not tell input from output. Other processes and logic gates do without
  the rule.
- Any number of modulation arcs per process, each aimed at the process centre.
- **No crossings** in a layout drawn here (our own blocks and maps up to about 30 processes): no arc crosses
  another, runs through a node or lies on another arc's line. A short diagonal arc is better than a crossing.
- **Room between lines**: an arc keeps 30 px from every node it passes and from another arc running beside it.
  Branches of one source into processes on one line share that line and fork at the processes.
- **Room at arrowheads and bends**: an arrow (its last segment) is at least 30 px long, and no bend is nearer
  than 30 px to an arrow's tip or to the node an arc leaves. A junction next to a process does not count.
- **Lanes**: two processes on one pair of nodes, opposite reactions or the same step by two enzymes, run in two
  lanes 12 px either side of the line between the nodes, their catalysts mirrored, never a V.
- **Regular series**: metabolites in a straight series at equal steps where possible, each process midway between
  its input and output, the outputs of one fan on one row. From scratch: a large grid first for the main story,
  then a smaller one for the rest.
- **A protein with one connection** sits beside the process it modulates, on a free side, level with it; several
  of one process are stacked 70 px apart along the flow. With one connection there is no conflict to weigh.

## Arcs (preferences for maps drawn in yEd)

- Arcs leave from and aim at the centre of the node, so the drawing stays right when nodes move. Exceptions: two
  arcs that would lie on one line into one side of a node (ports -6 and +6) and lanes (+-12).
- Every bend is soft (rounded corners). Hard corners only where the curator drew them.
- No bend points that do nothing. An arc bends only to go around something, and nodes are aligned so arcs run
  straight.
- An arc into a metabolite does not run through its name. The name goes under the circle, else above, else
  beside it, where none of its arcs run; only when all are taken, the metabolite or the arc's port moves 10 px.

## Placement (options)

- Main chain: a vertical column, top to bottom. A side chain may run towards the row it feeds. Cycles: a
  clockwise rectangle.
- Repeated events (a run of steps of one shape, each output acting on the next step) share one geometry: the
  same step, the same distances inside each step.
- A side substrate or product: beside the stem at the height of its junction, entering or leaving horizontally.
  Two side substrates: one on each side of the stem. Outputs mirror inputs about the process.
- A catalyst: on a free side of its process, on the line through its centre, a straight arc. Catalysts of the
  steps of one reaction row form one row beside it. A catalyst of two processes, also two consecutive steps:
  level with one, one bend to the other. A catalyst of several processes: one target in line with it, the others' processes on one column
  beside it, reached by one line that forks.
- One catalyst for parallel columns: the processes staggered in height so each catalysis arc is one straight
  line between the columns' nodes.
- A regulator on the main column leaves horizontally at its own level and turns once onto its target.
- A kinase and phosphatase switch can stand vertically, the active form nearest the reactions it catalyses.
- Transport across the plasma membrane: a thin membrane strip above the cytosol, the transport process on it,
  the outside species above it.
- Logic gates sit by their inputs, not by their target: each input joins the gate directly, the distance is
  carried by the one output line.

## Complexes (strict)

Packed compactly, the same margins on every complex, measured from a member's outline with everything yEd counts
(state variables, units of information, a multimer's second outline):

| Distance | px |
|---|---|
| Left and right edges | 12 |
| Top and bottom | 16 (units of information of a first-row member may sit in the top margin) |
| Between members, side by side or one above the other | 8 |
| Between a member and an inner complex one above the other | 10 |

Members in a row share a centre line, in a column too. A member with nothing beside it is centred on the others.
A ligand bound to a protein stands on top of it in a narrow column, the same in every complex of a chain.
Repeated complexes have the same inner layout on every map. Repacking keeps the arrangement and the complex's
centre, so the arcs at it stay straight.

## State variables and units of information

- One shape per place on a map: a site drawn as a capsule on one instance of a protein is a capsule on every
  instance.
- None on the top side of a multimer, where CellDesigner and MINERVA draw the multimer count (its top corners are
  allowed when there are many). Preferred: bottom right, then bottom left, then the sides.
- On the top or bottom side a state variable sits at the centre or a quarter point of the node's width, a pair at
  both quarter points, its centre on the node's border. A unit of information alone on a side is centred on it.
- Text centred in its icon.

## Compartments

- Every process and logic gate lies inside a compartment.
- Distances from a compartment edge to what it holds: a node or complex 32 px, a node with state variables on
  that side 40, a process or gate 48, an inner compartment 32. At these distances Newt keeps the compartment as
  drawn.
- Edges of sibling compartments on one side within 30 px of each other are one line.

## Grid

Node centres on an 8 px grid, bends on 4 px, for maps drawn in yEd. A complex's centre goes on the grid and its
members follow its packing, not the grid. Maps converted from CellDesigner keep their ports and get regular hubs
instead: parallel arcs leaving one side of a metabolite hub at regular intervals, processes off neighbouring
lines and on a straight run of their arc.

{% endraw %}

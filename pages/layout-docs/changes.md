---
layout: layout-docs
title: "Changes"
permalink: /human-like-layout/documentation/changes/
sitemap: false
noindex: true
---
{% raw %}

What changed for maps laid out with the tool, by date.

## 2026-10-26

- The finishing pass (`standardise.py`) runs again: its room-at-arrowheads step had stopped on the check's renamed
  line for reversible processes.

- Names of proteins, metabolites and the like always inside their shape, centred (strict); the check lists any
  that is not, and no longer counts arcs through a centred name.

- Two antennas only for reversible processes: elsewhere inputs, outputs and modulation may attach on any side, logic
  gates included. The check reports only reversible processes without them.

- A first layout grown from a map's content alone (`tree_layout.py`) is now a skill of its own, growing-layout,
  built on how plants grow. This tool finishes its drafts.

- One order for rules that collide (Drawing rules), and a point where work stops: when the check shows nothing new
  on the story, overlaps, crossings and room. Contradictions between pages removed: lanes 12 px, complex margins
  16 px, metabolites 40 x 40 circles, a metabolite's name placed before its arcs are moved, catalysts on the line
  through their process, previews no longer delivered with a layout.
- The skill's instructions halved (rules only, each marked strict, preference or option). Spacing of scripted
  builds 56 px from a node to its process and 24 px to a junction (was 50 and 29), side inputs 80 px from the stem
  (was 110): arrows and lines keep 30 px. An enzyme of two steps sits level with one of them, one bend to the other.

- A new map from its content is drawn first and fast, by the moves a person makes (`tree_layout.py`, under a
  second on 81 reactions): main story down the left column, branches in columns to the right, catalysts beside
  their process, branches as blocks on shelves, gates by their inputs. The other rules are checks for the
  finishing step. With `--both` the main story stays in the middle and the branches go to both sides, for a
  busy, large map.

- Paths: the steps of a layout can run in other orders, each a numbered path (P1 the order of the large-maps
  guide, P7 every arc at node centres until the end, metabolite names cleared last). Which is faster is tried on
  real maps. A vocabulary page defines the terms (story, block, module, push-out, breathing, ...).
- Two processes for the same step by two enzymes go into lanes like opposite reactions, never a V. The check
  reports pairs not in lanes.
- A guide for large maps and for confusing or slow tasks: nine steps coarse to fine.
- Breathing (`breathe.py`): room for a packed map from its hub outward, story by story or over the whole map,
  each node keeping its size; level and vertical arcs stay straight.
- A protein with one connection sits beside the process it modulates (`catalysts.py`).
- Regular series (`series.py`): equal steps along a story, processes midway between their input and output.

## 2026-10-25

- Room between lines: an arc keeps 30 px from the nodes it passes and from arcs beside it. The check reports
  arcs too close.
- Ligand complexes as narrow stacks, the ligand on top. A catalyst of several processes forks to them from one
  line. Complex packing counts a complex name shown at the bottom.
- The tool lays out only: content changes belong to the development of the map's content.

## 2026-10-24

- Opposite reactions in two lanes 12 px either side of the line between their nodes.
- Overlaps measured by shapes (circle, box, icons, name), 8 px between shapes.
- Stacked metabolites move 8 px apart with their branches. A catalyst of two processes: level with one, one
  bend to the other.

## 2026-10-23

- Every metabolite a 40 x 40 circle, a long name running past it. Arcs kept off a metabolite's name, and the
  check reports arcs through their own name.

## 2026-10-22

- The standardising pass: state variables and units of information, complexes packed, room at arrowheads and
  bends, compartments safe for Newt.
- No crossings in layouts drawn with the tool.
- State variables: circles of 18 px or capsules, one shape per place on a map, places at the centre, quarter
  points or corners. Units of information 16 px tall.
- Complex packing: 12 px sides, 16 px top and bottom, 8 px between members, members centred.

{% endraw %}

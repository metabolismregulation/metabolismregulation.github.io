---
layout: layout-docs
title: "Lay out a first map"
permalink: /human-like-layout/documentation/start/
sitemap: false
noindex: true
---
{% raw %}

The steps on one map of about 20 processes. A larger map goes through the same steps block by block
([Large maps](/human-like-layout/documentation/large-maps/)).

## 1. Read the map

`inspect_graphml.py` lists the map as text: every node with its size and position, the members of each complex,
every arc with its SBGN meaning (consumption, production, catalysis, inhibition), and the processes with several
modulators. A process has four sides: inputs take one, outputs the opposite one, so two sides are left for
modulation. A process on a cycle has only one side facing out. This decides early where modulators can come from.

## 2. Decide the story

The person decides, Claude proposes:

- the anchor, the step the map is about, usually a metabolic step,
- the main story, one chain from the anchor, top to bottom,
- the substories, chains with a biological meaning (one signalling route, one branch of a synthesis),
- the side each substory joins from: signals from outside the cell from the top, sensing inside the cell from a
  side, one branch on the straight line.

## 3. Draw the blocks

Each substory is a block in its own coordinates, in the standard form of the
[drawing rules](/human-like-layout/documentation/rules/): the main chain straight, side substrates beside the stem,
catalysts level with their process, complexes packed. A map build (a short Python script per map, with
`kit.py`) places the blocks in story order and routes the arcs between them.

## 4. Tidy

`standardise.py` sets the state variables and units of information to their sizes and places, packs the
complexes, makes room at arrowheads and bends, and brings compartments to standard distances. Two processes on
one pair of nodes go into lanes (`lanes.py`). A map drawn in yEd can be snapped to the grid (`snap_grid.py`), so
near-straight lines become straight.

## 5. Check

```
python3 check.py new.graphml --input old.graphml
```

It lists every change of content (there should be none), then the faults: overlaps, arcs through nodes,
crossings, arcs too close, short arrows, processes with an input on a modulator side, and more
([Checks](/human-like-layout/documentation/checks/)). Fix, check again. Three to six rounds are usual.

## 6. Finish in yEd

The GraphML goes to the curator, who opens it in yEd, moves what reads better elsewhere and exports SVG and PNG.
What the curator changes there is how the rules grow.

{% endraw %}

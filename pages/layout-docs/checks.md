---
layout: layout-docs
title: "Checks"
permalink: /human-like-layout/documentation/checks/
sitemap: false
noindex: true
---
{% raw %}

`check.py` reads a map and reports what breaks the [drawing rules](/human-like-layout/documentation/rules/). With
`--input old.graphml` it first lists every change of content since that file.

```
python3 check.py map.graphml [--input old.graphml]
```

## Content

Every node or arc added or removed, and every change of parent, class, name, state variables, properties, arc
ends or arrowheads. Nodes and arcs are matched by id. After a layout this list is empty.

## Faults

| Report | What it means |
|---|---|
| overlaps | two nodes closer than 8 px, shape by shape, at the top level and inside one compartment. Members of one complex only when their boxes overlap |
| edges through nodes | an arc runs through a node it does not belong to (a complex counts as one box) |
| arcs through their own name | an arc's end runs through the part of its own metabolite's name outside the circle |
| crossings | two arcs cross |
| arcs too close | an arc closer than 30 px to a node it passes or to an arc running beside it |
| room at arrowheads and bends | an arrow shorter than 30 px, or a bend nearer than 30 px to an arrow's tip or to the node an arc leaves |
| names not inside, centred | a protein, metabolite or the like whose name is not centred in its shape (strict) |
| reversible processes without two antennas | a reversible process whose two ends are not on opposite sides, or with a modulator on one of them |
| pairs of processes not in lanes | two processes on one pair of nodes not drawn as two lanes |
| icons off the standard | a state variable or unit of information off its size or place |
| complexes not as packed | a complex larger than its packing |
| groups yEd redraws | a complex or compartment whose stored box differs from what yEd draws on opening, so yEd would grow it into its neighbours |
| Newt would move or resize | a process outside every compartment, or a compartment edge closer to its contents than Newt needs |

## Preferences for maps drawn in yEd

| Report | What it means |
|---|---|
| off-centre ports | an arc that does not leave from or aim at the centre of its node (a port on the line the arc runs along counts as the centre) |
| bends not smoothed | an arc with hard corners |

## Measures

The share of orthogonal segments (level or vertical within 0.6 px), almost straight segments (off by 0.6 to 12 px
over a length at least twice that, meant straight but not quite), the extent of the map and its width to height
ratio.

{% endraw %}

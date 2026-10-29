---
layout: layout-docs
title: "Human-like layout documentation"
permalink: /human-like-layout/documentation/
sitemap: false
noindex: true
---
{% raw %}

Human-like layout lays out SBGN Process Description maps in yEd GraphML the way a curator draws them: the story
of the map first, then blocks, straight arcs and compact complexes. It is not a program with a layout engine. It
is a Claude skill: drawing rules that Claude follows, and scripts in Python that each do one fixed job on a map
(pack the complexes, size the state variables, put two parallel processes into lanes, snap to a grid, check).
The story decisions stay with the person who draws the map, and the map is finished by hand in yEd.

| Input | Output |
|---|---|
| yEd GraphML in the SBGN palette, drawn by hand or converted from CellDesigner or SBGN-ML by the [Converter](/converter/) | the same map in yEd GraphML, laid out, with a report of what the checks still find |

A layout changes geometry only: positions, sizes, arc routes and label places. Nodes, labels, complexes, state
variables and arcs stay as the map holds them, and the check lists every change of content since the input file.

## This documentation

- **Start**: [Lay out a first map](/human-like-layout/documentation/start/), the steps on one map.
- **How-to guides**: [short recipes](/human-like-layout/documentation/howto/) for one task each (tidy a map after a
  change, two processes in lanes, make room, carry a layout to a twin map, a large map).
- **Reference**: the [drawing rules](/human-like-layout/documentation/rules/), what the
  [checks](/human-like-layout/documentation/checks/) report, and the [scripts](/human-like-layout/documentation/scripts/), and the [vocabulary](/human-like-layout/documentation/vocabulary/).
- **Explanation**: how the tool is built ([Architecture](/human-like-layout/architecture/)), the
  [principles](/human-like-layout/documentation/principles/) it follows and how it handles
  [large maps](/human-like-layout/documentation/large-maps/).
- **Development**: the [issues](/human-like-layout/documentation/issues/), what is
  [planned](/human-like-layout/documentation/planned/) and the [changes](/human-like-layout/documentation/changes/) by date.

## Where it is used

The maps of the [Metabolism Regulation Atlas](/atlas/) are laid out with it. The rules come from the curator's
own edits: when a map comes back corrected in yEd, what applies to other maps becomes a rule.

{% endraw %}

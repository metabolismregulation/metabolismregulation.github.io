---
layout: layout-docs
title: "How-to guides"
permalink: /human-like-layout/documentation/howto/
sitemap: false
noindex: true
---
{% raw %}

Short recipes, one task each. The scripts run from the skill folder with Python 3 and lxml.

## Tidy a map after a change

After nodes were added or moved:

```
python3 standardise.py map.graphml map-tidy.graphml
python3 check.py map-tidy.graphml --input map.graphml
```

Four passes in a fixed order, each on the sizes the one before leaves: state variables and units of information,
complexes packed, room at arrowheads and bends, compartments safe for Newt. Nothing is kept that the check finds
worse. What could not be done is printed ("not done"): that part is left to the person.

## Put two processes on one pair of nodes into lanes

Two processes between the same two nodes, opposite (a kinase and a phosphatase) or parallel (the same step by two
enzymes), are drawn as two lanes 12 px either side of the line between the nodes, never as a V:

```
python3 lanes.py map.graphml map-lanes.graphml
```

The two nodes should stand on one line first. The check reports pairs not in lanes.

## Make room

When an arrow is too short or a new node needs space, in this order:

1. move the one node along its own line, if it can move freely,
2. move its connected block as one piece, so its lines stay as they are,
3. move everything past a line through the gap, the compartments the line crosses growing.

Move in 8 px steps and keep a move only when nothing else gets worse. `arrow_room.py` does this for room at
arrowheads and bends. `move_node.py` moves given nodes by whole steps with the bends on their centre lines.

## Snap a map drawn in yEd to the grid

```
python3 snap_grid.py map.graphml map-snapped.graphml
```

Node centres go onto an 8 px grid, bends onto 4 px. Points that belong on one line are grouped first, so a node
2 px off a column joins it. Not for maps converted from CellDesigner: use regular hubs there (below).

## Regular hubs on a map converted from CellDesigner

```
python3 hub_grid.py map.graphml map-hubs.graphml [hub label ...]
```

Parallel arcs leaving one side of a metabolite hub get regular intervals, processes come off neighbouring lines,
and bend points that do nothing go.

## Carry a layout to a twin map

Two maps with the same nodes and arcs (the same ids) but some content of their own, such as glycogen metabolism
in muscle and in liver: the layout of one goes onto the other, each keeping its content.

```
python3 transfer_layout.py edited.graphml twin.graphml twin-laid-out.graphml
```

## Check that the content did not change

```
python3 check.py new.graphml --input old.graphml
```

Nodes and arcs are matched by id. yEd renumbers ids when it saves a file, so compare a script's output with its
own input, not with a file saved by yEd in between.

## Lay out a large map

From a map of about 80 reactions, or when local fixes start undoing each other, stop fixing locally and go
coarse to fine: the story, blocks, placing the blocks, routing between them, hubs, the small grid, local passes,
labels, the check ([Large maps](/human-like-layout/documentation/large-maps/)).

{% endraw %}

---
layout: layout-docs
title: "Planned"
permalink: /human-like-layout/documentation/planned/
sitemap: false
noindex: true
---
{% raw %}

Agreed or proposed, not built yet.

| Piece | What it does | Size |
|---|---|---|
| Story spec | a short spec per map (main story, substories, hubs, sides), proposed from the graph and confirmed by the curator | about 100 lines |
| Placer | blocks placed on the large grid from the hubs outward, each arrangement scored (arc length between blocks, arcs against the flow, blocks out of their compartment) | about 150 lines |
| Router | the arcs between blocks on the 4 px grid, only through the strips between the blocks they join, longest first | about 200 lines |
| Path runner | runs each path's steps on a map and writes a table of the measures after every step | about 80 lines |
| Guard for snap to grid | a snap kept only when the check finds no new fault | small |
| Modules | pieces of biology drawn once and placed as they are on every map that needs them | files, little code |

{% endraw %}

---
layout: converter-docs
title: "How-to guides"
permalink: /converter/docs/howto/
sitemap: false
noindex: true
---
{% raw %}

Short recipes, one task each. They assume the [Converter page](/converter/) and a map that converts
(see [Convert a first map](/converter/docs/start/)).

## A round trip through CellDesigner

To edit a yEd map in CellDesigner and take it back to yEd.

1. Drop the GraphML on the Converter page. Take **CellDesigner (positions kept)** if it is offered: it
   is the CellDesigner file without the small moves that tidy lines, so nothing is moved that would
   add up over several trips. The button is there only when the moves changed the map.
2. Edit the file in CellDesigner 4.4 and save it.
3. Drop the saved file on the page and take **GraphML**: the CellDesigner drawing kept, as yEd draws
   it. **GraphML (straight line)** gives the same map with the yEd conventions and every arc straight.

What CellDesigner changed stays changed: the file is read as CellDesigner saved it.

## Open a map in Newt

1. Drop the GraphML, CellDesigner or SBGN-ML file on the page.
2. Click **Open in Newt** under the SBGN-ML files: Newt opens the file for Newt, in which every process
   sits in a compartment and each compartment has the room Newt's margin needs, so Newt keeps the
   map as drawn.
3. **Open in Newt / plain** opens the plain SBGN-ML, with the compartments as drawn, to see what Newt
   makes of it.

A file saved in Newt can come back the same way: drop the `.sbgn` or `.nwt` file on the page.

## Harmonise node sizes

To give a map the standard sizes (proteins 80 x 40, metabolites 40 x 40 circles, names in font size 14):

1. Tick **Standard node sizes** on the Converter page.
2. Drop the map. The button **GraphML (standard sizes)** gives the map with them, rescaled if its
   proteins are much larger or smaller.

Without the tick box the button appears only for a map drawn at another scale (thresholds in
[Inputs and outputs](/converter/description/)).

## A map the check marks red

A GraphML map that breaks a rule of SBGN Process Description (a production arrow pointing away
from its process, an arc ending on a compartment, ...) is converted without the elements that break it.

1. Take the red **GraphML (marked)** button: the map with those elements drawn red. In yEd, hovering
   over one shows the reason.
2. The same list is under the map as text, one line per element with its id and label.
3. Correct the map in yEd and drop it again. When nothing is red, every element is converted.

{% endraw %}

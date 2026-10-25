---
layout: converter-docs
title: "Convert a first map"
permalink: /converter/docs/start/
sitemap: false
noindex: true
---
{% raw %}

A walk through the [Converter page](/converter/) with a yEd map. It takes a minute.

## 1. A map to convert

Any yEd GraphML map drawn with the SBGN palette of yEd works. To start with a known map, download
the GraphML of a map from the [Atlas](/atlas/), for example glycolysis.

## 2. Drop it on the page

Open the [Converter page](/converter/) and drop the file on the drop area, or click it to choose the
file. The converter loads once (a few seconds the first time), then converts in the browser. A file
dropped while it loads waits and is converted once it has loaded.

The tick boxes next to the drop area choose the routes: only GraphML ⭤ CellDesigner at first. Tick
GraphML ⭤ SBGN-ML for the SBGN-ML files too. Ticking a box later adds its files to the maps already on
the page. The browser keeps the boxes as you left them.

## 3. Check what the converter said

Before conversion the map is checked against the rules of SBGN Process Description. If an element
breaks one, it is left out of the converted files, a red **GraphML (marked)** button gives the map with
it drawn red, and the problems are listed under the map, one per line. See
[A map the check marks red](/converter/docs/howto/#a-map-the-check-marks-red).

Under the buttons are the messages of each file: what was moved, written another way or left out. See
[Messages](/converter/docs/messages/).

## 4. Take the files

The blue button of each format is the recommended file. For a yEd map:

- **CellDesigner**: the drawing kept. Open it in CellDesigner 4.4.
- **SBGN-ML (newt-adjusted)**, with GraphML ⭤ SBGN-ML ticked: adjusted so that Newt keeps it as drawn.
  **Open in Newt** opens it there directly.
- The white buttons are fallback versions: straight line, plain SBGN-ML.

[Inputs and outputs](/converter/description/) says what each button's file holds.

## 5. Back to yEd

Drop the CellDesigner or SBGN-ML file on the page again: it gives a GraphML (for SBGN-ML, with
GraphML ⭤ SBGN-ML ticked). Compare it with the map
you started from. Differences beyond a few pixels are worth reporting.

{% endraw %}

---
layout: converter-docs
title: "Converter documentation"
permalink: /converter/docs/
sitemap: false
noindex: true
---
{% raw %}

The converter translates molecular interaction maps between three formats: yEd GraphML drawn in the
SBGN palette, CellDesigner 4.x and SBGN-ML (Process Description, also Newt files). It keeps the
drawing of the input map, the biology it states (entities, reactions, annotation) and says in its
messages what it changed or left out. It runs in the browser on the
[Converter page](/converter/), and the files never leave the computer.

| Input | Outputs |
|---|---|
| yEd GraphML | CellDesigner, SBGN-ML (plain and for Newt), each in two layouts |
| CellDesigner | GraphML, SBGN-ML (plain and for Newt), each in two layouts |
| SBGN-ML, Newt | GraphML, CellDesigner in two layouts |

Two layouts: advanced, the drawing of the input map kept, is the recommended file. Straight line, every
arc straight from centre to centre, is a fallback for laying out by hand.

## This documentation

- **Start**: [Convert a first map](/converter/docs/start/), a walk through the Converter page.
- **How-to guides**: [short recipes](/converter/docs/howto/) for one task each (a round trip through
  CellDesigner, opening a map in Newt, harmonising node sizes, a map the check marks red).
- **Reference**: what each input gives ([Inputs and outputs](/converter/description/)), what the
  [messages](/converter/docs/messages/) under a map mean, and the conventions of each format, as
  learnt from files saved by the programs themselves.
- **Explanation**: how the converter is built ([Architecture](/converter/architecture/)) and the
  [design principles](/converter/docs/design/) it follows, each with the reason it was chosen.
- **Development**: the [issues](/converter/docs/issues/), everything unresolved with how long it
  has been open, the [open questions](/converter/docs/decisions/), what is
  [planned](/converter/docs/planned/), how conversion [quality](/converter/docs/quality/) is
  measured, and the [changes](/converter/docs/changes/) by date.

The pages under Reference and Development are working records, kept as the converter is developed:
each rule names the file or the date it comes from.

{% endraw %}

---
title: "Multisite phosphorylation: ERK2 by MEK1"
topic: "Multisite phosphorylation"
tab: "ERK2 by MEK1"
page: ""
group: "Modification cycles"
order: 9
kind: "map"
draft: false
tag: ""
image: "/pattern-atlas-downloads/erk2-multisite-phosphorylation.svg"
width: 290
height: 519
scale: 1
annotation: "/atlas-data/pattern-erk2-multisite-phosphorylation.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/erk2-multisite-phosphorylation.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/erk2-multisite-phosphorylation.svg"}
---
MEK1 phosphorylates ERK2 on two sites in its activation loop, a threonine and a tyrosine. The phosphorylation is distributive: MEK1 releases ERK2 after each site, so full activation needs two separate encounters. Only the doubly phosphorylated ERK2 is fully active, the singly phosphorylated form being 10 to 100 times less active. Needing both sites makes the steady-state response more switch-like than a single site would, and it adds a lag to activation.

## Source

**Book.** Ferrell 2022, sections 5.8, 5.9 and 5.12, multisite phosphorylation (the two ERK2 sites in section 12.5). The book's example is ERK2, activated by MEK1 on two sites, with MEK1 itself as the contrast: MEK1 is phosphorylated on two sites too, but is fully active after the first.

**From the book in this map.** ERK2 in its three states (none, one and both sites phosphorylated) and MEK1 catalysing both steps. Drawn new for this page.

**Not in the book, so not drawn.** The phosphatase that reverses the two steps, which the book does not name in this example. Which site is phosphorylated first is not shown: the circles mark one and two phosphates.

**MRegAtlas.** The MRegAtlas draws MEK1/2 activating ERK1/2 as one step, in [Eicosanoids](/atlas/#eicosanoids) and [Pyrimidine biosynthesis](/atlas/#pyrimidine).

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

---
title: "Negative feedback oscillator: the Goodwin model"
topic: "Negative feedback oscillator (Goodwin)"
tab: "Gene, mRNA, enzyme and product"
page: ""
group: "Oscillators and excitability"
order: 30
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/goodwin-oscillator.svg"
width: 890
height: 535
scale: 1
annotation: "/atlas-data/pattern-goodwin-oscillator.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/goodwin-oscillator.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/goodwin-oscillator.svg"}
---
A negative feedback loop with enough delay and enough ultrasensitivity oscillates. In Goodwin's model a gene is transcribed into an mRNA, the mRNA translated into an enzyme, the enzyme makes a small molecule, and the small molecule inhibits transcription. Each tier is made and destroyed, so the product's rise shuts the gene off, and its fall lets it start again. Three tiers and a steep feedback are needed for sustained oscillations, which are born at a Hopf bifurcation. The model has been used for circadian clocks and the gliding of myxobacteria.

## Source

**Book.** Ferrell 2022, sections 14.1 to 14.5, the Goodwin oscillator.

**From the book in this map.** The gene, its transcription and the mRNA, translation and the enzyme, the product, the three degradations, and the product inhibiting transcription. Drawn new for this page.

**Not in the book, so not drawn.** The repressor through which the product acts, so it inhibits the transcription itself, and a particular gene: the labels are generic and have no identifiers. The model has no compartments, so the nucleus is not drawn.

**MRegAtlas.** Gene expression is drawn on the MRegAtlas in [Estrogen](/atlas/#estrogen) and [iNOS](/atlas/#inos). No MRegAtlas map draws a transcriptional oscillator.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

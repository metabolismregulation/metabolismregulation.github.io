---
title: "Regulated production and destruction: cAMP made and destroyed"
topic: "Regulated production and destruction"
tab: "cAMP"
page: ""
group: "Production and destruction"
order: 14
kind: "map"
draft: false
tag: ""
image: "/pattern-atlas-downloads/camp-production-destruction.svg"
width: 706
height: 878
scale: 1
annotation: "/atlas-data/pattern-camp-production-destruction.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/camp-production-destruction.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/camp-production-destruction.svg"}
---
Gsα bound to GTP activates adenylate cyclase, which makes cAMP from ATP. A phosphodiesterase, here PDE3B, hydrolyses cAMP to AMP. cAMP releases the catalytic subunit of PKA, the readout of the cAMP level.

With first-order destruction, the steady cAMP level is proportional to the rate of synthesis, and the time to reach a new level after a change of input depends on the rate of destruction alone.

## Source

**Book.** Ferrell 2022, sections 6.1 and 6.2, regulated production and destruction. The book's example is cAMP, made when the GTP-bound Gαs subunit activates adenylyl cyclase and acting on protein kinase A, with its destruction treated as a first-order process.

**From the book in this map.** Gsα with GTP, adenylate cyclase, ATP to cAMP, and PKA.

**Added from the MRegAtlas.** The enzyme that destroys cAMP, which the book does not name: PDE3B, as the MRegAtlas cAMP map draws it.

**MRegAtlas.** The book's example overlaps with the maps [Glycogen metabolism (muscle)](/atlas/#glycogen-muscle) (cAMP synthesis, PKA) and [cAMP hydrolysis](/atlas/#camp) (PDE3B). The drawing here is taken from them. The cAMP hydrolysis map also shows PKA and AKT phosphorylating PDE3B, so that cAMP speeds up its own destruction, a negative feedback.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

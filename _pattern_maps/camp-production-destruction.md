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
width: 1012
height: 712
scale: 1
annotation: "/atlas-data/pattern-camp-production-destruction.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/camp-production-destruction.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/camp-production-destruction.svg"}
---
Gαs bound to GTP activates adenylyl cyclase, which makes cAMP from ATP, and cAMP is destroyed at a rate proportional to its level. cAMP stoichiometrically activates its targets, protein kinase A and cAMP-regulated ion channels. The cAMP level is set by the balance of production and destruction, so a change in either rate changes the steady state, and the time to reach it is set by the destruction rate alone.

With first-order destruction, the steady cAMP level is proportional to the rate of synthesis, and the time to reach a new level after a change of input depends on the rate of destruction alone.

## Source

**Book.** Ferrell 2022, sections 6.1 and 6.2, regulated production and destruction. The book's example is cAMP, made when the GTP-bound Gαs subunit activates adenylyl cyclase and acting on protein kinase A, with its destruction treated as a first-order process.

**From the book in this map.** Gαs with GTP, adenylyl cyclase, ATP to cAMP, cAMP destroyed, and cAMP binding PKA and a cAMP-regulated ion channel. Drawn new for this page.

**Added for the drawing.** Gαs:GTP binding adenylyl cyclase into the complex that makes cAMP, as the MRegAtlas draws G proteins. The identifiers of Gαs and adenylyl cyclase as the MRegAtlas has them. PKA and the channel stay one box each, as the book names them, without identifiers.

**Not in the book, so not drawn.** The enzyme that destroys cAMP, so the destruction has no catalyst.

**MRegAtlas.** The book's example overlaps with the maps [Glycogen metabolism (muscle)](/atlas/#glycogen-muscle) (cAMP synthesis, PKA) and [cAMP hydrolysis](/atlas/#camp) (PDE3B). The extended version below is taken from them. The cAMP hydrolysis map also shows PKA and AKT phosphorylating PDE3B, so that cAMP speeds up its own destruction, a negative feedback.

## Extended version

![camp-production-destruction extended](/pattern-atlas-downloads/camp-production-destruction-extended.svg)

cAMP as the MRegAtlas maps draw it, with what the book does not name: PKA as its regulatory and catalytic subunits, cAMP freeing the catalytic subunit, and the phosphodiesterase PDE3B hydrolysing cAMP to AMP. Taken from the MRegAtlas maps of muscle glycogen and cAMP hydrolysis.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

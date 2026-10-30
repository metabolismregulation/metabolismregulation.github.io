---
title: "Multisite phosphorylation for specificity: MEK, ERK and JNK"
topic: "Multisite phosphorylation for specificity (kinetic proofreading)"
tab: "MEK on ERK and JNK"
page: ""
group: "Modification cycles"
order: 11
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/mek-erk-jnk-specificity.svg"
width: 710
height: 379
scale: 1
annotation: "/atlas-data/pattern-mek-erk-jnk-specificity.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/mek-erk-jnk-specificity.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/mek-erk-jnk-specificity.svg"}
---
Human cells run parallel MAP kinase cascades, MEK1/2 to ERK1/2 and MKK4/7 to the JNKs, with little cross-talk. The two phosphorylations each MAP kinase needs act as kinetic proofreading. MEK phosphorylates ERK twice, but when it phosphorylates an off-target MAP kinase once, the singly phosphorylated protein is likely to be released and dephosphorylated before the second phosphorylation, so the wrong kinase seldom becomes active.

## Source

**Book.** Ferrell 2022, section 5.11, multisite phosphorylation for specificity in parallel MAP kinase cascades.

**From the book in this map.** MEK phosphorylating ERK on two sites and JNK on one, and the dephosphorylation of the singly phosphorylated JNK. Drawn new for this page.

**Not in the book, so not drawn.** The phosphatase, so the dephosphorylation has no catalyst, and the JNK cascade's own kinases. The identifiers are MAP2K1 and MAP2K2 for MEK, MAPK3 and MAPK1 for ERK, MAPK8, MAPK9 and MAPK10 for JNK.

**MRegAtlas.** The MRegAtlas draws MEK1/2 activating ERK1/2 as one step, in [Eicosanoids](/atlas/#eicosanoids) and [Pyrimidine biosynthesis](/atlas/#pyrimidine). No MRegAtlas map draws JNK.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

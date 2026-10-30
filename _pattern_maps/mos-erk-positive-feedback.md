---
title: "Positive feedback: Mos and ERK2 in oocyte maturation"
topic: "Positive feedback: bistable switch (one variable)"
tab: "Mos and ERK2"
page: ""
group: "Feedback"
order: 9
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/mos-erk-positive-feedback.svg"
width: 575
height: 540
scale: 1
annotation: "/atlas-data/pattern-mos-erk-positive-feedback.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/mos-erk-positive-feedback.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/mos-erk-positive-feedback.svg"}
---
In Xenopus oocytes, progesterone starts the synthesis of Mos, a MAP kinase kinase kinase. Mos activates MEK1, MEK1 activates ERK2, and active ERK2 stimulates Mos synthesis in turn, while Mos is degraded. With this positive feedback the response of ERK2 is all-or-none, and it is irreversible: once ERK2 is active, it stays active for hours after progesterone is washed away. Blocking Mos synthesis makes the response graded. The switch flips when rising progesterone takes the system past a saddle-node bifurcation.

## Source

**Book.** Ferrell 2022, sections 8.2 to 8.8, bistability from positive feedback in progesterone-induced oocyte maturation.

**From the book in this map.** Progesterone, Mos made and degraded, MEK1 and ERK2 each activated by phosphorylation, and active ERK2 stimulating Mos synthesis. Mos synthesis is drawn as the book's model has it, one step stimulated by progesterone (the basal term) and by active ERK2 (the feedback term), not as transcription and translation. Drawn new for this page.

**Not in the book, so not drawn.** The steps between progesterone and Mos translation (the book names a drop in cAMP and Aurora A), the phosphatases, and Cdk1, the cascade's target in maturation.

**MRegAtlas.** No MRegAtlas map draws Mos. A positive feedback is drawn in [Eicosanoids](/atlas/#eicosanoids), where Ca2+ stimulates its own release from the endoplasmic reticulum.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

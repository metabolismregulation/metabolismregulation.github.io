---
title: "Excitability: ERK pulses"
topic: "Excitability"
tab: "ERK1/2 in epithelial cells"
page: ""
group: "Oscillators and excitability"
order: 36
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/erk-excitability.svg"
width: 825
height: 790
scale: 1
annotation: "/atlas-data/pattern-erk-excitability.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/erk-excitability.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/erk-excitability.svg"}
---
In MCF-10A epithelial cells ERK1/2 activity comes in sporadic pulses. A fast positive feedback loop coupled to a slower negative one makes an excitable system: it rests, but a large enough push makes it fire a full pulse and return. The book takes the metalloprotease loop as the positive feedback: active ERK activates metalloproteases that release EGF and TGF-α from the membrane, and these activate more EGF receptors. The slower negative feedback is the induction of a MAP kinase phosphatase, which inactivates ERK. Noise can make such a system fire at random.

## Source

**Book.** Ferrell 2022, sections 16.1 and 16.2, excitability, with ERK1/2 pulses and the loops the book chooses for its model.

**From the book in this map.** The release of EGF by a metalloprotease, EGF binding its receptor, ERK activated and inactivated by MKP, MKP made and destroyed, and active ERK acting on the release and on MKP synthesis. Drawn new for this page.

**Added for the drawing.** ERK's activation stimulated by the ligand-bound receptor and the release stimulated by active ERK, drawn on the processes since the steps between are not in the model. MKP made in one step, not as transcription and translation. The identifiers are EGF, EGFR, MAPK3 and MAPK1 for ERK and DUSP1 for MKP. The metalloprotease is generic and has none.

**Not in the book, so not drawn.** TGF-α and the other candidate loops (receptor and phosphatases, Ras-GTP on Sos, ERK's dual phosphorylation, FGF release).

**MRegAtlas.** The book's example overlaps with [Pyrimidine biosynthesis](/atlas/#pyrimidine), which draws EGF-bound EGFR and the cascade to ERK1/2. No MRegAtlas map draws MKP.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

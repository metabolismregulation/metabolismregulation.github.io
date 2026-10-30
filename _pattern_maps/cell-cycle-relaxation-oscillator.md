---
title: "Relaxation oscillator: the embryonic cell cycle"
topic: "Relaxation oscillator: negative feedback plus bistable trigger"
tab: "Cyclin B, Cdk1 and APC/C-Cdc20"
page: ""
group: "Oscillators and excitability"
order: 32
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/cell-cycle-relaxation-oscillator.svg"
width: 798
height: 775
scale: 1
annotation: "/atlas-data/pattern-cell-cycle-relaxation-oscillator.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/cell-cycle-relaxation-oscillator.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/cell-cycle-relaxation-oscillator.svg"}
---
The early Xenopus embryo divides every 30 minutes, driven by a biochemical oscillator. Cyclin B is made steadily and binds Cdk1. A bistable trigger of positive and double-negative feedback (Cdc25C and Wee1) holds the complex inactive until cyclin B passes a threshold and then switches it on explosively. Active Cdk1 activates APC/C-Cdc20 by phosphorylation, which polyubiquitylates cyclin B and sends it to the proteasome, so Cdk1 falls and the cycle starts again. A slow negative feedback around a fast bistable switch makes a relaxation oscillator, robust and tunable in period more than amplitude.

## Source

**Book.** Ferrell 2022, sections 15.1 to 15.6, the cell cycle oscillator, drawn as its simplified model (15.3).

**From the book in this map.** Cyclin B made and bound to Cdk1, the complex activated with positive feedback and inactivated, APC/C-Cdc20 activated by Cdk1, and the destruction of cyclin B, releasing Cdk1. Drawn new for this page.

**Added for the drawing.** New complexes entering in the inactive form, and a second Cdk1 for the one released, so the arc does not cross the map. The identifiers are CCNB1 and CCNB2 for cyclin B, CDK1 and CDC20. APC/C, a complex of many subunits, has none.

**Not in the book, so not drawn.** The destruction of cyclin B in the inactive complex and free, also in the model, and the parts of the full circuit the simplified model lumps: Cdc25C and Wee1 (the Pattern Atlas map [Hysteretic switch](/pattern-atlas/#cdk1-hysteretic-switch)), Greatwall, ENSA, ARPP19 and PP2A-B55.

**MRegAtlas.** No MRegAtlas map draws the cell cycle.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

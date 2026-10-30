---
title: "Hysteretic switch: cyclin B and Cdk1"
topic: "Hysteretic bistable switch"
tab: "Cyclin B-Cdk1 activation"
page: ""
group: "Feedback"
order: 21
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/cdk1-hysteretic-switch.svg"
width: 565
height: 705
scale: 1
annotation: "/atlas-data/pattern-cdk1-hysteretic-switch.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/cdk1-hysteretic-switch.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/cdk1-hysteretic-switch.svg"}
---
A bistable switch need not be irreversible. With weaker feedback it is hysteretic: it switches on at one input level and off at a lower one, and between the two it stays where it was. The activation of cyclin B-Cdk1 by cyclin B is hysteretic. Cyclin B is made and binds Cdk1, Wee1 phosphorylates and inactivates Cdk1 and Cdc25C reactivates it, and active Cdk1 activates Cdc25C and inactivates Wee1. Cdk1 turns on only when cyclin B passes a high threshold and stays on until cyclin B falls well below it, so mitotic entry and exit are clean transitions.

## Source

**Book.** Ferrell 2022, section 8.9, hysteretic responses, with the activation of Cdk1, and section 15.2, the mitotic trigger.

**From the book in this map.** Cyclin B made and bound to Cdk1, the phosphorylation and dephosphorylation of Cdk1 by Wee1 and Cdc25C, and Cdk1 acting on both. Drawn new for this page.

**Not in the book, so not drawn.** The kinases and phosphatases that reinforce the loops (PP2A-B55 and Greatwall). The identifiers are CCNB1 and CCNB2 for cyclin B, CDK1, WEE1 and CDC25C.

**MRegAtlas.** No MRegAtlas map draws the cell cycle. The same trigger without cyclin synthesis is the Pattern Atlas map [Interlinked feedback loops](/pattern-atlas/#cdk1-interlinked-loops).

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

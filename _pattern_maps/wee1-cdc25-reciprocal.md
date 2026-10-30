---
title: "Reciprocal regulation: DNA damage on Wee1 and Cdc25"
topic: "Reciprocal regulation"
tab: "Wee1 and Cdc25 on Cdk1"
page: ""
group: "Modification cycles"
order: 13
kind: "map"
draft: false
tag: ""
image: "/pattern-atlas-downloads/wee1-cdc25-reciprocal.svg"
width: 470
height: 561
scale: 1
annotation: "/atlas-data/pattern-wee1-cdc25-reciprocal.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/wee1-cdc25-reciprocal.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/wee1-cdc25-reciprocal.svg"}
---
Wee1 phosphorylates cyclin B-Cdk1 and blocks mitotic entry, and the phosphatase Cdc25 removes that phosphate. DNA damage leads to the phosphorylation and activation of Wee1 and to the phosphorylation and inhibition of Cdc25. One input turns up the enzyme that inactivates Cdk1 and turns down the one that reactivates it, so both act in the same direction. Regulating the two opposing enzymes in this way can make the response of Cdk1 more switch-like than acting on one of them.

## Source

**Book.** Ferrell 2022, section 5.15, reciprocal regulation. The book's example is DNA damage acting on Wee1 and Cdc25, which phosphorylate and dephosphorylate cyclin B-Cdk1, the master mitotic regulator.

**From the book in this map.** Every molecule and step the book names: DNA damage, Wee1 and Cdc25 each in two states, and cyclin B-Cdk1 active and phosphorylated. Drawn new for this page.

**Not in the book, so not drawn.** The kinases between DNA damage and Wee1 or Cdc25. DNA damage therefore acts on the two phosphorylations directly. Labels are as the book names the proteins. The identifiers are the human genes (WEE1, CDC25A, CDC25B, CDC25C, CCNB1, CCNB2, CDK1).

**MRegAtlas.** No MRegAtlas map draws Wee1 or Cdc25. The same pattern is in two maps: AMP stimulates the phosphorylation of AMPK and inhibits its dephosphorylation ([Mevalonate biosynthesis](/atlas/#mevalonate)), and the branched-chain keto acids inhibit the kinase BCKDK and stimulate the phosphatase PPM1K ([BCAA catabolism](/atlas/#bcaa)).

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

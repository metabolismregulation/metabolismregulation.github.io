---
title: "Adaptation: bacterial chemotaxis"
topic: "Negative feedback: adaptation"
tab: "E. coli chemotaxis"
page: ""
group: "Pulses and adaptation"
order: 27
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/chemotaxis-adaptation.svg"
width: 780
height: 699
scale: 1
annotation: "/atlas-data/pattern-chemotaxis-adaptation.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/chemotaxis-adaptation.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/chemotaxis-adaptation.svg"}
---
E. coli swims in runs and tumbles, and it adapts perfectly to a steady level of attractant. The aspartate receptor Tar, linked through CheW to the histidine kinase CheA, is active when methylated and free of aspartate. Aspartate binding inactivates it, and the cell suppresses tumbling. Active receptors activate the demethylase CheB, which demethylates active receptors and puts them in reserve, while the unregulated CheR methylates them back. When aspartate rises, active receptors fall, CheB activity falls, methylation wins and the active receptors return to exactly where they were, whatever the aspartate level.

## Source

**Book.** Ferrell 2022, sections 12.1 to 12.3, perfect adaptation through negative feedback, with E. coli chemotaxis.

**From the book in this map.** The receptor complex in its three states (active, aspartate-bound, demethylated in reserve), aspartate binding, demethylation by active CheB and methylation by CheR, and CheB activated by active receptors. Drawn new for this page.

**Added for the drawing.** CheB's two states as "active" and empty, as the book names them without saying how CheB is activated. The identifiers are the E. coli proteins in UniProt and aspartate in ChEBI.

**Not in the book, so not drawn.** The serine receptor Tsr, the flagellar motor and the signal from CheA to it.

**MRegAtlas.** No MRegAtlas map draws bacterial proteins.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

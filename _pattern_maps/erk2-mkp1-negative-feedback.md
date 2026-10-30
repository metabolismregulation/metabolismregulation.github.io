---
title: "Delayed negative feedback: ERK2 and MKP1"
topic: "Delayed negative feedback (transcriptional)"
tab: "ERK2 and MKP1"
page: ""
group: "Pulses and adaptation"
order: 12
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/erk2-mkp1-negative-feedback.svg"
width: 485
height: 575
scale: 1
annotation: "/atlas-data/pattern-erk2-mkp1-negative-feedback.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/erk2-mkp1-negative-feedback.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/erk2-mkp1-negative-feedback.svg"}
---
MEK activates ERK2. Active ERK2 induces the phosphatase MKP1, and MKP1 inactivates ERK2, while MKP1 is itself degraded. Because MKP1 has to be made first, the feedback comes with a delay: a sustained mitogen gives a pulse of ERK2 activity that falls back close to its starting level, near-perfect adaptation. Making the feedback more ultrasensitive makes the adaptation closer to perfect.

## Source

**Book.** Ferrell 2022, sections 12.4 to 12.6, adaptation by delayed negative feedback, with ERK2 and MKP1 as the example. The book adds that in several cell types (PC12, 3T3-L1, PAE) the ERK pulse does not need new gene products, so other loops act there (section 12.7).

**From the book in this map.** MEK, ERK2 inactive and doubly phosphorylated, MKP1 made at a rate set by active ERK2 and degraded. MKP1 synthesis is drawn as the book's model has it, one step stimulated by active ERK2, not as transcription and translation. Drawn new for this page.

**MRegAtlas.** No MRegAtlas map draws MKP1. A negative feedback is in [cAMP hydrolysis](/atlas/#camp): cAMP frees PKA, which phosphorylates the phosphodiesterase PDE3B that destroys cAMP.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

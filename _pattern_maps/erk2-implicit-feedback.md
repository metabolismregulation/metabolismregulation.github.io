---
title: "Implicit positive feedback: ERK2 dual phosphorylation"
topic: "Implicit positive feedback in multisite phosphorylation"
tab: "ERK2, MEK1 and MKP3 (model)"
page: ""
group: "Feedback"
order: 27
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/erk2-implicit-feedback.svg"
width: 470
height: 599
scale: 1
annotation: "/atlas-data/pattern-erk2-implicit-feedback.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/erk2-implicit-feedback.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/erk2-implicit-feedback.svg"}
---
MEK1 phosphorylates ERK2 on two sites and the phosphatase MKP3 removes them, each one site at a time. When both enzymes work near saturation and ERK2 is about as abundant as they are, the three forms of ERK2 compete for the kinase and the phosphatase. The doubly phosphorylated form then promotes its own production, a positive feedback that no arc carries, and the system can be bistable with two sites or multistable with more. This was found in a computational study and has not been tested in cells. The documented cases of bistability in cells all involve explicit feedback loops, and depending on the parameters, sequestration of the substrate by the enzymes can instead reduce ultrasensitivity.

## Source

**Paper.** Ferrell and Ha 2014b, section "Saturation and competition in multisite phosphorylation" and its box on implicit positive feedback, describing the computational study of Kholodenko and co-workers on ERK2, MEK1 and MKP3. Not in the book.

**From the paper in this map.** ERK2 in its three forms, MEK1 on both phosphorylations and MKP3 on both dephosphorylations. Drawn new for this page. The feedback is in the kinetics, so the map shows only the two cycles it needs.

**Added for the drawing.** The identifiers are MAPK1, MAP2K1 and DUSP6 (MKP3).

**MRegAtlas.** The MRegAtlas draws MEK1/2 activating ERK1/2 as one step, in [Eicosanoids](/atlas/#eicosanoids) and [Pyrimidine biosynthesis](/atlas/#pyrimidine). The two steps apart, without the phosphatase, are the Pattern Atlas map [Multisite phosphorylation](/pattern-atlas/#erk2-multisite-phosphorylation).

## References

1. Ferrell JE Jr, Ha SH. Ultrasensitivity part II: multisite phosphorylation, stoichiometric inhibitors, and positive feedback. Trends Biochem Sci. 2014;39(11):556-569. doi: [10.1016/j.tibs.2014.09.003](https://doi.org/10.1016/j.tibs.2014.09.003){:target="_blank" rel="noopener"}.

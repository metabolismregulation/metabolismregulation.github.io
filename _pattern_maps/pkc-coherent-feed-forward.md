---
title: "Coherent feed-forward: PKC activated by DAG and Ca2+"
topic: "Coherent feed-forward"
tab: "PKC by DAG and Ca2+"
page: ""
group: "Feed-forward"
order: 4
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/pkc-coherent-feed-forward.svg"
width: 754
height: 994
scale: 1
annotation: "/atlas-data/pattern-pkc-coherent-feed-forward.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/pkc-coherent-feed-forward.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/pkc-coherent-feed-forward.svg"}
---
A phospholipase C converts PI(4,5)P2 into diacylglycerol (DAG) and IP3. DAG binds classical protein kinase C (PKC) and helps recruit it to the plasma membrane. IP3 binds its receptor and releases Ca2+ from the endoplasmic reticulum, and Ca2+ then binds DAG-bound PKC and activates it. PLC reaches active PKC by two routes of the same sign, one through DAG and one through IP3 and Ca2+, so the active kinase needs both. Coherent feed-forward regulation of this kind can make the response ultrasensitive.

## Source

**Book.** Ferrell 2022, section 5.14, coherent feed-forward regulation. The book's example is the activation of classical PKC: PLC makes DG and IP3 from PIP2, DG recruits PKC to the plasma membrane, IP3 releases Ca2+ from the endoplasmic reticulum, and Ca2+ activates DG-bound PKC. The book's model has the three PKC states drawn here: free, with DG, and with DG and Ca2+.

**From the book in this map.** Every molecule and step the book names. Drawn new for this page. DG is labelled DAG, as on the MRegAtlas.

**Added for the drawing.** The IP3 receptor: the book says IP3 regulates Ca2+ release from the endoplasmic reticulum, and the MRegAtlas draws that release through IP3 bound to its receptor. The identifiers are the human genes, PKC as the classical isoforms (PRKCA, PRKCB, PRKCG), PLC and the IP3 receptor as the families the MRegAtlas uses.

**MRegAtlas.** The book's example overlaps with the [Eicosanoids](/atlas/#eicosanoids) map, which draws PLC making DAG and IP3, the IP3 receptor releasing Ca2+, and DAG acting on PKC. Names and identifiers here are taken from it. The same pattern is in [Triacylglycerol hydrolysis](/atlas/#tag), where PKA acts on lipolysis by two routes, through hormone-sensitive lipase and through its complex with perilipin 1.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

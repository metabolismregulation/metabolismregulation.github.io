---
title: "Incoherent feed-forward: EGFR, Sos and GAP on Ras"
topic: "Incoherent feed-forward"
tab: "EGFR, Sos and GAP on Ras"
page: ""
group: "Feed-forward"
order: 8
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/egfr-sos-gap-incoherent.svg"
width: 702
height: 689
scale: 1
annotation: "/atlas-data/pattern-egfr-sos-gap-incoherent.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/egfr-sos-gap-incoherent.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/egfr-sos-gap-incoherent.svg"}
---
The activated, autophosphorylated EGF receptor recruits the exchange factor Sos, and then the GTPase-activating protein p120 GAP. EGFR with Sos turns Ras on, exchanging its GDP for GTP, and EGFR with Sos and GAP turns it off by hydrolysing the GTP. The receptor thus brings about both the activation of Ras and, after a lag, its inactivation: a pulse of Ras activity under a sustained stimulus, and one that returns to the same baseline whatever the stimulus, perfect adaptation.

## Source

**Book.** Ferrell 2022, sections 13.1 to 13.4, incoherent feed-forward regulation, with the sequential recruitment of Sos and GAP to the EGFR as the example. The book's model has the receptor in three forms (alone, with Sos, with Sos and GAP) and adds that strict ordering of the two is not needed for perfect adaptation.

**From the book in this map.** The activated EGFR, Sos, GAP, the two receptor complexes, and Ras with GDP and with GTP. Drawn new for this page. Bound GDP and GTP are drawn as members of the Ras complexes, as on the MRegAtlas.

**Not in the book, so not drawn.** The adaptors Shc and Grb2 through which Sos comes to the receptor, and Ras-GTP activating Sos (a positive feedback, in its own map). The free GTP, GDP and phosphate are left out of the two Ras steps.

**MRegAtlas.** The book's example overlaps with [Pyrimidine biosynthesis](/atlas/#pyrimidine), where EGF-bound EGFR stimulates the GDP for GTP exchange on RAS. Sos and GAP are not drawn there.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

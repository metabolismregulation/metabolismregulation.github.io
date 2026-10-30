---
title: "Regulation of glutamine synthesis via glutamine synthetase degradation"
topic: "Glutamine synthetase"
tab: ""
page: "/glutamine-synthetase/"
group: "Amino acid metabolism"
order: 27
kind: "map"
draft: true
tag: "draft-ext"
image: "/atlas-downloads/F032-glutamine-synthetase.svg"
width: 1206
height: 498
scale: 1
annotation: "/atlas-data/F032-glutamine-synthetase.json"
image_error: ""
contributors:
  - alexander-mazein: [lih-cancer]
downloads:
  - {label: "GraphML", url: "/atlas-downloads/F032-glutamine-synthetase.graphml"}
  - {label: "SVG", url: "/atlas-downloads/F032-glutamine-synthetase.svg"}
---
## Selection

Selected by literature curation, as part of the extension of the Atlas. The feedback of glutamine on the enzyme that makes it acts through acetylation and ubiquitin-dependent degradation, steps that the Reactome-Recon lists do not hold for glutamine synthetase.

## Description

Glutamine synthetase (GLUL) builds glutamine from glutamate, ammonium and ATP, the step by which cells store nitrogen and remove ammonia. Its own product closes a feedback loop on the enzyme. When glutamine is abundant, glutamine synthetase is acetylated on Lys11 and Lys14 near its amino terminus, and the acetylated end acts as a degron recognised by cereblon (CRBN), the substrate receptor of the CRL4 ubiquitin ligase (Nguyen 2016). Cereblon directs the ubiquitylation of the enzyme, which is then extracted by the ATPase p97 (VCP) and destroyed by the proteasome (Nguyen 2017). The deubiquitinase USP15 opposes this, removing ubiquitin from glutamine synthetase and slowing its turnover, so the balance of ligase and deubiquitinase sets how much enzyme survives (Nguyen 2021). The acetyltransferase that writes the degron has not been identified. Because cereblon is also the target of thalidomide-type drugs, this acetylation signal links the control of glutamine supply to a pathway better known from cancer therapy, although the drugs bind cereblon without competing with the degron (Nguyen 2016).

## References

1. Nguyen TV, Lee JE, Sweredoski MJ, Yang SJ, Jeon SJ, Harrison JS, Yim JH, Lee SG, Handa H, Kuhlman B, Jeong JS, Reitsma JM, Park CS, Hess S, Deshaies RJ. Glutamine Triggers Acetylation-Dependent Degradation of Glutamine Synthetase via the Thalidomide Receptor Cereblon. Mol Cell. 2016 Mar 17;61(6):809-20. doi: 10.1016/j.molcel.2016.02.032. PMID: 26990986.
1. Nguyen TV, Li J, Lu CJ, Mamrosh JL, Lu G, Cathers BE, Deshaies RJ. p97/VCP promotes degradation of CRBN substrate glutamine synthetase and neosubstrates. Proc Natl Acad Sci U S A. 2017 Apr 4;114(14):3565-3571. doi: 10.1073/pnas.1700949114. PMID: 28320958.
1. Nguyen TV. USP15 antagonizes CRL4(CRBN)-mediated ubiquitylation of glutamine synthetase and neosubstrates. Proc Natl Acad Sci U S A. 2021 Oct 5;118(40). doi: 10.1073/pnas.2111391118. PMID: 34583995.
1. Reactome: glutamate + NH4+ + ATP => glutamine + ADP + orthophosphate [GLUL]. [Reactome:R-HSA-70606](https://reactome.org/content/detail/R-HSA-70606){:target="_blank" rel="noopener"}.

## Contributors

{% include contributors.html %}

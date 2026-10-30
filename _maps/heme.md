---
title: "Regulation of heme synthesis via ALAS1"
topic: "Heme synthesis"
tab: ""
page: "/heme/"
group: "Porphyrin metabolism"
order: 31
kind: "map"
draft: true
tag: "draft-ext"
image: "/atlas-downloads/F030-heme.svg"
width: 930
height: 1382
scale: 1
annotation: "/atlas-data/F030-heme.json"
image_error: ""
contributors:
  - alexander-mazein: [lih-cancer]
downloads:
  - {label: "GraphML", url: "/atlas-downloads/F030-heme.graphml"}
  - {label: "SVG", url: "/atlas-downloads/F030-heme.svg"}
---
## Selection

Selected by literature curation, as part of the extension of the Atlas. The feedback of heme on the first enzyme of its synthesis acts through protein import, cofactor loading and protein degradation, steps that the Reactome-Recon lists do not hold for ALAS1, which appears there only through its gene expression.

## Description

Heme controls its own production by acting on the first enzyme of the pathway. In cells outside the erythron, 5-aminolevulinate synthase 1 (ALAS1) condenses glycine with succinyl-CoA to 5-aminolevulinate, carbon dioxide and coenzyme A, a reaction that depends on pyridoxal 5'-phosphate (PLP) and sets the rate of heme synthesis (Brown 2018). The enzyme is made in the cytoplasm as a precursor and must be carried into the mitochondrial matrix. Heme binds short cysteine-proline motifs in the precursor and holds it back from import, so a cell with ample heme delivers less enzyme to the matrix (Lathrop 1993, Munakata 2004). Inside the matrix the chaperone CLPX loads the PLP cofactor and so switches the enzyme on (Kardon 2015). The same chaperone also ends its life. When heme occupies a cysteine-proline motif at the start of the mature protein, the enzyme is handed to the CLPX-CLPP protease (Kubota 2016, Nomura 2021). The heme-sensing adaptor POLDIP2 binds the heme-loaded enzyme and delivers it for destruction (Cottle 2026). A second route through the matrix protease LONP1 acts after heme has oxidatively modified the enzyme (Tian 2011). Heme also lowers the amount of ALAS1 mRNA, and in fasting the coactivator PGC-1alpha raises it, which links nutritional state to heme production and explains why fasting can precipitate attacks of acute hepatic porphyria (Handschin 2005, Roberts 2005).

## References

1. Brown BL, Kardon JR, Sauer RT, Baker TA. Structure of the Mitochondrial Aminolevulinic Acid Synthase, a Key Heme Biosynthetic Enzyme. Structure. 2018 Apr 3;26(4):580-589.e4. doi: 10.1016/j.str.2018.02.012. PMID: 29551290.
1. Cottle T, Joh L, Posner C, DeCosta A, Campagna DR, Fleming MD, Ducamp S, Kardon JR. An adaptor for feedback regulation of heme biosynthesis by a mitochondrial protease. Science. 2026 Jul 30;393(6810):eads5397. doi: 10.1126/science.ads5397. PMID: 42531414.
1. Handschin C, Lin J, Rhee J, Peyer AK, Chin S, Wu PH, Meyer UA, Spiegelman BM. Nutritional regulation of hepatic heme biosynthesis and porphyria through PGC-1alpha. Cell. 2005 Aug 26;122(4):505-15. doi: 10.1016/j.cell.2005.06.040. PMID: 16122419.
1. Kardon JR, Yien YY, Huston NC, Branco DS, Hildick-Smith GJ, Rhee KY, Paw BH, Baker TA. Mitochondrial ClpX Activates a Key Enzyme for Heme Biosynthesis and Erythropoiesis. Cell. 2015 May 7;161(4):858-67. doi: 10.1016/j.cell.2015.04.017. PMID: 25957689.
1. Kubota Y, Nomura K, Katoh Y, Yamashita R, Kaneko K, Furuyama K. Novel Mechanisms for Heme-dependent Degradation of ALAS1 Protein as a Component of Negative Feedback Regulation of Heme Biosynthesis. J Biol Chem. 2016 Sep 23;291(39):20516-29. doi: 10.1074/jbc.M116.719161. PMID: 27496948.
1. Lathrop JT, Timko MP. Regulation by heme of mitochondrial protein transport through a conserved amino acid motif. Science. 1993 Jan 22;259(5094):522-5. doi: 10.1126/science.8424176. PMID: 8424176.
1. Munakata H, Sun JY, Yoshida K, Nakatani T, Honda E, Hayakawa S, Furuyama K, Hayashi N. Role of the heme regulatory motif in the heme-mediated inhibition of mitochondrial import of 5-aminolevulinate synthase. J Biochem. 2004 Aug;136(2):233-8. doi: 10.1093/jb/mvh112. PMID: 15496594.
1. Nomura K, Kitagawa Y, Aihara M, Ohki Y, Furuyama K, Hirokawa T. Heme-dependent recognition of 5-aminolevulinate synthase by the human mitochondrial molecular chaperone ClpX. FEBS Lett. 2021 Dec;595(24):3019-3029. doi: 10.1002/1873-3468.14214. PMID: 34704252.
1. Roberts AG, Redding SJ, Llewellyn DH. An alternatively-spliced exon in the 5'-UTR of human ALAS1 mRNA inhibits translation and renders it resistant to haem-mediated decay. FEBS Lett. 2005 Feb 14;579(5):1061-6. doi: 10.1016/j.febslet.2004.12.080. PMID: 15710391.
1. Tian Q, Li T, Hou W, Zheng J, Schrum LW, Bonkovsky HL. Lon peptidase 1 (LONP1)-dependent breakdown of mitochondrial 5-aminolevulinic acid synthase protein by heme in human liver cells. J Biol Chem. 2011 Jul 29;286(30):26424-30. doi: 10.1074/jbc.M110.215772. PMID: 21659532.

## Contributors

{% include contributors.html %}

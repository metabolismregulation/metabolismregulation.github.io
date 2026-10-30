---
title: "Regulation of cytosolic aconitase and iron sensing via IRP1 and IRP2"
topic: "Iron sensing"
tab: ""
page: "/iron-sensing/"
group: "Iron-sulfur cluster metabolism"
order: 40
kind: "map"
draft: true
tag: "draft-ext"
image: "/atlas-downloads/F029-iron-sensing.svg"
width: 1226
height: 866
scale: 1
annotation: "/atlas-data/F029-iron-sensing.json"
image_error: ""
contributors:
  - alexander-mazein: [lih-cancer]
downloads:
  - {label: "GraphML", url: "/atlas-downloads/F029-iron-sensing.graphml"}
  - {label: "SVG", url: "/atlas-downloads/F029-iron-sensing.svg"}
---
## Selection

Selected from the Reactome-Recon pipeline, as part of the extension of the Atlas. ACO1 and IREB2 are in the <a href="/reactome-recon-proteins/">Reactome-Recon lists</a>, proteins of the Recon2 metabolic reconstruction that take part in Reactome signalling processes, through the processes <a href="https://reactome.org/content/detail/R-HSA-5690873">ACO1 binds 4Fe-4S</a> (R-HSA-5690873) and <a href="https://reactome.org/content/detail/R-HSA-5691108">SKP1:FBXL5:CUL1:NEDD8 ubiquitinylates IREB2</a> (R-HSA-5691108).

## Description

Cytosolic aconitase (ACO1) interconverts citrate and isocitrate through cis-aconitate when it holds an intact [4Fe-4S] cluster (Kaptain 1991, Dupuy 2006). The cluster makes the enzyme a sensor of cellular iron. When iron is scarce or the cluster is lost, ACO1 loses its aconitase activity and becomes iron regulatory protein 1 (IRP1), which binds iron-responsive elements in messenger RNAs (Rouault 2006). Its binding to the element at the start of the ferritin heavy chain (FTH1) mRNA keeps the ribosome off, so less ferritin is made when iron is short (Walden 2006). At the oxygen levels of tissues most IRP1 stays an aconitase, and a second protein, IRP2 (IREB2), which has no enzyme activity, carries most of the regulation of the same mRNAs (Meyron-Holtz 2004, Hentze 2010). IRP2 is controlled by its stability. In cells with enough iron and oxygen, the F-box protein FBXL5 binds both through its hemerythrin domain and, as part of the SKP1-CUL1-FBXL5 ubiquitin ligase, marks IRP2 for degradation by the proteasome (Salahudeen 2009, Vashisht 2009, Ruiz 2014). An oxygen-sensitive [2Fe-2S] cluster in FBXL5 adds a further check on this step (Wang 2020). Iron and oxygen thus set the balance between the enzyme form and the RNA-binding forms of these proteins, and through them how much iron the cell stores.

## References

1. Dupuy J, Volbeda A, Carpentier P, Darnault C, Moulis JM, Fontecilla-Camps JC. Crystal structure of human iron regulatory protein 1 as cytosolic aconitase. Structure. 2006 Jan;14(1):129-39. doi: 10.1016/j.str.2005.09.009. PMID: 16407072.
1. Hentze MW, Muckenthaler MU, Galy B, Camaschella C. Two to tango: regulation of Mammalian iron metabolism. Cell. 2010 Jul 9;142(1):24-38. doi: 10.1016/j.cell.2010.06.028. PMID: 20603012.
1. Kaptain S, Downey WE, Tang C, Philpott C, Haile D, Orloff DG, Harford JB, Rouault TA, Klausner RD. A regulated RNA binding protein also possesses aconitase activity. Proc Natl Acad Sci U S A. 1991 Nov 15;88(22):10109-13. doi: 10.1073/pnas.88.22.10109. PMID: 1946430.
1. Meyron-Holtz EG, Ghosh MC, Rouault TA. Mammalian tissue oxygen levels modulate iron-regulatory protein activities in vivo. Science. 2004 Dec 17;306(5704):2087-90. doi: 10.1126/science.1103786. PMID: 15604406.
1. Reactome: ACO1 binds 4Fe-4S. [Reactome:R-HSA-5690873](https://reactome.org/content/detail/R-HSA-5690873){:target="_blank" rel="noopener"}.
1. Reactome: SKP1:FBXL5:CUL1:NEDD8 ubiquitinylates IREB2. [Reactome:R-HSA-5691108](https://reactome.org/content/detail/R-HSA-5691108){:target="_blank" rel="noopener"}.
1. Rouault TA. The role of iron regulatory proteins in mammalian iron homeostasis and disease. Nat Chem Biol. 2006 Aug;2(8):406-14. doi: 10.1038/nchembio807. PMID: 16850017.
1. Ruiz JC, Bruick RK. F-box and leucine-rich repeat protein 5 (FBXL5): sensing intracellular iron and oxygen. J Inorg Biochem. 2014 Apr;133:73-7. doi: 10.1016/j.jinorgbio.2014.01.015. PMID: 24508277.
1. Salahudeen AA, Thompson JW, Ruiz JC, Ma HW, Kinch LN, Li Q, Grishin NV, Bruick RK. An E3 ligase possessing an iron-responsive hemerythrin domain is a regulator of iron homeostasis. Science. 2009 Oct 30;326(5953):722-6. doi: 10.1126/science.1176326. PMID: 19762597.
1. Vashisht AA, Zumbrennen KB, Huang X, Powers DN, Durazo A, Sun D, Bhaskaran N, Persson A, Uhlen M, Sangfelt O, Spruck C, Leibold EA, Wohlschlegel JA. Control of iron homeostasis by an iron-regulated ubiquitin ligase. Science. 2009 Oct 30;326(5953):718-21. doi: 10.1126/science.1176333. PMID: 19762596.
1. Walden WE, Selezneva AI, Dupuy J, Volbeda A, Fontecilla-Camps JC, Theil EC, Volz K. Structure of dual function iron regulatory protein 1 complexed with ferritin IRE-RNA. Science. 2006 Dec 22;314(5807):1903-8. doi: 10.1126/science.1133116. PMID: 17185597.
1. Wang H, Shi H, Rajan M, Canarie ER, Hong S, Simoneschi D, Pagano M, Bush MF, Stoll S, Leibold EA, Zheng N. FBXL5 Regulates IRP2 Stability in Iron Homeostasis via an Oxygen-Responsive [2Fe2S] Cluster. Mol Cell. 2020 Apr 2;78(1):31-41.e5. doi: 10.1016/j.molcel.2020.02.011. PMID: 32126207.

## Contributors

{% include contributors.html %}

---
layout: default
title: Tools
permalink: /tools/
---

# yEd Graph Editor

<a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> from yWorks GmbH is a freely available graph editor written in Java that runs on Windows, macOS, and Linux/Unix. It is a powerful desktop application that can be used to quickly and effectively generate high-quality diagrams.

yEd uses the XML-based GraphML format to load and save diagrams and additionally supports import from Excel spreadsheets (.xls, .xlsx) and arbitrary XML (via XSLT). Creating diagrams manually is easy and fun with the intuitive user interface, and a large collection of powerful layout algorithms allows nodes and edges to be arranged automatically. Diagrams can be exported to bitmap and vector formats: PNG, JPG, SVG and PDF.

Since <a href="https://www.yworks.com/products/yed/release-notes" target="_blank">version 3.17.1</a>, yEd provides a palette section for Systems Biology Graphical Notation.

There are some <a href="/help/" target="_blank">tips</a> available on how to use yEd for drawing SBGN diagrams.

# ySBGN

<a href="https://github.com/sbgn/ySBGN" target="_blank">ySBGN</a> is a standalone Java application, a bidirectional converter between the GraphML format of the <a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> and the SBGN Process Description or Activity Flow languages (Balaur et al., 2022, PMID: 36563404).

Now diagrams can be created in the intuitive general-purpose <a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> using the SBGN Palette available since <a href="https://www.yworks.com/products/yed/release-notes" target="_blank">version 3.17.1</a>, and, thanks to the converter, the outcome can be offered in the standard SBGN-ML format. The ySBGN tool supports keeping annotation information in the SBGN-ML format.

For reporting issues please use the <a href="https://github.com/sbgn/ySBGN/issues" target="_blank">ySBGN GitHub Issues</a> page.

# CellDesigner

<a href="http://www.celldesigner.org" target="_blank">CellDesigner</a> is a diagram editor developed by the Systems Biology Institute for drawing process diagrams (Kitano et al., 2005, PMID: 16082367) using the graphical notation proposed by Prof. Hiroaki Kitano. The diagrams are stored in <a href="http://sbml.org/" target="_blank">SBML</a> format. CellDesigner supports the development of mathematical models and is integrated with SBML ODE Solver, SBML Simulation Core and Copasi. The entities on a diagram can be annotated and linked to various databases.

CellDesigner supports a system of symbols based on a draft of the Systems Biology Graphical Notation (SBGN) Process Description language Level 1 proposed in 2008 (more information can be found <a href="http://www.celldesigner.org/features.html" target="_blank">here</a>). The <a href="http://www.celldesigner.org/help/CDH_View_08.html" target="_blank">SBGN Viewer</a> tool in CellDesigner can be used to see a diagram in the current version of <a href="http://sbgn.org/" target="_blank">SBGN</a> (Le Novère et al., 2009, PMID: 19668183).

# Newt Editor

<a href="http://newteditor.org/" target="_blank">Newt Editor</a> is a free, web-based, open-source viewer and editor for pathways in Systems Biology Graphical Notation.  It is written with a series of libraries and extensions based on <a href="http://js.cytoscape.org/" target="_blank">Cytoscape.js</a>.

Newt is developed to make it easy to design SBGN diagrams: rich yet minimalistic user-friendly UI; support for developing maps from scratch; automatic layout facilities; full support for complexes, compartments and submaps; state-of-the-art complexity management through hide-show and collapse-expand functionalities; advanced diagramming with grid and alignment support, resizing and styling map objects, and more.

# SBGN-ED

[SBGN-ED](http://www.sbgn-ed.org) is an open-source SBGN editor which allows users to create, edit and explore diagrams in all three SBGN languages: Process Description, Activity Flow and Entity Relationship (Czauderna et al., 2010, PMID: 20628075). It allows validation of the syntactic and semantic correctness of created or edited maps. Already existing non-SBGN maps from the KEGG database can be translated into SBGN PD maps including automatic layout. Translation of PD to AF maps and visualisation of SBML models in SBGN PD are also provided. Additionally, the tool allows SBGN maps to be exported into several file and image formats including the SBGN-ML format.  

SBGN-ED is an add-on to the [VANTED framework](http://www.vanted.org). VANTED is an integrative and extendable framework for systems biology applications which aims at the integration, analysis and visual exploration of experimental data in the context of biological networks as well as the modelling, simulation and analysis of molecular biological processes.

# References

1. Balaur I, Roy L, Touré V, Mazein A, Auffray C. GraphML-SBGN bidirectional converter for metabolic networks. J Integr Bioinform. 2022 Dec 1;19(4):20220030. doi: 10.1515/jib-2022-0030. PMID: 36563404.
1. Czauderna T, Klukas C, Schreiber F. Editing, validating and translating of SBGN maps. Bioinformatics. 2010 Sep 15;26(18):2340-1. doi: 10.1093/bioinformatics/btq407. PMID: 20628075.
1. Kitano H, Funahashi A, Matsuoka Y, Oda K. Using process diagrams for the graphical representation of biological networks. Nat Biotechnol. 2005 Aug;23(8):961-6. doi: 10.1038/nbt1111. PMID: 16082367.
1. Le Novère N, Hucka M, Mi H, Moodie S, Schreiber F, Sorokin A, Demir E, Wegner K, Aladjem MI, Wimalaratne SM, Bergman FT, Gauges R, Ghazal P, Kawaji H, Li L, Matsuoka Y, Villéger A, Boyd SE, Calzone L, Courtot M, Dogrusoz U, Freeman TC, Funahashi A, Ghosh S, Jouraku A, Kim S, Kolpakov F, Luna A, Sahle S, Schmidt E, Watterson S, Wu G, Goryanin I, Kell DB, Sander C, Sauro H, Snoep JL, Kohn K, Kitano H. The Systems Biology Graphical Notation. Nat Biotechnol. 2009 Aug;27(8):735-41. doi: 10.1038/nbt.1558. PMID: 19668183.


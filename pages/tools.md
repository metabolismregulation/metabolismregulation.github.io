---
layout: default
title: Tools
permalink: /tools/
---

# yEd Graph Editor
        
<p><a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> from yWorks GmbH is a freely available graph editor written in Java that runs on Windows, macOS, and Linux/Unix. It is a powerful desktop application that can be used to quickly and effectively generate high-quality diagrams.</p>
        
<p>yEd uses the XML-based GraphML format to load/save diagrams and additionally supports import from Excel spreadsheets (.xls, .xlsx) and arbitrary XML (via XSLT). Creating diagrams manually is easy and fun with the intuitive user interface, and a large collection of powerful layout algorithms allows to automatically arrange nodes and edges. Diagrams can be exported to bitmap and vector formats: PNG, JPG, and SVG, PDF.</p>
        
<p>Since <a href="https://www.yworks.com/products/yed/download#ReleaseNotes" target="_blank">version 3.17.1</a> yEd provides a palette section for Systems Biology Graphical Notation.</p>

<p>There are some <a href="/help/" target="_blank">tips</a> available on how to use yEd for drawing SBGN diagrams.</p>

# ySBGN

<p><a href="https://github.com/sbgn/ySBGN" target="_blank">ySBGN</a> is a standalone Java application, a bidirectional converter between GraphML format of the <a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> and the SBGN Process Description or Activity Flow languages [Balaur et al. 2022, PMID: 36563404; DOI: <a href="https://www.degruyter.com/document/doi/10.1515/jib-2022-0030/html">10.1515/jib-2022-0030</a>. </p>

<p>Now diagrams can be created in the intuitive general-purpose <a href="https://www.yworks.com/products/yed" target="_blank">yEd Graph Editor</a> using the SBGN Palette available since <a href="https://www.yworks.com/products/yed/download#ReleaseNotes" target="_blank">version 3.17.1</a>, and, thanks to the converter, the outcome could be offered in the standard Systems Biology format. The ySBGN tool supports keeping annotation information in the SBGN-ML format.</p>

<p>For reporting issues please use <a href="https://github.com/sbgn/ySBGN/issues" target="_blank">ySBGN GitHub Issues</a> page.</p>
        
# Newt Editor

<p><a href="http://newteditor.org/" target="_blank">Newt Editor</a> is a free, web-based, open-source viewer and editor for pathways in Systems Biology Graphical Notation.  It is written with a series of libraries and extensions based on <a href="http://js.cytoscape.org/" target="_blank">Cytoscape.js</a>.</p>
        
<p>Newt is developed to make it easy to design SBGN diagrams: rich yet minimalistic user-friendly IU; support for developing maps from scratch; automatic layout facilities; full support for complexes, compartments and submaps; state-of-the-art complexity management through hide-show and collapse-expand functionalities; advanced diagramming with grid and alignment support, resizing and styling map objects, and more.</p>

# SBGN-ED

[SBGN-ED](http://www.sbgn-ed.org) is an open-source SBGN editor which allows creating, editing and exploring diagrams in all three SBGN languages: Process Description, Activity Flow and Entity Relationship (Czauderna et al., 2010, [doi:/10.1093/bioinformatics/btq407](https://doi.org/10.1093/bioinformatics/btq407)). It allows validation of the syntactical and semantical correctness of created or edited maps. Already existing non-SBGN maps from the KEGG database can be translated into SBGN PD maps including automatic layout. Translation of PD to AF maps and visualisation of SBML models in SBGN PD are also provided. Additionally, the tool allows exporting of SBGN maps into several file and image formats including the SBGN-ML format.  

SBGN-ED is an add-on of the [VANTED framework](http://www.vanted.org). VANTED is an integrative and extendable framework for systems biology applications which aims at the integration, analysis and visual exploration of experimental data in the context of biological networks as well as the modelling, simulation and analysis of molecular biological processes.

# CellDesigner

<p><a href="http://www.celldesigner.org" target="_blank">CellDesigner</a> is a diagram editor developed by the Systems Biology Institute for drawing process diagrams (Kitano et al., 2005, PMID <a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=19668183" target="_blank">19668183</a>) using the graphical notation proposed by Prof. Hiroaki Kitano, and stored in <a href="http://sbml.org/" target="_blank">SBML</a> format. CellDesigner supports the development of mathematical models and is integrated with SBML ODE Solver, SBML Simulation Core and Copasi. The entities on a diagram can be annotated and linked to various databases.</p>
        
<p>CellDesigner supports a system of symbols based on a draft of the Systems Biology Graphical Notation (SBGN) Process Description language Level 1 proposed in 2008 (more information can be found <a href="http://www.celldesigner.org/features.html" target="_blank">here</a>). <a href="http://www.celldesigner.org/help/CDH_View_08.html" target="_blank">SBGN Viewer</a> tool in CellDesigner can be used to see a diagram in the current version of <a href="http://sbgn.org/" target="_blank">SBGN</a> (Le Novère et al., 2009, PMID <a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=19668183" target="_blank">19668183</a>).</p>

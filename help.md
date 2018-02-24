---
layout: default
title: Quick Help
permalink: /help/
---

# How to draw SBGN diagrams in yEd

## Modifying general settings

* The SBGN palette can be placed to the top of the palette section: Edit > Manage Palette. Here you can delete unwanted palettes and define in what order palettes will be shown.  

## Auxiliary units

* To transform a shape into a unit of information or a state variable: **right click on the shape > Convert to Label**

* To edit a unit of information or a state variable: **right click on the label > Convert to Node** and then transform back to label.

## Process "ports"

* A process is represented by a square box linked to two connectors, small arcs attached to the centers of opposite sides.

&emsp; &emsp; &emsp; <img src="/images/yEd/processglyph150.png" alt="process" style="width:50px;height:50px;">

* In addition to snap-to-guideline feature of yEd, there is snap-to-bend-point feature. This feature is to be used to co-position bend points as if they were "ports" of a process so you see two small arcs for each process or a logic operator.

## Complex

* Hold **Shift** and drag for moving a shape inside a complex or a compartment.

* To copy an element which is inside a complex it is better to use right click options. This might not work easily with the usual shortcuts: for some reason **Ctrl-V** copies the element inside the same complex or compartment. Instead, after **Ctrl-C**, use right click to paste the selected element outside the complex or compartment.

## Tips

* To modify all objects of the same type: go to Current Elements palette at the bottom of the palette section, select an element, **right click > Select Matching Elements**.

* To make smooth bend points: **right click on a link > Properties > Bends > Smooth Bends**.

* To modify font size for all objects: select all objects and edit using Properties View on the right-hand side.

## Contact 

With questions or suggestion please [contact us](/about).


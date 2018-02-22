---
layout: default
title: Quick Help
permalink: /help/
---

# How to draw SBGN diagrams in yEd

## Modifying general settings

* The SBGN palette can be placed to the top of the palette section: Edit > Manage Palette. Here you can delete unwanted palettes and define in what order palettes will be shown.  

* Making shapes painted over links (this way links will not cross auxiliary units): Preferences > Display > Paint Nodes Over Edges. Still, in case of incoming links, arrowheads might be partly hidden behind an auxiliary unit. Then the coordinates of the port can be modified manually by dragging the port or by typing in new coordinates.

## Auxiliary units

* To transform a shape into a unit of information or a state variable: **right click on the shape > Convert to Label**

* To edit a unit of information or a state variable: **right click on the label > Convert to Node**. And then, to transform back to label: **right click on the shape > Convert to Label**

## Process "ports"

A process is represented by a square box linked to two connectors, small arcs attached to the centers of opposite sides.

image

In addition to snap-to-guideline feature of yEd, there is snap-to-bend-point feature. This feature is to be used to co-position bend points as if they were "ports" of a process so you see two small arcs for each process or a logic operator.

## Complex

* Hold **Shift** for moving a shape inside a complex

* To copy an element which is inside a complex. This might not work easily with shortcuts: **Ctrl-C** followed by **Ctrl-V**. Instead use right click to paste the element outside this complex or compartment.

## Tips

* To modify all objects of the same type: go to **Current Elements** palette at the bottom of the palette section, select an element, **right click > Select Matching Elements**.

* To make smooth bend points: **right click on a link > Properties > Bends > Smooth Bends**.

* To modify font size for all objects: **Ctrl-A** on Windows or **Command-A** on Mac, then edit using **Properties View** on the right-hand side.



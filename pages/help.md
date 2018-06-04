---
layout: default
title: Quick Help
permalink: /help/
---

# How to draw SBGN diagrams in yEd

This is a collection of tips on drawing SBGN diagrams in yEd Graph Editor. This page is not meant to be an introduction to yEd. To learn more about yEd please review tutorials at the yEd website and relevant YouTube videos. Here we offer a quick help for the use of the SBGN palette.

## Modifying general settings

* The SBGN palette can be placed to the top of the palette section: Edit > Manage Palette. Here you can delete unwanted palettes and define in what order palettes will be shown.  
* File > Preferences > Editor > Dynamically Adjust Node Size to Label Size. Make sure the box is unchecked.
* To remove group state icon for compartments: File > Preferences > Display > Group State Icon > Never Show Group State.

## Auxiliary units

* To transform a shape into a unit of information or a state variable: place _State Variable_ or _Unit of Information_ from the SBGN palette to the canvas on the top of the shape you would like it to be attached to, right click on a shape, then choose Convert to Label. If created properly, the auxiliary unit will move when the "host" shape is moved.

* To edit a _Unit of Information_ or a _State Variable_: right click on the label, choose Convert to Node and then transform back to label as described above.

## Process "ports"

In SBGN a process is represented by a square box linked to two connectors, small arcs ("antennas") attached to the centers of opposite sides.  

&emsp; <img src="/images/yEd/processglyph150.png" alt="process" style="width:50px;height:50px;">  

There is no dedicated support for such "ports" in yEd at the moment. The small two small "antennas" have to be created by making bend points on the links. There is the snap-to-bend-point feature in yEd. This feature is to be used to co-position bend points as if they were "ports" of a process so you see two small arcs for each process or a logic operator.

## Complex and compartment

* Hold Shift and drag for moving a shape inside a complex or a compartment. When an element belongs to a complex or compartment, it will move when the complex/compartment is moved.

* To copy an element which is inside a complex it is better to use right click options. This might not work easily with the usual shortcuts: for some reason Ctrl-V copies the element inside the same complex or compartment. Instead, after Ctrl-C, use right click to paste the selected element outside the complex or compartment.

## Cardinality

To add cardinality to an arc: right click on the arc that links the entity to the process > Properties > Label tab. The following settings should be used:  

Background: #ffffff  
Border: #000000  
Model: Side Slider  
Position: Dynamic  
Along Edge: Centered  
Side of Edge: On Edge  
Orientation: Parallel  
Auto-Rotate with Edge: check  

<img src="/images/yEd/cardinality.png" alt="cardinality" style="width:400px;">

Then move the label manually to the desired position.  

## Other tips

* To transform one object type into another object type, for example to transform *macromolecule* glyph into *nucleic acid feature* glyph: select an object, on the palette choose the desired object, right click > Apply Type.

* To edit all objects of the same type: go to Current Elements palette at the bottom of the palette section, select an element, right click > Select Matching Elements.

* To make smooth bend points: right click on a link > Properties > Bends > Smooth Bends.

* To modify font size for all objects: select all objects and edit using Properties View on the right-hand side.

## Contact 

With questions or suggestion please [contact](/about) us.



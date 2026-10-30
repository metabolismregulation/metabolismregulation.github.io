---
title: "FitzHugh-Nagumo oscillator"
topic: "FitzHugh–Nagumo oscillator"
tab: "Membrane potential and recovery"
page: ""
group: "Oscillators and excitability"
order: 33
kind: "map"
draft: false
tag: "draft"
image: "/pattern-atlas-downloads/fitzhugh-nagumo-oscillator.svg"
width: 860
height: 430
scale: 1
annotation: "/atlas-data/pattern-fitzhugh-nagumo-oscillator.json"
image_error: ""
downloads:
  - {label: "GraphML", url: "/pattern-atlas-downloads/fitzhugh-nagumo-oscillator.graphml"}
  - {label: "SVG", url: "/pattern-atlas-downloads/fitzhugh-nagumo-oscillator.svg"}
---
The FitzHugh-Nagumo model reduces the Hodgkin-Huxley model of the action potential to two variables. A fast bistable switch drives the membrane potential up once it passes a threshold, and a slow recovery variable, raised by the potential, brings it back to rest. With the right parameters the potential oscillates like the pacemaker of the sinoatrial node. The model has the same systems-level logic as the cell cycle oscillator, a quick switch with slower negative feedback.

## Source

**Book.** Ferrell 2022, sections 15.8 to 15.10, the FitzHugh-Nagumo model.

**From the book in this map.** The two variables, the potential stimulating its own rise and the rise of the recovery variable, and the recovery variable inhibiting the potential. Drawn new for this page.

**Added for the drawing.** The two variables as unspecified entities, made and removed: SBGN Process Description has no glyph for a voltage, so this drawing shows the model's logic and not a molecular mechanism.

**Not in the book, so not drawn.** The ion channels behind the two variables.

**MRegAtlas.** No MRegAtlas map draws membrane potential.

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

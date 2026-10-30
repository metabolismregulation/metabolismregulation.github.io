---
layout: page
title: Regulation Patterns
permalink: /regulation-patterns/
sitemap: false
noindex: true
---

{% assign dl = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg>' %}

Cell signalling and metabolic regulation use the same few patterns again and again: binding, covalent modification cycles, regulated production and destruction, cascades, feedback and feed-forward loops. Each pattern gives a characteristic response, graded or switch-like, a lasting switch, a pulse or an oscillation. This page collects the patterns with the examples their sources give and draws some of them as SBGN Process Description maps, cut from the maps of this website.

## Example maps

### Glycogen phosphorylase switch

Pattern: covalent modification cycle with zero-order ultrasensitivity.

<a href="/regulation-patterns/glycogen-phosphorylase-switch.graphml" download>GraphML{{ dl }}</a> &nbsp;
<a href="/regulation-patterns/glycogen-phosphorylase-switch.svg" download>SVG{{ dl }}</a>
<p align="middle"><img src="/regulation-patterns/glycogen-phosphorylase-switch.svg" width="620" alt="Glycogen phosphorylase switch"/></p>

Phosphorylase kinase phosphorylates muscle glycogen phosphorylase (PYGM) on Ser15, and protein phosphatase 1 (PP1) removes the phosphate. The phosphorylated enzyme breaks glycogen down to glucose 1-phosphate. Phosphorylase kinase itself is turned on by Ca2+ binding to its calmodulin subunit and by PKA phosphorylation. When the kinase and the phosphatase both work close to saturation, the share of phosphorylated PYGM changes steeply over a narrow range of kinase activity. In reconstituted muscle enzymes the response was sigmoidal at a phosphorylase concentration a few times above the enzymes' KM values, and phosphorylase is that abundant in skeletal muscle (Ferrell 2022, section 5.7). The map is cut from the muscle map of [glycogen metabolism](/glycogen/).

### cAMP made and destroyed

Pattern: regulated production and destruction.

<a href="/regulation-patterns/camp-production-destruction.graphml" download>GraphML{{ dl }}</a> &nbsp;
<a href="/regulation-patterns/camp-production-destruction.svg" download>SVG{{ dl }}</a>
<p align="middle"><img src="/regulation-patterns/camp-production-destruction.svg" width="473" alt="cAMP made and destroyed"/></p>

Gsα bound to GTP activates adenylate cyclase, which makes cAMP from ATP. The phosphodiesterase PDE3B hydrolyses cAMP to AMP. cAMP releases the catalytic subunit of PKA, the readout of the cAMP level. With first-order destruction, the steady cAMP level is proportional to the rate of synthesis, and the time to reach a new level after a change of input depends on the rate of destruction alone (Ferrell 2022, sections 6.1 and 6.2). The map joins cAMP synthesis and PKA activation from the muscle map of [glycogen metabolism](/glycogen/) with cAMP hydrolysis from the map of [cAMP hydrolysis](/camp/).

## Patterns

<table class="rp-table">
<thead><tr><th>Pattern</th><th>What it produces</th><th>Example</th><th>Section</th></tr></thead>
<tbody>
{% for p in site.data.regulation_patterns %}<tr><td><b>{{ p.pattern }}</b><br><span class="rp-group">{{ p.group }}</span></td><td>{{ p.produces }}</td><td>{{ p.example }}: {{ p.molecules }}</td><td>{{ p.section }}</td></tr>
{% endfor %}</tbody>
</table>

<style>
  .rp-table { font-size: 14px; border-collapse: collapse; width: 100%; }
  .rp-table th, .rp-table td { border-top: 1px solid #eee; padding: 6px 8px; vertical-align: top; text-align: left; }
  .rp-table th { border-top: none; }
  .rp-group { color: #777; font-size: 12px; }
</style>

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

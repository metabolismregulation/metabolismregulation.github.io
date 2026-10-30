---
layout: page
title: Pattern List
permalink: /pattern-list/
sitemap: false
noindex: true
---

Cell signalling and metabolic regulation use the same few patterns again and again: binding, covalent modification cycles, regulated production and destruction, cascades, feedback and feed-forward loops. Each pattern gives a characteristic response, graded or switch-like, a lasting switch, a pulse or an oscillation. This list collects the patterns with the examples their sources give. Patterns drawn as maps link to the [Pattern Atlas](/pattern-atlas/).

## Patterns

<table class="pl-table">
<thead><tr><th>Pattern</th><th>What it produces</th><th>Example</th><th>Section</th><th>Maps</th></tr></thead>
<tbody>
{% for p in site.data.pattern_list %}<tr><td><b>{{ p.pattern }}</b><br><span class="pl-group">{{ p.group }}</span></td><td>{{ p.produces }}</td><td>{{ p.example }}: {{ p.molecules }}</td><td>{{ p.section }}</td><td>{% if p.maps %}{% assign ms = p.maps | split: ";" %}{% for m in ms %}{% assign x = m | split: "|" %}<a href="/pattern-atlas/#{{ x[0] }}">{{ x[1] }}</a>{% unless forloop.last %}<br>{% endunless %}{% endfor %}{% endif %}</td></tr>
{% endfor %}</tbody>
</table>

## Response types

<table class="pl-table">
<thead><tr><th>Response</th><th>What it looks like</th><th>Patterns behind it</th><th>Examples</th><th>Section</th></tr></thead>
<tbody>
{% for r in site.data.pattern_response_types %}<tr><td><b>{{ r.response_type }}</b></td><td>{{ r.looks_like }}</td><td>{{ r.motifs }}</td><td>{{ r.examples }}</td><td>{{ r.section }}</td></tr>
{% endfor %}</tbody>
</table>

<style>
  .pl-table { font-size: 14px; border-collapse: collapse; width: 100%; }
  .pl-table th, .pl-table td { border-top: 1px solid #eee; padding: 6px 8px; vertical-align: top; text-align: left; }
  .pl-table th { border-top: none; }
  .pl-group { color: #777; font-size: 12px; }
</style>

## References

1. Ferrell JE Jr. Systems Biology of Cell Signaling: Recurring Themes and Quantitative Models. Boca Raton: CRC Press; 2022. doi: [10.1201/9781003124269](https://doi.org/10.1201/9781003124269){:target="_blank" rel="noopener"}.

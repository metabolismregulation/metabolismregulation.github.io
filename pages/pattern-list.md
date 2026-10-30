---
layout: page
title: Pattern List
permalink: /pattern-list/
sitemap: false
noindex: true
masthead: patterns
icon: favicon-patterns
---

Cell signalling and metabolic regulation use the same few patterns again and again: binding, covalent modification cycles, regulated production and destruction, cascades, feedback and feed-forward loops. Each pattern gives a characteristic response, graded or switch-like, a lasting switch, a pulse or an oscillation. This list collects the patterns with the examples their sources give, grouped by family. Patterns drawn as maps link to the [Pattern Atlas](/pattern-atlas/).

## Patterns

Patterns and examples in black are from the book. Those in <span class="pl-papers">blue</span> are from papers by the same author, and those in <span class="pl-metabolism">green</span> from sources on metabolic regulation (see Sources).

{% assign srcs = site.data.pattern_sources %}
<table class="pl-table">
<thead><tr><th>Pattern</th><th>What it produces</th><th>Example</th><th>Section</th><th>Maps</th></tr></thead>
<tbody>
{% assign fam = "" %}{% for p in site.data.pattern_list %}{% if p.family != fam %}{% assign fam = p.family %}<tr class="pl-family"><td colspan="5">{{ fam }}</td></tr>
{% endif %}{% assign src = srcs | where: "id", p.source | first %}<tr class="pl-{{ p.kind }}"><td><b>{{ p.pattern }}</b></td><td>{{ p.produces }}</td><td>{{ p.example }}: {{ p.molecules }}{% assign exs = site.data.pattern_examples | where: "pattern", p.pattern %}{% for e in exs %}{% assign es = srcs | where: "id", e.source | first %}<div class="pl-ex pl-{{ e.kind }}">{{ e.example }}: {{ e.molecules }} ({{ e.organism }}). {{ es.label }}, {{ e.section }}.</div>{% endfor %}</td><td>{% if p.kind != "book" %}{{ src.label }}, {% endif %}{{ p.section }}</td><td>{% if p.maps %}{% assign ms = p.maps | split: ";" %}{% for m in ms %}{% assign x = m | split: "|" %}<a href="/pattern-atlas/#{{ x[0] }}">{{ x[1] }}</a>{% unless forloop.last %}<br>{% endunless %}{% endfor %}{% endif %}</td></tr>
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
  .pl-table tr.pl-family td { font-weight: 600; font-size: 15px; padding-top: 18px; border-top: none; }
  .pl-ex { margin-top: 4px; }
  .pl-papers, .pl-table tr.pl-papers td { color: #0066CC; }
  .pl-metabolism, .pl-table tr.pl-metabolism td { color: #2E7D32; }
</style>

## Sources

{% assign groups = "book|The book,papers|Papers by the same author (blue),metabolism|Metabolic regulation (green)" | split: "," %}{% for g in groups %}{% assign gk = g | split: "|" %}{% assign ss = site.data.pattern_sources | where: "kind", gk[0] %}{% if ss.size > 0 %}
**{{ gk[1] }}**

{% for r in ss %}- <span class="pl-{{ r.kind }}">{{ r.citation }}</span> doi: [{{ r.doi }}](https://doi.org/{{ r.doi }}){:target="_blank" rel="noopener"}
{% endfor %}{% endif %}{% endfor %}

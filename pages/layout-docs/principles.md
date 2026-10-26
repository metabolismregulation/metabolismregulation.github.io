---
layout: layout-docs
title: "Principles"
permalink: /human-like-layout/documentation/principles/
sitemap: false
noindex: true
---
{% raw %}

What the tool holds to, and why.

## The story first

A curator starts from the point the figure is about and adds the other pieces on the side that tells the story
best. A reader follows a story along a line. Algorithms that minimise crossings over the whole map grow with the
number of possibilities and still miss what a curator sees. So the person decides the story (the anchor, the
main story, the substories, the side each joins from), and scripts apply those decisions exactly. The scripts
make no story decisions.

## No layout engine

There is no step that computes a whole layout. Each script does one job that is the same on every map, and the
map is finished by hand in yEd. This keeps the tool small and its results predictable, and keeps the judgement of
what reads well with the person.

## Layout only

A layout changes geometry: positions, sizes, arc routes, label places. It never changes what a map says. Which
molecules a complex holds, what a state variable means, whether a hub is drawn twice: these are decided before
the layout, in the development of the map's content. The check lists every change of content, so this is tested,
not assumed.

## Keep what is good

A map that already has a good layout keeps it: its readers know its arrangement. Only crowded or confusing parts
are redrawn, and room is made where the map is too compact. A layout the curator drew by hand is carried over
unchanged, and its arcs are never rerouted.

## Coarse to fine

Decisions with the largest effect come first (the story, the blocks, where the blocks go), cheap local fixes last
(the grid, names, arrow room). A late fix then never undoes an early one. Every step keeps a change only when the
check finds nothing new wrong.

## One general rule over special cases

A rule earns its place when it applies across maps. A choice for one map stays with that map. Before code is
added, what it costs (lines, parameters, run time) is weighed against what it gains across maps. A detail that
costs more than it gives the whole tool is left to the person in yEd.

## How the rules grow

Every map the curator corrects teaches something. A lesson is noted with the map, the date and what the curator
changed, then goes to one of three places: a rule, when it applies across maps, the map's own notes, when it is
a choice for that map, or nowhere, when a rule already covers it. A lesson improves a rule in place or covers a
situation no rule covers yet. It never restates, patches or contradicts a rule already there. Each rule lives in
one place, marked strict, preference or option, with its scope. A rule about geometry gets a check, and every
check runs on the layouts the curator approved: a check that flags an approved layout means the rule
contradicts the curator's taste.

The measure is the curator's work: how many nodes and arcs the curator changes in a version the tool drew. The
rules may grow as long as that falls.

{% endraw %}

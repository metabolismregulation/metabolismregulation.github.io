---
layout: layout-docs
title: "Issues"
permalink: /human-like-layout/documentation/issues/
sitemap: false
noindex: true
---
{% raw %}

Everything unresolved, by what it waits on, with the date it was found.

## A decision

| Since | Issue |
|---|---|
| 2026-10-26 | Whether the router or the path runner is built first. |
| 2026-10-26 | The large grid for placing blocks (64 and 16 px) and the spacing of `kit.py` on 16 px, which changes the output of every build that uses it. |
| 2026-10-26 | Which Atlas map serves as the test for a new layout from content alone. |

## A known fault

| Since | Issue |
|---|---|
| 2026-10-26 | `snap_grid.py` has no guard: on a map of about 80 reactions it sent 14 more arcs through their own metabolite's name. |
| 2026-10-26 | `standardise.py` is slow on large maps: over 10 minutes on a map of about 80 reactions. |
| 2026-10-26 | One rule out of date in the skill's text: lanes 14 px apart in one place, 12 px in the script and elsewhere. |

## To be sorted out

| Since | Issue |
|---|---|
| 2026-10-17 | Lessons from the curator's edits not yet sorted into the rules (20 on 2026-10-26). |
| 2026-10-19 | yEd GraphML is read in five places, and two renderers draw maps. None has drifted so far. |
| 2026-10-26 | Five layout scripts are kept with the map builds, not in the skill: room by moving blocks, arcs off a metabolite's name, like steps at one spacing, standard protein and metabolite sizes. |

{% endraw %}

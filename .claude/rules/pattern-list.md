---
paths:
  - "pages/pattern-list.md"
  - "_data/pattern_list.csv"
  - "_data/pattern_response_types.csv"
---

## Pattern List

/pattern-list/ (user, 2026-10-30; hidden: not in the navigation, no sitemap, noindex) is the list of recurring
regulation patterns with their sources' examples: one table of patterns grouped by family (as the Pattern Atlas), one of response types, the sources. A list
only: maps are not kept on it, they are in the Pattern Atlas, which the column Maps links (user, 2026-10-30).

This site holds three websites under one roof (user, 2026-10-30): the official site, the Atlas, and the pattern
pages (Pattern List, Pattern Atlas). Flat addresses, no nesting and no redirects (user). They may be untangled later.

`_data/pattern_list.csv` and `_data/pattern_response_types.csv` are copies: the lists are kept in a private
repository, whose copy script writes them here. Change them there and copy again, never here. The page text is
edited here.

## Top bar of the pattern pages

The pattern pages (Pattern List, Pattern Atlas, its backup) have their own top bar (user, 2026-10-30): no logo (the
title is enough, user), "Regulation Patterns", "Recurring patterns in cell signalling and metabolic regulation", a
menu of Pattern Atlas then Pattern List (the Atlas on the left, user), and the same name in the tab title. A page gets it by `masthead: patterns` in its front matter;
`_layouts/default.html` chooses by that setting, and every other page keeps the site's top bar. A change to the
layout is checked by building the site before and after: no page other than the pattern pages may differ (build
timestamps aside), since the layout serves the official pages too.

Colours and Sources (user, 2026-10-30): patterns and examples from the book in black, from papers by the same author in
blue (#0066CC), from sources on metabolic regulation in green (#2E7D32), by the kind each source has in
`_data/pattern_sources.csv`; examples from other sources than the row's come from `_data/pattern_examples.csv`. The
Sources section at the end lists the sources grouped by kind. Both files are copies from the private repository.

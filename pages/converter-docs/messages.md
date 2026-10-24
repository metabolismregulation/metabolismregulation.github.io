---
layout: converter-docs
title: "Messages"
permalink: /converter/docs/messages/
sitemap: false
noindex: true
---
{% raw %}

Every conversion says what it did in a list of messages, shown under the map on the Converter page
and printed on the command line. Each message has a kind (`mapconv/report.py`):

| Kind | Meaning | Example |
|---|---|---|
| problem | A rule of SBGN the map breaks, found by the check before conversion. The element is left out and drawn red in GraphML (marked). | a production arrow points away from its process |
| left out | Something the output format cannot hold, not converted. | clone marker: 8 left out |
| changed | Moved, joined or written another way. | *node* moved *way*: *why* |
| warning | Converted, worth a look. | *process*: the arc from *modifier* runs through *node* |
| summary | What a written file holds. | *map*: *n* species, *n* proteins, *n* reactions |

On the Converter page the messages are grouped by the files they come from, the files named over each
group as on their buttons. The messages of several files come first, then those of each file alone.

What a file loses always appears as `left out`. A loss that is not in the messages is a bug.

{% endraw %}

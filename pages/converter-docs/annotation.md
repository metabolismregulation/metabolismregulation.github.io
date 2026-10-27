---
layout: converter-docs
title: "Annotating a map for the Atlas click panel"
permalink: /converter/docs/annotation/
sitemap: false
noindex: true
---
{% raw %}

The Atlas shows a protein's or metabolite's annotation when it is clicked on
the map, and a protein family as cards (one per member) that open each
member's record. The map's GraphML carries only the identifiers, as yEd custom
node properties (Properties > Data in yEd), and the converter writes them into
the CellDesigner file (MIRIAM). Names, function, location, formula and
cross-references are fetched from the identifiers by the website
(`scripts/make_maps.py`, kept in its `atlas-data/`; user, 2026-10-18). The scripts are in the converter's repository (since
2026-10-16); the label tables and record caches stay with each map in the
working repository of the maps (`<map>/annotation/`). Everything below can be rerun at any
time: records are fetched once into the map's annotation folder and reused.
From a repository that holds the converter as a submodule, its folder goes on the
module path: `PYTHONPATH=<converter folder> python3 -m mapconv.<script> ...`.

## 1. The label table: `<map>/annotation/ids.csv`

One row per entry a node label stands for:

    label,source,id,family,uniprot
    COX-2,hgnc,PTGS2,,
    aspirin,chebi,CHEBI:15365,,
    ADCY,hgnc,ADCY5,Adenylate cyclases,O95622

- `source`: `hgnc` (protein, by HGNC symbol) or `chebi` (metabolite, by ChEBI id).
- Several rows with the same label make a protein family; `family` names it
  (on any of its rows).
- `uniprot` (optional) picks the UniProt entry when HGNC lists several (GNAS:
  P63092 is Gαs, HGNC lists O95467 first); otherwise HGNC's first is used.

Starting from scratch: list the labels of the map's Macromolecule and
SimpleChemical nodes, and fill in the entries. A protein label that is a gene
symbol or an HGNC alias may be left out: `annotate.py` looks it up in HGNC and
uses it when exactly one gene matches (and says so; add it to the table to
keep it). Short names are often ambiguous: COX2 is an alias of PTGS2 and of
MT-CO2, COX-2 of PTGER2, so such labels need a row. Metabolites always need a
row; check each ChEBI id by its name.

## 2. Annotate the map: `mapconv/annotate.py`

    python3 -m mapconv.annotate <map>/sources/<map>-website.graphml <map>/versions/<map>-annotated.graphml <map>/annotation/ids.csv <map>/annotation

Adds the identifiers: HGNC, HGNC symbol and UniProt for a protein, ChEBI for a
metabolite, and for a family Family, Members and Member annotation (one record
per member: HGNC, HGNC symbol, UniProt, and the member's sites, PTM, kept from
the node's earlier record). The node property PTM is not touched. The fields of
earlier runs (names, function, cross-references, Note) and the node and edge
URLs are removed. It warns when a protein label is not a symbol or alias of its
gene, and lists labels left without annotation. Labels and geometry are not
changed; check with the comparison in the map README.

## 3. Publish

Copy the annotated GraphML to the website's `downloads/<map>.graphml` and run
the website's `python3 scripts/make_maps.py`: it fetches what the panel shows
for new identifiers and writes `atlas-data/<map>.json` (node boxes and
properties for the panel). The SVG
export does not change.

{% endraw %}

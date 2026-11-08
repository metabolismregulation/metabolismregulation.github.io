# The click boxes and search index of the Pattern Atlas (its own site since 2026-11-08), from its maps in
# <folder>/pattern-atlas-downloads/ (GraphML and SVG, copied there with their entries by the patterns' copy script).
# Usage: python3 scripts/make_pattern_atlas.py <folder>
# Writes <folder>/atlas-data/pattern-<map>.json for each map (the same click panel as the Atlas, from this site's
# shared caches atlas-data/uniprot.json, hgnc.json, chebi.json, pubmed.json, which keep identifiers new to them) and
# <folder>/atlas-data/pattern-search.json. Rerun after a pattern map changes.
import glob, json, os, sys
import make_maps as mm

OUT = os.path.abspath(sys.argv[1])
DL = os.path.join(OUT, 'pattern-atlas-downloads')  # absolute, so make_maps reads it in place of a folder of this site
search = []
for g in sorted(glob.glob(os.path.join(DL, '*.graphml'))):
    base = os.path.basename(g)[:-8]
    ann = mm.annotation(base, DL) or []  # a map of generic labels only has none, and its page still loads the file
    json.dump({'nodes': ann}, open(os.path.join(OUT, 'atlas-data', 'pattern-%s.json' % base), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    search += mm.search_entries(base, ann)
    print(base, len(ann), 'annotated nodes')
json.dump(search, open(os.path.join(OUT, 'atlas-data', 'pattern-search.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
for n, f in mm.CACHE.items():  # identifiers new to the caches, kept for the Atlas too
    json.dump(mm.cache[n], open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)

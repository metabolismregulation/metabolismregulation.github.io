# The click boxes and search index of the Pattern Atlas (/pattern-atlas/), from its maps in
# pattern-atlas-downloads/ (GraphML and SVG, copied there with their entries in _pattern_maps/).
# Usage: python3 scripts/make_pattern_atlas.py
# Writes atlas-data/pattern-<map>.json for each map (the same click panel as the Atlas, from the
# shared caches atlas-data/uniprot.json, hgnc.json, chebi.json, pubmed.json) and
# atlas-data/pattern-search.json. Rerun after a pattern map changes.
import glob, json, os
import make_maps as mm

DL = 'pattern-atlas-downloads'
search = []
for g in sorted(glob.glob(os.path.join(mm.ROOT, DL, '*.graphml'))):
    base = os.path.basename(g)[:-8]
    ann = mm.annotation(base, DL)
    if ann:
        json.dump({'nodes': ann}, open(os.path.join(mm.ROOT, 'atlas-data', 'pattern-%s.json' % base), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=0)
        search += mm.search_entries(base, ann)
    print(base, len(ann or []), 'annotated nodes')
json.dump(search, open(os.path.join(mm.ROOT, 'atlas-data', 'pattern-search.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
for n, f in mm.CACHE.items():  # identifiers new to the caches, kept for the Atlas too
    json.dump(mm.cache[n], open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)

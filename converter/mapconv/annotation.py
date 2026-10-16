# MIRIAM annotation of a map's labels: label -> (family, [urn]). A family (several rows for
# one label) is written as bqbiol:hasVersion, one entity as bqbiol:is.
# - load: from the map's table (ids.csv) and the cached HGNC records (hgnc-<symbol>.json)
# - from_links: from the GraphML alone, its node links to ChEBI and UniProt (no HGNC, no families)
import csv, json, os, re

LINK = [(r'chebiId=(CHEBI:\d+)', lambda x: 'urn:miriam:obo.chebi:' + x.replace(':', '%3A')),
        (r'uniprot(?:kb)?/(\w+)', lambda x: 'urn:miriam:uniprot:' + x)]


def from_links(diagram):
    out = {}
    for d in diagram.nodes.values():
        lab = ' '.join(d.labels[0].split()) if d.labels else ''
        for pat, urn in LINK:
            hit = re.search(pat, d.url or '')
            if hit and lab and lab not in out:
                out[lab] = (False, [urn(hit.group(1))])
    return out


def load(path, cache):
    ids = {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            ids.setdefault(r['label'], []).append(r)
    def miriam(r):
        if r['source'] == 'chebi':  # CellDesigner drops other ChEBI forms when it saves
            return ['urn:miriam:obo.chebi:' + r['id'].replace(':', '%3A')]
        out = ['urn:miriam:hgnc.symbol:' + r['id']]
        p = os.path.join(cache, 'hgnc-%s.json' % r['id'])
        if os.path.exists(p):
            with open(p) as f:
                h = json.load(f)['response']['docs'][0]
            out.append('urn:miriam:hgnc:' + h['hgnc_id'].replace('HGNC:', ''))
            uni = r.get('uniprot') or (h.get('uniprot_ids') or [''])[0]
        else:
            uni = r.get('uniprot')
        if uni:
            out.append('urn:miriam:uniprot:' + uni)
        return out
    return {lab: (len(rows) > 1, [u for r in rows for u in miriam(r)]) for lab, rows in ids.items()}

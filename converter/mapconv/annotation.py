# MIRIAM annotation of a map's labels: label -> (family, [urn]). A family is written as
# bqbiol:hasVersion, one entity as bqbiol:is.
# Read from the GraphML's node properties as annotate.py writes them (HGNC symbol, HGNC,
# UniProt, ChEBI; Member annotation for a family). A map without them (not annotated):
# from the node links to ChEBI and UniProt.
import json, re

LINK = [(r'chebiId=(CHEBI:\d+)', lambda x: ['urn:miriam:obo.chebi:' + x.replace(':', '%3A')]),
        (r'uniprot(?:kb)?/(\w+)', lambda x: ['urn:miriam:uniprot:' + x])]


def miriam(p):
    # the URNs of one entity's properties
    if p.get('ChEBI'):  # CellDesigner drops other ChEBI forms when it saves
        return ['urn:miriam:obo.chebi:' + p['ChEBI'].replace(':', '%3A')]
    out = ['urn:miriam:hgnc.symbol:' + p['HGNC symbol']]
    if p.get('HGNC'): out.append('urn:miriam:hgnc:' + p['HGNC'].replace('HGNC:', ''))
    if p.get('UniProt'): out.append('urn:miriam:uniprot:' + p['UniProt'])
    return out


def from_graphml(diagram):
    out = {}
    links = not any(d.data.get(k) for d in diagram.nodes.values() for k in ('ChEBI', 'HGNC symbol', 'Member annotation'))
    for d in diagram.nodes.values():
        lab = ' '.join(d.labels[0].split()) if d.labels else ''
        if not lab or lab in out:
            continue
        p = d.data
        if p.get('Member annotation'):
            out[lab] = (True, [u for m in json.loads(p['Member annotation']) for u in miriam(dict(m['props']))])
        elif p.get('ChEBI') or p.get('HGNC symbol'):
            out[lab] = (False, miriam(p))
        elif links:
            for pat, urns in LINK:
                hit = re.search(pat, p.get('url', ''))
                if hit:
                    out[lab] = (False, urns(hit.group(1))); break
    return out

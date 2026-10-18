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
    out = ['urn:miriam:hgnc.symbol:' + p['HGNC symbol']] if p.get('HGNC symbol') else []  # CellDesigner: UniProt alone
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


def to_properties(family, uris):
    # inverse of miriam(): node properties from an entity's URNs; a family's URNs are its
    # members' one after another, each starting with an HGNC symbol or a ChEBI id
    members = []
    for u in uris:
        db, _, x = u.rpartition(':')
        if db in ('urn:miriam:hgnc.symbol', 'urn:miriam:obo.chebi') or not members:
            members.append({})
        k = {'urn:miriam:hgnc.symbol': 'HGNC symbol', 'urn:miriam:hgnc': 'HGNC', 'urn:miriam:uniprot': 'UniProt',
             'urn:miriam:obo.chebi': 'ChEBI'}.get(db)
        if k: members[-1][k] = 'HGNC:' + x if k == 'HGNC' else x.replace('%3A', ':')
    if not family:
        return members[0] if members else {}
    order = ['HGNC', 'HGNC symbol', 'UniProt', 'ChEBI']  # as annotate.py lists them
    return {'Members': '; '.join(m.get('HGNC symbol', m.get('ChEBI', '')) for m in members),
            'Member annotation': json.dumps([{'symbol': m.get('HGNC symbol', ''), 'props': [[k, m[k]] for k in order if k in m]}
                                             for m in members], ensure_ascii=False)}

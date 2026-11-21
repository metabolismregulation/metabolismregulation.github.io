import json, re, urllib.parse

LINK = [(r'chebiId=(CHEBI:\d+)', lambda x: ['urn:miriam:obo.chebi:' + x.replace(':', '%3A')]),
        (r'uniprot(?:kb)?/(\w+)', lambda x: ['urn:miriam:uniprot:' + x])]


def miriam(p):
    if p.get('ChEBI'):
        return ['urn:miriam:obo.chebi:' + p['ChEBI'].replace(':', '%3A')]
    out = ['urn:miriam:hgnc.symbol:' + p['HGNC symbol']] if p.get('HGNC symbol') else []
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
    members = []
    for u in uris:
        db, _, x = u.rpartition(':')
        if db in ('urn:miriam:hgnc.symbol', 'urn:miriam:obo.chebi') or not members:
            members.append({})
        k = {'urn:miriam:hgnc.symbol': 'HGNC symbol', 'urn:miriam:hgnc': 'HGNC', 'urn:miriam:uniprot': 'UniProt',
             'urn:miriam:obo.chebi': 'ChEBI'}.get(db)
        if k: members[-1][k] = 'HGNC:' + x if k == 'HGNC' else x.replace('%3A', ':')
    if not family:
        return {k: v for m in reversed(members) for k, v in m.items()}
    order = ['HGNC', 'HGNC symbol', 'UniProt', 'ChEBI']
    return {'Members': '; '.join(m.get('HGNC symbol', m.get('ChEBI', '')) for m in members),
            'Member annotation': json.dumps([{'symbol': m.get('HGNC symbol', ''), 'props': [[k, m[k]] for k in order if k in m]}
                                             for m in members], ensure_ascii=False)}


def units(p):
    return [' '.join(x.split()) for x in (p.get('Unit of information') or '').splitlines() if x.strip()]


def notes(p):
    lines = ['Family: ' + ' '.join(p['Family'].split())] if p.get('Family') else []
    lines += ['Unit of information: ' + '; '.join(units(p))] if units(p) else []
    for m in json.loads(p.get('Member annotation') or '[]'):
        ptm = ' '.join((dict(m['props']).get('PTM') or '').split())
        if ptm:
            lines.append('%s: %s' % (m['symbol'], ptm))
    return lines


def from_notes(text, p):
    members = json.loads(p.get('Member annotation') or '[]')
    out = dict(p)
    for line in (text or '').splitlines():
        k, _, v = line.strip().partition(': ')
        if k == 'Family' and v:
            out['Family'] = v
        if k == 'Unit of information' and v:
            out['Unit of information'] = '\n'.join(units(out) + [u.strip() for u in v.split('; ') if u.strip()])
        for m in members:
            if m['symbol'] == k and v:
                m['props'] = [x for x in m['props'] if x[0] != 'PTM'] + [['PTM', v]]
                out['Member annotation'] = json.dumps(members, ensure_ascii=False)
    return out



def references(text):
    out = []
    for x in re.split(r'[\s,;]+', text or ''):
        db, _, i = ('doi', '', x) if x.lower().startswith('10.') else x.partition(':') if ':' in x else ('', '', x)
        db = {'pmid': 'pubmed', '': 'pubmed' if i.isdigit() else ''}.get(db.lower(), db.lower())
        if db and i:
            out.append('urn:miriam:%s:%s' % (db, urllib.parse.quote(i, safe='')))
    return out


def from_references(urns):
    return ' '.join('%s:%s' % (db, urllib.parse.unquote(i)) for db, _, i in
                    (u[len('urn:miriam:'):].partition(':') for u in urns if u.startswith('urn:miriam:')))

# The Metabolism Regulation website's map scripts (this site's official maps; the Atlas is built in the workbench
# since 2026-11-11, its folders _maps/, atlas-data/ and atlas-downloads/ removed here the same day, user).
#   python3 scripts/make_maps.py: checks every official page for the complete set of files (COMPLETE) and for links
#     to another site's folder; a missing file is a warning.
#   python3 scripts/make_maps.py --official-csv F021-ureacycle "Urea cycle": the annotation CSV of a published map,
#     downloads/<base>.csv, from downloads/<base>.graphml.
# Imported as a library by the builds of other atlas sites and by scripts/make_pattern_atlas.py: annotation()
# (each annotated node's box in SVG pixels and its properties, for the click panel), search_entries() (the search
# index), the identifier caches in cache/ (CACHE, cache; uniprot, hgnc, chebi, pubmed, overrides) and stale.
import os, re, sys, csv, glob, json, time, collections, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DL = 'downloads'

GN, YN = '{http://graphml.graphdrawing.org/xmlns}', '{http://www.yworks.com/xml/graphml}'
# the annotation properties shown in the click panel, in this order (other
# custom properties, e.g. from a CellDesigner import, are left out)
ANN_FIELDS = ['PTM', 'Full name', 'Alternative names', 'Synonyms', 'Definition', 'Function', 'Location', 'Formula',
              'HGNC', 'HGNC symbol', 'Previous symbols', 'Alias symbols', 'Entrez', 'Ensembl', 'RefSeq', 'UniProt',
              'ChEBI', 'LIPID MAPS', 'KEGG', 'HMDB', 'InChI', 'InChIKey', 'Family', 'Members']
# a protein family node: its members' records, as JSON in this property
MEMBERS_FIELD = 'Member annotation'
# PTM: the node's post-translational modifications, one per line as on a state variable
# (P@S505); the map shows only the symbol (user, 2026-10-17). Other states (active, bound
# ions) are not described. The panel lists one line per site, by position: "Phosphorylated at Ser505".
MODIFIED = {'P': 'Phosphorylated', 'Ac': 'Acetylated', 'Me': 'Methylated', 'Ub': 'Ubiquitinated',
            'Su': 'Succinylated', 'Glut': 'Glutarylated', 'Pa': 'Palmitoylated', 'My': 'Myristoylated'}
RESIDUE = {'S': 'Ser', 'T': 'Thr', 'Y': 'Tyr', 'K': 'Lys', 'C': 'Cys', 'G': 'Gly', 'R': 'Arg', 'H': 'His'}


# Extended annotation (user, 2026-10-18): the map file keeps the identifiers (UniProt, HGNC,
# HGNC symbol, ChEBI) and what is curated (PTM, Family, Members); the names, function, location,
# formula and cross-references shown in the panel and searched come from UniProt, HGNC and ChEBI.
# Each identifier is fetched once, the first time a map has it, and kept in cache/uniprot.json,
# hgnc.json and chebi.json (one entry per identifier, shared by all maps); never fetched again on
# its own. "make_maps.py --refresh" fetches every entry again, keeping the old one when a fetch
# fails (the workflow's "refresh" option, run by hand). A failed first fetch is not cached, so the
# next run tries again; until then the panel shows what the GraphML itself has.
# UniProt's enzyme for a site the map draws (user, 2026-10-18): "Phosphorylated at Ser312, by IKKB,
# MAPK8 and RPS6KB1", from the entry's Modified residue features with experimental evidence
# (ECO:0000269), not the proteomics-only ones; kept as "sites" in uniprot.json. Only the drawn
# sites: the rest stays at UniProt, linked from the panel.
# Identifiers that no longer resolve (2026-10-18): when a fetch finds the entry merged, split,
# deleted, withdrawn or moved to another ID, the old entry is kept (the panel keeps its text) and
# marked "stale" with the reason, and every run warns, naming the maps, until the map is fixed.
# The same for an HGNC symbol in the map that HGNC no longer approves.
# Corrections (2026-10-18): cache/overrides.json, by hand, beats the fetched value and
# survives a refresh: {"uniprot": {"P47712": {"Location": "Cytoplasm"}}}, the same for "hgnc"
# (by HGNC ID) and "chebi" (CHEBI:...), any field the panel shows; "" hides it.
REFRESH = '--refresh' in sys.argv
SOURCE = {'uniprot': 'https://rest.uniprot.org/uniprotkb/%s.json?fields=protein_name,cc_function,cc_subcellular_location,ft_mod_res',
          'hgnc': 'https://rest.genenames.org/fetch/hgnc_id/%s',
          'hgnc-symbol': 'https://rest.genenames.org/fetch/symbol/%s',
          'chebi': 'https://www.ebi.ac.uk/chebi/backend/api/public/compound/%s/',
          'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=%s'}
CACHE = {n: os.path.join(ROOT, 'cache', n + '.json') for n in ('uniprot', 'hgnc', 'chebi', 'pubmed')}
cache = {n: json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {} for n, f in CACHE.items()}
fetched = set()  # what this run has fetched (with --refresh, each entry once)
OVERRIDES = json.load(open(os.path.join(ROOT, 'cache', 'overrides.json'), encoding='utf-8'))
stale = collections.defaultdict(set)  # (source, identifier, reason) -> the maps that have it
current = ''  # the map being read, for the warnings
PREFIX = {'P': 'phospho', 'Ac': 'acetyl', 'Me': 'methyl', 'Su': 'succinyl', 'Glut': 'glutaryl'}


def fetch(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'metabolismregulation.github.io'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def gone(src, key, d):
    """Why an identifier no longer resolves, from the source's answer ('' when it does)."""
    if src == 'uniprot':
        r = d.get('inactiveReason')
        if r:
            return r['inactiveReasonType'].lower() + (' into ' + ', '.join(r['mergeDemergeTo']) if r.get('mergeDemergeTo') else '')
        return 'now ' + d['primaryAccession'] if d['primaryAccession'] != key else ''
    if src == 'chebi':
        return 'now ' + d['chebi_accession'] if d['chebi_accession'] != key else ''
    if src == 'pubmed':
        return 'not found' if 'error' in d['result'].get(key, {'error': 1}) else ''
    docs = d['response']['docs']
    return 'not found' if not docs else docs[0]['status'].lower() if docs[0]['status'] != 'Approved' else ''


def cached(src, key, url, parse):
    if key and (key not in cache[src] or REFRESH and (src, key) not in fetched):
        fetched.add((src, key))
        why = ''
        try:
            d = fetch(url)
            why = gone(src, key, d)
            if not why:
                cache[src][key] = parse(d)
        except (OSError, ValueError, KeyError, IndexError) as e:
            if getattr(e, 'code', None) in (400, 404):  # the source has no such entry
                why = 'not found'
            else:
                print('%s %s: not fetched (%s)%s' % (src, key, e, ', the old entry kept' if key in cache[src] else ''))
        if why:
            cache[src][key] = dict(cache[src].get(key, {}), stale=why)
    got = cache[src].get(key, {})
    if got.get('stale'):
        stale[(src, key, got['stale'])].add(current)
    return dict(got, **OVERRIDES.get(src, {}).get(key, {}))


def first_sentences(text, n=2):
    # UniProt's function text without its evidence, in its first two sentences
    text = re.sub(r'\s*\((?:PubMed|By similarity|Ref\.)[^()]*\)', '', text)
    return ' '.join(re.split(r'(?<=\.)\s+(?=[A-Z0-9])', text)[:n]).strip()


def parse_uniprot(u):
    pd, com = u.get('proteinDescription', {}), u.get('comments', [])
    fn = [c['texts'][0]['value'] for c in com if c['commentType'] == 'FUNCTION' and c.get('texts')]
    return {'Full name': pd.get('recommendedName', {}).get('fullName', {}).get('value', ''),
            'Alternative names': '; '.join(a['fullName']['value'] for a in pd.get('alternativeNames', [])),
            'Function': first_sentences(fn[0]) if fn else '',
            # every location, the isoforms' too, in UniProt's order
            'Location': ', '.join(dict.fromkeys(l['location']['value'] for c in com if c['commentType'] == 'SUBCELLULAR LOCATION'
                                                for l in c.get('subcellularLocations', []) if 'location' in l)),
            # position -> [description, enzymes] for the sites UniProt gives an enzyme for
            'sites': {str(f['location']['start']['value']): [f['description'].split(';')[0], f['description'].split('; by ', 1)[1].split(';')[0]]
                      for f in u.get('features', []) if '; by ' in f.get('description', '')
                      and any(e.get('evidenceCode') == 'ECO:0000269' for e in f.get('evidences', []))}}


def parse_hgnc(h):
    d = h['response']['docs'][0]
    return {'HGNC': d['hgnc_id'], 'HGNC symbol': d['symbol'],
            'Previous symbols': ', '.join(d.get('prev_symbol', [])), 'Alias symbols': ', '.join(d.get('alias_symbol', [])),
            'Entrez': d.get('entrez_id', ''), 'Ensembl': d.get('ensembl_gene_id', ''),
            'RefSeq': ', '.join(d.get('refseq_accession', [])), 'uniprot': d.get('uniprot_ids', [])}


def parse_chebi(d):
    # names checked by ChEBI only (status C), not the brand names it takes from ChEMBL
    names, syn = sorted({x['ascii_name'] for l in (d.get('names') or {}).values() for x in l if x.get('status') == 'C'}), []
    seen = {d['name'].lower(), d['ascii_name'].lower()}
    for x in names:
        if x.lower() not in seen:
            seen.add(x.lower())
            syn.append(x)
    st, acc = d.get('default_structure') or {}, d.get('database_accessions') or {}
    xref = lambda pre: ', '.join(dict.fromkeys(a['accession_number'] for t, l in acc.items() if t != 'CAS'
                                               for a in l if (a.get('prefix') or '') == pre))
    return {'Full name': d['ascii_name'], 'Synonyms': '; '.join(syn),
            'Definition': re.sub(r'<[^>]+>', '', d.get('definition') or ''),
            'Formula': (d.get('chemical_data') or {}).get('formula') or '',
            'KEGG': xref('kegg.compound'), 'HMDB': xref('hmdb'),
            'InChI': st.get('standard_inchi') or '', 'InChIKey': st.get('standard_inchi_key') or ''}


# A process's references (user, 2026-10-27): the node property References, prefix:id separated by
# spaces (pubmed:32441256 doi:10.1016/...), as the converter reads and writes them. The panel lists each
# as a citation, first author, year, title and journal from PubMed (cache/pubmed.json, fetched
# once per PMID as the other sources), with its PUBMED link; a DOI only as its link.
def parse_pubmed(d):
    r = next(v for k, v in d['result'].items() if k != 'uids')
    names = [a['name'] for a in r.get('authors', []) if a.get('authtype') == 'Author']
    return {'authors': (names[0] + (' et al.' if len(names) > 1 else '')) if names else '',
            'year': r.get('pubdate', '')[:4], 'title': r.get('title', ''), 'journal': r.get('source', '')}


def references(text):
    out = []
    for x in (text or '').split():
        db, _, i = x.partition(':') if ':' in x else ('pubmed', '', x)
        db = 'pubmed' if db.lower() in ('pubmed', 'pmid') else db.lower()
        if db == 'pubmed' and (i not in cache['pubmed'] or REFRESH):
            time.sleep(0.4)  # PubMed answers at most three requests a second
        out.append(dict(cached('pubmed', i, SOURCE['pubmed'] % i, parse_pubmed), db=db, id=i) if db == 'pubmed' else {'db': db, 'id': i})
    return out


PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess', 'Association', 'Dissociation')


def uniprot(acc):
    return cached('uniprot', acc, SOURCE['uniprot'] % acc, parse_uniprot)


def hgnc(hgnc_id='', symbol=''):
    if not hgnc_id and symbol:
        hgnc_id = next((k for k, v in cache['hgnc'].items() if v.get('HGNC symbol') == symbol), '')
        if not hgnc_id:  # a symbol not seen yet: found by the symbol, kept under its HGNC ID
            try:
                h = parse_hgnc(fetch(SOURCE['hgnc-symbol'] % urllib.parse.quote(symbol)))
                hgnc_id = h['HGNC']
                cache['hgnc'][hgnc_id] = h
                fetched.add(('hgnc', hgnc_id))
            except (OSError, ValueError, KeyError, IndexError) as e:
                if isinstance(e, IndexError):  # no approved symbol of that name
                    stale[('hgnc', symbol, 'not an approved symbol')].add(current)
                else:
                    print('hgnc %s: not fetched (%s)' % (symbol, e))
                return {}
    return cached('hgnc', hgnc_id, SOURCE['hgnc'] % hgnc_id, parse_hgnc)


def chebi(chebi_id):
    return cached('chebi', chebi_id, SOURCE['chebi'] % chebi_id.split(':')[-1], parse_chebi)


def ptm_text(ptm, acc=''):
    # by position in the protein (Gly2, Cys15, Cys26), not in the stored order around the node
    sites = sorted((s.strip().partition('@') for s in ptm.split('\n')),
                   key=lambda x: int(re.sub(r'\D', '', x[2]) or 1e9))
    known = uniprot(acc.split(',')[0].strip()).get('sites', {}) if acc else {}
    def by(sym, site):
        u = known.get(site[1:])
        return ', by ' + u[1] if u and u[0].lower().startswith(PREFIX.get(sym, '-')) else ''
    return '\n'.join(MODIFIED.get(sym, sym) + (' at ' + RESIDUE.get(site[:1], site[:1]) + site[1:] + by(sym, site) if site else '')
                     for sym, _, site in sites)


def record(data):
    """The panel's properties of a node or a family member, in ANN_FIELDS order: its identifiers
    and curated fields from the GraphML, the rest from the cache (the GraphML's own value where
    the cache has none)."""
    rec = dict(data)
    h = hgnc(data.get('HGNC', ''), data.get('HGNC symbol', ''))
    if data.get('HGNC symbol') and h.get('HGNC symbol', data['HGNC symbol']) != data['HGNC symbol']:
        stale[('hgnc', data['HGNC symbol'], 'now ' + h['HGNC symbol'])].add(current)
    acc = (data.get('UniProt') or '').split(',')[0].strip()
    if not acc and len(h.get('uniprot', [])) > 1:
        print('%s: HGNC gives several UniProt entries (%s), none taken' % (h['HGNC symbol'], ', '.join(h['uniprot'])))
    acc = acc or (h['uniprot'][0] if len(h.get('uniprot', [])) == 1 else '')
    if acc:
        rec['UniProt'] = data.get('UniProt') or acc
    for got in (h, uniprot(acc) if acc else {}, chebi(data['ChEBI']) if data.get('ChEBI') else {}):
        rec.update({k: v for k, v in got.items() if v and k in ANN_FIELDS})
    return [[f, ptm_text(rec[f], rec.get('UniProt', '')) if f == 'PTM' else rec[f]] for f in ANN_FIELDS if rec.get(f)]


def realizer(n):
    gn = n.find(GN + 'data/' + YN + 'GenericNode')
    if gn is None:  # a group node: its open realizer
        gn = n.find(GN + 'data/' + YN + 'ProxyAutoBoundsNode/' + YN + 'Realizers/*')
    return gn


def first_label(gn):
    labels = [] if gn is None else [l.text.strip() for l in gn.findall(YN + 'NodeLabel') if l.text and l.text.strip() and not l.get('iconData')]
    return ' '.join(labels[0].split()) if labels else ''


def annotation(base, folder=DL):
    """Annotated nodes of a map: box in SVG pixels, label, class, properties.
    None when the GraphML has no custom node properties."""
    global current
    current = base
    g = os.path.join(ROOT, folder, base + '.graphml')
    svg = os.path.join(ROOT, folder, base + '.svg')
    if not (os.path.exists(g) and os.path.exists(svg)):
        return None
    root = ET.parse(g).getroot()
    keys = {k.get('id'): k.get('attr.name') for k in root.findall(GN + 'key')
            if k.get('for') == 'node' and k.get('attr.name')}
    custom = sorted((k for k, n in keys.items() if n in ANN_FIELDS), key=lambda k: ANN_FIELDS.index(keys[k]))
    if not custom and 'References' not in keys.values():
        return None
    # the yEd SVG export draws everything under matrix(1,0,0,1,tx,ty), the drawn one
    # (scripts/make_images.py) under translate(tx,ty): svg = yEd + (tx, ty)
    c = collections.Counter(re.findall(r'(?:matrix\(1,0,0,1,|translate\()(-?[\d.]+),(-?[\d.]+)\)', open(svg, encoding='utf-8').read()))
    tx, ty = (float(v) for v in c.most_common(1)[0][0])
    nodes = []
    label = {n.get('id'): first_label(realizer(n)) for n in root.iter(GN + 'node')}  # for a process's participants
    arrow = lambda e: next((a.get('target', 'none') for a in e.iter(YN + 'Arrows')), 'none')
    arcs = [(e.get('source'), e.get('target'), arrow(e)) for e in root.iter(GN + 'edge')]
    for n in root.iter(GN + 'node'):
        data = {keys.get(d.get('key')): (d.text or '').strip() for d in n.findall(GN + 'data') if d.get('key') in keys}
        gn = realizer(n)
        kind = (gn.get('configuration') or '').replace('com.yworks.sbgn.', '') if gn is not None else ''
        if kind in PROCESSES:
            # a process with references: its reaction (consumption arcs end without an arrow, modulations
            # with one, production arcs leave it) and the references
            if data.get('References'):
                nid, geo = n.get('id'), gn.find(YN + 'Geometry')
                x, y, w, h = (float(geo.get(a)) for a in ('x', 'y', 'width', 'height'))
                pad = max(0, 24 - w) / 2  # a process glyph is small: a click a little outside it still finds it
                nodes.append({'id': nid, 'label': '', 'class': kind, 'box': [round(x + tx - pad, 1), round(y + ty - pad, 1), round(w + 2 * pad, 1), round(h + 2 * pad, 1)], 'props': [],
                              'reaction': {'in': [label[s] for s, t, a in arcs if t == nid and a == 'none'],
                                           'out': [label[t] for s, t, a in arcs if s == nid],
                                           'by': [label[s] for s, t, a in arcs if t == nid and a != 'none']},
                              'references': references(data['References'])})
                # where a build gives them: the cells that carry the step and where in the cell (node
                # properties Cells and Site, user 2026-11-02), each shown as a line under the modifiers
                for f in ('Site', 'Cells'):
                    if data.get(f):
                        nodes[-1][f.lower()] = data[f]
            continue
        data = {k: v for k, v in data.items() if v and k in ANN_FIELDS + [MEMBERS_FIELD]}
        if not any(k in data for k in ANN_FIELDS):
            continue
        props = record({k: v for k, v in data.items() if k != MEMBERS_FIELD})
        # a family's members, by their HGNC symbols in Members; a member's sites (PTM) are
        # still read from its record in Member annotation
        old = {m['symbol']: dict(m['props']) for m in json.loads(data.get(MEMBERS_FIELD) or '[]')}
        symbols = [x.strip() for x in data.get('Members', '').split(';') if x.strip()] or list(old)
        members = [{'symbol': sym, 'props': record(dict({k: v for k, v in old.get(sym, {}).items() if k in ANN_FIELDS}, **{'HGNC symbol': sym}))}
                   for sym in symbols] or None
        geo = gn.find(YN + 'Geometry')
        nodes.append({'label': first_label(gn), 'class': kind,
                      'box': [round(float(geo.get('x')) + tx, 1), round(float(geo.get('y')) + ty, 1),
                              round(float(geo.get('width')), 1), round(float(geo.get('height')), 1)],
                      'props': props})
        if members:
            nodes[-1]['members'] = members
    return nodes


# The annotation table (user, 2026-10-18): the map file's content as a table, one row per
# protein, family member or metabolite, rebuilt from the GraphML for every CSV a map page
# links (a draft has none). Lean: identifiers and sites only, what the panel shows is not copied.
CSV_COLUMNS = ['Pathway', 'Entity type', 'Name', 'HGNC symbol', 'HGNC ID', 'UniProt ID', 'ChEBI ID', 'PTM']


def table_rows(base, pathway, folder=DL):
    root = ET.parse(os.path.join(ROOT, folder, base + '.graphml')).getroot()
    keys = {k.get('id'): k.get('attr.name') for k in root.findall(GN + 'key') if k.get('for') == 'node'}
    rows = []
    for n in root.iter(GN + 'node'):
        p = {keys.get(d.get('key')): (d.text or '').strip() for d in n.findall(GN + 'data')}
        gn = n.find(GN + 'data/' + YN + 'GenericNode')
        if gn is None:
            gn = n.find(GN + 'data/' + YN + 'ProxyAutoBoundsNode/' + YN + 'Realizers/*')
        labels = [l.text.strip() for l in gn.findall(YN + 'NodeLabel') if l.text and l.text.strip() and not l.get('iconData')] if gn is not None else []
        name = ' '.join(labels[0].split()) if labels else ''
        kind = 'Nucleic acid' if 'NucleicAcid' in (gn.get('configuration') or '') else 'Protein'
        records = [dict(m['props']) for m in json.loads(p.get(MEMBERS_FIELD) or '[]')] or [p]
        for r in records:
            if r.get('ChEBI') or r.get('HGNC symbol') or r.get('UniProt'):
                row = (pathway, 'Metabolite' if r.get('ChEBI') else kind, name, r.get('HGNC symbol', ''), r.get('HGNC', ''),
                             r.get('UniProt', ''), r.get('ChEBI', ''), '; '.join(x.strip() for x in r.get('PTM', '').split('\n') if x.strip()))
                if row not in rows:
                    rows.append(row)
    return rows


def search_entries(mid, nodes):
    """The search index of one map: one entry per molecule (copies of a node
    are joined), with its node indices in the map's click data (<base>.json).
    a: label and symbols, b: other names, i: database IDs (exact match only)."""
    out = collections.OrderedDict()
    for idx, n in enumerate(nodes):
        if 'reaction' in n:  # processes are not searched
            continue
        p = dict(n['props'])
        members = n.get('members') or []
        if members:
            key = 'fam:' + ','.join(sorted(m['symbol'] for m in members))
        else:
            key = (p.get('UniProt') or p.get('ChEBI') or p.get('HGNC symbol') or '').strip()
            key = key or 'lab:%s:%s' % (n['class'], n['label'].lower())
        a, b, i = [n['label']], [], []
        for rec in [p] + [dict(m['props'], _sym=m['symbol']) for m in members]:
            for f in ('_sym', 'HGNC symbol'):
                if rec.get(f):
                    a.append(rec[f])
            for f in ('Full name', 'Family'):
                if rec.get(f):
                    b.append(rec[f])
            for f in ('Alternative names', 'Synonyms', 'Previous symbols', 'Alias symbols'):
                if rec.get(f):
                    # HGNC symbols are separated by commas, the names by semicolons
                    b += [x.strip() for x in rec[f].split(';' if f in ('Alternative names', 'Synonyms') else ',') if x.strip()]
            for f in ('UniProt', 'ChEBI', 'HGNC', 'KEGG', 'HMDB', 'Entrez'):
                if rec.get(f):
                    i += [x.strip() for x in rec[f].split(',') if x.strip()]
        e = out.get(key)
        if not e:
            e = out[key] = {'k': key, 'l': n['label'], 'c': n['class'], 'm': mid, 'n': [], 'a': [], 'b': [], 'i': []}
        e['n'].append(idx)
        for f, v in (('a', a), ('b', b), ('i', i)):
            for x in v:
                if x not in e[f]:
                    e[f].append(x)
    return list(out.values())


# The complete set of files of a published map (user, 2026-10-18): each linked from its page and
# present in downloads/. Newt and MINERVA are links, not files.
COMPLETE = ['GraphML', 'PNG', 'SVG', 'CellDesigner', 'SBML', 'SBGN-ML', 'Annotation']


def check_complete(slug, body):
    links = dict((m.group(2), m.group(1)) for m in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]+)</a>',
                 re.sub(r'<svg\b.*?</svg>|\{%[^%]*%\}', '', body, flags=re.S)))
    missing = [l for l in COMPLETE if l not in links or not os.path.exists(os.path.join(ROOT, links[l].lstrip('/')))]
    if missing:
        print('%sWARNING _projects/%s.md: no %s in downloads/ or on the page (the complete set: %s)' % (
              '::warning::' if os.environ.get('GITHUB_ACTIONS') else '', slug, ', '.join(missing), ', '.join(COMPLETE)))


def write_table(path, rows):
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(CSV_COLUMNS)
        w.writerows(rows)


def main():
    """Every official page: the complete set of files, and no link to another site's folder."""
    for path in sorted(glob.glob(os.path.join(ROOT, '_projects', '*.md'))):
        slug = os.path.basename(path)[:-3]
        body = open(path, encoding='utf-8').read().split('---', 2)[2]
        if re.search(r'(?:href|src)="/atlas-downloads/', body):
            print('WARNING _projects/%s.md links /atlas-downloads/ files' % slug)
        check_complete(slug, body)


if __name__ == '__main__':  # run as a script; imported, only its functions
    if '--official-csv' in sys.argv:
        base, pathway = sys.argv[sys.argv.index('--official-csv') + 1:][:2]
        rows = table_rows(base, pathway, 'downloads')
        write_table(os.path.join(ROOT, 'downloads', base + '.csv'), rows)
        print('downloads/%s.csv: %d rows' % (base, len(rows)))
    else:
        main()

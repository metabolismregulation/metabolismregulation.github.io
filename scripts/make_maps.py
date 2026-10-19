# Build the map files for the experimental /atlas/ page.
# Usage: python3 scripts/make_maps.py
# Reads the map pages in _projects/ and draftpages/ (draft maps, listed with a
# draft mark once their PNG or SVG is in atlas-downloads/; a draft with the name
# of a published page is its new version and takes its place in the Atlas)
# and the files in atlas-downloads/ (the
# Atlas's own copy of downloads/, where maps are worked on before they replace
# the official files), and writes
# one file per map image to _maps/<id>.md:
#   - front matter: title, topic, tab, image and its size, scale, contributors, downloads
#   - body: the page text (contributors, description, references)
# A page with several map images (glycogen) gives one file per image; the
# text goes to the first, the others show it through their shared topic.
# scale = image pixels per yEd unit, so the viewer can show every map at the
# same zoom. 1 for an SVG (yEd exports it at 1:1); for a PNG only an estimate
# from the GraphML layout, which can extend beyond what is drawn.
# A map whose GraphML has annotation (yEd custom node properties such as
# UniProt, HGNC, ChEBI) also gets atlas-data/<base>.json: each annotated
# node's box in SVG pixels and its properties, for the Atlas click panel, the
# names and the rest taken from atlas-data/uniprot.json, hgnc.json, chebi.json.
# All maps' annotated nodes also go to atlas-data/search.json, the index of
# the Atlas search (names, symbols, synonyms and IDs of what is on the maps).
# Rerun after changing a map page or a map image. Needs: pillow.
# python3 scripts/make_maps.py --refresh fetches the cached annotation again.
# python3 scripts/make_maps.py --copy-official copies the official files of every map tagged draft
# into atlas-downloads/copy/ (OFFICIAL_COPY), and --check-official compares them with downloads/.
# Both are run by hand in a session, never by the workflow.
# python3 scripts/make_maps.py --official-csv F021-ureacycle "Urea cycle" writes the
# annotation CSV of a published map, downloads/<base>.csv, from downloads/<base>.graphml
# (the same table as the Atlas one), and nothing else. Every official page is checked for the
# complete set of files (COMPLETE), and a missing one is a warning.
import os, re, sys, csv, glob, json, collections, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, '_maps')
DL = 'atlas-downloads'
# Newt opens an SBGN-ML file given by its URL
NEWT = 'http://web.newteditor.org/?URL=https://metabolismregulation.github.io'

# order and short names as on the Maps and Gallery pages
ORDER = re.findall(r'^  - (\S+)$', open(os.path.join(ROOT, 'pages/maps.html'), encoding='utf-8').read(), re.M)
SHORT = dict(re.findall(r'class="gallery-title" href="/([^/]+)/">([^<]+)<',
                        open(os.path.join(ROOT, 'pages/gallery.md'), encoding='utf-8').read()))
# map pages shown as a tab of another page's topic
# tab: the variant shown in brackets after the topic in the list, as in
# Glycogen metabolism (muscle)
JOIN = {'glycolysis-cardiac': ('glycolysis', 'cardiac muscle'), 'eicosanoids-platelet': ('eicosanoids', 'platelet'),
        'eicosanoids-mast-cell': ('eicosanoids', 'mast cell')}
TABS = {'F004-glycogen-muscle': 'muscle', 'F004-glycogen-liver': 'liver', 'F001-glycolysis': 'generic', 'F002-eicosanoids': 'generic'}
# the Atlas list: groups in this order, maps in this order within a group.
# Groups without maps are planned for future maps and are not shown.
# Xenobiotic (drug) metabolism goes into Biological oxidations, as in Reactome.
GROUPS = [
    ('Carbohydrate metabolism', ['glycolysis', 'glycolysis-cardiac', 'glycolysis-extended', 'pdh', 'glycogen-muscle', 'glycogen-liver', 'acly']),
    ('Lipid metabolism', ['eicosanoids', 'eicosanoids-platelet', 'eicosanoids-mast-cell', 'alox5', 'mevalonate', 'carnitine', 'srebp', 'tag', 'estrogen', 'phosphoinositides', 'gba1', 'aspirin']),
    ('Amino acid metabolism', ['glutaminase', 'bcaa', 'ureacycle']),
    ('Nucleotide metabolism', ['pyrimidine', 'camp']),
    ('Nitric oxide metabolism', ['inos', 'enos', 'nnos']),
    ('Vitamin & cofactor metabolism', []),
    ('Energy metabolism', []),
    ('Porphyrin metabolism', []),
    ('Inositol phosphate metabolism', []),
    ('Glycan metabolism', []),
    ('Biological oxidations', []),
    ('Iron-sulfur cluster metabolism', []),
]
# drug action mechanism maps, marked with a capsule in the Atlas list
DRUG = {'aspirin'}
# tags set by hand (user, 2026-10-18), in place of the automatic draft tag of a page in draftpages/:
# new (blue): a map not on the official site; draft: the biology differs from the official map;
# draft-white: the same biology as the official map, with small changes to its file
TAGS = {'alox5': 'new', 'gba1': 'new', 'glycolysis-cardiac': 'new', 'glycolysis-extended': 'new'}
# the official copy (user, 2026-10-18): a map tagged draft is preceded in the list by its official
# version (the reference first, then the working version), under the same name with the tag copy, for comparison: the official page's text and the
# complete official file set, frozen copies of the files in downloads/. Made by --copy-official,
# never edited: Atlas work never touches them, and the Atlas never reads downloads/. A map gets
# its copy entry when its files are in OFFICIAL_COPY.
OFFICIAL_COPY = os.path.join(DL, 'copy')
GROUP_OF = {m: (g, i) for i, (g, ms) in enumerate(GROUPS) for m in ms}
POSITION = [m for g, ms in GROUPS for m in ms]
# list names that differ from the Gallery's short names
TOPIC = {'eicosanoids': 'Eicosanoids', 'phosphoinositides': 'Phosphoinositide metabolism', 'bcaa': 'BCAA catabolism', 'ureacycle': 'Urea cycle', 'pdh': 'Pyruvate dehydrogenase', 'alox5': 'Leukotriene synthesis', 'nnos': 'nNOS pathway', 'gba1': 'Glucosylceramide hydrolysis', 'glycolysis-extended': 'Glycolysis (extended)'}
# download buttons in this order: GraphML and the map images (PNG, SVG; added
# and the SBGN-ML, SBML, CellDesigner files and the Newt link are added when
# DL has them), the other files, then the annotation table, then
# the two online viewers
IMAGES = json.load(open(os.path.join(ROOT, 'atlas-data', 'images.json'))) if os.path.exists(os.path.join(ROOT, 'atlas-data', 'images.json')) else {}
LABELS = ['GraphML', 'PNG', 'SVG', 'SBGN-ML', 'SBML', 'CellDesigner', 'Annotation', 'Newt', 'MINERVA']


def scale_of(base, width):
    """PNG pixels per yEd unit, from the layout extent in the GraphML file."""
    g = os.path.join(ROOT, DL, base + '.graphml')
    if not os.path.exists(g):
        return None
    s = open(g, encoding='utf-8', errors='ignore').read()
    xs = []
    for m in re.finditer(r'<y:Geometry height="[\d.]+" width="([\d.]+)" x="(-?[\d.]+)" y="-?[\d.]+"', s):
        w, x = float(m.group(1)), float(m.group(2))
        xs += [x, x + w]
    return round(width / (max(xs) - min(xs)), 3) if xs else None


GN, YN = '{http://graphml.graphdrawing.org/xmlns}', '{http://www.yworks.com/xml/graphml}'
# the annotation properties shown in the Atlas panel, in this order (other
# custom properties, e.g. from a CellDesigner import, are left out)
ANN_FIELDS = ['PTM', 'Full name', 'Alternative names', 'Synonyms', 'Definition', 'Function', 'Location', 'Formula',
              'HGNC', 'HGNC symbol', 'Previous symbols', 'Alias symbols', 'Entrez', 'Ensembl', 'RefSeq', 'UniProt',
              'ChEBI', 'KEGG', 'HMDB', 'InChI', 'InChIKey', 'Family', 'Members']
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
# Each identifier is fetched once, the first time a map has it, and kept in atlas-data/uniprot.json,
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
# Corrections (2026-10-18): atlas-data/overrides.json, by hand, beats the fetched value and
# survives a refresh: {"uniprot": {"P47712": {"Location": "Cytoplasm"}}}, the same for "hgnc"
# (by HGNC ID) and "chebi" (CHEBI:...), any field the panel shows; "" hides it.
REFRESH = '--refresh' in sys.argv
SOURCE = {'uniprot': 'https://rest.uniprot.org/uniprotkb/%s.json?fields=protein_name,cc_function,cc_subcellular_location,ft_mod_res',
          'hgnc': 'https://rest.genenames.org/fetch/hgnc_id/%s',
          'hgnc-symbol': 'https://rest.genenames.org/fetch/symbol/%s',
          'chebi': 'https://www.ebi.ac.uk/chebi/backend/api/public/compound/%s/'}
CACHE = {n: os.path.join(ROOT, 'atlas-data', n + '.json') for n in ('uniprot', 'hgnc', 'chebi')}
cache = {n: json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {} for n, f in CACHE.items()}
fetched = set()  # what this run has fetched (with --refresh, each entry once)
OVERRIDES = json.load(open(os.path.join(ROOT, 'atlas-data', 'overrides.json'), encoding='utf-8'))
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
    if not custom:
        return None
    # the yEd SVG export draws everything under matrix(1,0,0,1,tx,ty), the drawn one
    # (scripts/make_images.py) under translate(tx,ty): svg = yEd + (tx, ty)
    c = collections.Counter(re.findall(r'(?:matrix\(1,0,0,1,|translate\()(-?[\d.]+),(-?[\d.]+)\)', open(svg, encoding='utf-8').read()))
    tx, ty = (float(v) for v in c.most_common(1)[0][0])
    nodes = []
    for n in root.iter(GN + 'node'):
        data = {keys.get(d.get('key')): (d.text or '').strip() for d in n.findall(GN + 'data') if d.get('key') in keys}
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
        gn = n.find(GN + 'data/' + YN + 'GenericNode')
        if gn is None:  # a group node: its open realizer
            gn = n.find(GN + 'data/' + YN + 'ProxyAutoBoundsNode/' + YN + 'Realizers/*')
        geo = gn.find(YN + 'Geometry')
        labels = [l.text.strip() for l in gn.findall(YN + 'NodeLabel') if l.text and l.text.strip() and not l.get('iconData')]
        nodes.append({'label': ' '.join(labels[0].split()) if labels else '',
                      'class': (gn.get('configuration') or '').replace('com.yworks.sbgn.', ''),
                      'box': [round(float(geo.get('x')) + tx, 1), round(float(geo.get('y')) + ty, 1),
                              round(float(geo.get('width')), 1), round(float(geo.get('height')), 1)],
                      'props': props})
        if members:
            nodes[-1]['members'] = members
    return nodes


# The Atlas annotation table (user, 2026-10-18): the map file's content as a table, one row per
# protein, family member or metabolite, rebuilt from the GraphML for every Atlas CSV a map page
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
    are joined), with its node indices in atlas-data/<base>.json.
    a: label and symbols, b: other names, i: database IDs (exact match only)."""
    out = collections.OrderedDict()
    for idx, n in enumerate(nodes):
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


def yaml_str(v):
    return json.dumps(v, ensure_ascii=False)


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


def page_bases(path):
    """The map files (bases) a page shows, in its order."""
    body = open(path, encoding='utf-8').read().split('---', 2)[2]
    return re.findall(r'<img [^>]*src="/(?:atlas-)?downloads/([^"]+)\.(?:png|svg)"', body)


def official_copies():
    """The maps shown with an official copy: tagged draft (by hand or by a page in draftpages/)
    and published. {slug: [bases]}"""
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, '_projects', '*.md'))):
        slug = os.path.basename(path)[:-3]
        draft = TAGS.get(slug) in ('draft', 'draft-white') or (
            slug not in TAGS and os.path.exists(os.path.join(ROOT, 'draftpages', slug + '.md')))
        if draft:
            out[slug] = page_bases(path)
    return out


COPY_FILES = ('.graphml', '.png', '.svg', '.xml', '-SBML.xml', '.sbgn', '.csv')


def copy_official():
    """Copies the official files of every map tagged draft into OFFICIAL_COPY."""
    import shutil
    os.makedirs(os.path.join(ROOT, OFFICIAL_COPY), exist_ok=True)
    for slug, bases in official_copies().items():
        for base in bases:
            for e in COPY_FILES:
                src = os.path.join(ROOT, 'downloads', base + e)
                if os.path.exists(src):
                    shutil.copyfile(src, os.path.join(ROOT, OFFICIAL_COPY, base + e))
                    print('%s/%s%s' % (OFFICIAL_COPY, base, e))


def check_official():
    """Copies that differ from downloads/ or are missing, and copies of maps no longer tagged draft."""
    want = {b for bases in official_copies().values() for b in bases}
    have = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, OFFICIAL_COPY, '*')))
    problems = 0
    for name in have:
        base = next((b for b in want if name.startswith(b) and name[len(b):] in COPY_FILES), None)
        off = os.path.join(ROOT, 'downloads', name)
        if base is None:
            print('%s/%s: the map is not tagged draft (published?): delete the copy' % (OFFICIAL_COPY, name)); problems += 1
        elif not os.path.exists(off):
            print('%s/%s: not in downloads/' % (OFFICIAL_COPY, name)); problems += 1
        elif open(off, 'rb').read() != open(os.path.join(ROOT, OFFICIAL_COPY, name), 'rb').read():
            print('%s/%s differs from downloads/' % (OFFICIAL_COPY, name)); problems += 1
    for base in sorted(want):
        for e in COPY_FILES:
            if os.path.exists(os.path.join(ROOT, 'downloads', base + e)) and base + e not in have:
                print('%s/%s missing' % (OFFICIAL_COPY, base + e)); problems += 1
    print('official copies: %d files, %d problems' % (len(have), problems))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.md')):
        os.remove(f)
    pages = sorted(glob.glob(os.path.join(ROOT, '_projects', '*.md')) + glob.glob(os.path.join(ROOT, 'draftpages', '*.md')))
    # draftpages/ comes last, so a draft replaces the published page of the same name
    folder = {os.path.basename(p)[:-3]: os.path.basename(os.path.dirname(p)) for p in pages}
    slugs = list(folder)
    rank = lambda s: ORDER.index(JOIN.get(s, (s,))[0]) + (0.5 if s in JOIN else 0) if JOIN.get(s, (s,))[0] in ORDER else 999
    written = []
    search = []
    tables = collections.defaultdict(list)  # Atlas CSV -> its rows
    jobs = []
    for slug in sorted(slugs, key=rank):
        jobs.append((slug, folder[slug], False))
        # the official copy (listed before the working version), when its files are in OFFICIAL_COPY
        page = os.path.join(ROOT, '_projects', slug + '.md')
        if os.path.exists(page) and any(os.path.exists(os.path.join(ROOT, OFFICIAL_COPY, b + '.graphml')) for b in page_bases(page)):
            jobs.append((slug, '_projects', True))
    for slug, src, copy in jobs:
        dl = OFFICIAL_COPY if copy else DL
        s = open(os.path.join(ROOT, src, slug + '.md'), encoding='utf-8').read()
        _, front, body = s.split('---', 2)
        # two separate environments (user, 2026-10-16): official pages use downloads/ only,
        # drafts atlas-downloads/ only
        wrong = '/%s/' % DL if src == '_projects' else '/downloads/'
        if not copy and re.search(r'(?:href|src)="%s' % re.escape(wrong), body):
            print('WARNING %s/%s.md links %s files' % (src, slug, wrong))
        if src == '_projects' and not copy:
            check_complete(slug, body)
        title = re.search(r'^title:\s*(.+)$', front, re.M).group(1).strip()
        permalink = re.search(r'^permalink:\s*(\S+)', front, re.M).group(1)
        # the contributors entry as written (one line, or a list with indented lines)
        contrib = re.search(r'^contributors:.*\n(?:[ \t]+\S.*\n)*', front, re.M)
        topic_slug, tab = JOIN.get(slug, (slug, None))
        topic = TOPIC.get(topic_slug, SHORT.get(topic_slug, title))
        # each map block: download links, then the image
        blocks = re.findall(r'((?:<a [^\n]*\n|Downloads:[^\n]*\n|<!--[^\n]*-->\n)+)<p align="middle"><a [^>]*><img [^>]*src="/(?:atlas-)?downloads/([^"]+)\.(?:png|svg)"', body)
        # the text: everything that is not a download line, an image line or a second-map heading
        text = []
        for line in body.split('\n'):
            if line.startswith('Downloads:') or re.match(r'<a href="[^"]*"[^>]*(download|noopener)[^>]*>', line):
                continue
            if line.startswith('<p align="middle">') or re.match(r'^# ', line):
                continue
            if re.match(r'<!--<a href="/[^"]*/"><img', line):
                continue
            text.append(line)
        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(text)).strip() + '\n'
        for k, (links, base) in enumerate(blocks):
            if copy and not all(os.path.exists(os.path.join(ROOT, dl, base + e)) for e in ('.graphml', '.svg')):
                continue
            # the SVG export when there is one (sharp at any zoom), else the PNG
            svg = os.path.join(ROOT, dl, base + '.svg')
            if os.path.exists(svg):
                head = re.search(r'<svg\b[^>]*>', open(svg, encoding='utf-8').read()).group(0)
                w = round(float(re.search(r'\swidth="([\d.]+)"', head).group(1)))
                h = round(float(re.search(r'\sheight="([\d.]+)"', head).group(1)))
                ext = '.svg'
                scale = 1  # yEd exports SVG at 1:1, one px per yEd unit
            else:
                w, h = Image.open(os.path.join(ROOT, dl, base + '.png')).size
                ext = '.png'
                scale = scale_of(base, w)
            ann = annotation(base, dl) if ext == '.svg' else None
            ann_url = ''
            if ann:
                os.makedirs(os.path.join(ROOT, 'atlas-data'), exist_ok=True)
                name = base + ('-copy' if copy else '')
                json.dump({'nodes': ann}, open(os.path.join(ROOT, 'atlas-data', name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
                ann_url = '/atlas-data/' + name + '.json'
                if not copy:  # the search finds the working version
                    search += search_entries(base.split('-', 1)[1], ann)
            downloads = []
            # the link names without their icons (an inline <svg>, or {% include icon-... %})
            for m in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', re.sub(r'<svg\b.*?</svg>|\{%[^%]*%\}', '', links, flags=re.S)):
                # no SBML on the Atlas (user, 2026-10-18): our converter writes none; an official copy keeps it
                if m.group(2) in LABELS and (copy or m.group(2) != 'SBML'):
                    url = m.group(1).replace('/downloads/', '/%s/' % dl)
                    # the Atlas offers only its own copies: a file missing in atlas-downloads/ is left out
                    # (Newt names its SBGN-ML file by full address: that file is checked too)
                    local = url[len(NEWT):] if url.startswith(NEWT) else url
                    if local.startswith('/') and not os.path.exists(os.path.join(ROOT, local.lstrip('/'))):
                        if not copy:
                            print('%s: no %s in %s/, not offered in the Atlas' % (slug, local.rsplit('/', 1)[1], DL))
                        continue
                    downloads.append({'label': m.group(2), 'url': url})
            map_title = title if k == 0 or len(blocks) == 1 else title.replace('muscle', 'liver')
            map_tab = tab or (TABS.get(base) if len(blocks) > 1 or base in TABS else None) or ''
            for d in downloads:
                # an official copy is frozen: its table is not rebuilt
                if not copy and d['label'] == 'Annotation' and d['url'].endswith('.csv') and os.path.exists(os.path.join(ROOT, DL, base + '.graphml')):
                    t = tables[d['url'].lstrip('/')]
                    t += [r for r in table_rows(base, topic + (', ' + map_tab if map_tab else '')) if r not in t]
            mid = base.split('-', 1)[1]
            order = POSITION.index(mid) + 1 if mid in POSITION else 900 + len(written)
            fm = ['---',
                  'title: ' + yaml_str(map_title),
                  'topic: ' + yaml_str(topic),
                  'tab: ' + yaml_str(map_tab),
                  'page: ' + yaml_str(permalink),
                  'group: ' + yaml_str(GROUP_OF.get(mid, ('Other', 0))[0]),
                  'order: %s' % (order - 0.5 if copy else order),  # the copy first, then the working version
                  'kind: ' + yaml_str('drug' if mid in DRUG else 'map'),
                  'draft: %s' % ('true' if folder[slug] == 'draftpages' and not copy else 'false'),
                  'tag: ' + yaml_str('copy' if copy else TAGS.get(mid, 'draft' if folder[slug] == 'draftpages' else '')),
                  'image: ' + yaml_str('/%s/' % dl + base + ext),
                  'width: %d' % w, 'height: %d' % h,
                  'scale: %s' % (scale or 'null'),
                  'annotation: ' + yaml_str(ann_url),
                  # images the GraphML could not be drawn into (scripts/make_images.py): the
                  # Atlas blocks their download and marks the map red
                  'image_error: ' + yaml_str('' if copy else IMAGES.get(base, {}).get('error', ''))]
            # the page's contributor keys, for {% include contributors.html %} in the text
            if contrib:
                fm.append(contrib.group(0).rstrip('\n'))
            fm.append('downloads:')
            for label, e in (('PNG', '.png'), ('SVG', '.svg'), ('SBGN-ML', '.sbgn'), ('SBML', '-SBML.xml'), ('CellDesigner', '.xml'), ('Newt', '.sbgn')):
                if not copy and os.path.exists(os.path.join(ROOT, DL, base + e)) and not any(d['label'] == label for d in downloads):
                    url = '/%s/' % DL + base + e
                    downloads.append({'label': label, 'url': NEWT + url if label == 'Newt' else url})
            downloads.sort(key=lambda d: LABELS.index(d['label']))
            fm += ['  - {label: %s, url: %s}' % (yaml_str(d['label']), yaml_str(d['url'])) for d in downloads]
            fm += ['---', '']
            out = '\n'.join(fm) + (text if k == 0 else '')
            mid += '-copy' if copy else ''
            open(os.path.join(OUT, mid + '.md'), 'w', encoding='utf-8').write(out)
            written.append(mid)
    json.dump(search, open(os.path.join(ROOT, 'atlas-data', 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for path, rows in tables.items():
        write_table(os.path.join(ROOT, path), rows)
    for n, f in CACHE.items():
        json.dump(cache[n], open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    # in the Atlas data workflow, a warning on the run's page
    for (src, key, why), maps in sorted(stale.items()):
        print('%sWARNING %s %s no longer resolves (%s): %s' % ('::warning::' if os.environ.get('GITHUB_ACTIONS') else '',
              {'uniprot': 'UniProt', 'hgnc': 'HGNC', 'chebi': 'ChEBI'}[src], key, why, ', '.join(sorted(maps))))
    print(len(written), 'maps:', ', '.join(written))


if '--copy-official' in sys.argv:
    copy_official()
elif '--check-official' in sys.argv:
    check_official()
elif '--official-csv' in sys.argv:
    base, pathway = sys.argv[sys.argv.index('--official-csv') + 1:][:2]
    rows = table_rows(base, pathway, 'downloads')
    write_table(os.path.join(ROOT, 'downloads', base + '.csv'), rows)
    print('downloads/%s.csv: %d rows' % (base, len(rows)))
else:
    main()

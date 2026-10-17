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
# Full name, UniProt, ChEBI) also gets atlas-data/<base>.json: each annotated
# node's box in SVG pixels and its properties, for the Atlas click panel.
# All maps' annotated nodes also go to atlas-data/search.json, the index of
# the Atlas search (names, symbols, synonyms and IDs of what is on the maps).
# Rerun after changing a map page or a map image. Needs: pillow.
import os, re, glob, json, collections, datetime
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
JOIN = {'glycolysis-cardiac': ('glycolysis', 'cardiac muscle')}
TABS = {'F004-glycogen-muscle': 'muscle', 'F004-glycogen-liver': 'liver', 'F001-glycolysis': 'generic'}
# the Atlas list: groups in this order, maps in this order within a group.
# Groups without maps are planned for future maps and are not shown.
# Xenobiotic (drug) metabolism goes into Biological oxidations, as in Reactome.
GROUPS = [
    ('Carbohydrate metabolism', ['glycolysis', 'glycolysis-cardiac', 'pdh', 'glycogen-muscle', 'glycogen-liver', 'acly']),
    ('Lipid metabolism', ['eicosanoids', 'aspirin', 'alox5', 'mevalonate', 'carnitine', 'srebp', 'tag', 'estrogen', 'phosphoinositides']),
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
# a map published for the first time is marked with an outlined "new" tag in the Atlas
# list for NEW_DAYS after the date in its page's "released:" line, written once at the
# first publication and never changed: a new version or a small fix does not make a map
# new (user, 2026-10-17). The daily run of atlas-data.yml takes the tag off on time.
NEW_DAYS = 30
GROUP_OF = {m: (g, i) for i, (g, ms) in enumerate(GROUPS) for m in ms}
POSITION = [m for g, ms in GROUPS for m in ms]
# list names that differ from the Gallery's short names
TOPIC = {'phosphoinositides': 'Phosphoinositide metabolism', 'bcaa': 'BCAA catabolism', 'ureacycle': 'Urea cycle', 'pdh': 'Pyruvate dehydrogenase', 'alox5': 'Leukotriene synthesis', 'nnos': 'nNOS pathway'}
# download buttons in this order: GraphML and the map images (PNG, SVG; added
# and the SBGN-ML, SBML, CellDesigner files and the Newt link are added when
# DL has them), the other files, then the annotation table, then
# the two online viewers
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
ANN_FIELDS = ['Full name', 'Alternative names', 'Synonyms', 'Definition', 'Function', 'Location', 'Formula',
              'HGNC', 'HGNC symbol', 'HGNC aliases', 'Entrez', 'Ensembl', 'RefSeq', 'UniProt',
              'ChEBI', 'KEGG', 'HMDB', 'InChI', 'InChIKey', 'Note', 'Family', 'Members']
# a protein family node: its members' records, as JSON in this property
MEMBERS_FIELD = 'Member annotation'


def annotation(base):
    """Annotated nodes of a map: box in SVG pixels, label, class, properties.
    None when the GraphML has no custom node properties."""
    g = os.path.join(ROOT, DL, base + '.graphml')
    svg = os.path.join(ROOT, DL, base + '.svg')
    if not (os.path.exists(g) and os.path.exists(svg)):
        return None
    root = ET.parse(g).getroot()
    keys = {k.get('id'): k.get('attr.name') for k in root.findall(GN + 'key')
            if k.get('for') == 'node' and k.get('attr.name')}
    custom = sorted((k for k, n in keys.items() if n in ANN_FIELDS), key=lambda k: ANN_FIELDS.index(keys[k]))
    mkey = [k for k, n in keys.items() if n == MEMBERS_FIELD]
    if not custom:
        return None
    # the yEd SVG export draws everything under matrix(1,0,0,1,tx,ty): svg = yEd + (tx, ty)
    c = collections.Counter(re.findall(r'matrix\(1,0,0,1,(-?[\d.]+),(-?[\d.]+)\)', open(svg, encoding='utf-8').read()))
    tx, ty = (float(v) for v in c.most_common(1)[0][0])
    nodes = []
    for n in root.iter(GN + 'node'):
        data = {keys.get(d.get('key')): (d.text or '').strip() for d in n.findall(GN + 'data') if d.get('key') in keys}
        props = [[keys[k], data[keys[k]]] for k in custom if data.get(keys[k])]
        if not props:
            continue
        members = json.loads(data[MEMBERS_FIELD]) if mkey and data.get(MEMBERS_FIELD) else None
        for m in members or []:
            m['props'] = [kv for kv in m['props'] if kv[0] in ANN_FIELDS]
        gn = n.find(GN + 'data/' + YN + 'GenericNode')
        if gn is None:  # a group node: its open realizer
            gn = n.find(GN + 'data/' + YN + 'ProxyAutoBoundsNode/' + YN + 'Realizers/*')
        geo = gn.find(YN + 'Geometry')
        labels = [l.text.strip() for l in gn.findall(YN + 'NodeLabel') if l.text and l.text.strip() and not l.get('iconData')]
        nodes.append({'label': ' '.join(labels[0].split()) if labels else '',
                      'class': (gn.get('configuration') or '').replace('com.yworks.sbgn.', ''),
                      'box': [round(float(geo.get('x')) + tx, 1), round(float(geo.get('y')) + ty, 1),
                              round(float(geo.get('width')), 1), round(float(geo.get('height')), 1)],
                      'url': data.get('url', ''), 'props': props})
        if members:
            nodes[-1]['members'] = members
    return nodes


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
            for f in ('Alternative names', 'Synonyms', 'HGNC aliases'):
                if rec.get(f):
                    # HGNC aliases are separated by commas, the names by semicolons
                    b += [x.strip() for x in rec[f].split(',' if f == 'HGNC aliases' else ';') if x.strip()]
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
    for slug in sorted(slugs, key=rank):
        s = open(os.path.join(ROOT, folder[slug], slug + '.md'), encoding='utf-8').read()
        _, front, body = s.split('---', 2)
        # two separate environments (user, 2026-10-16): official pages use downloads/ only,
        # drafts atlas-downloads/ only
        wrong = '/%s/' % DL if folder[slug] == '_projects' else '/downloads/'
        if re.search(r'(?:href|src)="%s' % re.escape(wrong), body):
            print('WARNING %s/%s.md links %s files' % (folder[slug], slug, wrong))
        title = re.search(r'^title:\s*(.+)$', front, re.M).group(1).strip()
        released = re.search(r'^released:\s*(\d{4}-\d\d-\d\d)', front, re.M)
        new = (folder[slug] == '_projects' and released is not None and
               (datetime.date.today() - datetime.date.fromisoformat(released.group(1))).days < NEW_DAYS)
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
            # the SVG export when there is one (sharp at any zoom), else the PNG
            svg = os.path.join(ROOT, DL, base + '.svg')
            if os.path.exists(svg):
                head = re.search(r'<svg\b[^>]*>', open(svg, encoding='utf-8').read()).group(0)
                w = round(float(re.search(r'\swidth="([\d.]+)"', head).group(1)))
                h = round(float(re.search(r'\sheight="([\d.]+)"', head).group(1)))
                ext = '.svg'
                scale = 1  # yEd exports SVG at 1:1, one px per yEd unit
            else:
                w, h = Image.open(os.path.join(ROOT, DL, base + '.png')).size
                ext = '.png'
                scale = scale_of(base, w)
            ann = annotation(base) if ext == '.svg' else None
            ann_url = ''
            if ann:
                os.makedirs(os.path.join(ROOT, 'atlas-data'), exist_ok=True)
                json.dump({'nodes': ann}, open(os.path.join(ROOT, 'atlas-data', base + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
                ann_url = '/atlas-data/' + base + '.json'
                search += search_entries(base.split('-', 1)[1], ann)
            downloads = []
            for m in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', links):
                if m.group(2) in LABELS:
                    url = m.group(1).replace('/downloads/', '/%s/' % DL)
                    # the Atlas offers only its own copies: a file missing in atlas-downloads/ is left out
                    # (Newt names its SBGN-ML file by full address: that file is checked too)
                    local = url[len(NEWT):] if url.startswith(NEWT) else url
                    if local.startswith('/') and not os.path.exists(os.path.join(ROOT, local.lstrip('/'))):
                        print('%s: no %s in %s/, not offered in the Atlas' % (slug, local.rsplit('/', 1)[1], DL))
                        continue
                    downloads.append({'label': m.group(2), 'url': url})
            mid = base.split('-', 1)[1]
            fm = ['---',
                  'title: ' + yaml_str(title if k == 0 or len(blocks) == 1 else title.replace('muscle', 'liver')),
                  'topic: ' + yaml_str(topic),
                  'tab: ' + yaml_str(tab or (TABS.get(base) if len(blocks) > 1 or base in TABS else None) or ''),
                  'page: ' + yaml_str(permalink),
                  'group: ' + yaml_str(GROUP_OF.get(mid, ('Other', 0))[0]),
                  'order: %d' % (POSITION.index(mid) + 1 if mid in POSITION else 900 + len(written)),
                  'kind: ' + yaml_str('drug' if mid in DRUG else 'map'),
                  'draft: %s' % ('true' if folder[slug] == 'draftpages' else 'false'),
                  'new: %s' % ('true' if new else 'false'),
                  'image: ' + yaml_str('/%s/' % DL + base + ext),
                  'width: %d' % w, 'height: %d' % h,
                  'scale: %s' % (scale or 'null'),
                  'annotation: ' + yaml_str(ann_url)]
            # the page's contributor keys, for {% include contributors.html %} in the text
            if contrib:
                fm.append(contrib.group(0).rstrip('\n'))
            fm.append('downloads:')
            for label, e in (('PNG', '.png'), ('SVG', '.svg'), ('SBGN-ML', '.sbgn'), ('SBML', '-SBML.xml'), ('CellDesigner', '.xml'), ('Newt', '.sbgn')):
                if os.path.exists(os.path.join(ROOT, DL, base + e)) and not any(d['label'] == label for d in downloads):
                    url = '/%s/' % DL + base + e
                    downloads.append({'label': label, 'url': NEWT + url if label == 'Newt' else url})
            downloads.sort(key=lambda d: LABELS.index(d['label']))
            fm += ['  - {label: %s, url: %s}' % (yaml_str(d['label']), yaml_str(d['url'])) for d in downloads]
            fm += ['---', '']
            out = '\n'.join(fm) + (text if k == 0 else '')
            open(os.path.join(OUT, mid + '.md'), 'w', encoding='utf-8').write(out)
            written.append(mid)
    json.dump(search, open(os.path.join(ROOT, 'atlas-data', 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(len(written), 'maps:', ', '.join(written))


main()

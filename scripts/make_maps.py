# Build the map files for the experimental /atlas/ page.
# Usage: python3 scripts/make_maps.py
# Reads the map pages in _projects/ and the files in downloads/, and writes
# one file per map image to _maps/<id>.md:
#   - front matter: title, topic, tab, image and its size, scale, downloads
#   - body: the page text (contributors, description, references)
# A page with several map images (glycogen) gives one file per image; the
# text goes to the first, the others show it through their shared topic.
# scale = image pixels per yEd unit, so the viewer can show every map at the
# same zoom. 1 for an SVG (yEd exports it at 1:1); for a PNG only an estimate
# from the GraphML layout, which can extend beyond what is drawn.
# Rerun after changing a map page or a map image. Needs: pillow.
import os, re, glob, json
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, '_maps')

# order and short names as on the Maps and Gallery pages
ORDER = re.findall(r'^  - (\S+)$', open(os.path.join(ROOT, 'pages/maps.html'), encoding='utf-8').read(), re.M)
SHORT = dict(re.findall(r'class="gallery-title" href="/([^/]+)/">([^<]+)<',
                        open(os.path.join(ROOT, 'pages/gallery.md'), encoding='utf-8').read()))
# map pages shown as a tab of another page's topic
# tab: the variant shown in brackets after the topic in the list, as in
# Glycogen metabolism (muscle)
JOIN = {'glycolysis-cardiac': ('glycolysis', 'cardiac muscle')}
TABS = {'F004-glycogen-muscle': 'muscle', 'F004-glycogen-liver': 'liver'}
# the Atlas list: groups in this order, maps in this order within a group
GROUPS = [
    ('Carbohydrate metabolism', ['glycolysis', 'glycolysis-cardiac', 'glycogen-muscle', 'glycogen-liver', 'acly']),
    ('Lipid metabolism', ['eicosanoids', 'mevalonate', 'carnitine', 'srebp', 'tag', 'estrogen', 'phosphoinositides', 'aspirin']),
    ('Amino acid metabolism', ['glutaminase']),
    ('Nitric oxide metabolism', ['inos', 'enos']),
    ('Nucleotide metabolism', ['pyrimidine', 'camp']),
    # planned groups, for future maps; a group without maps is not shown
    ('Vitamins & cofactors', []),
    ('Energy metabolism', []),
    ('Porphyrin metabolism', []),
    ('Biological oxidations', []),
]
GROUP_OF = {m: (g, i) for i, (g, ms) in enumerate(GROUPS) for m in ms}
POSITION = [m for g, ms in GROUPS for m in ms]
# list names that differ from the Gallery's short names
TOPIC = {'phosphoinositides': 'Phosphoinositide metabolism'}
LABELS = ['GraphML', 'SBGN-ML', 'SBML', 'CellDesigner', 'MINERVA', 'Newt', 'Annotation']


def scale_of(base, width):
    """PNG pixels per yEd unit, from the layout extent in the GraphML file."""
    g = os.path.join(ROOT, 'downloads', base + '.graphml')
    if not os.path.exists(g):
        return None
    s = open(g, encoding='utf-8', errors='ignore').read()
    xs = []
    for m in re.finditer(r'<y:Geometry height="[\d.]+" width="([\d.]+)" x="(-?[\d.]+)" y="-?[\d.]+"', s):
        w, x = float(m.group(1)), float(m.group(2))
        xs += [x, x + w]
    return round(width / (max(xs) - min(xs)), 3) if xs else None


def yaml_str(v):
    return json.dumps(v, ensure_ascii=False)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, '*.md')):
        os.remove(f)
    pages = sorted(glob.glob(os.path.join(ROOT, '_projects', '*.md')))
    slugs = [os.path.basename(p)[:-3] for p in pages]
    rank = lambda s: ORDER.index(JOIN.get(s, (s,))[0]) + (0.5 if s in JOIN else 0) if JOIN.get(s, (s,))[0] in ORDER else 999
    written = []
    for slug in sorted(slugs, key=rank):
        s = open(os.path.join(ROOT, '_projects', slug + '.md'), encoding='utf-8').read()
        _, front, body = s.split('---', 2)
        title = re.search(r'^title:\s*(.+)$', front, re.M).group(1).strip()
        topic_slug, tab = JOIN.get(slug, (slug, None))
        topic = TOPIC.get(topic_slug, SHORT.get(topic_slug, title))
        # each map block: download links, then the image
        blocks = re.findall(r'((?:<a [^\n]*\n|Downloads:[^\n]*\n|<!--[^\n]*-->\n)+)<p align="middle"><a [^>]*><img [^>]*src="/downloads/([^"]+)\.png"', body)
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
            svg = os.path.join(ROOT, 'downloads', base + '.svg')
            if os.path.exists(svg):
                head = re.search(r'<svg\b[^>]*>', open(svg, encoding='utf-8').read()).group(0)
                w = round(float(re.search(r'\swidth="([\d.]+)"', head).group(1)))
                h = round(float(re.search(r'\sheight="([\d.]+)"', head).group(1)))
                ext = '.svg'
                scale = 1  # yEd exports SVG at 1:1, one px per yEd unit
            else:
                w, h = Image.open(os.path.join(ROOT, 'downloads', base + '.png')).size
                ext = '.png'
                scale = scale_of(base, w)
            downloads = []
            for m in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', links):
                if m.group(2) in LABELS:
                    downloads.append({'label': m.group(2), 'url': m.group(1)})
            mid = base.split('-', 1)[1]
            fm = ['---',
                  'title: ' + yaml_str(title if k == 0 or len(blocks) == 1 else title.replace('muscle', 'liver')),
                  'topic: ' + yaml_str(topic),
                  'tab: ' + yaml_str(tab or (TABS.get(base) if len(blocks) > 1 or base in TABS else None) or ''),
                  'page: ' + yaml_str('/' + slug + '/'),
                  'group: ' + yaml_str(GROUP_OF.get(mid, ('Other', 0))[0]),
                  'order: %d' % (POSITION.index(mid) + 1 if mid in POSITION else 900 + len(written)),
                  'image: ' + yaml_str('/downloads/' + base + ext),
                  'width: %d' % w, 'height: %d' % h,
                  'scale: %s' % (scale or 'null'),
                  'downloads:']
            fm += ['  - {label: %s, url: %s}' % (yaml_str(d['label']), yaml_str(d['url'])) for d in downloads]
            fm += ['---', '']
            out = '\n'.join(fm) + (text if k == 0 else '')
            open(os.path.join(OUT, mid + '.md'), 'w', encoding='utf-8').write(out)
            written.append(mid)
    print(len(written), 'maps:', ', '.join(written))


main()

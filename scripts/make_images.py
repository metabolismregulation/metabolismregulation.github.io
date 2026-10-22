# Make the Atlas map images from the GraphML (user, 2026-10-17).
# Usage: python3 scripts/make_images.py   (before scripts/make_maps.py; the Atlas data
# workflow runs both). Needs: lxml, cairosvg, numpy, pillow.
# For every map in atlas-downloads/ (a GraphML with an SVG or PNG there, or named by a page),
# atlas-data/images.json keeps the GraphML and SVG as last seen. When a GraphML changes on its
# own, yrender/ (a copy of the workbench's tools/yrender.py, commit in VERSION) draws
# its SVG, and for a published map its PNG; a draft carries no PNG, so a draft's old PNG is
# removed. When the SVG changes too, or alone, it is a yEd export: it is kept, and how the
# drawn version compares with it is written to the record ("check") and printed.
# A map the tool cannot draw gets "error" (what it cannot draw): the Atlas then blocks its
# image downloads and marks it red. A yEd SVG upload or a new tool version clears it.
# Maps already there when this started count as seen: they are drawn at their next change.
import os, re, glob, json, hashlib, sys, tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DL = os.path.join(ROOT, 'atlas-downloads')
RECORD = os.path.join(ROOT, 'atlas-data', 'images.json')
sys.path.insert(0, os.path.join(ROOT, 'yrender'))
import yrender
from yrender_check import compare

VERSION = open(os.path.join(ROOT, 'yrender', 'VERSION')).read().split()[1]


def sha(path):
    return hashlib.sha1(open(path, 'rb').read()).hexdigest() if os.path.exists(path) else None


def pages(folder):
    return ''.join(open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(ROOT, folder, '*.md')))


def main():
    record = json.load(open(RECORD)) if os.path.exists(RECORD) else {}
    drafts, published = pages('draftpages'), pages('_projects')
    named = set(re.findall(r'/(?:atlas-)?downloads/([^"/]+)\.(?:svg|png|graphml)"', drafts + published))
    for gml in sorted(glob.glob(os.path.join(DL, '*.graphml'))):
        base = os.path.basename(gml)[:-8]
        svg, png = os.path.join(DL, base + '.svg'), os.path.join(DL, base + '.png')
        if base not in named and not os.path.exists(svg) and not os.path.exists(png):
            continue
        g, s, rec = sha(gml), sha(svg), record.get(base)
        if rec is None and s:
            record[base] = {'graphml': g, 'svg': s, 'source': 'yEd'}
            continue
        if rec and rec['svg'] != s and s:  # a yEd export uploaded
            record[base] = {'graphml': g, 'svg': s, 'source': 'yEd', 'check': check(gml, svg)}
            print(base, 'yEd SVG kept;', record[base]['check'])
            continue
        if rec and rec['graphml'] == g and not (rec.get('error') and rec.get('tool') != VERSION):
            continue
        draft = '/atlas-downloads/%s.' % base in drafts
        try:
            yrender.render(gml, svg, None if draft else png)
        except SystemExit as e:
            reason = str(e).split('\n', 1)[1].strip().replace('\n  ', '; ')
            record[base] = {'graphml': g, 'svg': s, 'source': (rec or {}).get('source', ''), 'tool': VERSION, 'error': reason}
            print(base, 'not drawn:', reason)
            continue
        if draft and os.path.exists(png):
            os.remove(png)
        record[base] = {'graphml': g, 'svg': sha(svg), 'source': 'drawn', 'tool': VERSION}
        print(base, 'drawn')
    json.dump(record, open(RECORD, 'w'), indent=1, sort_keys=True)


def check(gml, svg):
    # how the tool's drawing of this GraphML compares with yEd's SVG
    out = os.path.join(tempfile.mkdtemp(), 'drawn.svg')
    try:
        yrender.render(gml, out)
    except SystemExit as e:
        return 'tool cannot draw it: ' + str(e).split('\n', 1)[1].strip().replace('\n  ', '; ')
    ref, mine = open(svg, encoding='utf-8').read(), open(out, encoding='utf-8').read()
    return 'shapes differ %.2f%%, with text %.2f%%, tool %s' % (
        100 * compare(ref, mine, False)[2], 100 * compare(ref, mine, True)[2], VERSION)


main()

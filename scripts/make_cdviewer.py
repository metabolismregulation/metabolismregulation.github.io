# The images of the CD viewer (/cdviewer/, pages/cdviewer.html): every official map's
# CellDesigner file (downloads/, as linked from the pages in the Maps list) drawn by MINERVA's
# conversion service as SVG, the drawing of the MINERVA view, into cdviewer/<base>.svg, and the
# list cdviewer/maps.json (name, group, page, file, sha1, error). A file whose sha1 is unchanged
# is not sent again (--all sends every file). A file MINERVA cannot draw keeps no image: its
# entry carries MINERVA's reason, shown in the map window. Run by the Atlas data workflow.
#   python3 scripts/make_cdviewer.py [--all]
import hashlib, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'cdviewer')
URL = 'https://minerva-service.lcsb.uni.lu/minerva/api/convert/image/CellDesigner_SBML:svg'


def front(path):
    s = open(path, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---', s, re.S)
    return (m.group(1) if m else ''), s


def official():
    """(base, page slug) of each CellDesigner file the Maps list's pages link, in list order."""
    head, _ = front(os.path.join(ROOT, 'pages', 'maps.html'))
    slugs = re.findall(r'^\s+-\s+(\S+)', head.split('projects:', 1)[1], re.M)
    out = []
    for slug in slugs:
        _, s = front(os.path.join(ROOT, '_projects', slug + '.md'))
        for base in re.findall(r'href="/downloads/([^"/]+)\.xml"', s):
            if not base.endswith('-SBML') and (base, slug) not in out:
                out.append((base, slug))
    return out


def atlas_names():
    """base -> (name, group, order) from the Atlas list entries (_maps/, made by make_maps.py);
    a map with a tab (glycogen muscle and liver) is named with it."""
    names = {}
    for f in sorted(os.listdir(os.path.join(ROOT, '_maps'))):
        if f.endswith('-copy.md'):
            continue
        head, _ = front(os.path.join(ROOT, '_maps', f))
        img = re.search(r'^image: "/atlas-downloads/([^"/]+)\.(svg|png)"', head, re.M)
        if not img:
            continue
        get = lambda k: (re.search(r'^%s: "?(.*?)"?$' % k, head, re.M) or [None, ''])[1]
        tab = get('tab')
        name = get('topic') + (' (%s)' % tab if tab and tab != 'generic' else '')
        names[img.group(1)] = (name, get('group'), int(get('order') or 99))
    return names


def draw(xml):
    req = urllib.request.Request(URL, data=xml, headers={'Content-Type': 'text/plain'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        body = e.read()
    except Exception as e:
        return None, 'MINERVA could not be reached: %s' % e
    if not body.lstrip().startswith(b'<?xml') and b'<svg' not in body[:2000]:
        try:
            j = json.loads(body)
            return None, 'MINERVA: %s' % (j.get('reason') or j.get('error'))
        except ValueError:
            return None, 'MINERVA: %s' % body[:200].decode('utf-8', 'replace')
    svg = body.decode('utf-8')
    # MINERVA draws with Java's Dialog font, which browsers lack: Arial's metrics, as on the Atlas
    svg = svg.replace("font-family=\"'Dialog'\"", "font-family=\"'Dialog', 'Liberation Sans', Arial, sans-serif\"")
    return svg, ''


def main():
    os.makedirs(OUT, exist_ok=True)
    listing = os.path.join(OUT, 'maps.json')
    old = {m['base']: m for m in json.load(open(listing))} if os.path.exists(listing) else {}
    names = atlas_names()
    maps = []
    for base, slug in official():
        xml = open(os.path.join(ROOT, 'downloads', base + '.xml'), 'rb').read()
        sha = hashlib.sha1(xml).hexdigest()
        name, group, rank = names.get(base, ('', '', 99))
        if not name:
            name = re.sub(r'^Regulation of (the )?', '', front(os.path.join(ROOT, '_projects', slug + '.md'))[0].split('title:', 1)[1].split('\n')[0].strip().strip('"'))
            name = name[:1].upper() + name[1:]
        entry = {'base': base, 'name': name, 'group': group, 'page': '/%s/' % slug,
                 'file': '/downloads/%s.xml' % base, 'sha1': sha, 'error': '', 'order': rank}
        svg_path = os.path.join(OUT, base + '.svg')
        prev = old.get(base)
        if prev and prev['sha1'] == sha and '--all' not in sys.argv and (prev['error'] or os.path.exists(svg_path)):
            entry['error'] = prev['error']
        else:
            svg, err = draw(xml)
            entry['error'] = err
            if svg:
                open(svg_path, 'w', encoding='utf-8').write(svg)
            elif os.path.exists(svg_path):
                os.remove(svg_path)
            print('%s: %s' % (base, err or 'drawn'))
        if not entry['error']:
            head = re.search(r'<svg\b[^>]*>', open(svg_path, encoding='utf-8').read()).group(0)
            vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', head)
            entry['width'], entry['height'] = float(vb.group(1)), float(vb.group(2))
        maps.append(entry)
    maps.sort(key=lambda m: m.pop('order'))  # the Atlas's order
    for f in os.listdir(OUT):
        if f.endswith('.svg') and f[:-4] not in {m['base'] for m in maps}:
            os.remove(os.path.join(OUT, f))
    json.dump(maps, open(listing, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(listing, 'a').write('\n')


if __name__ == '__main__':
    main()

# Prepare the yEd SVG exports in downloads/ for the browser.
# Usage: python3 scripts/prepare_svgs.py   (safe to run again)
#  - adds a viewBox, so the map scales with the size it is drawn at
#    (yEd writes only width and height)
#  - gives yEd's font names a fallback: 'Dialog' is Java's name for its
#    standard sans-serif and 'Lucida Grande' exists only on a Mac, so
#    without a fallback other systems would draw those labels in a serif font
import glob, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FALLBACK = ", Arial, Helvetica, sans-serif"

for f in sorted(glob.glob(os.path.join(ROOT, 'downloads', '*.svg'))):
    s = open(f, encoding='utf-8').read()
    t = s
    head = re.search(r'<svg\b[^>]*>', t).group(0)
    if 'viewBox=' not in head:
        w = re.search(r'\swidth="([\d.]+)"', head).group(1)
        h = re.search(r'\sheight="([\d.]+)"', head).group(1)
        t = t.replace(head, head.replace('<svg ', '<svg viewBox="0 0 %s %s" ' % (w, h), 1), 1)
    t = re.sub(r"font-family=\"'(Dialog|Lucida Grande)'\"", lambda m: "font-family=\"'%s'%s\"" % (m.group(1), FALLBACK), t)
    if t != s:
        open(f, 'w', encoding='utf-8').write(t)
        print('prepared', os.path.basename(f))

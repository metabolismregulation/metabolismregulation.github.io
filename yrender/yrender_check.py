# Compare tools/yrender.py with yEd's own exports: every <map>.graphml in a folder that has
# a <map>.svg from yEd is drawn again and both images are compared pixel by pixel.
#   python3 tools/yrender_check.py <folder> <out folder>
# Per map: size match, share of drawn pixels whose colour has no match within 1 px in the
# other image, for shapes and lines alone and with text, and <map>-overlay.png: the yEd image
# faded, shape differences red, text differences blue.
import sys, os, glob, io, re
import numpy as np, cairosvg
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yrender


def raster(svg, size=None, text=True):
    # RGB pixels; fonts made the same in both images (yEd places text for the fonts of the
    # computer it ran on), text left out for the shapes-only comparison
    svg = re.sub(r'font-family="[^"]*"', 'font-family="Liberation Sans"', svg)
    if not text:
        svg = re.sub(r'<text\b.*?</text>', '', svg, flags=re.S)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size and size[0],
                           output_height=size and size[1], background_color='white')
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGB'), dtype=np.int16)


def mismatch(a, b):
    # pixels of a with no pixel of similar colour within 1 px in b
    best = np.full(a.shape[:2], 999, np.int16)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            sb = np.roll(np.roll(b, dy, 0), dx, 1)
            best = np.minimum(best, np.abs(a - sb).max(2))
    return best > 60


def compare(ref, mine, text):
    a = raster(ref, text=text)
    b = raster(mine, (a.shape[1], a.shape[0]), text)
    m = mismatch(a, b) | mismatch(b, a)
    drawn = (a.min(2) < 245) | (b.min(2) < 245)
    return a, m, m.sum() / max(1, drawn.sum())


def main(folder, out):
    os.makedirs(out, exist_ok=True)
    rows = []
    for gml in sorted(glob.glob(os.path.join(folder, '*.graphml'))):
        name = os.path.basename(gml)[:-8]
        ref = os.path.join(folder, name + '.svg')
        if not os.path.exists(ref):
            continue
        mine = os.path.join(out, name + '.svg')
        try:
            yrender.render(gml, mine)
        except SystemExit as e:
            rows.append((name, 'refused', str(e).split('\n', 1)[1])); continue
        ref_svg, mine_svg = open(ref, encoding='utf-8').read(), open(mine, encoding='utf-8').read()
        size = lambda t: tuple(re.search(r'<svg[^>]*?\s%s="([\d.]+)' % k, t).group(1) for k in ('width', 'height'))
        same = size(ref_svg) == size(mine_svg)
        a, m, share = compare(ref_svg, mine_svg, True)
        _, ms, share_shapes = compare(ref_svg, mine_svg, False)
        img = (255 - (255 - a) * 0.35).astype(np.uint8)
        img[m] = (120, 120, 255); img[ms] = (230, 30, 30)
        Image.fromarray(img).save(os.path.join(out, name + '-overlay.png'))
        rows.append((name, 'size ok' if same else f'size {size(mine_svg)} vs yEd {size(ref_svg)}',
                     f'shapes {share_shapes:.2%}', f'with text {share:.2%}'))
    for r in rows:
        print('  '.join(r))


if __name__ == '__main__':
    main(*sys.argv[1:3])

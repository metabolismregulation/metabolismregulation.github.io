# The PNG of a map from its SVG (user, 2026-10-18, File pipeline in CLAUDE.md): cairosvg at 2x,
# white background, the same renderer as the Atlas images (yrender/). yEd's SVG names
# its font Dialog or sans-serif, which each system resolves to another font, so both are drawn in
# Liberation Sans (Arial's metrics, as yEd's Dialog) and the PNG is the same everywhere. yEd's
# text-rendering="geometricPrecision" is dropped: cairosvg draws the letters on top of each other.
# Needs: cairosvg, fonts-liberation.
#   python3 scripts/make_png.py <map.svg> [<map.png>]
import re, sys
import cairosvg


def font(m):
    fam = m.group(1)
    return 'font-family="%s"' % ('Liberation Sans, ' + fam if 'Dialog' in fam or fam.strip() == 'sans-serif' else fam)


def make_png(svg_path, png_path):
    svg = open(svg_path, encoding='utf-8').read()
    head = re.search(r'<svg\b[^>]*>', svg).group(0)
    w, h = (float(re.search(r'\s%s="([\d.]+)' % a, head).group(1)) for a in ('width', 'height'))
    svg = re.sub(r'font-family="([^"]*)"', font, svg.replace(' text-rendering="geometricPrecision"', ''))
    cairosvg.svg2png(bytestring=svg.encode('utf-8'), output_width=round(2 * w), output_height=round(2 * h),
                     background_color='white', write_to=png_path)


if __name__ == '__main__':
    make_png(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1][:-4] + '.png')

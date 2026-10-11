# Make the liver glycogen map from the muscle map, so the two are the same
# map with only the liver protein names (GraphML and SVG).
# Usage: python3 scripts/make_glycogen_liver.py
#  - GraphML: the muscle file with the labels renamed. Open it in yEd and
#    export the SVG (and PNG) from it.
#  - SVG: the muscle SVG with the labels renamed. Each renamed label takes its
#    position from the liver SVG exported by yEd, which centres the new text;
#    everything else, the canvas size included, stays as in the muscle SVG.
#    Run scripts/prepare_svgs.py after the export, then this script.
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
D = os.path.join(ROOT, 'downloads')
MAP = {'PYGM': 'PYGL', 'GYS1': 'GYS2', 'PHKG1': 'PHKG2', 'PHKA1': 'PHKA2',
       'IRS1': 'IRS1/2', 'ADRB2': 'GCGR', 'epinephrine': 'GCG'}

def read(name):
    return open(os.path.join(D, name), encoding='utf-8').read()

def write(name, text):
    open(os.path.join(D, name), 'w', encoding='utf-8', newline='').write(text)

# GraphML
g = re.sub(r'(<y:NodeLabel\b[^>]*>)([^<]*)(<)',
           lambda m: m.group(1) + MAP.get(m.group(2), m.group(2)) + m.group(3),
           read('F004-glycogen-muscle.graphml'))
write('F004-glycogen-liver.graphml', g)

# SVG
TEXT = r'<text\b([^>]*)>([^<]*)</text>'
muscle = read('F004-glycogen-muscle.svg')
liver = list(re.finditer(TEXT, read('F004-glycogen-liver.svg')))
texts = list(re.finditer(TEXT, muscle))
assert len(texts) == len(liver), 'the two SVGs do not have the same labels'
out, last = [], 0
for m, l in zip(texts, liver):
    if MAP.get(m.group(2), m.group(2)) != l.group(2):
        raise SystemExit('label order differs: %s / %s' % (m.group(2), l.group(2)))
    if m.group(2) in MAP:
        x = re.search(r'\sx="[^"]*"', l.group(1)).group(0)
        attrs = re.sub(r'\sx="[^"]*"', x, m.group(1), count=1)
        out += [muscle[last:m.start()], '<text%s>%s</text>' % (attrs, MAP[m.group(2)])]
        last = m.end()
out.append(muscle[last:])
write('F004-glycogen-liver.svg', ''.join(out))
print('made F004-glycogen-liver.graphml and .svg')

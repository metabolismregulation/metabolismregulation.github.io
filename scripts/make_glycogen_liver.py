# Make the liver glycogen map from the muscle map, so the two are the same
# map with only the liver protein names.
# Usage: python3 scripts/make_glycogen_liver.py
# Writes downloads/F004-glycogen-liver.graphml: the muscle GraphML with the
# labels renamed and the isoform fill red (muscle) changed to yellow (liver).
# Export the SVG and PNG of both maps from yEd afterwards.
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
D = os.path.join(ROOT, 'downloads')
MAP = {'PYGM': 'PYGL', 'GYS1': 'GYS2', 'PHKG1': 'PHKG2', 'PHKA1': 'PHKA2',
       'IRS1': 'IRS1/2', 'ADRB2': 'GCGR', 'epinephrine': 'GCG'}

src = open(os.path.join(D, 'F004-glycogen-muscle.graphml'), encoding='utf-8').read()
src = src.replace('Fill color="#E2ACA3"', 'Fill color="#FFE067"')  # isoforms
out = re.sub(r'(<y:NodeLabel\b[^>]*>)([^<]*)(<)',
             lambda m: m.group(1) + MAP.get(m.group(2), m.group(2)) + m.group(3), src)
open(os.path.join(D, 'F004-glycogen-liver.graphml'), 'w', encoding='utf-8', newline='').write(out)
print('made F004-glycogen-liver.graphml')

# Make the liver glycogen map from the muscle map, so the two are the same
# map with only the liver protein names.
# Usage: python3 scripts/make_glycogen_liver.py
# Writes downloads/F004-glycogen-liver.graphml: the muscle GraphML with the
# labels renamed, the isoform fill red (muscle) changed to yellow (liver), and
# GCG drawn as a protein (blue macromolecule), where epinephrine is a small
# molecule (green simple chemical).
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

def protein(m):
    block = m.group(0)
    if '>GCG<' not in block or 'SimpleChemical' not in block:
        return block
    ind = re.search(r'\n(\s*)</y:GenericNode>', block).group(1)
    block = block.replace('com.yworks.sbgn.SimpleChemical', 'com.yworks.sbgn.Macromolecule', 1)
    block = block.replace('Fill color="#DBEBDB"', 'Fill color="#C8D8EB"', 1)
    return block.replace('\n' + ind + '</y:GenericNode>', '\n' + ind + '  <y:StyleProperties>\n'
        + ind + '    <y:Property class="java.lang.Integer" name="com.yworks.sbgn.style.radius" value="10"/>\n'
        + ind + '  </y:StyleProperties>\n' + ind + '</y:GenericNode>', 1)

# innermost nodes only (no nested <node> inside the match)
out = re.sub(r'<node id="[^"]*">(?:(?!<node ).)*?</node>', protein, out, flags=re.S)
open(os.path.join(D, 'F004-glycogen-liver.graphml'), 'w', encoding='utf-8', newline='').write(out)
print('made F004-glycogen-liver.graphml')

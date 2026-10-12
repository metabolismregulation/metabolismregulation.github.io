# v10: v9A (inside-out) plus the allosteric regulation of the PFK1 / FBPase
# substrate cycle.
# Usage (from _work/): python3 F001-glycolysis/build_v10.py
# Writes two variants that differ only in where AMP enters:
#   v10A  AMP inside the cycle, forking like F2,6BP (2 AMP glyphs in the map)
#   v10B  F2,6BP alone inside; AMP enters PFK1 and FBPase from the outer
#         sides, one AMP copy per enzyme (3 AMP glyphs in the map)
#
# Added content (rows in regulation.csv):
#   R10 F2,6BP stimulates PFK1           R11 F2,6BP inhibits FBPase
#   R12 ATP inhibits PFK1                R13 AMP stimulates PFK1
#   R14 AMP inhibits FBPase
# ATP and AMP are new copies of the ATP and AMP glyphs already in the map, as
# the map already does for ATP and AMP (no clone marker in the house style).
#
# Story decisions:
#   - The PFK1 and FBPase lanes move from 28 px to 120 px apart, so the space
#     inside the F6P / F16BP cycle takes the two shared effectors: F2,6BP
#     enters from above, AMP from below, each forking to PFK1 (stimulation)
#     and FBPase (inhibition). Both effectors then read as "push the cycle
#     towards glycolysis".
#     (v10A; in v10B only F2,6BP, entering at the middle of the side).
#   - ATP inhibition enters PFK1 from the outer side, next to the catalyst,
#     through the gap between process and enzyme.
#   - F6P and F16BP widen to 160 px to carry the wider lanes.
#   - PFKFB2 (kinase and phosphatase forms) move 25 px closer to their
#     interconversion so PFK1 can sit below the PFKFB2 phosphatase arc.
# F2,6BP sits inside a loop closed by its own two PFKFB2 reactions, so its
# arcs out cross one arc of that loop (PFKFB2 -> bisphosphatase) and the
# F6P -> PFK1 stem: 2 crossings, both at 90 degrees.
import os, sys, copy
VARIANT = sys.argv[1] if len(sys.argv) > 1 else None
if VARIANT is None:
    for v in ('A', 'B'):
        os.system('%s %s %s' % (sys.executable, os.path.abspath(__file__), v))
    sys.exit()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from ygml import load, nodes, edges, NS

SRC = os.path.join(HERE, 'sources', 'F001-glycolysis-PD-biology-v9A-inside-out.graphml')
OUT = os.path.join(HERE, 'versions', 'F001-glycolysis-PD-biology-v10%s.graphml' % VARIANT)
Y = '{%s}' % NS['y']

t, k = load(SRC)
N, E = nodes(t, k), edges(t, k)
EB = {e['id']: e for e in E}


def gen(i):
    el = N[i]['el']
    g = el.find('g:data/y:GenericNode', NS)
    return g


def place(i, cx, cy, w=None):
    """Centre node i at (cx, cy); optionally set its width and recentre the label."""
    g = gen(i)
    geo = g.find('y:Geometry', NS)
    if w is not None:
        geo.set('width', '%.1f' % w)
    W, H = float(geo.get('width')), float(geo.get('height'))
    geo.set('x', '%.1f' % (cx - W / 2))
    geo.set('y', '%.1f' % (cy - H / 2))
    if w is not None:
        for l in g.findall('y:NodeLabel', NS):
            if not l.get('iconData'):
                l.set('x', '%.4f' % ((W - float(l.get('width'))) / 2))


def route(eid, sx, sy, tx, ty, bends=()):
    p = EB[eid]['path']
    for a, v in zip(('sx', 'sy', 'tx', 'ty'), (sx, sy, tx, ty)):
        p.set(a, '%.1f' % v)
    for q in p.findall('y:Point', NS):
        p.remove(q)
    for x, y in bends:
        q = p.makeelement(Y + 'Point', {'x': '%.1f' % x, 'y': '%.1f' % y})
        p.append(q)


def stadium_dx(w, h, off):
    r = h / 2
    return w / 2 - r + (r * r - off * off) ** 0.5


def new_node(template, nid, cx, cy):
    el = copy.deepcopy(N[template]['el'])
    el.set('id', nid)
    N[template]['el'].getparent().append(el)
    N[nid] = dict(N[template], el=el)
    place(nid, cx, cy)


def new_edge(template, eid, s, tgt, arrow):
    el = copy.deepcopy(EB[template]['el'])
    el.set('id', eid)
    el.set('source', s)
    el.set('target', tgt)
    pl = el.find('g:data/y:PolyLineEdge', NS)
    pl.find('y:Arrows', NS).set('target', arrow)
    EB[template]['el'].getparent().append(el)
    EB[eid] = dict(el=el, path=pl.find('y:Path', NS))


# ---- anchor block: F6P <-> F16BP cycle -------------------------------------
AX = -439            # main column (G6P, F6P, F16BP)
LANE = 60            # PFK1 lane at AX+LANE, FBPase lane at AX-LANE
PY = 110             # height of the two processes
F16Y = 230 if VARIANT == 'A' else 262   # F16BP centre
WCH = 160            # width of F6P and F16BP
PFK, FBP = AX + LANE, AX - LANE

place('n8', AX, 0, WCH)                  # F6P
place('n13', AX, F16Y, WCH)              # F16BP
place('n11', PFK, PY)                    # PFK1 process
place('n12', FBP, PY)                    # FBPase process
GAP = 40 if VARIANT == 'A' else 60      # process - enzyme gap
place('n15', PFK + 9 + GAP + 40, PY)     # PFK1 enzyme
place('n14', FBP - 9 - GAP - 40, PY)     # FBP1/2 enzyme

route('e13', LANE, 16, 0, -9)            # F6P -> PFK1
route('e12', 0, 9, LANE, -16)            # PFK1 -> F16BP
route('e10', -LANE, -16, 0, 9)           # F16BP -> FBPase
route('e11', 0, -9, -LANE, 16)           # FBPase -> F6P
CY = 0 if VARIANT == 'A' else -7         # PFK1 catalysis port
route('e14', -40, CY, 9, CY)             # PFK1 catalysis
route('e9', 40, 0, -9, 0)                # FBP1/2 catalysis

# F6P <-> F2,6BP lanes keep their place; only the F6P end moves out
d = stadium_dx(WCH, 32, 14)
route('e17', d, -14, *(float(EB['e17']['path'].get(a)) for a in ('tx', 'ty')))
route('e16', *(float(EB['e16']['path'].get(a)) for a in ('sx', 'sy')), d, 14)

# ---- PFKFB2 interconversion: kinase / phosphatase forms 25 px closer -------
place('n23', 0, -70)
place('n24', 0, 70)
LX = -288                                # x of the F2,6BP lanes (n17, n18)
route('e19', 0, -9, 0, 20)
route('e20', 0, -20, 0, 9)
route('e25', -40, 0, 0, -9, [(LX, -70)])
route('e26', -40, 0, 0, 9, [(LX, 70)])

# ---- new: F2,6BP -> PFK1 (stimulation), -| FBPase (inhibition) ----------
F26 = N['n16']['geo']
f26cx = F26[0] + F26[2] / 2
TRUNK = 50                               # trunk height, between F6P and the processes
sx = -40
new_edge('e25', 'e78', 'n16', 'n11', 'white_delta')
new_edge('e25', 'e79', 'n16', 'n12', 't_shape')
FY = -7 if VARIANT == 'A' else 0          # F2,6BP port on the inner sides
for eid, tx in (('e78', -9), ('e79', 9)):
    route(eid, sx, 16, tx, FY, [(f26cx + sx, TRUNK), (AX, TRUNK), (AX, PY + FY)])

# ---- new: AMP -> PFK1 (stimulation), -| FBPase (inhibition) --------------
# ---- new: ATP -| PFK1, outer side next to the catalyst -------------------
new_edge('e25', 'e80', 'n75', 'n11', 'white_delta')
new_edge('e25', 'e81', 'n75', 'n12', 't_shape')
new_edge('e25', 'e82', 'n74', 'n11', 't_shape')
if VARIANT == 'A':
    new_node('n67', 'n75', AX, 172)
    for eid, tx in (('e80', -9), ('e81', 9)):
        route(eid, 0, -16, tx, 7, [(AX, PY + 7)])
    GX = PFK + 9 + GAP / 2               # vertical in the process-enzyme gap
    new_node('n20', 'n74', GX + 15 + 30, 172)
    route('e82', -30, 0, 9, 7, [(GX, 172), (GX, PY + 7)])
else:
    # PFK1 gap: catalyst at -7, ATP at 0 (outer vertical), AMP at +7
    # (inner vertical); the nested L shapes do not cross.
    XO, XI = PFK + 9 + 35, PFK + 9 + 15
    new_node('n20', 'n74', XO + 10 + 30, 160)
    route('e82', -30, 0, 9, 0, [(XO, 160), (XO, PY)])
    new_node('n67', 'n75', XI + 10 + 30, 210)
    route('e80', -30, 0, 9, 7, [(XI, 210), (XI, PY + 7)])
    # FBPase gap: catalyst at 0, AMP (second copy) at +7
    XF = FBP - 9 - GAP / 2
    new_node('n67', 'n76', XF - 15 - 30, 172)
    EB['e81']['el'].set('source', 'n76')
    route('e81', 30, 0, -9, 7, [(XF, 172), (XF, PY + 7)])

t.write(OUT, xml_declaration=True, encoding='UTF-8', standalone=False)
print('wrote', OUT)

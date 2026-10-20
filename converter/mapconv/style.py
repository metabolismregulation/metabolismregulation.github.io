# Standard sizes (user, 2026-10-16), for a map from another drawing (CellDesigner -> GraphML):
# proteins, genes and RNAs 80 x 40; metabolites (chemical()) 36 x 36 circles where the map
# draws them as circles, else stadiums 32 high, as wide as the name needs in steps of 10; centres
# kept. A map whose objects are clearly larger or smaller than
# ours (median protein height off 40 by more than 20%, e.g. a large font) is first scaled as a
# whole, distances included. Collisions that follow are the user's to look at.
# The file with standard sizes is made when asked (the page's tick box, to harmonise a map) or when
# the map is drawn at another scale than usual (user, 2026-10-20): the median protein height off our 40, the median
# label font off the program's default, or, on a map without proteins, the median metabolite height
# off CHEMICAL, each by more than NOTICED.
import math, statistics
from dataclasses import replace
from . import report

PROTEIN = (80.0, 40.0)
SIZE = {'Macromolecule': PROTEIN, 'NucleicAcidFeature': PROTEIN}
CIRCLE = (36.0, 36.0)  # the yEd metabolite glyph is a circle when square, else a stadium
NOTICED = 1.2  # a scale this far from 1 (either way) is rescaled
# the program's default label font: CellDesigner (all 926 labels of the website's CellDesigner
# files), Newt (its sample files)
FONT = {'CellDesigner': 12.0, 'Newt': 11.0}
CHEMICAL = (25.0, 40.0)  # usual metabolite heights: CellDesigner's 70 x 25 to Newt's 40 (ours 32 to 36; user, 2026-10-20)
ENTITY = ('Macromolecule', 'NucleicAcidFeature', 'SimpleChemical', 'Complex', 'UnspecifiedEntity', 'Perturbation', 'Phenotype')


def chemical(d):
    # a metabolite's size: a circle stays a circle; a stadium is 32 high and 60, 70, 80, ... wide,
    # about 7 px per character of its longest name line plus 14 (the user's maps: 60 for Pi,
    # 80 glutamate, 90 citrulline, 100 oxaloacetate, 180 alpha-keto-beta-methylvalerate)
    w, h = d.box[2:]
    if abs(w - h) <= 0.1 * max(w, h):
        return CIRCLE
    name = max((d.labels[0] if d.labels else '').split('\n'), key=len)
    return (max(60.0, 10.0 * math.ceil((7 * len(name) + 14) / 10)), 32.0)


def scale_of(m):
    hs = [d.box[3] for d in m.nodes.values() if d.kind == 'Macromolecule' and d.count == 1]
    s = statistics.median(hs) / PROTEIN[1] if hs else 1.0
    return s if s > NOTICED or s < 1 / NOTICED else 1.0


def off(v, default):
    return v > default * NOTICED or v < default / NOTICED


def reasons(m, program):
    # why the map is not at the usual scale, [] when it is
    font = FONT[program]
    median = lambda vs: statistics.median(vs) if vs else None
    fonts = median([d.font for d in m.nodes.values() if d.font and d.kind in ENTITY])
    proteins = median([d.box[3] for d in m.nodes.values() if d.kind == 'Macromolecule' and d.count == 1])
    chems = median([d.box[3] for d in m.nodes.values() if d.kind == 'SimpleChemical' and d.count == 1])
    why = []
    if fonts and off(fonts, font):
        why.append('Median font size %g, %s default %g.' % (fonts, program, font))
    if proteins and off(proteins, PROTEIN[1]):
        why.append('Median protein height %g, standard %g.' % (proteins, PROTEIN[1]))
    if not proteins and chems and (chems < CHEMICAL[0] / NOTICED or chems > CHEMICAL[1] * NOTICED):
        why.append('Median metabolite height %g, usual range %g to %g.' % (chems, *CHEMICAL))
    return why


def standard(m, program, asked=False):
    # the map with standard node sizes when asked or drawn at another scale (reasons), else None; one
    # note for every case, in the user's words (2026-10-20)
    if not asked and not reasons(m, program):
        return None
    report.say('changed', 'GraphML standard sizes: map set to font size 14, protein size 80 x 40, metabolite circles '
               '36 x 36 or stadium shapes with height 32.')
    return standardise(m)


def standardise(m):
    s = scale_of(m)
    nodes, ratio = {}, {}
    for i, d in m.nodes.items():
        x, y, w, h = (v / s for v in d.box)
        W, H = chemical(d) if d.kind == 'SimpleChemical' else SIZE.get(d.kind, (w, h))
        if d.kind.endswith('Process') or d.kind == 'Operator':
            W, H = d.box[2], d.box[3]  # glyphs of their own fixed size
        ratio[i] = (W / w if w else 1, H / h if h else 1)
        nodes[i] = replace(d, box=(x + w / 2 - W / 2, y + h / 2 - H / 2, W, H),
                           label_at=tuple(v / s for v in d.label_at) if d.label_at else None)
    # ports keep their place on the node's border; bends move with the map, and the bend next to
    # a port stays in line with it where it was (a straight run into the node stays straight)
    cen = lambda b: (b[0] + b[2] / 2, b[1] + b[3] / 2)
    def end(i, at, new):  # the arc's end point, before (scaled) and after
        (cx, cy), (nx, ny) = cen(m.nodes[i].box), cen(nodes[i].box)
        return ((cx + at[0]) / s, (cy + at[1]) / s), (nx + new[0], ny + new[1])
    def keep(p, old, new):
        return (new[0] if abs(p[0] - old[0]) < 0.5 else p[0], new[1] if abs(p[1] - old[1]) < 0.5 else p[1])
    arcs = []
    for e in m.arcs:
        sa = (e.source_at[0] / s * ratio[e.source][0], e.source_at[1] / s * ratio[e.source][1])
        ta = (e.target_at[0] / s * ratio[e.target][0], e.target_at[1] / s * ratio[e.target][1])
        pts = [(px / s, py / s) for px, py in e.points]
        if pts:
            pts[0] = keep(pts[0], *end(e.source, e.source_at, sa))
            pts[-1] = keep(pts[-1], *end(e.target, e.target_at, ta))
        arcs.append(replace(e, points=pts, source_at=sa, target_at=ta))
    return replace(m, nodes=nodes, arcs=arcs)

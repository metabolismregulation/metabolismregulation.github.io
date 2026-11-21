import math, statistics
from dataclasses import replace

PROTEIN = (80.0, 40.0)
SIZE = {'Macromolecule': PROTEIN, 'NucleicAcidFeature': PROTEIN,
        'SimpleChemical': (40.0, 40.0)}
NOTICED = 1.2
FONT_STANDARD = 14.0
FONT = {'CellDesigner': 12.0, 'Newt': 11.0}
CHEMICAL = (25.0, 40.0)
ENTITY = ('Macromolecule', 'NucleicAcidFeature', 'SimpleChemical', 'Complex', 'UnspecifiedEntity', 'Perturbation', 'Phenotype')


def scale_of(m):
    hs = [d.box[3] for d in m.nodes.values() if d.kind == 'Macromolecule' and d.count == 1]
    s = statistics.median(hs) / PROTEIN[1] if hs else 1.0
    return s if s > NOTICED or s < 1 / NOTICED else 1.0


def off(v, default):
    return v > default * NOTICED or v < default / NOTICED


def reasons(m, program):
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
    if not asked and not reasons(m, program):
        return None
    return standardise(m)


def standardise(m):
    s = scale_of(m)
    nodes, ratio = {}, {}
    for i, d in m.nodes.items():
        x, y, w, h = (v / s for v in d.box)
        W, H = SIZE.get(d.kind, (w, h))
        if d.kind.endswith('Process') or d.kind == 'Operator':
            W, H = d.box[2], d.box[3]
        ratio[i] = (W / w if w else 1, H / h if h else 1)
        nodes[i] = replace(d, box=(x + w / 2 - W / 2, y + h / 2 - H / 2, W, H),
                           font=FONT_STANDARD if d.kind in ENTITY else None, small=10.0 if d.states or d.units else None,
                           label_at=tuple(v / s for v in d.label_at) if d.label_at else None)
    cen = lambda b: (b[0] + b[2] / 2, b[1] + b[3] / 2)
    def end(i, at, new):
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

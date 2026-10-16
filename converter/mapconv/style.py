# Standard sizes (user, 2026-10-16), for a map from another drawing (CellDesigner -> GraphML):
# proteins, genes and RNAs 80 x 40; metabolites 36 x 36 circles where the map draws them as
# circles, else 60 x 32 (after a direct read they are 60 x 32 already); centres kept. A map whose objects are clearly larger or smaller than
# ours (median protein height off 40 by more than 20%, e.g. a large font) is first scaled as a
# whole, distances included. Collisions that follow are the user's to look at.
import statistics
from dataclasses import replace

PROTEIN = (80.0, 40.0)
SIZE = {'Macromolecule': PROTEIN, 'NucleicAcidFeature': PROTEIN}
CIRCLE, OVAL = (36.0, 36.0), (60.0, 32.0)
NOTICED = 1.2  # a scale this far from 1 (either way) is rescaled


def scale_of(m):
    hs = [d.box[3] for d in m.nodes.values() if d.kind == 'Macromolecule' and d.count == 1]
    s = statistics.median(hs) / PROTEIN[1] if hs else 1.0
    return s if s > NOTICED or s < 1 / NOTICED else 1.0


def standardise(m):
    s = scale_of(m)
    chem = [d.box for d in m.nodes.values() if d.kind == 'SimpleChemical']
    round_ = sum(abs(w - h) <= 0.1 * max(w, h) for _, _, w, h in chem) * 2 >= len(chem)
    size = dict(SIZE, SimpleChemical=CIRCLE if round_ else OVAL)
    nodes, ratio = {}, {}
    for i, d in m.nodes.items():
        x, y, w, h = (v / s for v in d.box)
        W, H = size.get(d.kind, (w, h))
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

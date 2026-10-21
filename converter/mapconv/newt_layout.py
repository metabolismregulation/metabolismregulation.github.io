# The Newt adapter (restructuring step 4, 2026-10-19): what an SBGN-ML map needs so Newt draws it as
# the source does, kept apart from the SBGN-ML itself (user, 2026-10-21: the "for Newt" files). Every
# process and gate in a compartment, each compartment as large as Newt's padding needs, neighbours
# too close for it moved apart (adjust); arcs drawn as Newt aims them (leaving, unaimed; SBGNML.md).
import math
from . import report
from .layout import PROCESSES, centre, compartment_of, decorations, unbent


def adjust(diagram, layout):
    # the map, its boxes as Newt keeps them (a process's port stubs only in advanced)
    return for_newt(placed(diagram), layout != 'straight')


def leaving(d, p, q, at_border, gap=3):
    # Newt draws only the bends and aims each end at the node's centre: an end at a yEd port p gets
    # a bend where the arc to q leaves the node, gap px beyond (Newt loses an arc whose bend lies on
    # the border), so the line keeps yEd's course (eNOS: arcs level with the process, at a complex's
    # side); none where that is the border point anyway
    x, y, w, h = d.box
    dx, dy = q[0] - p[0], q[1] - p[1]
    ts = [t for t in ((x + w - p[0]) / dx if dx > 0 else (x - p[0]) / dx if dx < 0 else None,
                      (y + h - p[1]) / dy if dy > 0 else (y - p[1]) / dy if dy < 0 else None) if t is not None]
    t = max(0.0, min(ts)) + gap / math.hypot(dx, dy) if ts else 0.0
    b = (p[0] + t * dx, p[1] + t * dy)
    return [b] if math.dist(b, at_border) > 5 else []


def unaimed(pts, a, b):
    # the bends without those on or near (5 px) the line from where Newt aims the ends (a port, else
    # the node's centre): Newt loses an arc with two bends in one place (iNOS, IRF1 mRNA; 2026-10-18)
    return unbent([a] + pts + [b], 5)[1:-1]


def placed(diagram):
    # a process or gate outside any compartment put into the smallest one its centre lies in, else
    # into its first neighbour's, as Newt does (Newt puts it in a neighbour's and grows that
    # compartment over the others: iNOS, the transports across the plasma membrane; carnitine,
    # LKB1 out of the nucleus; user, 2026-10-18)
    N = diagram.nodes
    for d in N.values():
        if d.kind in ('Operator',) + PROCESSES and compartment_of(N, d.id) is None:
            x, y = centre(d)
            at = [c for c, e in N.items() if e.kind == 'Compartment'
                  and e.box[0] <= x <= e.box[0] + e.box[2] and e.box[1] <= y <= e.box[1] + e.box[3]]
            near = [compartment_of(N, a.target if a.source == d.id else a.source) for a in diagram.arcs if d.id in (a.source, a.target)]
            d.parent = min(at, key=lambda c: N[c].box[2] * N[c].box[3]) if at else next((c for c in near if c), d.parent)
    return diagram


# Newt (sbgnml-to-cytoscape bboxProp): a compartment's padding, 24 (its 14 and the compound 10),
# with half a border and 1, 30 to be safe; a complex inside it stands out by its own padding
NEWT_PAD, COMPLEX_PAD = 30, 20


def for_newt(diagram, ports=True):
    # compartments as Newt keeps them (user, 2026-10-18): Newt keeps a compartment's box only when
    # its contents (state variables, units, a complex's padding, a process's port stubs) stay
    # NEWT_PAD inside every edge, else it wraps the contents and edges aligned in the source drift
    # apart or overlap. Each box is widened as its contents need; edges aligned in the source (within
    # 2 px) move together. Where two neighbours' contents are too close across their shared edge,
    # everything past that edge moves on by what is missing, so the edges stay aligned (printed).
    # Compartments side by side keep the gap the source has between them, up to NEWT_PAD (platelet
    # eicosanoids: 2.7 px apart in yEd, CYTOSOL grew into DENSE TUBULAR SYSTEM; user, 2026-10-19)
    N = diagram.nodes
    comps = [c for c, d in N.items() if d.kind == 'Compartment']
    value = lambda c, k: N[c].box[k % 2] + (N[c].box[2 + k % 2] if k > 1 else 0)
    # facing pairs: a before b along an axis, side by side on the other, neither around the other
    within = lambda a, b: all(value(a, k) >= value(b, k) - 1 for k in (0, 1)) and all(value(a, k) <= value(b, k) + 1 for k in (2, 3))
    facing = [(a, b, ax, min(NEWT_PAD, max(0.0, value(b, ax) - value(a, ax + 2)))) for a in comps for b in comps for ax in (0, 1)
              if a != b and not within(a, b) and not within(b, a) and value(a, ax + 2) - 2 <= value(b, ax)
              and min(value(a, 3 - ax), value(b, 3 - ax)) - max(value(a, 1 - ax), value(b, 1 - ax)) > 0.5]
    # a node outside every compartment that a compartment, once in place, grows over by more than
    # half is covered whole, so the edge does not stop inside it (SREBP from CellDesigner, straight:
    # the COPII vesicle grew to its process and cut the Sec23:Sec24 complex; user, 2026-10-20); one
    # the growth only grazes, or the source draws across the edge, stays as it is
    free = [i for i, d in N.items() if d.kind != 'Compartment' and d.parent is None and compartment_of(N, i) is None]
    covered = {}
    inside = lambda b, q: max(0, min(b[0] + b[2], q[2]) - max(b[0], q[0])) * max(0, min(b[1] + b[3], q[3]) - max(b[1], q[1]))
    for _ in range(50):
        ext = {c: [math.inf, math.inf, -math.inf, -math.inf] for c in comps}
        for i, d in N.items():
            c = covered.get(i, compartment_of(N, i))
            if c is None or d.parent is not None and N[d.parent].kind == 'Complex':  # a member: inside its complex
                continue
            # a complex with its padding, a process or gate as Newt draws it (18 px: 51 with its
            # ports, 27 without)
            e = COMPLEX_PAD if d.kind == 'Complex' else NEWT_PAD - 4 if d.kind == 'Compartment' else \
                (17 if ports else 5) if d.kind in ('Operator',) + PROCESSES else 0
            states, units = decorations(d)
            for (x, y, w, h), e in [(d.box, e)] + [(b, 0) for b in states + [b for _, b in units]]:
                for k, v in enumerate((x - e, y - e, x + w + e, y + h + e)):
                    ext[c][k] = min(ext[c][k], v) if k < 2 else max(ext[c][k], v)
        groups = []
        for c, k in ((c, k) for c in comps for k in range(4)):
            g = next((g for g in groups if g[0][1] % 2 == k % 2 and abs(value(*g[0]) - value(c, k)) <= 2), None)
            g.append((c, k)) if g else groups.append([(c, k)])
        bounds = [(g, max([ext[c][k] + NEWT_PAD for c, k in g if k > 1 and ext[c][k] > -math.inf], default=-math.inf),
                   min([ext[c][k] - NEWT_PAD for c, k in g if k < 2 and ext[c][k] < math.inf], default=math.inf)) for g in groups]
        # each edge where it ends up (an edge grows outward as its contents need); a facing pair
        # closer than its gap moves b's side on
        end = {(c, k): max(lo, value(c, k)) if k > 1 else min(hi, value(c, k)) for g, lo, hi in bounds for c, k in g}
        clash = sorted([(value(*g[0]), g, lo - hi) for g, lo, hi in bounds if lo > hi + 0.5] +
                       [(value(b, ax), [(b, ax)], end[a, ax + 2] + gap - end[b, ax]) for a, b, ax, gap in facing
                        if end[a, ax + 2] + gap > end[b, ax] + 0.5 and abs(value(a, ax + 2) - value(b, ax)) > 2],
                       key=lambda t: (t[1][0][1] % 2, t[0]))
        if not clash:
            grown = {c: [min(value(c, k), ext[c][k] - NEWT_PAD) if k < 2 else max(value(c, k), ext[c][k] + NEWT_PAD) for k in range(4)] for c in comps}
            hit = {i: c for i in free if i not in covered for c in comps
                   if 0.5 * N[i].box[2] * N[i].box[3] < inside(N[i].box, grown[c]) < N[i].box[2] * N[i].box[3]
                   and not inside(N[i].box, [value(c, k) for k in range(4)])}
            if not hit:
                break
            covered.update(hit)
            continue
        at, g, by = clash[0]
        moved(diagram, g[0][1] % 2, at, by)
        report.say('changed', 'compartments %s: moved %d px apart, so that Newt does not overlap them'
              % (', '.join(sorted({N[c].labels[0] if N[c].labels else c for c, _ in g})), by))
    for g, lo, hi in bounds:
        v = min(max(value(*g[0]), lo), hi)
        for c, k in g:
            d = N[c]
            x0, y0, x1, y1 = d.box[0], d.box[1], d.box[0] + d.box[2], d.box[1] + d.box[3]
            x0, y0, x1, y1 = [v if j == k else q for j, q in enumerate((x0, y0, x1, y1))]
            if d.label_at and k < 2:  # the name stays where it is
                d.label_at = (d.label_at[0] + d.box[0] - x0, d.label_at[1] + d.box[1] - y0)
            d.box = (x0, y0, x1 - x0, y1 - y0)
    return diagram


def moved(diagram, axis, at, by):
    # everything past the line at (x or y, by axis) moved on by `by`: the compartments that start
    # there with their contents, the nodes outside any compartment, the bends; a compartment the
    # line runs through grows
    N = diagram.nodes
    past = lambda d: d.box[axis] >= at - 2
    shift = lambda b: tuple(v + by if j == axis else v for j, v in enumerate(b))
    for i, d in N.items():
        c = compartment_of(N, i) if d.kind != 'Compartment' else None
        if d.kind == 'Compartment':
            if past(d):
                d.box = shift(d.box)
            elif d.box[axis] + d.box[2 + axis] > at - 2:
                d.box = tuple(v + by if j == 2 + axis else v for j, v in enumerate(d.box))
        elif c is not None and past(N[c]) or c is None and centre(d)[axis] > at:
            d.box = shift(d.box)
    for a in diagram.arcs:
        a.points = [shift(p) if p[axis] > at else p for p in a.points]

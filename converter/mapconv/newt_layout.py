import math
from . import report
from .layout import PROCESSES, centre, compartment_of, decorations, unbent


def adjust(diagram, layout):
    return for_newt(placed(diagram), layout != 'straight')


def leaving(d, p, q, at_border, gap=3):
    x, y, w, h = d.box
    dx, dy = q[0] - p[0], q[1] - p[1]
    ts = [t for t in ((x + w - p[0]) / dx if dx > 0 else (x - p[0]) / dx if dx < 0 else None,
                      (y + h - p[1]) / dy if dy > 0 else (y - p[1]) / dy if dy < 0 else None) if t is not None]
    t = max(0.0, min(ts)) + gap / math.hypot(dx, dy) if ts else 0.0
    b = (p[0] + t * dx, p[1] + t * dy)
    return [b] if math.dist(b, at_border) > 5 else []


def unaimed(pts, a, b):
    return unbent([a] + pts + [b], 5)[1:-1]


def placed(diagram):
    N = diagram.nodes
    for d in N.values():
        if d.kind in ('Operator',) + PROCESSES and compartment_of(N, d.id) is None:
            x, y = centre(d)
            at = [c for c, e in N.items() if e.kind == 'Compartment'
                  and e.box[0] <= x <= e.box[0] + e.box[2] and e.box[1] <= y <= e.box[1] + e.box[3]]
            near = [compartment_of(N, a.target if a.source == d.id else a.source) for a in diagram.arcs if d.id in (a.source, a.target)]
            d.parent = min(at, key=lambda c: N[c].box[2] * N[c].box[3]) if at else next((c for c in near if c), d.parent)
    return diagram


NEWT_PAD, PORTS = 30, 12


def for_newt(diagram, ports=True):
    N = diagram.nodes
    comps = [c for c, d in N.items() if d.kind == 'Compartment']
    value = lambda c, k: N[c].box[k % 2] + (N[c].box[2 + k % 2] if k > 1 else 0)
    within = lambda a, b: all(value(a, k) >= value(b, k) - 1 for k in (0, 1)) and all(value(a, k) <= value(b, k) + 1 for k in (2, 3))
    facing = [(a, b, ax, min(NEWT_PAD, max(0.0, value(b, ax) - value(a, ax + 2)))) for a in comps for b in comps for ax in (0, 1)
              if a != b and not within(a, b) and not within(b, a) and value(a, ax + 2) - 2 <= value(b, ax)
              and min(value(a, 3 - ax), value(b, 3 - ax)) - max(value(a, 1 - ax), value(b, 1 - ax)) > 0.5]
    free = [i for i, d in N.items() if d.kind != 'Compartment' and d.parent is None and compartment_of(N, i) is None]
    covered = {}
    inside = lambda b, q: max(0, min(b[0] + b[2], q[2]) - max(b[0], q[0])) * max(0, min(b[1] + b[3], q[3]) - max(b[1], q[1]))
    for _ in range(50):
        ext = {c: [math.inf, math.inf, -math.inf, -math.inf] for c in comps}
        for i, d in N.items():
            c = covered.get(i, compartment_of(N, i))
            if c is None or d.parent is not None and N[d.parent].kind == 'Complex':
                continue
            e = -NEWT_PAD if d.kind == 'Compartment' else \
                PORTS * ports if d.kind in ('Operator',) + PROCESSES else 0
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
            if d.label_at and k < 2:
                d.label_at = (d.label_at[0] + d.box[0] - x0, d.label_at[1] + d.box[1] - y0)
            d.box = (x0, y0, x1 - x0, y1 - y0)
    return diagram


def moved(diagram, axis, at, by):
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

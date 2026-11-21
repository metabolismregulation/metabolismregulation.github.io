import math, re
from dataclasses import replace
from .model import HEADS
from .style import SIZE

PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess')
MODIFIERS = HEADS[1:]


def centre(d):
    x, y, w, h = d.box
    return x + w / 2, y + h / 2


def compartment_of(N, i):
    q = N[i].parent
    while q is not None and N[q].kind != 'Compartment':
        q = N[q].parent
    return q


def decorations(d):
    x, y, w, h = d.box
    cx, cy = x + w / 2, y + h / 2
    states = []
    for txt, rx, ry in d.states:
        sw = 15.0 if len(txt) <= 2 else 45.0
        states.append((cx + rx * w - sw / 2, cy + ry * h - 7.5, sw, 15.0))
    units = d.units + (['N:%d' % d.count] if d.count > 2 and not any(re.fullmatch(r'N:\d+', u) for u in d.units) else [])
    uw = [max(3, len(u)) * 7.0 for u in units]
    return states, [(u, (x + (k + 1) / (len(units) + 1) * w - uw[k] / 2, y - 7.5, uw[k], 15.0)) for k, u in enumerate(units)]


def main_lines(diagram, box, ents, origin=(0, 0)):
    N, E = diagram.nodes, diagram.arcs
    procs = [i for i, d in N.items() if d.kind in PROCESSES]
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    cen = lambda i: (box[i][0] + box[i][2] / 2, box[i][1] + box[i][3] / 2)
    steps = {}
    for q in procs:
        cons = {e.source for e in E if e.target == q and e.source in ents and e.head is None} | \
            {e.target for e in E if e.source == q and e.target in ents and e.head is None and not e.tail}
        prod = {e.target for e in E if e.source == q and e.target in ents and e.head == 'production'}
        steps[q] = (cons or prod, prod)

    def flows(p):
        ins = [e for e in E if e.target == p and e.source in ents and e.head is None]
        ins += [replace(e, source=e.target, target=p, points=e.points[::-1], source_at=e.target_at, target_at=e.source_at) for e in E
                if e.source == p and e.target in ents and e.head is None and not e.tail]
        outs = [e for e in E if e.source == p and e.target in ents and e.head is not None]
        mods = [e for e in E if e.target == p and e.source in ents and e.head in MODIFIERS]
        gates = [e for e in E if e.target == p and e.source in ops and e.head in MODIFIERS]
        reversible = not ins and len(outs) >= 2
        c = cen(p)
        if reversible:
            at = lambda e: (e.points[0][0] - origin[0], e.points[0][1] - origin[1]) if e.points else cen(e.target)
            ax = 1 if sum(abs(at(e)[1] - c[1]) for e in outs) >= sum(abs(at(e)[0] - c[0]) for e in outs) else 0
            ins = [replace(e, source=e.target, target=p, points=e.points[::-1], source_at=e.target_at, target_at=e.source_at) for e in outs if at(e)[ax] < c[ax]]
            outs = [e for e in outs if at(e)[ax] >= c[ax]]
        if not ins or not outs:
            return None
        def through(a, b):
            (ax, ay), (bx, by) = cen(a), cen(b)
            L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1
            t_ = ((c[0] - ax) * (bx - ax) + (c[1] - ay) * (by - ay)) / L2
            d = abs((bx - ax) * (c[1] - ay) - (by - ay) * (c[0] - ax)) / math.sqrt(L2)
            return d + (0 if 0 < t_ < 1 else 1e6)
        small = lambda i: 1 if N[i].kind in ('SimpleChemical', 'EmptySet') else 0
        def cycle(a, b):
            seen, todo = {b}, [b]
            for i in todo:
                for q, (cons, prod) in steps.items():
                    if q != p and i in cons:
                        todo += [j for j in prod if j not in seen]
                        seen |= prod
            return a not in seen
        def covered(a, b):
            mx, my = ((cen(a)[0] + cen(b)[0]) / 2, (cen(a)[1] + cen(b)[1]) / 2)
            return any(box[j][0] < mx < box[j][0] + box[j][2] and box[j][1] < my < box[j][1] + box[j][3]
                       for j in ents if j not in (a, b))
        bi, bo = min(((a, b) for a in range(len(ins)) for b in range(len(outs))),
                     key=lambda ab: (small(ins[ab[0]].source) + small(outs[ab[1]].target),
                                     covered(ins[ab[0]].source, outs[ab[1]].target),
                                     through(ins[ab[0]].source, outs[ab[1]].target) > 3,
                                     cycle(ins[ab[0]].source, outs[ab[1]].target),
                                     through(ins[ab[0]].source, outs[ab[1]].target), ab))
        ins = [ins[bi]] + ins[:bi] + ins[bi + 1:]; outs = [outs[bo]] + outs[:bo] + outs[bo + 1:]
        return ins, outs, mods, gates, reversible, c

    return {p: flows(p) for p in procs}


def twins(diagram, ents):
    N, E = diagram.nodes, diagram.arcs
    joins = {p: frozenset(e.target if e.source == p else e.source for e in E if p in (e.source, e.target) and e.head not in MODIFIERS
                          and (e.source in ents or e.target in ents)) for p, d in N.items() if d.kind in PROCESSES}
    return {p for p in joins if any(q != p and joins[q] == joins[p] for q in joins)}


def route(pts, c, box):
    return [q for q in pts if math.dist(q, c) > max(box[2], box[3]) + 3]


EPS = 20.0
MIN_LEN = 150.0


def off(p, a, b):
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    return abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / L


def _simplify(pts, eps):
    if len(pts) < 3:
        return pts
    d = [off(p, pts[0], pts[-1]) for p in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] < eps:
        return [pts[0], pts[-1]]
    return _simplify(pts[:i + 2], eps)[:-1] + _simplify(pts[i + 1:], eps)


def turn(route):
    if sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(route, route[1:])) < MIN_LEN:
        return None
    keep = _simplify(route, EPS)
    if len(keep) != 3:
        return None
    (sx, sy), (cx, cy) = keep[0], keep[1]
    return 'h' if abs(cy - sy) < abs(cx - sx) else 'v'


def unbent(run, tol=1):
    run = list(run)
    k = 1
    while k < len(run) - 1:
        (ax, ay), (bx, by), (qx, qy) = run[k - 1], run[k], run[k + 1]
        if off(run[k], run[k - 1], run[k + 1]) < tol and \
                min(ax, qx) - tol <= bx <= max(ax, qx) + tol and min(ay, qy) - tol <= by <= max(ay, qy) + tol:
            del run[k]
        else:
            k += 1
    return run


def exit_point(b, p, q):
    x, y, w, h = b
    t = 1.0
    for v, d, lo, hi in ((p[0], q[0] - p[0], x, x + w), (p[1], q[1] - p[1], y, y + h)):
        if d:
            t = min(t, ((hi if d > 0 else lo) - v) / d)
    return p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])


NEAR = 3.5
fixed = PROCESSES + ('Operator',)


def visible(m):
    def inside(q, d):
        b, e = d.box, 0.0 if d.kind in fixed else NEAR
        return b[0] - e < q[0] < b[0] + b[2] + e and b[1] - e < q[1] < b[1] + b[3] + e
    at = lambda d, p: (p[0] - centre(d)[0], p[1] - centre(d)[1])
    for a in m.arcs:
        S, T = m.nodes[a.source], m.nodes[a.target]
        s = (centre(S)[0] + a.source_at[0], centre(S)[1] + a.source_at[1])
        t = (centre(T)[0] + a.target_at[0], centre(T)[1] + a.target_at[1])
        pts = list(a.points)
        k = 0
        while k < len(pts) and inside(pts[k], S):
            k += 1
        if k:
            nxt = pts[k] if k < len(pts) else t
            if S.kind not in fixed and not inside(nxt, S) and off(exit_point(S.box, pts[k - 1], nxt), s, nxt) >= 1:
                s = exit_point(S.box, pts[k - 1], nxt)
                a.source_at = at(S, s)
            pts = pts[k:]
        k = len(pts)
        while k and inside(pts[k - 1], T):
            k -= 1
        if k < len(pts):
            prev = pts[k - 1] if k else s
            if T.kind not in fixed and not inside(prev, T) and off(exit_point(T.box, pts[k], prev), t, prev) >= 1:
                t = exit_point(T.box, pts[k], prev)
                a.target_at = at(T, t)
            pts = pts[:k]
        a.points = unbent([s] + pts + [t])[1:-1]
    return m


def bends(route):
    return _simplify(route, EPS)[1:-1]


def corner(a, b, way):
    return (b[0], a[1]) if way == 'h' else (a[0], b[1])


TOL = 3


def aligned(m, tol=TOL):
    end = lambda i, at: (centre(m.nodes[i])[0] + at[0], centre(m.nodes[i])[1] + at[1])
    lines = [[end(a.source, a.source_at)] + [list(p) for p in a.points] + [end(a.target, a.target_at)] for a in m.arcs]
    for ax in (0, 1):
        ends = sorted({P[k][ax] for P in lines for k in (0, -1)})
        free = []
        for P in lines:
            for k in range(1, len(P) - 1):
                near = [P[j][ax] for j in (k - 1, k + 1) if j in (0, len(P) - 1) and abs(P[j][ax] - P[k][ax]) <= tol]
                if near:
                    P[k][ax] = min(near, key=lambda v: abs(v - P[k][ax]))
                else:
                    free.append(P[k])
        free.sort(key=lambda p: p[ax])
        i = 0
        while i < len(free):
            j = i
            while j + 1 < len(free) and free[j + 1][ax] - free[i][ax] <= tol:
                j += 1
            run = free[i:j + 1]
            mid = run[len(run) // 2][ax]
            e = min(ends, key=lambda v: abs(v - mid), default=None)
            v = e if e is not None and all(abs(e - p[ax]) <= tol for p in run) else mid
            for p in run:
                p[ax] = v
            i = j + 1
    for a, P in zip(m.arcs, lines):
        keep = [P[k] for k in range(1, len(P) - 1)
                if not any(P[k - 1][x] == P[k][x] == P[k + 1][x] for x in (0, 1))]
        a.points = [tuple(p) for p in keep]
    return m


def at_centres(m):
    for d in m.nodes.values():
        if d.kind == 'SimpleChemical':
            W, H = SIZE['SimpleChemical']
            d.box = (d.box[0] + d.box[2] / 2 - W / 2, d.box[1] + d.box[3] / 2 - H / 2, W, H)
    for a in m.arcs:
        a.source_at = a.target_at = (0.0, 0.0)
    return m

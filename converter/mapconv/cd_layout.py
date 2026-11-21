import math
from dataclasses import dataclass
from . import layout, report
from .layout import main_lines

MARGIN = 40
NAME_ROOM = 14.0
SHIFT = 3.0
EDGE = 3.0
CHEMICAL = 40.0
SQUARE = {2: (0, -1), 3: (0, 1), 4: (-1, -1), 5: (1, -1), 6: (-1, 1), 7: (1, 1)}

QUARTER = {'NNE': (.75, 0), 'ENE': (1, .25), 'ESE': (1, .75), 'SSE': (.75, 1),
           'SSW': (.25, 1), 'WSW': (0, .75), 'WNW': (0, .25), 'NNW': (.25, 0)}
ANCHOR = dict(QUARTER, N=(.5, 0), NE=(1, 0), E=(1, .5), SE=(1, 1), S=(.5, 1), SW=(0, 1), W=(0, .5), NW=(0, 0))
ANGLE = {k: 22.5 * i for i, k in enumerate(['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW',
                                            'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE'])}


def anchor_point(box, side, circle=False, hexagon=False):
    x, y, w, h = box
    if not side:
        return (x + w / 2, y + h / 2)
    if circle:
        a = math.radians(ANGLE[side])
        return (x + w / 2 * (1 + math.cos(a)), y + h / 2 * (1 - math.sin(a)))
    if hexagon:
        i = min(h / 2, w / 2)
        fx, fy = ANCHOR[side]
        if fy in (0, 1):
            u = {0: i, .25: (w / 2 + i) / 2, .5: w / 2, .75: (w * 1.5 - i) / 2, 1: w - i}[fx]
            return (x + u, y + fy * h)
        d = i * (1 - 2 * min(fy, 1 - fy))
        return (x + fx * w + (d if fx == 0 else -d), y + fy * h)
    fx, fy = ANCHOR[side]
    return (x + fx * w, y + fy * h)


def square_point(sq, f, a, c, r=5):
    return (sq[0] + r * (a * f[0] - c * f[1]), sq[1] + r * (a * f[1] + c * f[0]))


def meet(M, T, way=None):
    dx, dy = (T[0] - M[0]) * (way != 'v'), (T[1] - M[1]) * (way != 'h')
    if abs(dy) >= abs(dx):
        return 'N' if dy < 0 else 'S'
    return 'ESE' if dx > 0 else 'WSW'

def to_frame(a, b, p):
    ex = (b[0] - a[0], b[1] - a[1]); ey = (-ex[1], ex[0])
    det = ex[0] * ey[1] - ex[1] * ey[0]
    q = (p[0] - a[0], p[1] - a[1])
    return ((q[0] * ey[1] - q[1] * ey[0]) / det, (ex[0] * q[1] - ex[1] * q[0]) / det)


def from_frame(a, b, p):
    ex = (b[0] - a[0], b[1] - a[1]); ey = (-ex[1], ex[0])
    return (a[0] + p[0] * ex[0] + p[1] * ey[0], a[1] + p[0] * ex[1] + p[1] * ey[1])

def boxes(N, ents, members):
    x0 = min(d.box[0] for d in N.values()) - MARGIN
    y0 = min(d.box[1] for d in N.values()) - MARGIN
    box = {i: (d.box[0] - x0, d.box[1] - y0, d.box[2], d.box[3]) for i, d in N.items()}
    W = max(b[0] + b[2] for b in box.values()) + MARGIN
    H = max(b[1] + b[3] for b in box.values()) + MARGIN
    for i, d in N.items():
        if d.kind == 'SimpleChemical':
            x, y, w, h = box[i]
            box[i] = (x + w / 2 - CHEMICAL / 2, y + h / 2 - CHEMICAL / 2, CHEMICAL, CHEMICAL)
    def low(j):
        x, y, w, h = box[j]
        n = N[j].count if j in ents else 1
        return y + h + max([0.0] + [8.5 for s in N[j].states if s[2] > 0.45] + [6.0] * (n > 1))
    for c in sorted(members, key=lambda c: len(descendants(c, members))):
        inner = descendants(c, members)
        x, y, w, h = box[c]
        need = max(low(j) for j in inner) + NAME_ROOM - (y + h)
        if need > 0:
            up = min(need, max(0.0, min(box[j][1] for j in inner) - y - 8))
            for j in inner:
                box[j] = (box[j][0], box[j][1] - up) + box[j][2:]
            box[c] = (x, y, w, h + need - up)
    return box, (x0, y0), (W, H)


@dataclass
class Drawing:
    box: dict
    front: dict
    size: tuple
    cen: object
    lines: object
    geometry: object
    modifier: object
    side: object
    end: object
    yed: object


def draw(diagram, ents, members, label, advanced, held=False):
    N = diagram.nodes
    box, (x0, y0), size = boxes(N, ents, members)
    cen = lambda i: (box[i][0] + box[i][2] / 2, box[i][1] + box[i][3] / 2)
    lines = lambda: main_lines(diagram, box, ents, (x0, y0))

    front = {}
    for i, d in ents.items():
        k = 6 if d.count > 1 and d.kind != 'SimpleChemical' else 0
        front[i] = (box[i][0], box[i][1], box[i][2] - k, box[i][3] - k)

    twins = layout.twins(diagram, ents)
    yed = lambda pts: [(q[0] - x0, q[1] - y0) for q in pts]

    route = lambda p, pts: layout.route(yed(pts), cen(p), box[p])

    def off_line(i, a, T):
        A, C = anchor_point(box[i], a, N[i].kind == 'SimpleChemical', N[i].kind == 'Phenotype'), cen(i)
        return abs((T[0] - C[0]) * (A[1] - C[1]) - (T[1] - C[1]) * (A[0] - C[0])) / (math.dist(C, T) or 1) > 2

    def nearest(i, at):
        u, v = at[0] * box[i][2] / N[i].box[2], at[1] * box[i][3] / N[i].box[3]
        pt = lambda a: anchor_point(box[i], a, N[i].kind == 'SimpleChemical', N[i].kind == 'Phenotype')
        a = min(ANCHOR, key=lambda a: math.dist(pt(a), (cen(i)[0] + u, cen(i)[1] + v)))
        if math.dist(pt(a), (cen(i)[0] + u, cen(i)[1] + v)) >= math.hypot(u, v):
            return None
        return {'E': 'ESE', 'W': 'WSW'}.get(a, a) if N[i].kind == 'SimpleChemical' else a

    def level(e, c):
        q = yed(e.points)[-1] if e.points else \
            (cen(e.source)[0] + e.source_at[0], cen(e.source)[1] + e.source_at[1])
        return any(min(abs(q[0] - c[0] - t[0]), abs(q[1] - c[1] - t[1])) <= 5 for t in (e.target_at, (0, 0)))

    def reach(s, v, b):
        t0, t1 = 0.0, math.inf
        for a in (0, 1):
            lo, hi = b[a] - EDGE, b[a] + b[a + 2] + EDGE
            if abs(v[a]) < 1e-12:
                if not lo <= s[a] <= hi: return math.inf
            else:
                ta, tb = sorted(((lo - s[a]) / v[a], (hi - s[a]) / v[a]))
                t0, t1 = max(t0, ta), min(t1, tb)
        return t0 if t0 <= t1 else math.inf

    def geometry(p, fl, place=True):
        ins, outs, mods, gates, reversible, c = fl
        r_, q_ = ins[0].source, outs[0].target
        ra = qa = None
        rb = layout.bends([cen(r_)] + route(p, ins[0].points) + [c]) if advanced else []
        qb = layout.bends([c] + route(p, outs[0].points) + [cen(q_)]) if advanced else []
        if not rb + qb and p in twins:
            (rx_, ry_), (qx_, qy_) = cen(r_), cen(q_)
            side = (qx_ - rx_) * (c[1] - ry_) - (qy_ - ry_) * (c[0] - rx_)
            if abs(qx_ - rx_) >= abs(qy_ - ry_):
                v = 'N' if (side < 0) == (qx_ > rx_) else 'S'
                fr, fq = ('E', 'W') if qx_ > rx_ else ('W', 'E')
                ra, qa = fr + v + fr, fq + v + fq
            else:
                v = 'W' if (side > 0) == (qy_ > ry_) else 'E'
                fr, fq = ('S', 'N') if qy_ > ry_ else ('N', 'S')
                ra, qa = fr + fr + v, fq + fq + v
        twin = bool(ra)
        wr = layout.turn([cen(r_)] + yed(ins[0].points) + [c])
        wq = layout.turn([cen(q_)] + yed(outs[0].points)[::-1] + [c])
        if advanced and not twin:
            other = {'h': 'v', 'v': 'h'}
            ra = nearest(r_, ins[0].source_at) or (meet(cen(r_), c, wr or (other[wq] if wq else None)) if N[r_].kind == 'SimpleChemical' else None)
            qa = nearest(q_, outs[0].target_at) or (meet(cen(q_), c, wq or (other[wr] if wr else None)) if N[q_].kind == 'SimpleChemical' else None)
            ra = ra if ra and off_line(r_, ra, (rb + [c])[0]) else None
            qa = qa if qa and off_line(q_, qa, (qb[::-1] + [c])[0]) else None
        under = None
        if held and not twin and not rb + qb:
            ps = [(cen(r_)[0] + ins[0].source_at[0], cen(r_)[1] + ins[0].source_at[1])] + yed(ins[0].points + outs[0].points) + \
                [c, (cen(q_)[0] + outs[0].target_at[0], cen(q_)[1] + outs[0].target_at[1])]
            for ax in (0, 1):
                if max(q[ax] for q in ps) - min(q[ax] for q in ps) < 1 and abs(cen(r_)[ax] - cen(q_)[ax]) > 0.5:
                    for i, at, o, other in ((q_, outs[0].target_at, ins[0].source_at, r_), (r_, ins[0].source_at, outs[0].target_at, q_)):
                        v = cen(other)[1 - ax]
                        x, w = box[i][1 - ax], box[i][3 - ax]
                        H = tuple(cen(other)[ax] if a == ax else (x - EDGE if v < x else x + w + EDGE) for a in (0, 1))
                        if abs(o[ax]) < 0.5 and abs(at[ax]) > SHIFT and box[i][ax] < H[ax] < box[i][ax] + box[i][ax + 2]:
                            under = (i, H)
            if under:
                ra, qa = (None, qa) if under[0] == r_ else (ra, None)
        A = anchor_point(front[r_] if ra else box[r_], ra, N[r_].kind == 'SimpleChemical', N[r_].kind == 'Phenotype')
        B = anchor_point(front[q_] if qa else box[q_], qa, N[q_].kind == 'SimpleChemical', N[q_].kind == 'Phenotype')
        pts, k, corner = rb + qb, len(rb), False
        for j, (i, a, P) in ((0, (r_, ra, A)), (-1, (q_, qa, B))):
            if pts and a and N[i].kind == 'SimpleChemical':
                q, C = pts[j], cen(i)
                ax = 1 if abs(q[0] - C[0]) >= abs(q[1] - C[1]) else 0
                if abs(q[ax] - C[ax]) < 1:
                    pts[j] = (q[0], P[1]) if ax else (P[0], q[1])
        if under:
            pts, k = [under[1]], int(under[0] == r_)
        bend = (layout.corner(A, B, wr) if wr else layout.corner(B, A, wq)) if bool(wr) != bool(wq) and not twin and not under else None
        if bend and (not pts or len(pts) == 1 and math.dist(bend, pts[0]) < layout.EPS):
            corner = min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (A, B)) >= layout.EPS
            pts, k = ([bend], 1 if wr else 0) if corner else ([], 0)
        run = [A] + pts + [B]
        P, Q = run[k], run[k + 1]
        sq = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
        L = math.hypot(Q[0] - P[0], Q[1] - P[1])
        f = ((Q[0] - P[0]) / L, (Q[1] - P[1]) / L)
        ep = [to_frame(A, B, q) for q in pts]
        u = ((c[0] - P[0]) * f[0] + (c[1] - P[1]) * f[1]) / L
        across = abs((c[0] - P[0]) * f[1] - (c[1] - P[1]) * f[0])
        if held and across < 12 and abs(u - 0.5) * L > SHIFT and 0.1 < u < 0.9:
            at = (P[0] + u * L * f[0], P[1] + u * L * f[1])
            ds = [min(min(u, 1 - u) / 2 * L, *(reach(at, (w * f[0], w * f[1]), box[i]) for i in (r_, q_))) for w in (-1, 1)]
            if min(ds) >= 1:
                sq = at
                split = [to_frame(A, B, (sq[0] + d * f[0], sq[1] + d * f[1])) for d in (-min(ds), min(ds))]
                ep, k = ep[:k] + split + ep[k:], k + 1
        off = lambda m: min(abs(cen(m)[0] - sq[0]), abs(cen(m)[1] - sq[1]))
        if advanced and not held and place and not corner and any(level(e, c) and off(e.source) > 0.5 for e in mods + gates):
            if across < 3 and abs(u - 0.5) * L > 3 and 0.1 < u < 0.9:
                at = (P[0] + u * L * f[0], P[1] + u * L * f[1])
                d = min(min(u, 1 - u) / 2 * L, *(reach(at, (w * f[0], w * f[1]), box[i]) for w in (-1, 1) for i in (r_, q_)))
                if d >= 1:
                    sq, h = at, min(u, 1 - u) / 2
                    h = h if d >= h * L else d / L
                    split = [(u - h, 0.0), (u + h, 0.0)] if not pts else \
                        [to_frame(A, B, (sq[0] + t * f[0], sq[1] + t * f[1])) for t in (-h * L, h * L)]
                    ep, k = ep[:k] + split + ep[k:], k + 1
        return dict(r=r_, q=q_, ra=ra, qa=qa, A=A, B=B, ep=ep, k=k, sq=sq, f=f)

    def side(g, pt):
        f, sq = g['f'], g['sq']
        return 2 if f[0] * (pt[1] - sq[1]) - f[1] * (pt[0] - sq[0]) < 0 else 3

    def lane(m, M, T, e):
        pts = yed(e.points)
        if not pts:
            if layout.off((M[0] + e.source_at[0], M[1] + e.source_at[1]), M, T) <= 2:
                return None
            x, y, w, h = box[m]
            return layout.unbent([M, (x + w + 1 if T[0] > M[0] else x - 1, T[1]), T])[1:-1] \
                if abs(M[1] + e.source_at[1] - T[1]) <= 5 else None
        chain = [M] + pts
        for i in range(1, len(chain)):
            a, b = chain[i - 1], chain[i]
            chain[i] = (b[0], a[1]) if abs(b[1] - a[1]) < abs(b[0] - a[0]) else (a[0], b[1])
        last = chain[-1]
        chain[-1] = (last[0], T[1]) if abs(T[1] - last[1]) < abs(T[0] - last[0]) else (T[0], last[1])
        if len(chain) > 2:
            a, b = chain[-2], chain[-1]
            if abs(a[0] - chain[-3][0]) < 0.5 and abs(a[1] - b[1]) < abs(a[0] - b[0]):
                chain[-2] = (a[0], b[1])
        return layout.unbent(chain + [T])[1:-1]

    def crosses(a, b, r):
        t0, t1 = 0.0, 1.0
        for p_, q_ in ((a[0] - b[0], a[0] - r[0]), (b[0] - a[0], r[0] + r[2] - a[0]),
                       (a[1] - b[1], a[1] - r[1]), (b[1] - a[1], r[1] + r[3] - a[1])):
            if p_ == 0:
                if q_ < 0: return False
            elif p_ < 0: t0 = max(t0, q_ / p_)
            else: t1 = min(t1, q_ / p_)
        return t0 < t1

    def target(g, e, pt, many):
        o, h, f = e.target_at, N[e.target].box[2] / 2, g['f']
        if advanced and many and math.hypot(*o) > 2:
            a, c = (o[0] * f[0] + o[1] * f[1]) / h, (o[1] * f[0] - o[0] * f[1]) / h
            if abs(c) > 0.5:
                return min(SQUARE, key=lambda i: math.dist(SQUARE[i], (a, c)))
        return side(g, pt)

    def attach(g, i):
        return square_point(g['sq'], g['f'], *SQUARE[i])

    def modifier(p, g, e, many):
        m = e.source; M = cen(m)
        i = target(g, e, (yed(e.points)[-1] if advanced and e.points else M), many)
        T = attach(g, i)
        at = advanced and not e.points and N[m].kind != 'SimpleChemical' and nearest(m, e.source_at)
        if at and off_line(m, at, T) and abs(M[1] + e.source_at[1] - cen(p)[1]) > 5:
            M = anchor_point(front[m], at, hexagon=N[m].kind == 'Phenotype')
        else:
            at = None
        pts = advanced and not at and lane(m, M, T, e)
        if advanced and N[m].kind == 'SimpleChemical':
            at = meet(M, pts[0] if pts else T)
            M = anchor_point(box[m], at, True)
            if pts:
                q = pts[0]
                pts[0] = (q[0], M[1]) if at in ('ESE', 'WSW') else (M[0], q[1])
        if pts:
            run = [M] + pts + [T]
            for j in ents:
                if j != m and N[j].parent not in ents and m not in descendants(j, members) and \
                        any(crosses(a, b, box[j]) for a, b in zip(run, run[1:])):
                    report.say('warning', '%s: the arc from %s runs through %s' % (p, label[m] or m, label[j] or j))
        else:
            w = layout.turn([cen(m)] + route(p, e.points) + [cen(p)])
            bend = layout.corner(M, T, w) if w else None
            if bend and min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (M, T)) < layout.EPS:
                bend = None
            pts = [bend] if bend else []
        return i, M, T, at, pts

    end = lambda g, e, M, many: attach(g, target(g, e, M, many))
    return Drawing(box, front, size, cen, lines, geometry, modifier, side, end, yed)


def descendants(i, members):
    out = []
    for m in members.get(i, []):
        out += [m] + descendants(m, members)
    return out

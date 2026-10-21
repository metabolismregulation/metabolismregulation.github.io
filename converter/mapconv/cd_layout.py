# The CellDesigner adapter (restructuring step 4, 2026-10-19): where every line, square and point
# goes as CellDesigner draws it, before the file is written. The boxes in CellDesigner's frame and
# sizes, the tidy moves (on unless the user forbids moving nodes), each reaction's main line and
# each modifier arc's end, anchor and edit points.
import math
from dataclasses import dataclass
from . import cd_straighten, layout, report
from .layout import main_lines

MARGIN = 40
NAME_ROOM = 14.0  # below the members' outline in a complex, for its name (as the yEd packing rule)
CHEMICAL = 36.0  # metabolites are drawn as circles of this diameter, centred on the yEd node
ALIGN = 15.0  # largest move of a modifier onto its square (px)
# the points of the process square a modifier can end at (targetLineIndex -1,i): (along the flow,
# to its right) in half square sizes (MINERVA's getAnchorPointOnReactionRect; the user's PDH edit
# has 6 and 7)
SQUARE = {2: (0, -1), 3: (0, 1), 4: (-1, -1), 5: (1, -1), 6: (-1, 1), 7: (1, 1)}

# CellDesigner's anchor points on a node box (Startup Guide, Appendix 2.3; cd2sbgnml): the
# quarter points (written for two processes on the same two species), the sides' middles and
# the corners
QUARTER = {'NNE': (.75, 0), 'ENE': (1, .25), 'ESE': (1, .75), 'SSE': (.75, 1),
           'SSW': (.25, 1), 'WSW': (0, .75), 'WNW': (0, .25), 'NNW': (.25, 0)}
ANCHOR = dict(QUARTER, N=(.5, 0), NE=(1, 0), E=(1, .5), SE=(1, 1), S=(.5, 1), SW=(0, 1), W=(0, .5), NW=(0, 0))
# on an ellipse the points sit at 22.5 degree steps (checked through MINERVA; cd2sbgnml)
ANGLE = {k: 22.5 * i for i, k in enumerate(['E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW',
                                            'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE'])}


def anchor_point(box, side, circle=False):
    x, y, w, h = box
    if not side:  # no anchor: the centre
        return (x + w / 2, y + h / 2)
    if circle:
        a = math.radians(ANGLE[side])
        return (x + w / 2 * (1 + math.cos(a)), y + h / 2 * (1 - math.sin(a)))
    fx, fy = ANCHOR[side]
    return (x + fx * w, y + fy * h)


def square_point(sq, f, a, c, r=5):
    # a point of the process square at sq (half size r), flow f: a along the flow, c to its right
    return (sq[0] + r * (a * f[0] - c * f[1]), sq[1] + r * (a * f[1] + c * f[0]))


def meet(M, T, way=None):
    # the anchor where a line from a metabolite circle at M towards T leaves it, its name across
    # the middle: the top or bottom, or the lower quarter of a side (way 'h' or 'v': its first leg)
    dx, dy = (T[0] - M[0]) * (way != 'v'), (T[1] - M[1]) * (way != 'h')
    if abs(dy) >= abs(dx):
        return 'N' if dy < 0 else 'S'
    return 'ESE' if dx > 0 else 'WSW'

def to_frame(a, b, p):
    # p in CellDesigner's edit point frame: origin a, x axis b - a, y axis the
    # x axis turned 90 degrees (screen coordinates)
    ex = (b[0] - a[0], b[1] - a[1]); ey = (-ex[1], ex[0])
    det = ex[0] * ey[1] - ex[1] * ey[0]
    q = (p[0] - a[0], p[1] - a[1])
    return ((q[0] * ey[1] - q[1] * ey[0]) / det, (ex[0] * q[1] - ex[1] * q[0]) / det)


def from_frame(a, b, p):
    # inverse of to_frame: a point given in the edit point frame a -> b
    ex = (b[0] - a[0], b[1] - a[1]); ey = (-ex[1], ex[0])
    return (a[0] + p[0] * ex[0] + p[1] * ey[0], a[1] + p[0] * ex[1] + p[1] * ey[1])

def boxes(N, ents, members):
    # (box, origin, size): every node's box with the map starting at MARGIN, origin what was taken
    # off the map's coordinates, size the canvas; ents the entity ids, members complex -> members
    x0 = min(d.box[0] for d in N.values()) - MARGIN
    y0 = min(d.box[1] for d in N.values()) - MARGIN
    box = {i: (d.box[0] - x0, d.box[1] - y0, d.box[2], d.box[3]) for i, d in N.items()}
    W = max(b[0] + b[2] for b in box.values()) + MARGIN
    H = max(b[1] + b[3] for b in box.values()) + MARGIN
    # metabolites: circles, centre kept (the map size above keeps room for their labels)
    for i, d in N.items():
        if d.kind == 'SimpleChemical':
            x, y, w, h = box[i]
            box[i] = (x + w / 2 - CHEMICAL / 2, y + h / 2 - CHEMICAL / 2, CHEMICAL, CHEMICAL)
    # multimers of more than 2: the box grows 6 per extra unit, top left kept (yEd draws N:2's size)
    for i in ents:
        n = N[i].count
        if n > 2:
            x, y, w, h = box[i]
            box[i] = (x, y, w + 6 * (n - 2), h + 6 * (n - 2))
    # CellDesigner writes a complex's name at the bottom inside it: its members move up to leave
    # NAME_ROOM below their outline (a state variable on the bottom edge 8.5 px below the node,
    # yEd's second shape of a multimer 6 px), as far as the space above allows, and the complex
    # grows down for the rest; a GraphML packed by the skill's complex_pack.py has the room and
    # keeps its geometry (user, 2026-10-18; first 25 px from the node, pyrimidine edits 2026-10-16);
    # inner complexes first
    def low(j):
        x, y, w, h = box[j]
        n = N[j].count if j in ents else 1
        return y + h + max([0.0] + [8.5 for s in N[j].states if s[2] > 0.45] + [6.0 * (3 - n)] * (n > 1))
    for c in sorted(members, key=lambda c: len(cd_straighten.descendants(c, members))):
        inner = cd_straighten.descendants(c, members)
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
    box: dict       # id -> (x, y, w, h), CellDesigner's frame
    front: dict     # entity -> the box its lines meet (a multimer's front shape)
    size: tuple     # the canvas
    cen: object     # id -> the centre of its box
    lines: object   # () -> each process's arcs, the main reactant and product first (layout.py)
    geometry: object  # (process, its lines) -> its main line: ends, anchors, edit points, square
    modifier: object  # (process, main line, arc, several regulators) -> (square point, M, T, anchor, bends)
    side: object    # (main line, point) -> the side of the square facing the point


def draw(diagram, ents, members, label, advanced, move):
    # ents the entity ids, members complex -> members, label entity -> name (for the messages);
    # advanced: the advanced layout; move: the tidy moves allowed
    N = diagram.nodes
    comps = {i for i, d in N.items() if d.kind == 'Compartment'}
    def comp_of(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return q
    box, (x0, y0), size = boxes(N, ents, members)
    cen = lambda i: (box[i][0] + box[i][2] / 2, box[i][1] + box[i][3] / 2)
    # each process's arcs, the main reactant and product first (layout.py), on the boxes as they are
    lines = lambda: main_lines(diagram, box, ents, (x0, y0))

    # straighten main lines a few pixels off the vertical or horizontal (cd_straighten.py)
    def said_move(j, dx, dy, why):  # every tidy move in the messages (user, 2026-10-19)
        way = ' and '.join('%.0f px %s' % (abs(v), w[v > 0]) for v, w in ((dx, ('left', 'right')), (dy, ('up', 'down'))) if abs(v) >= 0.05)
        if way:
            report.say('changed', '%s moved %s: %s' % (label[j] or j, way, why))
    if move:
        for j, (dx, dy) in cd_straighten.straighten(box, [(f[0][0].source, f[1][0].target) for f in lines().values() if f], members).items():
            if N[j].parent not in ents:  # a member moves with its complex
                said_move(j, dx, dy, 'its main line straightened')
    # anchor points sit on the front shape of a multimer: CellDesigner draws it 6 smaller in
    # width and height (the user's glycolysis file: PFKFB2 dimer)
    front = {}
    for i, d in ents.items():
        k = 6 * (d.count - 1) if d.kind != 'SimpleChemical' else 0
        front[i] = (box[i][0], box[i][1], box[i][2] - k, box[i][3] - k)

    twins = layout.twins(diagram, ents)
    yed = lambda pts: [(q[0] - x0, q[1] - y0) for q in pts]  # yEd points in the map's frame here

    route = lambda p, pts: layout.route(yed(pts), cen(p), box[p])

    def off_line(i, a, T):  # anchor a of entity i moves its line to T by more than 2 px
        A, C = anchor_point(box[i], a, N[i].kind == 'SimpleChemical'), cen(i)
        return abs((T[0] - C[0]) * (A[1] - C[1]) - (T[1] - C[1]) * (A[0] - C[0])) / (math.dist(C, T) or 1) > 2

    def nearest(i, at):
        # the anchor nearest to where an arc meets entity i (scaled to its box here), if nearer than
        # its centre; on a metabolite circle not E or W, where the name is: ESE, WSW
        u, v = at[0] * box[i][2] / N[i].box[2], at[1] * box[i][3] / N[i].box[3]
        pt = lambda a: anchor_point(box[i], a, N[i].kind == 'SimpleChemical')
        a = min(ANCHOR, key=lambda a: math.dist(pt(a), (cen(i)[0] + u, cen(i)[1] + v)))
        if math.dist(pt(a), (cen(i)[0] + u, cen(i)[1] + v)) >= math.hypot(u, v):
            return None
        return {'E': 'ESE', 'W': 'WSW'}.get(a, a) if N[i].kind == 'SimpleChemical' else a

    def level(e, c):
        # a modifier arc that reaches the process at c straight across in yEd (5 px), in line with
        # its port or its centre (PD02 eicosanoids: an arc from above the process to a corner)
        q = yed(e.points)[-1] if e.points else \
            (cen(e.source)[0] + e.source_at[0], cen(e.source)[1] + e.source_at[1])
        return any(min(abs(q[0] - c[0] - t[0]), abs(q[1] - c[1] - t[1])) <= 5 for t in (e.target_at, (0, 0)))

    def geometry(p, fl, place=True):
        # the main line of process p: its ends, anchors, bend, the square and the flow direction;
        # place: the square where yEd has it, where a modifier needs it (else midway)
        ins, outs, mods, gates, reversible, c = fl
        r_, q_ = ins[0].source, outs[0].target
        ra = qa = None  # line ends at the centres
        # advanced: the significant bends of the yEd route (a Z, a detour round other nodes; PD02
        # eicosanoids, 2026-10-16)
        rb = layout.bends([cen(r_)] + route(p, ins[0].points) + [c]) if advanced else []
        qb = layout.bends([c] + route(p, outs[0].points) + [cen(q_)]) if advanced else []
        if not rb + qb and p in twins:
            # two processes on the same two species, drawn straight (user's edit of mevalonate,
            # HMGCR): each a straight line between quarter points on the facing sides, on the side
            # of the line between the centres where yEd has the process (upper/lower, left/right)
            (rx_, ry_), (qx_, qy_) = cen(r_), cen(q_)
            side = (qx_ - rx_) * (c[1] - ry_) - (qy_ - ry_) * (c[0] - rx_)  # >0: process right of r->q
            if abs(qx_ - rx_) >= abs(qy_ - ry_):  # side by side: E/W faces, upper or lower quarter
                v = 'N' if (side < 0) == (qx_ > rx_) else 'S'
                fr, fq = ('E', 'W') if qx_ > rx_ else ('W', 'E')
                ra, qa = fr + v + fr, fq + v + fq
            else:  # stacked: N/S faces, left or right quarter
                v = 'W' if (side > 0) == (qy_ > ry_) else 'E'
                fr, fq = ('S', 'N') if qy_ > ry_ else ('N', 'S')
                ra, qa = fr + fr + v, fq + fq + v
        twin = bool(ra)
        # a significant bend on the main line: one long L on the reactant arc or on the product arc
        # (with the bend at the process's port: it says from which side the line comes in;
        # user's iNOS v08 edit, ASL and ASS1 as L shapes)
        wr = layout.turn([cen(r_)] + yed(ins[0].points) + [c])
        wq = layout.turn([cen(q_)] + yed(outs[0].points)[::-1] + [c])
        if advanced and not twin:
            # a line meets an entity where the yEd arc meets its border (a CellDesigner anchor read
            # back); else a metabolite circle where its name is not: N, S, ESE or WSW, by the way
            # it leaves (the L's first leg, else towards the process; user's PD02 eicosanoids)
            other = {'h': 'v', 'v': 'h'}
            ra = nearest(r_, ins[0].source_at) or (meet(cen(r_), c, wr or (other[wq] if wq else None)) if N[r_].kind == 'SimpleChemical' else None)
            qa = nearest(q_, outs[0].target_at) or (meet(cen(q_), c, wq or (other[wr] if wr else None)) if N[q_].kind == 'SimpleChemical' else None)
            # only where they change the line (user's edit of pyrimidine v06: side middles on the
            # line's own axis removed)
            ra = ra if ra and off_line(r_, ra, (rb + [c])[0]) else None
            qa = qa if qa and off_line(q_, qa, (qb[::-1] + [c])[0]) else None
        A = anchor_point(front[r_] if ra else box[r_], ra, N[r_].kind == 'SimpleChemical')
        B = anchor_point(front[q_] if qa else box[q_], qa, N[q_].kind == 'SimpleChemical')
        # edit points: one long L (both layouts); in the advanced layout else the route's bends
        pts, k, corner = rb + qb, len(rb), False
        bend = (layout.corner(A, B, wr) if wr else layout.corner(B, A, wq)) if bool(wr) != bool(wq) and not twin else None
        if bend and (not pts or len(pts) == 1 and math.dist(bend, pts[0]) < layout.EPS):  # else a slanting leg (PD02)
            corner = min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (A, B)) >= layout.EPS
            pts, k = ([bend], 1 if wr else 0) if corner else ([], 0)  # else the ends are already in line
        # the square (CellDesigner: midway on segment k; after the corner when yEd has the
        # process on the arc that bends from the reactant) and the flow direction through it
        run = [A] + pts + [B]
        P, Q = run[k], run[k + 1]
        sq = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
        L = math.hypot(Q[0] - P[0], Q[1] - P[1])
        f = ((Q[0] - P[0]) / L, (Q[1] - P[1]) / L)
        ep = [to_frame(A, B, q) for q in pts]
        off = lambda m: min(abs(cen(m)[0] - sq[0]), abs(cen(m)[1] - sq[1]))  # a modifier off its square
        if advanced and place and not corner and any(level(e, c) and off(e.source) > 0.5 for e in mods + gates):
            # a modifier (or logic gate) straight across in yEd that could not be moved onto the midway square
            # (more than ALIGN px, or other squares it reaches): the square where yEd has the
            # process, if that is on its segment. Two edit points half way to the nearer end on
            # either side, so the arcs keep their antennas (user's pyrimidine v07 edit, CAD)
            u = ((c[0] - P[0]) * f[0] + (c[1] - P[1]) * f[1]) / L
            across = abs((c[0] - P[0]) * f[1] - (c[1] - P[1]) * f[0])
            if across < 3 and abs(u - 0.5) * L > 3 and 0.1 < u < 0.9:
                sq = (P[0] + u * L * f[0], P[1] + u * L * f[1])
                h = min(u, 1 - u) / 2
                split = [(u - h, 0.0), (u + h, 0.0)] if not pts else \
                    [to_frame(A, B, (sq[0] + d * f[0], sq[1] + d * f[1])) for d in (-h * L, h * L)]
                ep, k = ep[:k] + split + ep[k:], k + 1
        return dict(r=r_, q=q_, ra=ra, qa=qa, A=A, B=B, ep=ep, k=k, sq=sq, f=f)

    def side(g, pt):  # the side of the square facing a point: 2 left of the flow, 3 right
        f, sq = g['f'], g['sq']
        return 2 if f[0] * (pt[1] - sq[1]) - f[1] * (pt[0] - sq[0]) < 0 else 3

    def lane(m, M, T, e):
        # advanced layout: the edit points of a modifier arc from M to T as yEd draws it, or
        # None for a straight arc from the centre
        pts = yed(e.points)
        if not pts:
            if layout.off((M[0] + e.source_at[0], M[1] + e.source_at[1]), M, T) <= 2:
                return None  # the yEd arc runs as from the centre
            # an off-centre start at the square's height: straight across, from just outside the node
            x, y, w, h = box[m]
            return layout.unbent([M, (x + w + 1 if T[0] > M[0] else x - 1, T[1]), T])[1:-1] \
                if abs(M[1] + e.source_at[1] - T[1]) <= 5 else None
        # the yEd bends, each segment made horizontal or vertical, the last one ending on the square
        chain = [M] + pts
        for i in range(1, len(chain)):
            a, b = chain[i - 1], chain[i]
            chain[i] = (b[0], a[1]) if abs(b[1] - a[1]) < abs(b[0] - a[0]) else (a[0], b[1])
        last = chain[-1]
        chain[-1] = (last[0], T[1]) if abs(T[1] - last[1]) < abs(T[0] - last[0]) else (T[0], last[1])
        if len(chain) > 2:  # the point before keeps its segment straight
            a, b = chain[-2], chain[-1]
            if abs(a[0] - chain[-3][0]) < 0.5 and abs(a[1] - b[1]) < abs(a[0] - b[0]):
                chain[-2] = (a[0], b[1])
        return layout.unbent(chain + [T])[1:-1]

    def crosses(a, b, r):  # the segment a-b runs through the box r (Liang-Barsky)
        t0, t1 = 0.0, 1.0
        for p_, q_ in ((a[0] - b[0], a[0] - r[0]), (b[0] - a[0], r[0] + r[2] - a[0]),
                       (a[1] - b[1], a[1] - r[1]), (b[1] - a[1], r[1] + r[3] - a[1])):
            if p_ == 0:
                if q_ < 0: return False
            elif p_ < 0: t0 = max(t0, q_ / p_)
            else: t1 = min(t1, q_ / p_)
        return t0 < t1

    def target(g, e, pt, many):
        # the point of the square an arc from pt ends at: the side facing pt; in the advanced layout,
        # where several arcs regulate the process and yEd ends this one off its centre, the point
        # nearest that yEd port, so the arcs stay apart (user, PDH 2026-10-17)
        o, h, f = e.target_at, N[e.target].box[2] / 2, g['f']
        if advanced and many and math.hypot(*o) > 2:
            a, c = (o[0] * f[0] + o[1] * f[1]) / h, (o[1] * f[0] - o[0] * f[1]) / h
            if abs(c) > 0.5:
                return min(SQUARE, key=lambda i: math.dist(SQUARE[i], (a, c)))
        return side(g, pt)

    def attach(g, i):  # the square's point i (targetLineIndex -1,i)
        return square_point(g['sq'], g['f'], *SQUARE[i])

    def overlap(a, b):
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

    def shift(m, ax, d, ends, why):
        # move entity m by d along axis ax, with the entities joined to it by main lines straight
        # on that axis (and their complex members), if all stay in their compartments and overlap
        # nothing (user's pyrimidine v08 edit: ERK1/2 and its phosphorylation moved together)
        if not move:
            return
        group = [m]
        for j in group:
            group += [b if a == j else a for a, b in ends if j in (a, b) and abs(cen(a)[ax] - cen(b)[ax]) < 1
                      and (b if a == j else a) not in group]
        moved = group + [i for j in group for i in cd_straighten.descendants(j, members)]
        new = {j: tuple(v + (d if k == ax else 0) for k, v in enumerate(box[j])) for j in moved}
        inside = lambda j, cm: box[cm][0] <= new[j][0] and new[j][0] + new[j][2] <= box[cm][0] + box[cm][2] \
            and box[cm][1] <= new[j][1] and new[j][1] + new[j][3] <= box[cm][1] + box[cm][3]
        if any(comp_of(j) and not inside(j, comp_of(j)) for j in group):
            return
        if any(overlap(new[g_], box[j]) for g_ in group for j in ents if j not in moved and N[j].parent not in moved
               and g_ not in cd_straighten.descendants(j, members)):
            return
        box.update(new)
        for j in moved:
            front[j] = (box[j][0], box[j][1]) + front[j][2:]
        for j in group:
            said_move(j, d * (ax == 0), d * (ax == 1), why)

    # a main line yEd draws level into a larger node off its centre (an end point beside the
    # centre): CellDesigner aims at the centre, so the other end moves onto its centre line
    # (user's iNOS v07 and v08 edits: CaM moved 25 px for CaM -> CaM:iNOS)
    fls = {p: fl for p, fl in lines().items() if fl}
    ends = [(fl[0][0].source, fl[1][0].target) for fl in fls.values()]
    for p, (ins, outs, mods, gates, reversible, c) in fls.items():
        r_, q_ = ins[0].source, outs[0].target
        pts = [(cen(r_)[0] + ins[0].source_at[0], cen(r_)[1] + ins[0].source_at[1])] + \
            yed(ins[0].points + outs[0].points) + [c] + \
            [(cen(q_)[0] + outs[0].target_at[0], cen(q_)[1] + outs[0].target_at[1])]
        for ax in (0, 1):
            if max(q[ax] for q in pts) - min(q[ax] for q in pts) < 1 and abs(cen(r_)[ax] - cen(q_)[ax]) > 0.5:
                if abs(ins[0].source_at[ax]) < 0.5 <= abs(outs[0].target_at[ax]):
                    shift(r_, ax, cen(q_)[ax] - cen(r_)[ax], ends, 'onto the centre line of %s' % (label[q_] or q_))
                elif abs(outs[0].target_at[ax]) < 0.5 <= abs(ins[0].source_at[ax]):
                    shift(q_, ax, cen(r_)[ax] - cen(q_)[ax], ends, 'onto the centre line of %s' % (label[r_] or r_))

    # modifiers onto their (midway) square: a small move so the arc meets the square straight
    # (the user's edits of the full set: 23 such moves). Only a move of at most ALIGN px along
    # one axis, the same for every reaction the modifier acts on (shift above)
    geo = {p: geometry(p, fl, False) for p, fl in fls.items()}
    want = {}
    for p, g in geo.items():
        for e in fls[p][2]:
            m = e.source
            if N[m].parent in ents or layout.turn([cen(m)] + route(p, e.points) + [cen(p)]):
                continue  # complex members move with their complex; an L arc is straight already
            M = cen(m)
            T = attach(g, target(g, e, M, len(fls[p][2]) + len(fls[p][3]) > 1))
            ax = 0 if abs(M[0] - T[0]) < abs(M[1] - T[1]) else 1  # the axis with the small offset
            want.setdefault((m, ax), []).append(T[ax] - M[ax])
    for (m, ax), ds in sorted(want.items()):
        if 0.5 < abs(ds[0]) <= ALIGN and max(ds) - min(ds) <= 1:
            shift(m, ax, ds[0], ends, 'onto its process glyph')

    def modifier(p, g, e, many):
        # a modifier arc of process p (main line g): the point of the square it ends at, its start M,
        # its end T, the anchor on the modifier and its edit points; many: several arcs regulate p
        m = e.source; M = cen(m)
        i = target(g, e, M, many)
        T = attach(g, i)  # the arc's end on the square (the user's glycolysis v01 bends)
        # a slanting straight arc from the border of another entity: that anchor (as read
        # back); one that runs across at the process's height takes a lane (below)
        at = advanced and not e.points and N[m].kind != 'SimpleChemical' and nearest(m, e.source_at)
        if at and off_line(m, at, T) and abs(M[1] + e.source_at[1] - cen(p)[1]) > 5:
            M = anchor_point(front[m], at)
        else:
            at = None
        pts = advanced and not at and lane(m, M, T, e)
        if advanced and N[m].kind == 'SimpleChemical':
            # it leaves the circle where the name is not (meet), its first bend in line with that point
            at = meet(M, pts[0] if pts else T)
            M = anchor_point(box[m], at, True)
            if pts:
                q = pts[0]
                pts[0] = (q[0], M[1]) if at in ('ESE', 'WSW') else (M[0], q[1])
        if pts:
            run = [M] + pts + [T]
            for j in ents:
                if j != m and N[j].parent not in ents and m not in cd_straighten.descendants(j, members) and \
                        any(crosses(a, b, box[j]) for a, b in zip(run, run[1:])):
                    report.say('warning', '%s: the arc from %s runs through %s' % (p, label[m] or m, label[j] or j))
        else:
            # a significant bend: one long L from the modifier to that end
            w = layout.turn([cen(m)] + route(p, e.points) + [cen(p)])
            bend = layout.corner(M, T, w) if w else None
            if bend and min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (M, T)) < layout.EPS:
                bend = None
            pts = [bend] if bend else []
        return i, M, T, at, pts

    return Drawing(box, front, size, cen, lines, geometry, modifier, side)

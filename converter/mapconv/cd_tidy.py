# The tidy moves (user, 2026-10-19): nodes moved a few px so that CellDesigner's lines come out
# straight, on the drawing of the CellDesigner adapter (cd_layout.draw) before anything is written.
# An add-on, not part of the adapter: celldesigner.write runs it with tidy (the advanced file; user,
# 2026-10-24: close to what the user does by hand, good for the Metabolism Regulation maps), on the
# adapter's drawing made with tidy (process glyph placed only for a modifier straight across). Every
# move is in the messages; a node moves only if it stays in its compartment and overlaps nothing.
from . import layout, report
from .cd_layout import descendants

# Main lines only slightly off the vertical or horizontal (user's glycolysis edit, 2026-10-13: the
# PKA complexes and PKA cat put on one vertical line by hand). Across all maps the slightly-off
# main lines are 0-5 px off and the next ones 20+ px (intended diagonals), so TOL = 10 separates them.
TOL = 10.0
ALIGN = 15.0  # largest move of a modifier onto its square (px)


def straighten(box, pairs, members, tol=TOL):
    # nodes joined by an almost vertical main line get one common x (the median of their centres),
    # by an almost horizontal one a common y; complex members move with their complex.
    # box: id -> (x, y, w, h), changed in place; pairs: (reactant, product) of each main line;
    # members: complex -> its members. Returns {id: (dx, dy)}.
    cen = lambda i: (box[i][0] + box[i][2] / 2, box[i][1] + box[i][3] / 2)
    move = {}
    for axis in (0, 1):  # 0: common x (vertical lines), 1: common y (horizontal lines)
        parent = {}
        def root(i):
            while parent.setdefault(i, i) != i:
                i = parent[i]
            return i
        for a, b in pairs:
            d, other = abs(cen(a)[axis] - cen(b)[axis]), abs(cen(a)[1 - axis] - cen(b)[1 - axis])
            if 0 < d <= tol and other > d:
                parent[root(a)] = root(b)
        groups = {}
        for i in parent:
            groups.setdefault(root(i), []).append(i)
        for g in groups.values():
            if len(g) < 2: continue
            vals = sorted(cen(i)[axis] for i in g)
            target = vals[len(vals) // 2]
            for i in g:
                delta = target - cen(i)[axis]
                if delta:
                    for j in [i] + descendants(i, members):
                        x, y, w, h = box[j]
                        box[j] = (x + delta, y, w, h) if axis == 0 else (x, y + delta, w, h)
                        dx, dy = move.get(j, (0.0, 0.0))
                        move[j] = (dx + delta, dy) if axis == 0 else (dx, dy + delta)
    return move


def tidy(diagram, drawing, ents, members, label):
    # the moves, in place on the drawing's boxes; ents the entity ids, members complex -> members,
    # label entity -> name (for the messages)
    N = diagram.nodes
    box, front, cen, yed = drawing.box, drawing.front, drawing.cen, drawing.yed
    comps = {i for i, d in N.items() if d.kind == 'Compartment'}
    def comp_of(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return q

    def said_move(j, dx, dy, why):  # every tidy move in the messages (user, 2026-10-19)
        way = ' and '.join('%.0f px %s' % (abs(v), w[v > 0]) for v, w in ((dx, ('left', 'right')), (dy, ('up', 'down'))) if abs(v) >= 0.05)
        if way:
            report.say('changed', '%s moved %s: %s' % (label[j] or j, way, why))

    # main lines a few pixels off the vertical or horizontal
    for j, (dx, dy) in straighten(box, [(f[0][0].source, f[1][0].target) for f in drawing.lines().values() if f], members).items():
        if j in front:
            front[j] = (box[j][0], box[j][1]) + front[j][2:]
        if N[j].parent not in ents:  # a member moves with its complex
            said_move(j, dx, dy, 'its main line straightened')

    def overlap(a, b):
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]

    def shift(m, ax, d, ends, why):
        # move entity m by d along axis ax, with the entities joined to it by main lines straight
        # on that axis (and their complex members), if all stay in their compartments and overlap
        # nothing (user's pyrimidine v08 edit: ERK1/2 and its phosphorylation moved together)
        group = [m]
        for j in group:
            group += [b if a == j else a for a, b in ends if j in (a, b) and abs(cen(a)[ax] - cen(b)[ax]) < 1
                      and (b if a == j else a) not in group]
        moved = group + [i for j in group for i in descendants(j, members)]
        new = {j: tuple(v + (d if k == ax else 0) for k, v in enumerate(box[j])) for j in moved}
        inside = lambda j, cm: box[cm][0] <= new[j][0] and new[j][0] + new[j][2] <= box[cm][0] + box[cm][2] \
            and box[cm][1] <= new[j][1] and new[j][1] + new[j][3] <= box[cm][1] + box[cm][3]
        if any(comp_of(j) and not inside(j, comp_of(j)) for j in group):
            return
        if any(overlap(new[g_], box[j]) for g_ in group for j in ents if j not in moved and N[j].parent not in moved
               and g_ not in descendants(j, members)):
            return
        box.update(new)
        for j in moved:
            front[j] = (box[j][0], box[j][1]) + front[j][2:]
        for j in group:
            said_move(j, d * (ax == 0), d * (ax == 1), why)

    # a main line yEd draws level into a larger node off its centre (an end point beside the
    # centre): CellDesigner aims at the centre, so the other end moves onto its centre line
    # (user's iNOS v07 and v08 edits: CaM moved 25 px for CaM -> CaM:iNOS)
    fls = {p: fl for p, fl in drawing.lines().items() if fl}
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
    geo = {p: drawing.geometry(p, fl, False) for p, fl in fls.items()}
    want = {}
    for p, g in geo.items():
        for e in fls[p][2]:
            m = e.source
            if N[m].parent in ents or layout.turn([cen(m)] + layout.route(yed(e.points), cen(p), box[p]) + [cen(p)]):
                continue  # complex members move with their complex; an L arc is straight already
            M = cen(m)
            T = drawing.end(g, e, M, len(fls[p][2]) + len(fls[p][3]) > 1)
            ax = 0 if abs(M[0] - T[0]) < abs(M[1] - T[1]) else 1  # the axis with the small offset
            want.setdefault((m, ax), []).append(T[ax] - M[ax])
    for (m, ax), ds in sorted(want.items()):
        if 0.5 < abs(ds[0]) <= ALIGN and max(ds) - min(ds) <= 1:
            shift(m, ax, ds[0], ends, 'onto its process glyph')

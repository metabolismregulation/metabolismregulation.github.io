# Straighten main lines that are only slightly off the vertical or horizontal
# (user's glycolysis edit, 2026-10-13: the PKA complexes and PKA cat put on one
# vertical line by hand). Nodes joined by an almost vertical main line get one
# common x (the median of their centres), by an almost horizontal one a common
# y. Complex members move with their complex. Run before anything is written.
# Across all maps the slightly-off main lines are 0-5 px off and the next ones
# 20+ px (intended diagonals), so TOL = 10 separates them.
TOL = 10.0


def straighten(box, pairs, members, tol=TOL):
    # box: id -> (x, y, w, h), changed in place; pairs: (reactant, product) of
    # each main line; members: complex -> its members. Returns {id: (dx, dy)}.
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


def descendants(i, members):
    out = []
    for m in members.get(i, []):
        out += [m] + descendants(m, members)
    return out

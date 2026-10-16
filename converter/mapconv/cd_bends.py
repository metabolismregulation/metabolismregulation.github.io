# Significant bends (user, 2026-10-13): CellDesigner lines stay straight except
# for a long connector that yEd draws as one L (one corner). From yEd only the
# way the L turns is taken (horizontal or vertical first); the corner itself is
# built from centres in the CellDesigner file: x of one end, y of the other (the
# user's edits of glycolysis v08 and aspirin v02 match this to the pixel).
import math

EPS = 20.0       # a yEd bend counts if leaving it out moves the line by more than this
MIN_LEN = 150.0  # only connectors at least this long


def _off(p, a, b):
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    return abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / L


def _simplify(pts, eps):
    # Ramer-Douglas-Peucker: keep only the points that shape the line
    if len(pts) < 3:
        return pts
    d = [_off(p, pts[0], pts[-1]) for p in pts[1:-1]]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] < eps:
        return [pts[0], pts[-1]]
    return _simplify(pts[:i + 2], eps)[:-1] + _simplify(pts[i + 1:], eps)


def turn(route):
    # 'h' (horizontal first) or 'v' (vertical first) when the route from its
    # first point is one long L, else None
    if sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(route, route[1:])) < MIN_LEN:
        return None
    keep = _simplify(route, EPS)
    if len(keep) != 3:
        return None
    (sx, sy), (cx, cy) = keep[0], keep[1]
    return 'h' if abs(cy - sy) < abs(cx - sx) else 'v'


def corner(a, b, way):
    return (b[0], a[1]) if way == 'h' else (a[0], b[1])


def to_frame(a, b, p):
    # p in CellDesigner's edit point frame: origin a, x axis b - a, y axis the
    # x axis turned 90 degrees (screen coordinates)
    ex = (b[0] - a[0], b[1] - a[1]); ey = (-ex[1], ex[0])
    det = ex[0] * ey[1] - ex[1] * ey[0]
    q = (p[0] - a[0], p[1] - a[1])
    return ((q[0] * ey[1] - q[1] * ey[0]) / det, (ex[0] * q[1] - ex[1] * q[0]) / det)

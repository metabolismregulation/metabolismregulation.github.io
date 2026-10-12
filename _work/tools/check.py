# Layout checks for a yEd SBGN graphml: python3 check.py map.graphml
# Reports node overlaps (6 px clearance), edges running through foreign
# top-level nodes, proper edge crossings, share of orthogonal segments,
# extent and aspect ratio.
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ygml import load, nodes, edges


def polyline(N, e):
    S, T, p = N[e['s']]['geo'], N[e['t']]['geo'], e['path']
    a = (S[0] + S[2] / 2 + float(p.get('sx')), S[1] + S[3] / 2 + float(p.get('sy')))
    b = (T[0] + T[2] / 2 + float(p.get('tx')), T[1] + T[3] / 2 + float(p.get('ty')))
    return [a] + e['pts'] + [b]


def top(i):
    return i.split('::')[0]


def seg_hits_box(p, q, box, pad=1):
    x0, y0, x1, y1 = box[0] + pad, box[1] + pad, box[0] + box[2] - pad, box[1] + box[3] - pad
    for k in range(41):
        t = k / 40
        x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if x0 < x < x1 and y0 < y < y1:
            return True
    return False


def cross(p1, p2, p3, p4):
    d = lambda a, b, c: (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = d(p3, p4, p1), d(p3, p4, p2), d(p1, p2, p3), d(p1, p2, p4)
    return d1 * d2 < -1e-6 and d3 * d4 < -1e-6


def check(path):
    t, k = load(path)
    N, E = nodes(t, k), edges(t, k)
    tops = {i: d for i, d in N.items() if d['parent'] is None}
    out = {'overlaps': [], 'through': [], 'crossings': []}
    for (i, a), (j, b) in itertools.combinations(tops.items(), 2):
        A, B, c = a['geo'], b['geo'], 6
        if A[0] < B[0] + B[2] + c and B[0] < A[0] + A[2] + c and A[1] < B[1] + B[3] + c and B[1] < A[1] + A[3] + c:
            out['overlaps'].append((i, a['label'] or a['cls'], j, b['label'] or b['cls']))
    P = {e['id']: polyline(N, e) for e in E}
    ortho = total = 0
    for e in E:
        pl = P[e['id']]
        for p, q in zip(pl, pl[1:]):
            total += 1
            ortho += abs(p[0] - q[0]) < 0.6 or abs(p[1] - q[1]) < 0.6
            for i, d in tops.items():
                if i in (top(e['s']), top(e['t'])):
                    continue
                if seg_hits_box(p, q, d['geo']):
                    out['through'].append((e['id'], i, d['label'] or d['cls']))
    for e, f in itertools.combinations(E, 2):
        for p, q in zip(P[e['id']], P[e['id']][1:]):
            for r, s in zip(P[f['id']], P[f['id']][1:]):
                if cross(p, q, r, s):
                    out['crossings'].append((e['id'], f['id']))
    xs = [d['geo'][0] for d in tops.values()] + [d['geo'][0] + d['geo'][2] for d in tops.values()]
    ys = [d['geo'][1] for d in tops.values()] + [d['geo'][1] + d['geo'][3] for d in tops.values()]
    W, H = max(xs) - min(xs), max(ys) - min(ys)
    print(path)
    print('  nodes %d, edges %d' % (len(N), len(E)))
    print('  overlaps (6 px):', len(out['overlaps']), out['overlaps'])
    print('  edges through nodes:', len(set(out['through'])), sorted(set(out['through'])))
    print('  crossings:', len(out['crossings']), out['crossings'])
    print('  orthogonal segments: %d/%d' % (ortho, total))
    print('  extent %.0f x %.0f, ratio %.2f' % (W, H, W / H))
    return out


if __name__ == '__main__':
    for p in sys.argv[1:]:
        check(p)

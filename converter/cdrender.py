# A CellDesigner file drawn as CellDesigner draws it (user, 2026-10-22): the CD viewer's
# CellDesigner view. The rules are read off the user's SVG exports from CellDesigner
# (cdviewer/celldesigner/: iNOS, eNOS, ACLY, mevalonate, SREBP, estrogen), the geometry of lines
# as the converter reads it (anchors, edit points in the frame of their two ends, added links
# joining the main line at 3/8 and 5/8).
#   python3 converter/cdrender.py <map.xml> <out.svg>
import math, os, sys
from xml.sax.saxutils import escape
from lxml import etree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'converter'))
from mapconv.cd_layout import ANCHOR, ANGLE, SQUARE, from_frame
from mapconv.celldesigner import plain_name

NS = {'cd': 'http://www.sbml.org/2001/ns/celldesigner', 's': 'http://www.sbml.org/sbml/level2/version4'}
FONT = "'Dialog', 'Liberation Sans', Arial, sans-serif"
SYMBOL = {'phosphorylated': 'P', 'acetylated': 'Ac', 'ubiquitinated': 'Ub', 'methylated': 'Me',
          'hydroxylated': 'OH', 'glycosylated': 'G', 'myristoylated': 'My', 'palmytoylated': 'Pa',
          'prenylated': 'Pr', 'sulfated': 'S', 'protonated': 'H', "don't care": '*', 'unknown': '?', 'empty': ''}
GATE = {'AND': '&amp;', 'OR': '|', 'NOT': '!'}
ROUND = ('SIMPLE_MOLECULE', 'ION', 'DRUG', 'UNKNOWN', 'DEGRADED')


# Helvetica's widths (Arial's metrics), per 1000 of the font size, for characters 32 to 126
WIDTHS = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556,
          556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778,
          722, 278, 500, 667, 556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278,
          278, 278, 469, 556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
          556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]


def width(s, size):
    return sum(WIDTHS[ord(c) - 32] if 32 <= ord(c) < 127 else 556 for c in s) * size / 1000


def colour(c, default='#000000'):  # aarrggbb -> (#rrggbb, alpha)
    return ('#' + c[2:], int(c[:2], 16) / 255) if c else (default, 1.0)


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def pts(p):
    return ' '.join('%s,%s' % (fmt(x), fmt(y)) for x, y in p)


def edit_points(s):
    return [tuple(float(v) for v in q.split(',')) for q in (s or '').split()]


def unit(dx, dy):
    L = math.hypot(dx, dy) or 1
    return dx / L, dy / L


def ellipse(x, y, w, h, n=48):
    return [(x + w / 2 * (1 + math.cos(2 * math.pi * i / n)), y + h / 2 * (1 + math.sin(2 * math.pi * i / n))) for i in range(n)]


def octagon(x, y, w, h, c):
    return [(x + c, y), (x + w - c, y), (x + w, y + c), (x + w, y + h - c), (x + w - c, y + h), (x + c, y + h), (x, y + h - c), (x, y + c)]


def hexagon(x, y, w, h):
    c = h / 2
    return [(x + c, y), (x + w - c, y), (x + w, y + h / 2), (x + w - c, y + h), (x + c, y + h), (x, y + h / 2)]


def parallelogram(x, y, w, h, s):
    return [(x + s, y), (x + w, y), (x + w - s, y + h), (x, y + h)]


def outline(cls, b):
    # the shape a line stops at, as a polygon
    x, y, w, h = b
    if cls == 'DEGRADED':
        return ellipse(x + w / 8, y + h / 8, w * 3 / 4, h * 3 / 4)
    if cls in ROUND:
        return ellipse(*b)
    if cls == 'COMPLEX':
        return octagon(x, y, w, h, 5)
    if cls == 'PHENOTYPE':
        return hexagon(*b)
    if cls == 'RNA':
        return parallelogram(x, y, w, h, h)
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def leave(poly, P, Q):
    # where the segment P (inside) -> Q leaves the polygon, else P
    best = None
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        dx, dy, ex, ey = Q[0] - P[0], Q[1] - P[1], bx - ax, by - ay
        d = dx * ey - dy * ex
        if abs(d) < 1e-9:
            continue
        t = ((ax - P[0]) * ey - (ay - P[1]) * ex) / d
        u = ((ax - P[0]) * dy - (ay - P[1]) * dx) / d
        if 0 <= t <= 1 and 0 <= u <= 1 and (best is None or t > best):
            best = t
    return P if best is None else (P[0] + best * (Q[0] - P[0]), P[1] + best * (Q[1] - P[1]))


class Drawing:
    def __init__(self, path):
        r = etree.parse(path).getroot()
        f = lambda x, q: x.find(q, NS)
        self.f = f
        model = f(r, 's:model')
        ext = f(model, 's:annotation/cd:extension')
        md = f(ext, 'cd:modelDisplay')
        self.W, self.H = float(md.get('sizeX')), float(md.get('sizeY'))
        self.out = []
        self.halo, self.lines = [], []
        species = {s.get('id'): (s.get('name'), f(s, 's:annotation/cd:extension/cd:speciesIdentity'))
                   for s in model.iterfind('s:listOfSpecies/s:species', NS)}
        species.update({s.get('id'): (s.get('name'), f(s, 'cd:annotation/cd:speciesIdentity'))
                        for s in ext.iterfind('cd:listOfIncludedSpecies/cd:species', NS)})
        self.residues = {(p.get('id'), m.get('id')): (float(m.get('angle', 0)), m.get('name'))
                         for p in ext.iterfind('cd:listOfProteins/cd:protein', NS)
                         for m in p.iterfind('cd:listOfModificationResidues/cd:modificationResidue', NS)}
        self.cnames = {c.get('id'): c.get('name') or c.get('id') for c in model.iterfind('s:listOfCompartments/s:compartment', NS)}
        # aliases: id -> (class, box, alias element, species name, identity)
        self.alias = {}
        for a in list(ext.iterfind('cd:listOfComplexSpeciesAliases/cd:complexSpeciesAlias', NS)) + \
                list(ext.iterfind('cd:listOfSpeciesAliases/cd:speciesAlias', NS)):
            name, si = species[a.get('species')]
            b = f(a, 'cd:bounds')
            self.alias[a.get('id')] = (f(si, 'cd:class').text, tuple(float(b.get(k)) for k in 'xywh'), a, name, si)
        self.ext, self.model = ext, model

    # -- nodes ----------------------------------------------------------------------------
    def compartments(self):
        cs = [a for a in self.ext.iterfind('cd:listOfCompartmentAliases/cd:compartmentAlias', self.NS())]
        cs.sort(key=lambda a: -float(self.f(a, 'cd:bounds').get('w')) * float(self.f(a, 'cd:bounds').get('h')))
        for a in cs:
            b = self.f(a, 'cd:bounds')
            if b is None:
                continue
            x, y, w, h = (float(b.get(k)) for k in 'xywh')
            dl = self.f(a, 'cd:doubleLine')
            t = float(dl.get('thickness', 12)) if dl is not None else 12
            ow = float(dl.get('outerWidth', 2)) if dl is not None else 2
            iw = float(dl.get('innerWidth', 1)) if dl is not None else 1
            fill, _ = colour(self.f(a, 'cd:paint').get('color'))
            oval = self.f(a, 'cd:class').text == 'OVAL'
            if oval:
                self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-opacity="0.5" stroke-width="%s"/>'
                                % (fmt(x + w / 2), fmt(y + h / 2), fmt(w / 2 - t / 2), fmt(h / 2 - t / 2), fill, fmt(t)))
                self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="#000" stroke-width="%s"/>' % (fmt(x + w / 2), fmt(y + h / 2), fmt(w / 2), fmt(h / 2), fmt(ow)))
                self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="#000" stroke-width="%s"/>' % (fmt(x + w / 2), fmt(y + h / 2), fmt(w / 2 - t), fmt(h / 2 - t), fmt(iw)))
            else:
                # the band between the two lines in the compartment's colour, half transparent
                self.out.append('<path d="%s %s" fill="%s" fill-opacity="0.5" fill-rule="evenodd"/>'
                                % (rrect(x, y, w, h, 20), rrect(x + t, y + t, w - 2 * t, h - 2 * t, 14), fill))
                self.out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="20" fill="none" stroke="#000" stroke-width="%s"/>' % (fmt(x), fmt(y), fmt(w), fmt(h), fmt(ow)))
                self.out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="14" fill="none" stroke="#000" stroke-width="%s"/>' % (fmt(x + t), fmt(y + t), fmt(w - 2 * t), fmt(h - 2 * t), fmt(iw)))
            np_ = self.f(a, 'cd:namePoint')
            if np_ is not None:
                self.text(plain_name(self.cnames.get(a.get('compartment'), '')), float(np_.get('x')), float(np_.get('y')) + 15.5, anchor='start')

    def NS(self):
        return NS

    def text(self, s, x, y, size=12, anchor='middle', family=FONT, extra=''):
        self.out.append('<text x="%s" y="%s" font-family="%s" font-size="%s" text-anchor="%s"%s>%s</text>'
                        % (fmt(x), fmt(y), family, fmt(size), anchor, extra, escape(s)))

    def name_lines(self, name):
        return plain_name(name or '').replace('_br_', '\n').split('\n')

    def species(self):
        # complexes first, outer ones before those inside them, then the other species
        depth = {}
        def d(i):
            if i not in depth:
                p = self.alias[i][2].get('complexSpeciesAlias')
                depth[i] = 0 if not p or p not in self.alias else d(p) + 1
            return depth[i]
        order = sorted(self.alias, key=lambda i: (self.alias[i][0] != 'COMPLEX', d(i)))
        for i in order:
            self.node(i)

    def node(self, i):
        cls, (x, y, w, h), a, name, si = self.alias[i]
        f = self.f
        hd = f(si, 'cd:state/cd:homodimer')
        n = int(hd.text) if hd is not None else 1
        paint = f(a, 'cd:usualView/cd:paint')
        fill, alpha = colour(paint.get('color') if paint is not None else 'ffffffff')
        hyp = f(si, 'cd:hypothetical')
        dash = ' stroke-dasharray="5,3"' if hyp is not None and hyp.text == 'true' else ''
        s = 6 * (n - 1)
        fw, fh = w - s, h - s
        for k in range(n - 1, -1, -1):  # the copies of a multimer behind, offset 6 each, each with its states
            self.shape(cls, (x + 6 * k, y + 6 * k, fw, fh), fill, alpha, dash)
            self.states(cls, (x + 6 * k, y + 6 * k, fw, fh), a, si, k == 0)
        if cls != 'COMPLEX':
            lines = self.name_lines(name) if cls != 'DEGRADED' else []
            cy = y + fh / 2 - 7 * (len(lines) - 1)
            for k, line in enumerate(lines):
                self.text(line, x + fw / 2, cy + 4 + 14 * k)
        else:
            self.text(' '.join(self.name_lines(name)), x + fw / 2, y + fh - 7)

    def shape(self, cls, b, fill, alpha, dash):
        x, y, w, h = b
        style = 'fill="%s"%s stroke="#000"%s' % (fill, ' fill-opacity="%s"' % fmt(alpha) if alpha < 1 else '', dash)
        if cls in ('PROTEIN', 'RECEPTOR', 'TRUNCATED', 'ION_CHANNEL'):
            self.out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="5" %s/>' % (fmt(x), fmt(y), fmt(w), fmt(h), style))
        elif cls == 'GENE':
            self.out.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (fmt(x), fmt(y), fmt(w), fmt(h), style))
        elif cls == 'DEGRADED':  # a circle of 3/8 the box, a slash across the whole box
            cx, cy = x + w / 2, y + h / 2
            self.out.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (fmt(cx), fmt(cy), fmt(w * 3 / 8), style))
            self.out.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#000"/>' % (fmt(cx + w / 5), fmt(cy - h / 2), fmt(cx - w / 5), fmt(cy + h / 2)))
        elif cls in ROUND:
            self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (fmt(x + w / 2), fmt(y + h / 2), fmt(w / 2), fmt(h / 2), style))
        else:
            self.out.append('<polygon points="%s" %s/>' % (pts(outline(cls, b)), style))

    def states(self, cls, b, a, si, front=True):
        x, y, w, h = b
        f = self.f
        pref = f(si, 'cd:proteinReference')
        for m in si.iterfind('cd:state/cd:listOfModifications/cd:modification', NS):
            ang, site = self.residues.get((pref.text if pref is not None else None, m.get('residue')), (0.0, None))
            px, py = on_border(b, ang)
            self.out.append('<circle cx="%s" cy="%s" r="8" fill="#fff" stroke="#000"/>' % (fmt(px), fmt(py)))
            sym = SYMBOL.get(m.get('state'), m.get('state'))
            if sym:
                self.text(sym, px, py + 3.5, size=9, family='sans-serif')
        for st in si.iterfind('cd:state/cd:listOfStructuralStates/cd:structuralState', NS):
            sa = f(a, 'cd:structuralState')
            ang = float(sa.get('angle')) if sa is not None else -math.pi / 2
            px, py = on_border(b, ang)
            label = st.get('structuralState')  # an ellipse 12 wider than its 10 px text on each side
            self.out.append('<ellipse cx="%s" cy="%s" rx="%d" ry="8" fill="#fff" stroke="#000"/>' % (fmt(px), fmt(py), int(width(label, 10) / 2 + 12)))
            self.text(label, px, py + 3, size=10)
        info = f(a, 'cd:info')
        if front and info is not None and info.get('state') == 'open':
            label = ' %s:%s ' % (info.get('prefix'), info.get('label')) if info.get('prefix') != 'free input' else ' %s ' % info.get('label')
            if len(label) > 11:
                label = label[:8] + '... '
            ux, uy = x + w / 2 - 35, y - 8
            self.out.append('<rect x="%s" y="%s" width="70" height="16" fill="#fff" stroke="#000"/>' % (fmt(ux), fmt(uy)))
            self.text(label, ux + 5, uy + 12, anchor='start', extra=' xml:space="preserve"')

    # -- lines ----------------------------------------------------------------------------
    def centre(self, i):
        x, y, w, h = self.box(i)
        return (x + w / 2, y + h / 2)

    def box(self, i):  # lines meet the alias's whole box, a multimer's copies included
        return self.alias[i][1]

    def end(self, e, i):
        # where a line meets alias i: its anchor (linkAnchor in e), else its centre; and whether anchored
        b = self.f(e, 'cd:linkAnchor') if e is not None else None
        x, y, w, h = self.box(i)
        side = b.get('position') if b is not None else None
        if side not in ANCHOR:
            return (x + w / 2, y + h / 2), False
        if self.alias[i][0] in ROUND:
            t = math.radians(ANGLE[side])
            return (x + w / 2 * (1 + math.cos(t)), y + h / 2 * (1 - math.sin(t))), True
        fx, fy = ANCHOR[side]
        return (x + fx * w, y + fy * h), True

    def clip(self, i, P, anchored, Q):
        # the line's end at alias i: an anchor as it is, else where the line from the centre leaves the shape
        if anchored:
            return P
        cls = self.alias[i][0]
        return leave(outline(cls, self.box(i)), P, Q)

    def path(self, p, colour_='#000', width=1.0, dash=False, start_node=True, end_node=True):
        # a line: a white halo under it (CellDesigner's, so crossings read), shortened at nodes
        h = list(p)
        if len(h) > 1:
            if start_node:
                u = unit(h[1][0] - h[0][0], h[1][1] - h[0][1]); h[0] = (h[0][0] + 8 * u[0], h[0][1] + 8 * u[1])
            if end_node:
                u = unit(h[-1][0] - h[-2][0], h[-1][1] - h[-2][1]); h[-1] = (h[-1][0] - 8 * u[0], h[-1][1] - 8 * u[1])
        self.halo.append('<polyline points="%s"/>' % pts(h))
        self.lines.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s/>' % (pts(p), colour_, fmt(width), ' stroke-dasharray="6,4"' if dash else ''))

    def head(self, kind, T, u):
        # an arrowhead with its tip at T, the line arriving along u; returns where the line stops
        n = (-u[1], u[0])
        at = lambda a, c: (T[0] - a * u[0] + c * n[0], T[1] - a * u[1] + c * n[1])
        if kind == 'production':
            self.lines.append('<polygon points="%s" fill="#000"/>' % pts([T, at(15, 5), at(15, -5)]))
            return at(14, 0)
        if kind == 'stimulation':
            self.lines.append('<polygon points="%s" fill="#fff" stroke="#000"/>' % pts([T, at(8, 4), at(8, -4)]))
            return at(8, 0)
        if kind == 'stimulation-reduced':  # a black triangle, white inside
            self.lines.append('<polygon points="%s" fill="#000"/>' % pts([T, at(15, 5), at(15, -5)]))
            self.lines.append('<polygon points="%s" fill="#fff"/>' % pts([at(4.8, 0), at(12, 2), at(12, -2)]))
            return at(15, 0)
        if kind == 'trigger':
            self.lines.append('<polygon points="%s" fill="#fff" stroke="#000"/>' % pts([T, at(15, 5), at(15, -5)]))
            self.lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#000"/>' % (*map(fmt, at(20, 4.5)), *map(fmt, at(20, -4.5))))
            return at(15, 0)
        if kind == 'catalysis':
            c = at(4.5, 0)
            self.lines.append('<circle cx="%s" cy="%s" r="3" fill="#fff" stroke="#000"/>' % (fmt(c[0]), fmt(c[1])))
            return at(7.5, 0)
        if kind == 'inhibition':
            self.lines.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#000"/>' % (*map(fmt, at(3, 6)), *map(fmt, at(3, -6))))
            return at(3, 0)
        if kind == 'modulation':
            self.lines.append('<polygon points="%s" fill="#fff" stroke="#000"/>' % pts([T, at(5, 4), at(10, 0), at(5, -4)]))
            return at(10, 0)
        return T

    def reactions(self):
        for rx in self.model.iterfind('s:listOfReactions/s:reaction', NS):
            try:
                self.reaction(rx)
            except Exception as e:  # a reaction this drawing cannot place is left out, said on stderr
                print('%s: %s' % (rx.get('id'), e), file=sys.stderr)

    def reaction(self, rx):
        f = self.f
        x = f(rx, 's:annotation/cd:extension')
        typ = f(x, 'cd:reactionType').text
        br = list(x.iterfind('cd:baseReactants/cd:baseReactant', NS))
        bp = list(x.iterfind('cd:baseProducts/cd:baseProduct', NS))
        ln = f(x, 'cd:line')
        col, _ = colour(ln.get('color') if ln is not None else None)
        width = float(ln.get('width', 1)) if ln is not None else 1.0
        ep = f(x, 'cd:editPoints')
        q = edit_points(ep.text if ep is not None else '')
        if len(br) != 1 or len(bp) != 1:
            raise ValueError('%d base reactants and %d base products, not drawn' % (len(br), len(bp)))
        ra, pa = br[0].get('alias'), bp[0].get('alias')
        A, ancA = self.end(br[0], ra)
        B, ancB = self.end(bp[0], pa)
        if typ == 'BOOLEAN_LOGIC_GATE':
            raise ValueError('a logic gate between entities, not drawn')
        line = [A] + [from_frame(A, B, p) for p in q] + [B]
        line[0] = self.clip(ra, A, ancA, line[1])
        line[-1] = self.clip(pa, B, ancB, line[-2])
        reduced = typ not in ('STATE_TRANSITION', 'KNOWN_TRANSITION_OMITTED', 'UNKNOWN_TRANSITION', 'TRANSPORT',
                              'TRANSCRIPTION', 'TRANSLATION', 'HETERODIMER_ASSOCIATION', 'DISSOCIATION', 'TRUNCATION')
        dash = reduced and typ.startswith('UNKNOWN')  # an unknown transition keeps a solid line, a ? in its square
        if reduced:  # an arc between the entities, its head by type
            kind = {'PHYSICAL_STIMULATION': 'stimulation-reduced', 'REDUCED_PHYSICAL_STIMULATION': 'stimulation-reduced',
                    'NEGATIVE_INFLUENCE': 'inhibition', 'REDUCED_MODULATION': 'modulation', 'REDUCED_TRIGGER': 'trigger',
                    'POSITIVE_INFLUENCE': 'production', 'CATALYSIS': 'catalysis', 'INHIBITION': 'inhibition'}.get(typ.replace('UNKNOWN_', ''), 'production')
            u = unit(line[-1][0] - line[-2][0], line[-1][1] - line[-2][1])
            stop = self.head(kind, line[-1], u)
            self.path(line[:-1] + [stop], col, width, dash)
            return
        cs = f(x, 'cd:connectScheme')
        k = int(cs.get('rectangleIndex', 0)) if cs is not None else 0
        k = min(k, len(line) - 2)
        P, Q = line[k], line[k + 1]
        sq = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
        fl = unit(Q[0] - P[0], Q[1] - P[1])
        reversible = rx.get('reversible') != 'false'
        # the main line: reactant to product, the head at the product (and the reactant if reversible)
        u = unit(line[-1][0] - line[-2][0], line[-1][1] - line[-2][1])
        main = list(line)
        main[-1] = self.head('production', line[-1], u)
        if reversible:
            v = unit(line[0][0] - line[1][0], line[0][1] - line[1][1])
            main[0] = self.head('production', line[0], v)
        self.path(main, col, width, dash)
        # added reactants and products join the square's segment at 3/8 and 5/8 of its ends' anchors
        joins = [(P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])) for t in (0.375, 0.625)]
        for tag, into in (('cd:listOfReactantLinks/cd:reactantLink', True), ('cd:listOfProductLinks/cd:productLink', False)):
            for l in x.iterfind(tag, NS):
                i = l.get('alias')
                if i not in self.alias:
                    continue
                O, anc = self.end(l, i)
                J = joins[0 if into else 1]
                bends = [from_frame(O, J, p) if into else from_frame(J, O, p) for p in edit_points(l.get('editPoints') or l.findtext('cd:editPoints', '', NS))]
                seq = [O] + (bends if into else bends[::-1]) + [J]
                seq[0] = self.clip(i, O, anc, seq[1])
                lc = f(l, 'cd:line')
                lcol = colour(lc.get('color'))[0] if lc is not None else col
                if into:
                    self.path(seq, lcol, width, dash, end_node=False)
                else:
                    seq = seq[::-1]
                    w_ = unit(seq[-1][0] - seq[-2][0], seq[-1][1] - seq[-2][1])
                    stop = self.head('production', seq[-1], w_)
                    self.path(seq[:-1] + [stop], lcol, width, dash, start_node=False)
        # modifiers end at the point of the square targetLineIndex names
        gate_inputs = set()
        mods = list(x.iterfind('cd:listOfModification/cd:modification', NS))
        for m in mods:
            if m.get('type', '').startswith('BOOLEAN_LOGIC_GATE'):
                gate_inputs |= {(a_, m.get('modificationType')) for a_ in m.get('aliases').split(',')}
        HEADS = {'CATALYSIS': 'catalysis', 'UNKNOWN_CATALYSIS': 'catalysis', 'INHIBITION': 'inhibition',
                 'UNKNOWN_INHIBITION': 'inhibition', 'PHYSICAL_STIMULATION': 'stimulation', 'TRIGGER': 'trigger',
                 'MODULATION': 'modulation', 'TRANSCRIPTIONAL_ACTIVATION': 'stimulation',
                 'TRANSCRIPTIONAL_INHIBITION': 'inhibition', 'TRANSLATIONAL_ACTIVATION': 'stimulation',
                 'TRANSLATIONAL_INHIBITION': 'inhibition'}
        squares = []
        for m in mods:
            t = m.get('type')
            a_ = m.get('aliases')
            spot = SQUARE.get(int(m.get('targetLineIndex', '-1,2').split(',')[1]), SQUARE[3])
            T = (sq[0] + 5 * (spot[0] * fl[0] - spot[1] * fl[1]), sq[1] + 5 * (spot[0] * fl[1] + spot[1] * fl[0]))
            if t.startswith('BOOLEAN_LOGIC_GATE'):
                G = edit_points(m.get('editPoints'))[0]
                for i in a_.split(','):
                    if i in self.alias:
                        c, anc = self.end(None, i)
                        S = self.clip(i, c, anc, G)
                        u = unit(G[0] - S[0], G[1] - S[1])
                        self.path([S, (G[0] - 6.5 * u[0], G[1] - 6.5 * u[1])], col, width, end_node=False)
                u = unit(T[0] - G[0], T[1] - G[1])
                stop = self.head(HEADS.get(m.get('modificationType'), 'stimulation'), T, u)
                self.path([G, stop], col, width, start_node=False, end_node=False)
                squares.append('<circle cx="%s" cy="%s" r="6" fill="#fff" stroke="#000"/>' % (fmt(G[0]), fmt(G[1])))
                squares.append('<text x="%s" y="%s" font-family="sans-serif" font-size="11" text-anchor="middle">%s</text>' % (fmt(G[0]), fmt(G[1] + 4), GATE[t.rsplit('_', 1)[1]]))
                continue
            if (a_, t) in gate_inputs or a_ not in self.alias:
                continue
            lt = f(m, 'cd:linkTarget')
            M, anc = self.end(lt, a_)
            bends = [from_frame(M, T, p) for p in edit_points(m.get('editPoints'))]
            seq = [M] + bends + [T]
            seq[0] = self.clip(a_, M, anc, seq[1])
            u = unit(seq[-1][0] - seq[-2][0], seq[-1][1] - seq[-2][1])
            stop = self.head(HEADS.get(t, 'stimulation'), T, u)
            mc = f(m, 'cd:line')
            self.path(seq[:-1] + [stop], colour(mc.get('color'))[0] if mc is not None else col, width, t.startswith('UNKNOWN'), end_node=False)
        # the process glyph: a 10 px square along the line, over the lines
        ang = math.degrees(math.atan2(fl[1], fl[0]))
        glyph = '<rect x="-5" y="-5" width="10" height="10" fill="#fff" stroke="#000" transform="translate(%s,%s) rotate(%s)"/>' % (
            fmt(sq[0]), fmt(sq[1]), fmt(ang))
        mark = {'UNKNOWN_TRANSITION': '?', 'KNOWN_TRANSITION_OMITTED': '//'}.get(typ)
        if mark:  # Times bold 10, upright
            glyph += '<text x="%s" y="%s" font-family="\'Times New Roman\', serif" font-weight="bold" font-size="10" text-anchor="middle">%s</text>' % (fmt(sq[0]), fmt(sq[1] + 3), mark)
        self.lines.append(glyph)
        self.lines.extend(squares)

    def svg(self):
        self.compartments()
        self.species()
        self.reactions()
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">\n'
                '<rect width="100%%" height="100%%" fill="#fff"/>\n%s\n'
                '<g fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">\n%s\n</g>\n%s\n</svg>\n'
                % (fmt(self.W), fmt(self.H), fmt(self.W), fmt(self.H), '\n'.join(self.out), '\n'.join(self.halo), '\n'.join(self.lines)))


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return ('M%s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s Z'
            % tuple(map(fmt, (x + r, y, x + w - r, r, r, x + w, y + r, y + h - r, r, r, x + w - r, y + h,
                              x + r, r, r, x, y + h - r, y + r, r, r, x + r, y))))


def on_border(b, a):
    # the point of the box's border at residue angle a (radians, y up), as CellDesigner places state circles
    x, y, w, h = b
    q = math.pi / 4
    a = (a + q) % (2 * math.pi) - q
    if a < q:
        fx, fy = 0.5, -0.5 * a / q
    elif a < 3 * q:
        fx, fy = 0.5 * (math.pi / 2 - a) / q, -0.5
    elif a < 5 * q:
        fx, fy = -0.5, -0.5 * (math.pi - a) / q
    else:
        fx, fy = 0.5 * (a - 3 * math.pi / 2) / q, 0.5
    return (x + w / 2 + fx * w, y + h / 2 + fy * h)


def render(path):
    return Drawing(path).svg()


if __name__ == '__main__':
    open(sys.argv[2], 'w', encoding='utf-8').write(render(sys.argv[1]))

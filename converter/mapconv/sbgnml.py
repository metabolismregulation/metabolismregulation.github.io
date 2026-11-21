import collections, math, copy, os, re
from lxml import etree
from . import report
from .annotation import from_graphml, from_notes, notes, to_properties
from .layout import bends, centre, compartment_of, decorations, unbent
from . import newt_layout
from .graphml import DELAY, EQUIV, LINE, CHAR, without_delays
from .model import Map, Node, Arc

NS = 'http://sbgn.org/libsbgn/0.3'
RENDER = 'http://www.sbml.org/sbml/level3/version1/render/version1'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
XH = 'http://www.w3.org/1999/xhtml'
BQBIOL = 'http://biomodels.net/biology-qualifiers/'
S, R = '{%s}' % NS, '{%s}' % RENDER
CLASS = {'Macromolecule': 'macromolecule', 'SimpleChemical': 'simple chemical', 'NucleicAcidFeature': 'nucleic acid feature',
         'UnspecifiedEntity': 'unspecified entity', 'Complex': 'complex',
         'Phenotype': 'phenotype', 'SourceAndSink': 'source and sink', 'EmptySet': 'source and sink',
         'Submap': 'submap', 'Compartment': 'compartment', 'Process': 'process', 'OmittedProcess': 'omitted process',
         'UncertainProcess': 'uncertain process'}
MULTIMER = ('Macromolecule', 'SimpleChemical', 'NucleicAcidFeature', 'Complex')
PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess')
OPERATORS = {'and': 'AND', 'or': 'OR', 'not': 'NOT', 'equivalence': EQUIV, 'delay': DELAY}
ARC = {'production': 'production', 'catalysis': 'catalysis', 'inhibition': 'inhibition', 'modulation': 'modulation',
       'stimulation': 'stimulation', 'trigger': 'necessary stimulation'}
DB = {'obo.chebi': 'CHEBI', 'hgnc': 'hgnc', 'hgnc.symbol': 'hgnc.symbol', 'uniprot': 'uniprot'}


def xml_id(i):
    return re.sub(r'[^\w.-]', '_', i if re.match(r'[A-Za-z_]', i) else '_' + i)


def border(d, p):
    (cx, cy), (w, h) = centre(d), d.box[2:]
    dx, dy = p[0] - cx, p[1] - cy
    if not dx and not dy:
        return cx, cy
    t = min(w / 2 / abs(dx) if dx else float('inf'), h / 2 / abs(dy) if dy else float('inf'))
    return cx + t * dx, cy + t * dy


def at(d, ref, p, q, port=None):
    if ref != d.id:
        if not port:
            return (0.0, 0.0)
        cx, cy = centre(d)
        return (port[0] - cx, port[1] - cy)
    if p is None or q is None:
        return (0.0, 0.0)
    (cx, cy) = centre(d)
    ux, uy, vx, vy = q[0] - cx, q[1] - cy, p[0] - cx, p[1] - cy
    n = math.hypot(ux, uy)
    if not n or (abs(ux * vy - uy * vx) / n <= 1.5 and ux * vx + uy * vy >= 0):
        return (0.0, 0.0)
    return (vx, vy)


def cuts(p, q, box, inset=1):
    x, y, w, h = box
    t0, t1 = 0.0, 1.0
    for d, lo, hi, a in ((q[0] - p[0], x + inset, x + w - inset, p[0]), (q[1] - p[1], y + inset, y + h - inset, p[1])):
        if not d:
            if not lo < a < hi:
                return False
            continue
        u, v = sorted(((lo - a) / d, (hi - a) / d))
        t0, t1 = max(t0, u), min(t1, v)
    return t0 < t1


def bbox(parent, x, y, w, h):
    etree.SubElement(parent, S + 'bbox', x=repr(float(x)), y=repr(float(y)), w=repr(float(w)), h=repr(float(h)))


def shifted(diagram, margin=20):
    d = copy.deepcopy(diagram)
    dx = margin - min(n.box[0] for n in d.nodes.values())
    dy = margin - min(n.box[1] for n in d.nodes.values())
    for n in d.nodes.values():
        n.box = (n.box[0] + dx, n.box[1] + dy) + tuple(n.box[2:])
    for a in d.arcs:
        a.points = [(x + dx, y + dy) for x, y in a.points]
    return d


UNKNOWN = 'Unknown (a dashed arc)'


def note(el, lines):
    h = etree.SubElement(etree.SubElement(el, S + 'notes'), '{%s}html' % XH, nsmap={None: XH})
    etree.SubElement(h, '{%s}body' % XH).text = '\n'.join(lines)


def write(diagram, layout='advanced', newt=False):
    diagram = without_delays(shifted(diagram), 'SBGN Process Description')
    if newt:
        diagram = newt_layout.adjust(diagram, layout)
    N = diagram.nodes
    ids = {i: xml_id(i) for i in N}
    ann = from_graphml(diagram)
    comps = {i for i, d in N.items() if d.kind == 'Compartment'}
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    hubs = {i for i, d in N.items() if d.kind in PROCESSES} | ops
    eq = {i for i in ops if N[i].labels[:1] == [EQUIV]}

    pairs = collections.Counter(frozenset((a.source, a.target)) for a in diagram.arcs)
    arcs = []
    for a in diagram.arcs:
        s, t, pts, s_at, t_at = a.source, a.target, list(a.points), a.source_at, a.target_at
        if layout == 'straight' and pairs[frozenset((s, t))] == 1 or s in ops or t in ops:
            pts = []
        given = (s_at, t_at)
        if layout == 'straight' or s in ops or t in ops:
            s_at, t_at = (0.0, 0.0), (0.0, 0.0)
        if a.head is None:
            if s in hubs - eq and t not in hubs:
                s, t, pts, s_at, t_at, given = t, s, pts[::-1], t_at, s_at, given[::-1]
            cls = 'logic arc' if t in ops or s in eq else 'consumption'
        else:
            cls = ARC.get(a.head)
            if cls is None:
                report.say('left out', 'arc %s: no SBGN arc for %s, left out' % (a.id, a.head)); continue
        if N[s].kind == 'Phenotype' and N[s].data.get('SBGN class') != 'perturbing agent':
            report.say('left out', 'arc %s: leaves phenotype %s (%s), no SBGN Process Description equivalent, left out'
                       % (a.id, s, N[s].labels[0] if N[s].labels else '')); continue
        if a.tail:
            report.say('left out', 'arc %s: its arrow at the source has no place in SBGN-ML, dropped' % a.id)
        arcs.append((a, cls, s, t, pts, s_at, t_at, given))

    ports = {}
    for p in hubs:
        ins = [pts[-1] if pts else centre(N[s]) for _, c, s, t, pts, *_ in arcs if t == p and c in ('consumption', 'logic arc')]
        outs = [pts[0] if pts else centre(N[t]) for _, c, s, t, pts, *_ in arcs if s == p and (c == 'production' or p in ops)]
        (cx, cy), w, h = centre(N[p]), N[p].box[2], N[p].box[3]
        out_of = lambda o: abs(o[0]) > w / 2 + 0.5 or abs(o[1]) > h / 2 + 0.5
        gin = next(((cx + g[1][0], cy + g[1][1]) for _, c, s, t, _, _, _, g in arcs
                    if t == p and c in ('consumption', 'logic arc') and out_of(g[1])), None)
        gout = next(((cx + g[0][0], cy + g[0][1]) for _, c, s, t, _, _, _, g in arcs
                     if s == p and (c == 'production' or p in ops) and out_of(g[0])), None)
        if gin and gout and math.dist(gin, gout) < 2:
            gin = gout = None
        if gin or gout:
            one = gin or (2 * cx - gout[0], 2 * cy - gout[1])
            two = gout or (2 * cx - gin[0], 2 * cy - gin[1])
            ports[p] = ('horizontal' if abs(two[0] - one[0]) >= abs(two[1] - one[1]) else 'vertical', one, two)
            continue
        mean = lambda q, d: (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q)) if q else d
        a, b = mean(ins, (cx, cy)), mean(outs, (cx, cy))
        if p in ops and outs:
            a = (cx, cy)
        if a == b:
            q = outs[:2] if len(outs) > 1 else [(cx - 1, cy), (cx + 1, cy)]
            a, b = q[0], q[1]
        vx, vy = b[0] - a[0], b[1] - a[1]
        horizontal = abs(vx) >= abs(vy)
        k = (1 if (vx if horizontal else vy) >= 0 else -1)
        side = w if horizontal else h
        r = side / 2 + max(0.5 * side, 9)
        one = (cx - k * r, cy) if horizontal else (cx, cy - k * r)
        two = (cx + k * r, cy) if horizontal else (cx, cy + k * r)
        ports[p] = ('horizontal' if horizontal else 'vertical', one, two)
    if layout == 'straight':
        ports = {}

    root = etree.Element(S + 'sbgn', nsmap={None: NS})
    m = etree.SubElement(root, S + 'map', id=xml_id(diagram.name.replace('-', '_')), language='process description')

    fills = {}
    for i, d in N.items():
        if d.fill or d.line or d.font or d.weight:
            fills.setdefault((d.fill.lower() if d.fill else None, d.line and d.line.lower(), d.font, d.weight), []).append(ids[i])
        if d.small:
            n = len(decorations(d)[1])
            fills.setdefault((None, None, d.small, None), []).extend(['%s_sv%d' % (ids[i], k) for k in range(len(d.states))] +
                                                         ['%s_ui%d' % (ids[i], k) for k in range(n)])
    if fills:
        ri = etree.SubElement(etree.SubElement(m, S + 'extension'), R + 'renderInformation', nsmap={None: RENDER},
                              id='renderInformation')
        cd = etree.SubElement(ri, R + 'listOfColorDefinitions')
        etree.SubElement(cd, R + 'colorDefinition', id='black', value='#000000')
        st = etree.SubElement(ri, R + 'listOfStyles')
        for k, ((f, line, size, weight), members) in enumerate(fills.items()):
            s = etree.SubElement(st, R + 'style', id='style_%d' % k, idList=' '.join(members))
            g = etree.SubElement(s, R + 'g', stroke='black')
            if f:
                etree.SubElement(cd, R + 'colorDefinition', id='color_%d' % k, value=f)
                g.set('fill', 'color_%d' % k)
            if line:
                etree.SubElement(cd, R + 'colorDefinition', id='line_%d' % k, value=line)
                g.set('stroke', 'line_%d' % k)
            g.set('stroke-width', '%g' % (weight or 1))
            if size:
                g.set('font-size', '%g' % size)

    def annotate(g, i, d):
        if d.kind not in CLASS or d.kind in PROCESSES:
            return
        if notes(d.data):
            note(g, notes(d.data))
        lab = ' '.join(d.labels[0].split()) if d.labels else ''
        if lab not in ann:
            return
        family, urns = ann[lab]
        uris = []
        for u in urns:
            db, _, x = u[len('urn:miriam:'):].rpartition(':')
            if db in DB:
                uris.append('http://identifiers.org/%s:%s' % (DB[db], x.replace('%3A', ':').replace('CHEBI:', '')))
        if not uris:
            return
        e = etree.SubElement(g, S + 'extension')
        r = etree.SubElement(etree.SubElement(e, S + 'annotation', nsmap={None: NS}), '{%s}RDF' % RDF,
                             nsmap={'rdf': RDF, 'bqbiol': BQBIOL})
        desc = etree.SubElement(r, '{%s}Description' % RDF, {'{%s}about' % RDF: '#' + ids[i]})
        bag = etree.SubElement(etree.SubElement(desc, '{%s}%s' % (BQBIOL, 'hasVersion' if family else 'is')), '{%s}Bag' % RDF)
        for u in uris:
            etree.SubElement(bag, '{%s}li' % RDF, {'{%s}resource' % RDF: u})

    def glyph(parent, i):
        d = N[i]
        x, y, w, h = d.box
        if d.kind == 'Operator':
            cls = {v: k for k, v in OPERATORS.items()}.get((d.labels[0] if d.labels else '').strip().upper())
            if cls is None:
                report.say('left out', 'gate %s: label %r is not AND, OR, NOT or %s, left out' % (i, d.labels[:1], EQUIV)); return
        elif d.kind in CLASS:
            cls = CLASS[d.kind] + (' multimer' if d.count > 1 and d.kind in MULTIMER else '')
            if DRAWN_AS.get(d.data.get('SBGN class')) == d.kind:
                cls = d.data['SBGN class']
        else:
            report.say('left out', 'node %s: no SBGN glyph for %s, left out' % (i, d.kind)); return
        g = etree.SubElement(parent, S + 'glyph', {'class': cls, 'id': ids[i]})
        q = compartment_of(N, i)
        if q and (d.parent is None or N[d.parent].kind != 'Complex'):
            g.set('compartmentRef', ids[q])
        if i in ports:
            g.set('orientation', ports[i][0])
        annotate(g, i, d)
        name = '' if d.kind in PROCESSES or not d.labels else d.labels[0]
        if d.kind != 'Operator' and name:
            lab = etree.SubElement(g, S + 'label', text=name)
            if d.kind == 'Compartment' and d.label_at:
                lines = name.split('\n')
                bbox(lab, x + d.label_at[0], y + d.label_at[1], max(len(t) for t in lines) * CHAR, len(lines) * LINE)
        elif d.kind == 'Operator' and cls != 'equivalence':
            etree.SubElement(g, S + 'label', text=cls.upper())
        bbox(g, x, y, w, h)
        states, units = decorations(d)
        for k, ((txt, _, _), box) in enumerate(zip(d.states, states)):
            value, _, var = txt.partition('@')
            sv = etree.SubElement(g, S + 'glyph', {'class': 'state variable', 'id': '%s_sv%d' % (ids[i], k)})
            st = etree.SubElement(sv, S + 'state', value=value)
            if var: st.set('variable', var)
            bbox(sv, *box)
        for k, (u, box) in enumerate(units):
            ui = etree.SubElement(g, S + 'glyph', {'class': 'unit of information', 'id': '%s_ui%d' % (ids[i], k)})
            etree.SubElement(ui, S + 'label', text=u)
            bbox(ui, *box)
        for j in kids.get(i, []) if d.kind == 'Complex' else []:
            glyph(g, j)
        if i in ports:
            for k, (px, py) in enumerate(ports[i][1:]):
                etree.SubElement(g, S + 'port', id='%s.%d' % (ids[i], k + 1), x=repr(float(px)), y=repr(float(py)))

    kids = {}
    for i, d in N.items():
        kids.setdefault(d.parent if d.parent in N else None, []).append(i)
    depth = lambda i: 0 if compartment_of(N, i) is None else 1 + depth(compartment_of(N, i))
    order = sorted((i for i, d in N.items() if d.parent is None or N[d.parent].kind != 'Complex'),
                   key=lambda i: (N[i].kind != 'Compartment', depth(i) if N[i].kind == 'Compartment' else 0))
    for i in order:
        glyph(m, i)

    made = {g.get('id') for g in m.iter(S + 'glyph')}
    def crossed(line, s, t):
        ends = {s, t}
        for i in (s, t):
            while N[i].parent is not None:
                i = N[i].parent; ends.add(i)
        xs, ys = [p[0] for p in line], [p[1] for p in line]
        return {i for i, d in N.items() if d.kind != 'Compartment' and i not in ends and (d.parent is None or N[d.parent].kind == 'Compartment')
                and d.box[0] < max(xs) and min(xs) < d.box[0] + d.box[2] and d.box[1] < max(ys) and min(ys) < d.box[1] + d.box[3]
                and any(cuts(p, q, d.box) for p, q in zip(line, line[1:]))}
    for a, cls, s, t, pts, s_at, t_at, _ in arcs:
        if ids[s] not in made or ids[t] not in made:
            continue
        k = 2
        if s in ports and s not in ops and not any(c == 'consumption' and y == s for _, c, _, y, *_ in arcs):
            dist = lambda q: (q[0] - centre(N[t])[0]) ** 2 + (q[1] - centre(N[t])[1]) ** 2
            k = 1 if dist(ports[s][1]) < dist(ports[s][2]) else 2
        src = '%s.%d' % (ids[s], k) if s in ports else ids[s]
        tgt = ids[t] + '.1' if t in ports and cls in ('consumption', 'logic arc') else ids[t]
        p0 = ports[s][k] if s in ports else None
        p1 = ports[t][1] if tgt.endswith('.1') and t in ports else None
        nxt = pts[0] if pts else (p1 or centre(N[t]))
        prv = pts[-1] if pts else (p0 or centre(N[s]))
        if p0 is None:
            p0 = (centre(N[s])[0] + s_at[0], centre(N[s])[1] + s_at[1]) if any(s_at) else border(N[s], nxt)
            if newt and any(s_at) and s not in hubs:
                pts = newt_layout.leaving(N[s], p0, nxt, border(N[s], nxt)) + pts
        if p1 is None:
            p1 = (centre(N[t])[0] + t_at[0], centre(N[t])[1] + t_at[1]) if any(t_at) else border(N[t], prv)
            if newt and any(t_at) and t not in hubs:
                pts = pts + newt_layout.leaving(N[t], p1, prv, border(N[t], prv))
        line = [p0] + pts + [p1]
        if layout == 'advanced' and not newt:
            pts = unbent(line, 0.5)[1:-1]
        else:
            key = [p0] + bends(line) + [p1]
            if crossed(key, s, t) - crossed(line, s, t):
                key = line
            pts = unbent(key, 5)[1:-1]
        if newt:
            pts = newt_layout.unaimed(pts, p0 if s in ports else centre(N[s]), p1 if t in ports else centre(N[t]))
        e = etree.SubElement(m, S + 'arc', {'class': cls, 'id': xml_id(a.id), 'source': src, 'target': tgt})
        if a.dashed:
            note(e, [UNKNOWN])
        etree.SubElement(e, S + 'start', x=repr(float(p0[0])), y=repr(float(p0[1])))
        for q in pts:
            etree.SubElement(e, S + 'next', x=repr(float(q[0])), y=repr(float(q[1])))
        etree.SubElement(e, S + 'end', x=repr(float(p1[0])), y=repr(float(p1[1])))
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')


def text_of(el):
    return ''.join(nt.itertext()) if (nt := el.find(S + 'notes')) is not None else ''


KIND = {v: k for k, v in CLASS.items() if k != 'SourceAndSink'}
KIND.update(association='Process', dissociation='Process')
KIND['perturbing agent'] = 'Phenotype'
KIND['perturbation'] = 'Phenotype'
DRAWN_AS = {'association': 'Process', 'dissociation': 'Process', 'perturbing agent': 'Phenotype', 'perturbation': 'Phenotype'}
HEAD = {'consumption': None, 'logic arc': None, 'production': 'production', 'catalysis': 'catalysis',
        'inhibition': 'inhibition', 'modulation': 'modulation', 'stimulation': 'stimulation',
        'necessary stimulation': 'trigger'}
ACTIVITY = {'macromolecule': 'Macromolecule', 'nucleic acid feature': 'NucleicAcidFeature', 'simple chemical': 'SimpleChemical',
            'unspecified entity': 'UnspecifiedEntity', 'complex': 'Complex', 'perturbation': 'Phenotype'}
HEAD.update({'positive influence': 'stimulation', 'negative influence': 'inhibition', 'unknown influence': 'modulation'})
URN = {v: k for k, v in DB.items()}


def urn(uri):
    if uri.startswith('urn:miriam:'):
        return uri
    m = re.match(r'https?://identifiers\.org/(?:([\w.]+)/|([\w.]+):)?(.+)$', uri, re.I)
    if not m:
        return None
    db, x = m.group(1) or m.group(2), m.group(3)
    if db is None or db.upper() == 'CHEBI':
        return 'urn:miriam:obo.chebi:CHEBI%3A' + x.split(':')[-1] if (db or x).upper().startswith('CHEBI') else None
    return 'urn:miriam:%s:%s' % (URN.get(db, db.lower()), x)


def colour(c, defs):
    v = defs.get(c, c)
    if not v or not v.startswith('#'):
        return None
    v = v.upper()
    return v[:7] if len(v) == 9 and v.endswith('FF') else v


def read(path):
    root = etree.parse(path).getroot()
    for e in root.iter(etree.Element):
        if e.tag.startswith('{http://sbgn.org/libsbgn/'):
            e.tag = S + etree.QName(e).localname
        if e.tag.startswith(R):
            for a in [a for a in e.attrib if a.startswith(R)]:
                e.set(a[len(R):], e.attrib.pop(a))
    m = root.find(S + 'map')
    af = m.get('language') == 'activity flow'
    defs = {c.get('id'): c.get('value') for c in m.iter(R + 'colorDefinition')}
    def style(a, f=str):
        return {i: f(st.find(R + 'g').get(a)) for st in m.iter(R + 'style') if st.find(R + 'g') is not None
                and st.find(R + 'g').get(a) for i in (st.get('idList') or '').split()}
    fill, line, weight, font = style('fill'), style('stroke'), style('stroke-width', float), style('font-size', float)
    line = {i: c for i, c in line.items() if colour(c, defs) != '#000000'}
    port, at_port = {}, {}
    nodes, skipped, activities, renamed = {}, {}, set(), []

    def text(g):
        lab = g.find(S + 'label')
        return lab.get('text', '') if lab is not None else ''

    def glyph(g, parent):
        cls, i = g.get('class'), g.get('id')
        x, y, w, h = (float(g.find(S + 'bbox').get(k)) for k in 'xywh')
        base = cls[:-len(' multimer')] if cls.endswith(' multimer') else cls
        kind = 'Operator' if cls in OPERATORS else KIND.get(base)
        unit = None
        if cls == 'biological activity':
            u = next((c.find(S + 'entity') for c in g.findall(S + 'glyph') if c.get('class') == 'unit of information'), None)
            unit = (u.get('name') or '') if u is not None else ''
            kind = ACTIVITY.get(unit.replace(' multimer', ''), 'Macromolecule')
            activities.add(i)
            if re.search(r'\sactivity\s*$', text(g), re.I):
                g.find(S + 'label').set('text', re.sub(r'\s+activity\s*$', '', text(g), flags=re.I))
                renamed.append(g.get('id'))
        if af and cls == 'submap':
            kind = 'Phenotype'
            for c in g.findall(S + 'glyph'):
                if c.get('class') == 'terminal':
                    port[c.get('id')] = i
        if kind is None:
            skipped.setdefault(cls, []).append(i); return
        for p in g.findall(S + 'port'):
            port[p.get('id')] = i
            at_port[p.get('id')] = (float(p.get('x')), float(p.get('y')))
        states, units = [], []
        for c in g.findall(S + 'glyph'):
            cb = c.find(S + 'bbox')
            if c.get('class') == 'state variable':
                st = c.find(S + 'state')
                v, var = (st.get('value') or '', st.get('variable') or '') if st is not None else ('', '')
                cx, cy = float(cb.get('x')) + float(cb.get('w')) / 2, float(cb.get('y')) + float(cb.get('h')) / 2
                states.append((v + ('@' + var if var else ''), (cx - x - w / 2) / w, (cy - y - h / 2) / h))
            elif c.get('class') == 'unit of information' and (text(c) or cls != 'biological activity'):
                units.append(text(c))
        n = [int(u[2:]) for u in units if re.fullmatch(r'N:\d+', u)]
        lab = g.find(S + 'label')
        lb = lab.find(S + 'bbox') if lab is not None else None
        data = {}
        own = [c for c in g if etree.QName(c).localname in ('extension', 'annotation')]
        for d in (x for c in own for x in c.iter('{%s}Description' % RDF)):
            for q in d:
                urns = [u for u in (urn(li.get('{%s}resource' % RDF) or '') for li in q.iter('{%s}li' % RDF)) if u]
                if urns and etree.QName(q).localname in ('is', 'hasVersion'):
                    data.update(to_properties(etree.QName(q).localname == 'hasVersion', urns))
            break
        data = from_notes(text_of(g), data)
        if cls in DRAWN_AS:
            data['SBGN class'] = cls
        if unit is not None:
            data['SBGN class'] = cls
            if unit:
                data['SBGN unit'] = unit
        nodes[i] = Node(id=i, kind=kind, box=(x, y, w, h), parent=parent,
                        labels=[OPERATORS[cls]] if kind == 'Operator' else [text(g)],
                        fill=colour(fill.get(i), defs), line=colour(line.get(i), defs),
                        weight=weight.get(i),
                        states=states, units=units,
                        count=(n[0] if n else 2) if cls.endswith(' multimer') else 1,
                        label_at=(float(lb.get('x')) - x, float(lb.get('y')) - y) if kind == 'Compartment' and lb is not None else None,
                        data=data, font=font.get(i),
                        small=next((font[c.get('id')] for c in g.findall(S + 'glyph') if c.get('id') in font and
                                    c.get('class') in ('state variable', 'unit of information')), None))
        if g.find(S + 'clone') is not None:
            skipped.setdefault('clone marker', []).append(i)
        for c in g.findall(S + 'glyph'):
            if c.get('class') not in ('state variable', 'unit of information'):
                glyph(c, i if kind == 'Complex' else parent)

    for g in m.findall(S + 'glyph'):
        glyph(g, g.get('compartmentRef'))
    arcs, performers = [], {}
    head = dict(HEAD, **{'equivalence arc': None})
    for a in m.findall(S + 'arc'):
        cls = a.get('class')
        s, t = (port.get(a.get(k), a.get(k)) for k in ('source', 'target'))
        if cls == 'performance arc' and t in activities and s in nodes and s not in activities:
            performers.setdefault(t, []).append((s, a.get('id'))); continue
        if cls not in head or s not in nodes or t not in nodes:
            skipped.setdefault(cls + ' arc' if cls not in head else 'arc to a glyph left out', []).append(a.get('id')); continue
        pts = [(float(p.get('x')), float(p.get('y'))) for p in a.findall(S + 'next')]
        flux = cls in ('consumption', 'logic arc')
        ends = [(float(e.get('x')), float(e.get('y'))) if e is not None else None for e in (a.find(S + 'start'), a.find(S + 'end'))]
        arcs.append(Arc(id=a.get('id'), source=s, target=t, head=head[cls], dashed=UNKNOWN in text_of(a), points=pts,
                        source_at=at(nodes[s], a.get('source'), ends[0], (pts or ends[1:])[0], at_port.get(a.get('source'))),
                        target_at=at(nodes[t], a.get('target'), ends[1], (pts[-1:] or ends[:1])[0], flux and at_port.get(a.get('target')))))
    for t, ps in performers.items():
        if len(ps) > 1:
            skipped.setdefault('performance arc', []).extend(i for _, i in ps); continue
        s = ps[0][0]
        for a in arcs:
            if t in (a.source, a.target):
                a.source, a.target, a.points = s if a.source == t else a.source, s if a.target == t else a.target, []
                a.source_at = a.target_at = (0.0, 0.0)
        report.say('changed', 'activity of %s: drawn as %s, its entity (performance arc)'
                   % (' '.join(nodes[t].labels[0].split()) or t, ' '.join(nodes[s].labels[0].split()) or s))
        del nodes[t]
    kept = [' '.join(nodes[i].labels[0].split()) for i in renamed if i in nodes]
    if kept:
        report.say('changed', '"activity" cut from the label of: %s' % ', '.join(kept))
    for what, ids in skipped.items():
        report.say('left out', '%s: %d left out (%s)' % (what, len(ids), ', '.join(ids[:5]) + (' ...' if len(ids) > 5 else '')))
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)

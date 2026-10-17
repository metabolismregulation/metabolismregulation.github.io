# Write a map (model.py) as SBGN-ML 0.3, the SBGN exchange format (Bergmann et al. 2020,
# doi:10.1515/jib-2020-0016; schema: libsbgn resources/SBGN.xsd). First direction: from yEd
# GraphML. Colours as the SBML render extension on the map (the spec's Appendix B), annotation
# as RDF in each glyph's extension with identifiers.org links in Newt's form (db:id).
# read() at the end goes the other way, also for Newt's .nwt (SBGN-ML with its settings).
import copy, math, os, re
from lxml import etree
from .annotation import from_graphml, to_properties
from .graphml import DELAY, EQUIV, LINE, CHAR, without_delays
from .model import Map, Node, Arc

NS = 'http://sbgn.org/libsbgn/0.3'
RENDER = 'http://www.sbml.org/sbml/level3/version1/render/version1'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
BQBIOL = 'http://biomodels.net/biology-qualifiers/'
S, R = '{%s}' % NS, '{%s}' % RENDER
CLASS = {'Macromolecule': 'macromolecule', 'SimpleChemical': 'simple chemical', 'NucleicAcidFeature': 'nucleic acid feature',
         'UnspecifiedEntity': 'unspecified entity', 'Complex': 'complex', 'Perturbation': 'perturbing agent',
         'Phenotype': 'phenotype', 'SourceAndSink': 'source and sink', 'EmptySet': 'source and sink',
         'Submap': 'submap', 'Compartment': 'compartment', 'Process': 'process', 'OmittedProcess': 'omitted process',
         'UncertainProcess': 'uncertain process'}
MULTIMER = ('Macromolecule', 'SimpleChemical', 'NucleicAcidFeature', 'Complex')
PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess')
OPERATORS = {'and': 'AND', 'or': 'OR', 'not': 'NOT', 'equivalence': EQUIV, 'delay': DELAY}  # SBGN class -> yEd label (delay: Activity Flow)
ARC = {'production': 'production', 'catalysis': 'catalysis', 'inhibition': 'inhibition', 'modulation': 'modulation',
       'stimulation': 'stimulation', 'trigger': 'necessary stimulation'}
# urn:miriam:<db> -> Newt's identifiers.org prefix (annotations-handler.js, dbList)
DB = {'obo.chebi': 'CHEBI', 'hgnc': 'hgnc', 'hgnc.symbol': 'hgnc.symbol', 'uniprot': 'uniprot'}


def xml_id(i):
    # yEd's nested ids (n0::n1) are not XML ids
    return re.sub(r'[^\w.-]', '_', i if re.match(r'[A-Za-z_]', i) else '_' + i)


def centre(d):
    x, y, w, h = d.box
    return x + w / 2, y + h / 2


def border(d, p):
    # where the line from the node's centre to p leaves its box
    (cx, cy), (w, h) = centre(d), d.box[2:]
    dx, dy = p[0] - cx, p[1] - cy
    if not dx and not dy:
        return cx, cy
    t = min(w / 2 / abs(dx) if dx else float('inf'), h / 2 / abs(dy) if dy else float('inf'))
    return cx + t * dx, cy + t * dy


def leave(d, p, q, gap=3):
    # where the line from p (inside the node's box or on it) to q leaves the box, gap px beyond
    # (Newt loses an arc whose bend lies on the node's border)
    x, y, w, h = d.box
    dx, dy = q[0] - p[0], q[1] - p[1]
    ts = [t for t in ((x + w - p[0]) / dx if dx > 0 else (x - p[0]) / dx if dx < 0 else None,
                      (y + h - p[1]) / dy if dy > 0 else (y - p[1]) / dy if dy < 0 else None) if t is not None]
    t = max(0.0, min(ts)) + gap / math.hypot(dx, dy) if ts else 0.0
    return p[0] + t * dx, p[1] + t * dy


def bbox(parent, x, y, w, h):
    etree.SubElement(parent, S + 'bbox', x=repr(float(x)), y=repr(float(y)), w=repr(float(w)), h=repr(float(h)))


def shifted(diagram, margin=20):
    # the map moved so that it starts at the margin: SBGN-ML's origin is its top left corner,
    # yEd's anywhere
    d = copy.deepcopy(diagram)
    dx = margin - min(n.box[0] for n in d.nodes.values())
    dy = margin - min(n.box[1] for n in d.nodes.values())
    for n in d.nodes.values():
        n.box = (n.box[0] + dx, n.box[1] + dy) + tuple(n.box[2:])
    for a in d.arcs:
        a.points = [(x + dx, y + dy) for x, y in a.points]
    return d


def write(diagram):
    diagram = without_delays(shifted(diagram), 'SBGN Process Description')
    N = diagram.nodes
    ids = {i: xml_id(i) for i in N}
    ann = from_graphml(diagram)
    comps = {i for i, d in N.items() if d.kind == 'Compartment'}
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    hubs = {i for i, d in N.items() if d.kind in PROCESSES} | ops
    eq = {i for i in ops if N[i].labels[:1] == [EQUIV]}  # its output, a plain line to the generic entity, keeps its direction

    # arcs in SBGN's direction: a consumption runs from the entity to the process (yEd maps
    # also draw it the other way), a logic arc from the entity into its gate
    arcs = []
    for a in diagram.arcs:
        s, t, pts, s_at, t_at = a.source, a.target, list(a.points), a.source_at, a.target_at
        if a.head is None:
            if s in hubs - eq and t not in hubs:
                s, t, pts, s_at, t_at = t, s, pts[::-1], t_at, s_at
            cls = 'logic arc' if t in ops or s in eq else 'consumption'
        else:
            cls = ARC.get(a.head)
            if cls is None:
                print('arc %s: no SBGN arc for %s, left out' % (a.id, a.head)); continue
        if a.tail:
            print('arc %s: its arrow at the source has no place in SBGN-ML, dropped' % a.id)
        arcs.append((a, cls, s, t, pts, s_at, t_at))

    # a process or gate has two ports, on the line from its inputs to its outputs (the spec,
    # 2.10): port 1 where the consumptions (gate inputs) come in, port 2 where the products leave.
    # An arc comes in from its last bend (glycogen: IRS1 from the left, through a bend below)
    ports = {}
    for p in hubs:
        ins = [pts[-1] if pts else centre(N[s]) for _, c, s, t, pts, *_ in arcs if t == p and c in ('consumption', 'logic arc')]
        outs = [pts[0] if pts else centre(N[t]) for _, c, s, t, pts, *_ in arcs if s == p and (c == 'production' or p in ops)]
        (cx, cy), w, h = centre(N[p]), N[p].box[2], N[p].box[3]
        mean = lambda q, d: (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q)) if q else d
        a, b = mean(ins, (cx, cy)), mean(outs, (cx, cy))
        if a == b:  # reversible (products on both sides): the line through the first two
            q = outs[:2] if len(outs) > 1 else [(cx - 1, cy), (cx + 1, cy)]
            a, b = q[0], q[1]
        vx, vy = b[0] - a[0], b[1] - a[1]
        horizontal = abs(vx) >= abs(vy)
        k = (1 if (vx if horizontal else vy) >= 0 else -1)
        one = (cx - k * w, cy) if horizontal else (cx, cy - k * h)
        two = (cx + k * w, cy) if horizontal else (cx, cy + k * h)
        ports[p] = ('horizontal' if horizontal else 'vertical', one, two)

    root = etree.Element(S + 'sbgn', nsmap={None: NS})
    # language, not version: libsbgn's schema lists no PD version after 1.3
    m = etree.SubElement(root, S + 'map', id=xml_id(diagram.name.replace('-', '_')), language='process description')

    # colours: one render style per fill
    fills = {}
    for i, d in N.items():
        if d.fill:
            fills.setdefault(d.fill.lower(), []).append(ids[i])
    if fills:
        ri = etree.SubElement(etree.SubElement(m, S + 'extension'), R + 'renderInformation', nsmap={None: RENDER},
                              id='renderInformation')
        cd = etree.SubElement(ri, R + 'listOfColorDefinitions')
        etree.SubElement(cd, R + 'colorDefinition', id='black', value='#000000')
        st = etree.SubElement(ri, R + 'listOfStyles')
        for k, (f, members) in enumerate(fills.items()):
            etree.SubElement(cd, R + 'colorDefinition', id='color_%d' % k, value=f)
            s = etree.SubElement(st, R + 'style', id='style_%d' % k, idList=' '.join(members))
            etree.SubElement(s, R + 'g', stroke='black', fill='color_%d' % k)
            s.find(R + 'g').set('stroke-width', '1')

    def annotate(g, i, d):
        lab = ' '.join(d.labels[0].split()) if d.labels else ''
        if lab not in ann or d.kind not in CLASS or d.kind in PROCESSES:
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

    def compartment(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return q

    def glyph(parent, i):
        d = N[i]
        x, y, w, h = d.box
        if d.kind == 'Operator':
            cls = {v: k for k, v in OPERATORS.items()}.get((d.labels[0] if d.labels else '').strip().upper())
            if cls is None:
                print('gate %s: label %r is not AND, OR, NOT or %s, left out' % (i, d.labels[:1], EQUIV)); return
        elif d.kind in CLASS:
            cls = CLASS[d.kind] + (' multimer' if d.count > 1 and d.kind in MULTIMER else '')
        else:
            print('node %s: no SBGN glyph for %s, left out' % (i, d.kind)); return
        g = etree.SubElement(parent, S + 'glyph', {'class': cls, 'id': ids[i]})
        q = compartment(i)
        if q and d.kind not in ('Compartment', 'Operator') + PROCESSES and N[d.parent].kind != 'Complex':
            g.set('compartmentRef', ids[q])
        if i in ports:
            g.set('orientation', ports[i][0])
        annotate(g, i, d)
        name = '' if d.kind in PROCESSES or not d.labels else d.labels[0]  # a second label is a unit (N:2)
        if d.kind != 'Operator' and name:
            lab = etree.SubElement(g, S + 'label', text=name)
            if d.kind == 'Compartment' and d.label_at:
                lines = name.split('\n')
                bbox(lab, x + d.label_at[0], y + d.label_at[1], max(len(t) for t in lines) * CHAR, len(lines) * LINE)
        elif d.kind == 'Operator' and cls != 'equivalence':  # the equivalence glyph has no label (the spec, 2.9.4)
            etree.SubElement(g, S + 'label', text=cls.upper())
        bbox(g, x, y, w, h)
        cx, cy = centre(d)
        for k, (txt, rx, ry) in enumerate(d.states):
            value, _, var = txt.partition('@')
            sv = etree.SubElement(g, S + 'glyph', {'class': 'state variable', 'id': '%s_sv%d' % (ids[i], k)})
            st = etree.SubElement(sv, S + 'state', value=value)
            if var: st.set('variable', var)
            sw = 15.0 if len(txt) <= 2 else 45.0  # as yEd's icons on our maps
            bbox(sv, cx + rx * w - sw / 2, cy + ry * h - 7.5, sw, 15)
        units = d.units + (['N:%d' % d.count] if d.count > 2 and not any(re.fullmatch(r'N:\d+', u) for u in d.units) else [])
        for k, u in enumerate(units):
            ui = etree.SubElement(g, S + 'glyph', {'class': 'unit of information', 'id': '%s_ui%d' % (ids[i], k)})
            etree.SubElement(ui, S + 'label', text=u)
            uw = max(15.0, len(u) * 7.0)
            bbox(ui, x + (k + 1) / (len(units) + 1) * w - uw / 2, y - 7.5, uw, 15)
        for j in kids.get(i, []) if d.kind == 'Complex' else []:
            glyph(g, j)
        if i in ports:
            for k, (px, py) in enumerate(ports[i][1:]):
                etree.SubElement(g, S + 'port', id='%s.%d' % (ids[i], k + 1), x=repr(float(px)), y=repr(float(py)))

    kids = {}
    for i, d in N.items():
        kids.setdefault(d.parent if d.parent in N else None, []).append(i)
    # compartments first (drawn under the rest), then every node outside a complex
    order = sorted((i for i, d in N.items() if d.parent is None or N[d.parent].kind != 'Complex'),
                   key=lambda i: N[i].kind != 'Compartment')
    for i in order:
        glyph(m, i)

    made = {g.get('id') for g in m.iter(S + 'glyph')}
    for a, cls, s, t, pts, s_at, t_at in arcs:
        if ids[s] not in made or ids[t] not in made:
            continue
        # the ends: a process's or gate's port on its flux side, else where the arc meets the
        # node's border (a yEd port: its own point)
        # a product leaves by port 2; of a reversible process (no consumption), by the nearer port
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
        # Newt draws only the bends and aims the ends at the node's centre: an end at a yEd port
        # gets a bend where the arc leaves the node, so the line keeps yEd's course (eNOS: arcs
        # level with the process, at a complex's side)
        if p0 is None:
            p0 = (centre(N[s])[0] + s_at[0], centre(N[s])[1] + s_at[1]) if any(s_at) else border(N[s], nxt)
            q = leave(N[s], p0, nxt)
            if any(s_at) and s not in hubs and math.dist(q, border(N[s], nxt)) > 5:
                pts = [q] + pts
        if p1 is None:
            p1 = (centre(N[t])[0] + t_at[0], centre(N[t])[1] + t_at[1]) if any(t_at) else border(N[t], prv)
            q = leave(N[t], p1, prv)
            if any(t_at) and t not in hubs and math.dist(q, border(N[t], prv)) > 5:
                pts = pts + [q]
        e = etree.SubElement(m, S + 'arc', {'class': cls, 'id': xml_id(a.id), 'source': src, 'target': tgt})
        etree.SubElement(e, S + 'start', x=repr(float(p0[0])), y=repr(float(p0[1])))
        for q in pts:
            etree.SubElement(e, S + 'next', x=repr(float(q[0])), y=repr(float(q[1])))
        etree.SubElement(e, S + 'end', x=repr(float(p1[0])), y=repr(float(p1[1])))
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')


# --- reading SBGN-ML (and Newt's .nwt) into the map model (docs/SBGNML.md, "The way back")
KIND = {v: k for k, v in CLASS.items() if k != 'SourceAndSink'}  # source and sink: yEd's EmptySet
KIND.update(association='Process', dissociation='Process')  # read as the generic process (MINERVA, Newt)
HEAD = {'consumption': None, 'logic arc': None, 'production': 'production', 'catalysis': 'catalysis',
        'inhibition': 'inhibition', 'modulation': 'modulation', 'stimulation': 'stimulation',
        'necessary stimulation': 'trigger'}
# Activity Flow (L1V1.2, read only; user, 2026-10-17): an activity is drawn as the entity it comes
# from, CellDesigner's way. Its unit of information's shape gives the glyph (none: a protein;
# perturbation: phenotype, as in CellDesigner), its label (the molecule's name) stays a unit; the
# influences are arcs between entities; a delay is an Operator labelled tau; a submap is a phenotype
# with its name (its terminals, tags and equivalence arcs left out)
ACTIVITY = {'macromolecule': 'Macromolecule', 'nucleic acid feature': 'NucleicAcidFeature', 'simple chemical': 'SimpleChemical',
            'unspecified entity': 'UnspecifiedEntity', 'complex': 'Complex', 'perturbation': 'Phenotype'}
HEAD.update({'positive influence': 'stimulation', 'negative influence': 'inhibition', 'unknown influence': 'modulation'})
URN = {v: k for k, v in DB.items()}


def urn(uri):
    # an identifiers.org link (db:id, or the older db/id) or a MIRIAM URN as a MIRIAM URN
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
    # a render colour (an id or #RRGGBB[AA]) as yEd writes it: #RRGGBB, #RRGGBBAA when not opaque
    v = defs.get(c, c)
    if not v or not v.startswith('#'):
        return None
    v = v.upper()
    return v[:7] if len(v) == 9 and v.endswith('FF') else v


def read(path):
    root = etree.parse(path).getroot()
    for e in root.iter(etree.Element):  # libsbgn 0.1 and 0.2 files: the same elements in an older namespace
        if e.tag.startswith('{http://sbgn.org/libsbgn/'):
            e.tag = S + etree.QName(e).localname
    m = root.find(S + 'map')
    af = m.get('language') == 'activity flow'
    defs = {c.get('id'): c.get('value') for c in m.iter(R + 'colorDefinition')}
    fill = {i: st.find(R + 'g').get('fill') for st in m.iter(R + 'style') if st.find(R + 'g') is not None
            for i in (st.get('idList') or '').split()}
    port = {}
    nodes, skipped = {}, {}

    def text(g):
        lab = g.find(S + 'label')
        return lab.get('text', '') if lab is not None else ''

    def glyph(g, parent):
        cls, i = g.get('class'), g.get('id')
        x, y, w, h = (float(g.find(S + 'bbox').get(k)) for k in 'xywh')
        base = cls[:-len(' multimer')] if cls.endswith(' multimer') else cls
        kind = 'Operator' if cls in OPERATORS else KIND.get(base)
        if cls == 'biological activity':
            u = next((c.find(S + 'entity') for c in g.findall(S + 'glyph') if c.get('class') == 'unit of information'), None)
            kind = ACTIVITY.get((u.get('name') if u is not None else '').replace(' multimer', ''), 'Macromolecule')
        if af and cls == 'submap':  # a phenotype with the submap's name, no terminals or tags (user, 2026-10-17)
            kind = 'Phenotype'
            for c in g.findall(S + 'glyph'):
                if c.get('class') == 'terminal':
                    port[c.get('id')] = i
        if kind is None:  # tag, annotation and the other glyphs our maps do not draw
            skipped.setdefault(cls, []).append(i); return
        for p in g.findall(S + 'port'):
            port[p.get('id')] = i
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
        for d in g.iter('{%s}Description' % RDF):
            for q in d:
                urns = [u for u in (urn(li.get('{%s}resource' % RDF) or '') for li in q.iter('{%s}li' % RDF)) if u]
                if urns and etree.QName(q).localname in ('is', 'hasVersion'):
                    data.update(to_properties(etree.QName(q).localname == 'hasVersion', urns))
            break  # the glyph's own description
        nodes[i] = Node(id=i, kind=kind, box=(x, y, w, h), parent=parent,
                        labels=[OPERATORS[cls]] if kind == 'Operator' else [text(g)],
                        fill=colour(fill.get(i), defs), states=states, units=units,
                        count=(n[0] if n else 2) if cls.endswith(' multimer') else 1,
                        label_at=(float(lb.get('x')) - x, float(lb.get('y')) - y) if kind == 'Compartment' and lb is not None else None,
                        data=data)
        if g.find(S + 'clone') is not None:
            skipped.setdefault('clone marker', []).append(i)
        for c in g.findall(S + 'glyph'):
            if c.get('class') not in ('state variable', 'unit of information'):
                glyph(c, i)  # a complex's members

    for g in m.findall(S + 'glyph'):
        glyph(g, g.get('compartmentRef'))
    arcs = []
    for a in m.findall(S + 'arc'):
        cls = a.get('class')
        s, t = (port.get(a.get(k), a.get(k)) for k in ('source', 'target'))
        if cls not in HEAD or s not in nodes or t not in nodes:
            skipped.setdefault(cls + ' arc' if cls not in HEAD else 'arc to a glyph left out', []).append(a.get('id')); continue
        arcs.append(Arc(id=a.get('id'), source=s, target=t, head=HEAD[cls],
                        points=[(float(p.get('x')), float(p.get('y'))) for p in a.findall(S + 'next')]))
    for what, ids in skipped.items():
        print('%s: %d left out (%s)' % (what, len(ids), ', '.join(ids[:5]) + (' ...' if len(ids) > 5 else '')))
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)

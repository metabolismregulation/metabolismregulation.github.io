# Read a yEd GraphML map drawn with the SBGN palette into the map model, and write one.
import copy, math, os, re
from dataclasses import replace
from lxml import etree
from . import report
from .model import Map, Node, Arc
from .style import scale_of

NS = {'g': 'http://graphml.graphdrawing.org/xmlns', 'y': 'http://www.yworks.com/xml/graphml'}
Y = '{%s}' % NS['y']
# yEd target arrow -> glyph at the arc's target (no arrow: None; any other arrow: production)
HEAD = {'white_circle': 'catalysis', 't_shape': 'inhibition', 'white_diamond': 'modulation',
        'white_delta': 'stimulation', 'white_delta_bar': 'trigger',
        'crows_foot_one': 'inhibition'}  # a bar like t_shape, from yEd's other arrows (AsthMap)
# plain yEd shapes (not the SBGN palette) read by their outline (user, 2026-10-16; AsthMap):
# a plain ellipse holding other nodes is an oval compartment (a cell), one labelled AND, OR or
# NOT a logic gate
# yEd's SBGN palette has no omitted or uncertain process: a Process labelled \\ or ? (user's example)
PROCESS_LABEL = {'\\\\': 'OmittedProcess', '?': 'UncertainProcess'}
OUTLINE = {'ShapeNode roundrectangle': 'Macromolecule', 'GenericNode com.yworks.flowchart.terminator': 'SimpleChemical',
           'ShapeNode ellipse': 'UnspecifiedEntity', 'ShapeNode rectangle': 'Phenotype', 'ShapeNode hexagon': 'Phenotype'}


def realizer(n):
    # the node's shape (GenericNode for the SBGN palette, ShapeNode and others from other
    # palettes), or the shown realizer of a group (complex, compartment)
    gn = n.find('g:data/*[y:Geometry]', NS)
    return gn if gn is not None else n.find('g:data/y:ProxyAutoBoundsNode/y:Realizers/*', NS)


def kind_of(n, gn):
    # the SBGN glyph; a plain group is a compartment; anything else is named by its yEd shape
    # ("ShapeNode ellipse"), for the rules to report
    conf = gn.get('configuration') or ''
    if conf.startswith('com.yworks.sbgn.'):
        return conf[len('com.yworks.sbgn.'):]
    if n.find('g:graph', NS) is not None and etree.QName(gn).localname == 'GroupNode':
        return 'Compartment'
    shape = gn.find('y:Shape', NS)
    return ' '.join(x for x in (etree.QName(gn).localname, conf, shape.get('type') if shape is not None else '') if x)


def text(r):
    return ''.join(x.text or '' for x in r.iter(Y + 'NodeLabel')).strip()


def states(gn, res):
    # state variable icons: (text, rx, ry); units of information are icons too, but not state variables
    out = []
    for l in gn.findall('y:NodeLabel', NS):
        r = res.get(l.get('iconData'))
        if r is None or r.find('.//y:GenericNode[@configuration="com.yworks.sbgn.StateVariable"]', NS) is None:
            continue
        # the icon's text, or the label's own text drawn over a blank icon (glycogen IRS1/2 "P")
        p = l.find('.//y:SmartNodeLabelModelParameter', NS)
        out.append((text(r) or (l.text or '').strip(), float(p.get('nodeRatioX')), float(p.get('nodeRatioY'))))
    return out


def units(gn, res):
    # units of information (ct:gene, ct:mRNA, N:4): icons, or a second, boxed label (iNOS ASL: "N:4")
    out = []
    for l in gn.findall('y:NodeLabel', NS)[1:]:
        if (l.text or '').strip() and not l.get('iconData'):
            out.append(l.text.strip()); continue
        r = res.get(l.get('iconData'))
        # a plain box (iNOS) or yEd's SBGN unit of information glyph (ACLY ct:gene, ct:mRNA)
        if r is None or (r.find('.//y:ShapeNode', NS) is None and
                         r.find('.//y:GenericNode[@configuration="com.yworks.sbgn.UnitOfInformation"]', NS) is None):
            continue
        out.append(text(r))
    return out


def count(gn, us):
    # the multimer count: N in the N:x unit of information, else yEd's mcount (the number of
    # shapes drawn, always 2) for a multimer, 1 for a single unit
    p = gn.find('y:StyleProperties/y:Property[@name="com.yworks.sbgn.style.mcount"]', NS)
    if p is None:
        return 1
    n = [int(u[2:]) for u in us if re.fullmatch(r'N:\d+', u)]
    return n[0] if n else int(p.get('value'))


def ovals(nodes):
    # a plain ellipse with other nodes' centres inside it is an oval compartment; a node with no
    # parent belongs to the smallest one around it
    cen = lambda d: (d.box[0] + d.box[2] / 2, d.box[1] + d.box[3] / 2)
    def holds(o, d):
        (cx, cy), (x, y) = cen(o), cen(d)
        return ((x - cx) / (o.box[2] / 2)) ** 2 + ((y - cy) / (o.box[3] / 2)) ** 2 <= 1
    flat = [d for d in nodes.values() if d.parent is None]
    for o in [d for d in flat if d.outline == 'ShapeNode ellipse' and d.kind == 'UnspecifiedEntity']:
        if any(d is not o and d.box[2] * d.box[3] < o.box[2] * o.box[3] and holds(o, d) for d in flat):
            o.kind = 'Compartment'
    cells = [d for d in flat if d.kind == 'Compartment' and d.outline]
    for d in flat:
        around = [o for o in cells if o is not d and o.box[2] * o.box[3] > d.box[2] * d.box[3] and holds(o, d)]
        if around:
            d.parent = min(around, key=lambda o: o.box[2] * o.box[3]).id


def read(path):
    root = etree.parse(path).getroot()
    res = {r.get('id'): r for r in root.iter(Y + 'Resource')}
    names = {k.get('id'): k.get('attr.name') for k in root.findall('g:key', NS) if k.get('for') == 'node' and k.get('attr.name')}
    nodes = {}
    for n in root.iter('{%s}node' % NS['g']):
        gn = realizer(n)
        kind = kind_of(n, gn)
        geo = gn.find('y:Geometry', NS)
        labs = gn.findall('y:NodeLabel', NS)
        fill = gn.find('y:Fill', NS)
        p = n.getparent().getparent()
        us = units(gn, res)
        # a compartment's name: the first label with text
        l = next((l for l in labs if (l.text or '').strip()), None)
        border = gn.find('y:BorderStyle', NS)

        def small(q):  # a state variable's or unit's font size: its label's own text, else its icon's
            if (q.text or '').strip():
                return q.get('fontSize')
            return next((x.get('fontSize') for x in (res[q.get('iconData')].iter(Y + 'NodeLabel') if q.get('iconData') in res else ())
                         if (x.text or '').strip()), None)
        if kind == 'Process' and l is not None:
            kind = PROCESS_LABEL.get(l.text.strip(), kind)
        if kind == 'Submap':  # our maps' phenotype, as in CellDesigner (user, 2026-10-21: SREBP's two submap glyphs)
            kind = 'Phenotype'
        outline = kind if kind in OUTLINE else None
        if outline:
            kind = 'Operator' if (l is not None and l.text.strip() in ('AND', 'OR', 'NOT') and 'ellipse' in outline) else OUTLINE[outline]
        nodes[n.get('id')] = Node(
            id=n.get('id'), kind=kind, outline=outline, box=tuple(float(geo.get(a)) for a in ('x', 'y', 'width', 'height')),
            labels=[(l.text or '').strip() for l in labs if not l.get('iconData')],
            parent=p.get('id') if p.tag.endswith('node') else None,
            fill=fill.get('color') if fill is not None else None,
            states=states(gn, res), units=us, count=count(gn, us),
            label_at=(float(l.get('x')), float(l.get('y'))) if (kind == 'Compartment' or outline) and l is not None else None,
            data={names[x.get('key')]: x.text.strip() for x in n.findall('g:data', NS)
                  if x.get('key') in names and (x.text or '').strip()},
            dashed=border is not None and border.get('type') != 'line',
            font=float(l.get('fontSize')) if l is not None and l.get('fontSize') else None,  # kept on conversion (user, 2026-10-28)
            small=next((float(f) for f in map(small, labs[1:]) if f), None))
    ovals(nodes)
    for d in nodes.values():
        if d.kind != 'Compartment':
            d.label_at = None
    arcs = []
    for e in root.iter('{%s}edge' % NS['g']):
        pl = e.find('g:data/*[y:Path]', NS)  # PolyLineEdge in the SBGN palette; curves too
        a = pl.find('y:Arrows', NS)
        head = a.get('target')
        yp = pl.find('y:Path', NS)
        arcs.append(Arc(id=e.get('id'), source=e.get('source'), target=e.get('target'),
                        # another arrow is kept by its yEd name, for the rules to report
                        head=None if head in ('none', None) else HEAD.get(head, 'production' if head == 'delta' else 'arrow ' + head),
                        tail=a.get('source') not in ('none', None),
                        points=[(float(q.get('x')), float(q.get('y'))) for q in yp.findall('y:Point', NS)],
                        source_at=(float(yp.get('sx')), float(yp.get('sy'))),
                        target_at=(float(yp.get('tx')), float(yp.get('ty'))),
                        dashed=pl.find('y:LineStyle', NS).get('type') != 'line'))
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)


# --- writing: every element is a copy of a template cut from our yEd files (yed.graphml)
G = '{%s}' % NS['g']
ARROW = {v: k for k, v in HEAD.items() if k != 'crows_foot_one'}  # AsthMap's bar is read, never written
ARROW['production'] = 'delta'
EQUIV = '≡'  # the equivalence operator's label in yEd's SBGN palette (user's file, 2026-10-17)
DELAY = 'τ'  # Activity Flow's delay: an Operator labelled tau, drawn as the equivalence (user, 2026-10-17)


def without_delays(m, form):
    # for a format with no delay (CellDesigner, SBGN PD): its input joined straight to its target,
    # with the type of the arc out of it
    ds = {i for i, d in m.nodes.items() if d.kind == 'Operator' and d.labels[:1] == [DELAY]}
    if not ds:
        return m
    report.say('changed', 'delay: no %s form, its input joined to its target (%s)' % (form, ', '.join(sorted(ds))))
    arcs = [a for a in m.arcs if a.source not in ds and a.target not in ds]
    for d in ds:
        outs = [a for a in m.arcs if a.source == d and (a.head or m.nodes[a.target].kind == 'Operator')]
        ins = [a.target if a.source == d else a.source for a in m.arcs if d in (a.source, a.target) and a not in outs]
        arcs += [replace(o, id='%s_%s' % (o.id, i), source=i, points=[], source_at=(0.0, 0.0)) for o in outs for i in ins]
    return replace(m, nodes={i: d for i, d in m.nodes.items() if i not in ds}, arcs=arcs)


LINE, CHAR = 16.5, 9.5  # a label line's height and a character's width at font size 14 (our maps)
ICON_CHAR = 5.4  # a character's width in a state variable or unit of information (Dialog 10)


def _label(l, text, w, h, k=1.0):
    # the label's text, its box estimated and centred (yEd measures it again when the text is edited);
    # k: the font size against our 14
    lines = text.split('\n') if text else []
    lw, lh = max([len(x) for x in lines] or [0]) * CHAR * k, len(lines) * LINE * k + 4
    l.text = text or None
    l.set('hasText', 'true' if text else 'false')
    for k, v in (('width', lw), ('height', lh), ('x', (w - lw) / 2), ('y', (h - lh) / 2)):
        l.set(k, repr(float(v)))


def corrected(m):
    # a map that looks like SBGN but is drawn with other shapes (read by their outline), redrawn
    # with the SBGN palette (user, 2026-10-17: <map>-corrected.graphml); None for a map already in it
    return write(m, soft=True) if any(d.outline for d in m.nodes.values()) else None


def write(diagram, soft=False):
    # the font follows the map's scale: 14 on our protein height (40), so Newt's 30 high gives 11
    font = round(14 * scale_of(diagram) + 0.01)
    t = etree.parse(os.path.join(os.path.dirname(__file__), 'yed.graphml')).getroot()
    tpl = {n.get('id'): n for n in t.iter(G + 'node')}
    icon = tpl['IconLabel'].find('.//y:NodeLabel', NS)
    arc = next(t.iter(G + 'edge'))
    res_tpl = {r.get('id'): r for r in t.iter(Y + 'Resource')}
    N = diagram.nodes
    names = list(dict.fromkeys(k for d in N.values() for k in d.data))
    root = etree.Element(G + 'graphml', nsmap={None: NS['g'], 'y': NS['y'], 'yed': 'http://www.yworks.com/xml/yed/3'})
    for k, name in enumerate(names):
        etree.SubElement(root, G + 'key', {'attr.name': name, 'attr.type': 'string', 'for': 'node', 'id': 'd%d' % k})
    for kid, f, y in (('ng', 'node', 'nodegraphics'), ('res', 'graphml', 'resources'), ('eg', 'edge', 'edgegraphics')):
        etree.SubElement(root, G + 'key', {'for': f, 'id': kid, 'yfiles.type': y})
    resources, rid, size = [], {}, {}

    def resource(kind, text, small=None):  # one icon per kind, text and font size, shared as yEd shares them
        if (kind, text, small) not in rid:
            r = copy.deepcopy(res_tpl[kind]); rid[kind, text, small] = str(len(rid) + 1); r.set('id', rid[kind, text, small])
            gn = r.find('.//y:GenericNode', NS)
            # as in our maps (user, 2026-10-22): a state variable of up to two letters an 18 x 18 circle,
            # a longer one a capsule 18 high, a unit of information 16 high; text 10, centred. Another
            # size from the source (user, 2026-10-28) kept, the icon grown or shrunk with it
            k = (small or 10) / 10
            if kind == 'StateVariable':
                w, h = (18.0 * k, 18.0 * k) if len(text) <= 2 else (float(math.ceil(len(text) * ICON_CHAR * k + 12 * k)), 18.0 * k)
            else:
                w, h = float(math.ceil(len(text) * ICON_CHAR * k + 8 * k)), 16.0 * k
            gn.find('y:Geometry', NS).set('width', repr(w)); gn.find('y:Geometry', NS).set('height', repr(h))
            if small:
                gn.find('y:NodeLabel', NS).set('fontSize', '%g' % small)
            _label(gn.find('y:NodeLabel', NS), text, w, h, k * 10 / 14)
            size[rid[kind, text, small]] = w, h
            resources.append(r)
        return rid[kind, text, small]

    kids = {}
    for i, d in N.items():
        kids.setdefault(d.parent if d.parent in N else None, []).append(i)

    missing = {}
    def node(parent, i):
        d = N[i]
        group = bool(kids.get(i)) or d.kind == 'Compartment'
        name = 'ComplexGroup' if group and d.kind == 'Complex' else 'Process' if d.kind in PROCESS_LABEL.values() else d.kind
        if name not in tpl:  # a glyph none of our yEd files has: no template to copy
            missing.setdefault(d.kind, []).append(i); return
        n = copy.deepcopy(tpl[name])
        n.set('id', i)
        parent.append(n)
        for k, name in enumerate(names):
            if d.data.get(name):
                x = etree.Element(G + 'data', key='d%d' % k); x.text = d.data[name]; n.insert(k, x)
        gn = realizer(n)
        x, y, w, h = d.box
        for k, v in zip(('x', 'y', 'width', 'height'), d.box):
            gn.find('y:Geometry', NS).set(k, repr(float(v)))
        fill = gn.find('y:Fill', NS)
        if d.fill: fill.set('color', d.fill)
        else: del fill.attrib['color']; fill.set('hasColor', 'false')  # no fill (aspirin's drugs)
        if d.dashed: gn.find('y:BorderStyle', NS).set('type', 'dashed')
        if not d.border: gn.find('y:BorderStyle', NS).set('hasColor', 'false')
        l = gn.find('y:NodeLabel', NS)
        sign = {v: k for k, v in PROCESS_LABEL.items()}.get(d.kind)
        fs = d.font or font  # the source's own size (CellDesigner, Newt; user, 2026-10-28), else the map's
        if not sign and (d.font or font != 14):
            l.set('fontSize', '%g' % fs)
        _label(l, sign or next((x for x in d.labels if x), ''), w, h, fs / 14)  # the name; a second label is a unit (N:4)
        if d.kind == 'Operator' and l.text in (EQUIV, DELAY):  # as yEd's palette draws the equivalence
            l.set('fontFamily', 'Monospaced'); l.set('fontSize', '18')
        if d.kind == 'Compartment':  # its name where the source has it, else centred at the top (the template's place)
            lx, ly = d.label_at or (float(l.get('x')), 0.0)
            l.set('x', repr(float(lx))); l.set('y', repr(float(ly)))
        for c in n.findall('g:data/y:ProxyAutoBoundsNode/y:Realizers/*', NS)[1:]:  # folded in yEd: its own name, not the template's
            c.find('y:NodeLabel', NS).text = l.text
        if group and d.kind == 'Complex':  # a complex's name at the bottom, as CellDesigner draws it (user, 2026-10-25)
            l.set('modelPosition', 'b'); l.set('borderDistance', '0.0'); l.set('y', repr(h - float(l.get('height'))))
        if d.count > 1:  # yEd draws a multimer as two shapes; N:x says how many
            sp = gn.find('y:StyleProperties', NS)
            if sp is None:  # the simple chemical template has none (a multimer Ca2+, O2)
                sp = etree.SubElement(gn, Y + 'StyleProperties')
            etree.SubElement(sp, Y + 'Property', {'class': 'java.lang.Integer', 'name': 'com.yworks.sbgn.style.mcount', 'value': '2'})
        units = d.units + (['N:%d' % d.count] if d.count > 2 and not any(re.fullmatch(r'N:\d+', u) for u in d.units) else [])
        icons = [('StateVariable', txt, rx, ry) for txt, rx, ry in d.states]
        icons += [('UnitOfInformation', u, (k + 1) / (len(units) + 1) - 0.5, -0.5) for k, u in enumerate(units)]
        for kind, txt, rx, ry in icons:
            il = copy.deepcopy(icon); il.set('iconData', resource(kind, txt, d.small))
            p = il.find('.//y:SmartNodeLabelModelParameter', NS)
            p.set('nodeRatioX', repr(float(rx))); p.set('nodeRatioY', repr(float(ry)))
            iw, ih = size[il.get('iconData')]  # the label is the icon, centred on its point of the border
            for k, v in (('width', iw), ('height', ih), ('x', (0.5 + rx) * w - iw / 2), ('y', (0.5 + ry) * h - ih / 2)):
                il.set(k, repr(float(v)))
            gn.findall('y:NodeLabel', NS)[-1].addnext(il)
        if group:
            sub = n.find('g:graph', NS); sub.set('id', i + ':')
            for j in kids.get(i, []):
                node(sub, j)

    g = etree.SubElement(root, G + 'graph', edgedefault='directed', id='G')
    for i in kids.get(None, []):
        node(g, i)
    for k, ids in missing.items():
        report.say('left out', 'no yEd template for %s: %d nodes left out (%s)' % (k, len(ids), ', '.join(N[i].labels[0] or i for i in ids)))
    gone = {i for ids in missing.values() for i in ids}
    for a in diagram.arcs:
        if a.source in gone or a.target in gone:
            continue
        e = copy.deepcopy(arc)
        e.set('id', a.id); e.set('source', a.source); e.set('target', a.target)
        pl = e.find('.//y:PolyLineEdge', NS)
        yp = pl.find('y:Path', NS)
        for k, v in zip(('sx', 'sy', 'tx', 'ty'), a.source_at + a.target_at):
            yp.set(k, repr(float(v)))
        for q in a.points:
            etree.SubElement(yp, Y + 'Point', x=repr(float(q[0])), y=repr(float(q[1])))
        if a.dashed: pl.find('y:LineStyle', NS).set('type', 'dashed')
        pl.find('y:Arrows', NS).set('target', ARROW[a.head] if a.head else 'none')
        pl.find('y:Arrows', NS).set('source', 'delta' if a.tail else 'none')
        if soft:  # soft bends on a map from yEd (user, 2026-10-14); from CellDesigner or Newt as they draw them, sharp (user, 2026-10-28)
            pl.find('y:BendStyle', NS).set('smoothed', 'true')
        g.append(e)
    rs = etree.SubElement(etree.SubElement(root, G + 'data', key='res'), Y + 'Resources')
    rs.extend(resources)
    etree.cleanup_namespaces(root)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')

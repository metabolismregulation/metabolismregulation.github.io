# Read a yEd GraphML map drawn with the SBGN palette into the map model, and write one.
import copy, os, re
from lxml import etree
from .model import Map, Node, Arc

NS = {'g': 'http://graphml.graphdrawing.org/xmlns', 'y': 'http://www.yworks.com/xml/graphml'}
Y = '{%s}' % NS['y']
# yEd target arrow -> glyph at the arc's target (no arrow: None; any other arrow: production)
HEAD = {'white_circle': 'catalysis', 't_shape': 'inhibition', 'white_diamond': 'modulation',
        'white_delta': 'stimulation', 'white_delta_bar': 'trigger'}


def realizer(n):
    # the node's GenericNode, or the shown realizer of a group (complex, compartment)
    gn = n.find('g:data/y:GenericNode', NS)
    return gn if gn is not None else n.find('g:data/y:ProxyAutoBoundsNode/y:Realizers/*', NS)


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


def read(path):
    root = etree.parse(path).getroot()
    res = {r.get('id'): r for r in root.iter(Y + 'Resource')}
    names = {k.get('id'): k.get('attr.name') for k in root.findall('g:key', NS) if k.get('for') == 'node' and k.get('attr.name')}
    nodes = {}
    for n in root.iter('{%s}node' % NS['g']):
        gn = realizer(n)
        group = n.find('g:data/y:GenericNode', NS) is None
        kind = (gn.get('configuration') or '').replace('com.yworks.sbgn.', '')
        if group and not kind:
            kind = 'Compartment'
        geo = gn.find('y:Geometry', NS)
        labs = gn.findall('y:NodeLabel', NS)
        fill = gn.find('y:Fill', NS)
        p = n.getparent().getparent()
        us = units(gn, res)
        # a compartment's name: the first label with text
        l = next((l for l in labs if (l.text or '').strip()), None)
        border = gn.find('y:BorderStyle', NS)
        nodes[n.get('id')] = Node(
            id=n.get('id'), kind=kind, box=tuple(float(geo.get(a)) for a in ('x', 'y', 'width', 'height')),
            labels=[(l.text or '').strip() for l in labs if not l.get('iconData')],
            parent=p.get('id') if p.tag.endswith('node') else None,
            fill=fill.get('color') if fill is not None else None,
            states=states(gn, res), units=us, count=count(gn, us),
            label_at=(float(l.get('x')), float(l.get('y'))) if kind == 'Compartment' and l is not None else None,
            data={names[x.get('key')]: x.text.strip() for x in n.findall('g:data', NS)
                  if x.get('key') in names and (x.text or '').strip()},
            dashed=border is not None and border.get('type') != 'line')
    arcs = []
    for e in root.iter('{%s}edge' % NS['g']):
        pl = e.find('g:data/y:PolyLineEdge', NS)
        a = pl.find('y:Arrows', NS)
        head = a.get('target')
        yp = pl.find('y:Path', NS)
        arcs.append(Arc(id=e.get('id'), source=e.get('source'), target=e.get('target'),
                        head=None if head in ('none', None) else HEAD.get(head, 'production'),
                        tail=a.get('source') not in ('none', None),
                        points=[(float(q.get('x')), float(q.get('y'))) for q in yp.findall('y:Point', NS)],
                        source_at=(float(yp.get('sx')), float(yp.get('sy'))),
                        target_at=(float(yp.get('tx')), float(yp.get('ty'))),
                        dashed=pl.find('y:LineStyle', NS).get('type') != 'line'))
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)


# --- writing: every element is a copy of a template cut from our yEd files (yed.graphml)
G = '{%s}' % NS['g']
ARROW = {v: k for k, v in HEAD.items()}
ARROW['production'] = 'delta'
LINE, CHAR = 16.5, 9.5  # a label line's height and a character's width at font size 14 (our maps)


def _label(l, text, w, h):
    # the label's text, its box estimated and centred (yEd measures it again when the text is edited)
    lines = text.split('\n') if text else []
    lw, lh = max([len(x) for x in lines] or [0]) * CHAR, len(lines) * LINE + 4
    l.text = text or None
    l.set('hasText', 'true' if text else 'false')
    for k, v in (('width', lw), ('height', lh), ('x', (w - lw) / 2), ('y', (h - lh) / 2)):
        l.set(k, repr(float(v)))


def write(diagram):
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
    resources, rid = [], {}

    def resource(kind, text):  # one icon per kind and text, shared as yEd shares them
        if (kind, text) not in rid:
            r = copy.deepcopy(res_tpl[kind]); rid[kind, text] = str(len(rid) + 1); r.set('id', rid[kind, text])
            gn = r.find('.//y:GenericNode', NS)
            gn.find('y:Geometry', NS).set('width', '15.0' if len(text) <= 2 else '45.0')  # as in our maps
            _label(gn.find('y:NodeLabel', NS), text, float(gn.find('y:Geometry', NS).get('width')), 15.0)
            resources.append(r)
        return rid[kind, text]

    kids = {}
    for i, d in N.items():
        kids.setdefault(d.parent if d.parent in N else None, []).append(i)

    def node(parent, i):
        d = N[i]
        group = bool(kids.get(i)) or d.kind == 'Compartment'
        n = copy.deepcopy(tpl['ComplexGroup' if group and d.kind == 'Complex' else d.kind])
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
        l = gn.find('y:NodeLabel', NS)
        _label(l, next((x for x in d.labels if x), ''), w, h)  # the name; a second label is a unit (N:4)
        if d.kind == 'Compartment' and d.label_at:
            l.set('x', repr(float(d.label_at[0]))); l.set('y', repr(float(d.label_at[1])))
        if d.count > 1:  # yEd draws a multimer as two shapes; N:x says how many
            sp = gn.find('y:StyleProperties', NS)
            etree.SubElement(sp, Y + 'Property', {'class': 'java.lang.Integer', 'name': 'com.yworks.sbgn.style.mcount', 'value': '2'})
        units = d.units + (['N:%d' % d.count] if d.count > 2 and not any(re.fullmatch(r'N:\d+', u) for u in d.units) else [])
        icons = [('StateVariable', txt, rx, ry) for txt, rx, ry in d.states]
        icons += [('UnitOfInformation', u, (k + 1) / (len(units) + 1) - 0.5, -0.5) for k, u in enumerate(units)]
        for kind, txt, rx, ry in icons:
            il = copy.deepcopy(icon); il.set('iconData', resource(kind, txt))
            p = il.find('.//y:SmartNodeLabelModelParameter', NS)
            p.set('nodeRatioX', repr(float(rx))); p.set('nodeRatioY', repr(float(ry)))
            gn.findall('y:NodeLabel', NS)[-1].addnext(il)
        if group:
            sub = n.find('g:graph', NS); sub.set('id', i + ':')
            for j in kids.get(i, []):
                node(sub, j)

    g = etree.SubElement(root, G + 'graph', edgedefault='directed', id='G')
    for i in kids.get(None, []):
        node(g, i)
    for a in diagram.arcs:
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
        pl.find('y:BendStyle', NS).set('smoothed', 'true')  # soft bends on every arc (user, 2026-10-14)
        g.append(e)
    rs = etree.SubElement(etree.SubElement(root, G + 'data', key='res'), Y + 'Resources')
    rs.extend(resources)
    etree.cleanup_namespaces(root)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')

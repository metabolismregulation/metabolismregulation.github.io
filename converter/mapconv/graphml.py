# Read a yEd GraphML map drawn with the SBGN palette into the map model.
import os, re
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
    url = [k.get('id') for k in root.findall('g:key', NS) if (k.get('for'), k.get('attr.name')) == ('node', 'url')]
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
        u = n.find('g:data[@key="%s"]' % url[0], NS) if url else None
        nodes[n.get('id')] = Node(
            id=n.get('id'), kind=kind, box=tuple(float(geo.get(a)) for a in ('x', 'y', 'width', 'height')),
            labels=[(l.text or '').strip() for l in labs if not l.get('iconData')],
            parent=p.get('id') if p.tag.endswith('node') else None,
            fill=fill.get('color') if fill is not None else None,
            states=states(gn, res), units=us, count=count(gn, us),
            label_at=(float(l.get('x')), float(l.get('y'))) if kind == 'Compartment' and l is not None else None,
            url=(u.text or '').strip() or None if u is not None else None)
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
                        target_at=(float(yp.get('tx')), float(yp.get('ty')))))
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)

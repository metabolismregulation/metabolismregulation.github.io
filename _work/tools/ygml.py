# Minimal parser for yEd graphml built with the SBGN palette.
# nodes(): id -> cls, label, state variables (sv), fill, parent, url,
#          description, geo (x, y, w, h; absolute) and the lxml element.
# edges(): id, source s, target t, arrow, path (ports), bends (pts), element.
from lxml import etree
NS={'g':'http://graphml.graphdrawing.org/xmlns','y':'http://www.yworks.com/xml/graphml'}
def load(p):
    t=etree.parse(p); r=t.getroot()
    keys={k.get('id'):(k.get('for'),k.get('yfiles.type') or k.get('attr.name')) for k in r.findall('g:key',NS)}
    return t,keys
def kid(keys,for_,name):
    return [k for k,(f,n) in keys.items() if f==for_ and n==name][0]
def nodes(t,keys):
    out={}
    for n in t.getroot().iter('{%s}node'%NS['g']):
        d={}
        gn=n.find('g:data/y:GenericNode',NS)
        if gn is None:
            gn=n.find('g:data/y:ProxyAutoBoundsNode/y:Realizers/*',NS)
            d['group']=True
        d['cls']=(gn.get('configuration') or '').replace('com.yworks.sbgn.','')
        geo=gn.find('y:Geometry',NS)
        d['geo']=tuple(float(geo.get(a)) for a in ('x','y','width','height'))
        labs=gn.findall('y:NodeLabel',NS)
        d['label']=' | '.join((l.text or '').strip() for l in labs if not l.get('iconData'))
        d['sv']=[(l.text or '').strip() for l in labs if l.get('iconData')]
        d['fill']=gn.find('y:Fill',NS).get('color') if gn.find('y:Fill',NS) is not None else None
        p=n.getparent().getparent(); d['parent']=p.get('id') if p.tag.endswith('node') else None
        d['el']=n
        for dd in n.findall('g:data',NS):
            nm=keys.get(dd.get('key'),(0,0))[1]
            if nm in('url','description'): d[nm]=(dd.text or '').strip()
        out[n.get('id')]=d
    return out
def edges(t,keys):
    out=[]
    for e in t.getroot().iter('{%s}edge'%NS['g']):
        pl=e.find('g:data/y:PolyLineEdge',NS)
        a=pl.find('y:Arrows',NS); p=pl.find('y:Path',NS)
        out.append(dict(id=e.get('id'),s=e.get('source'),t=e.get('target'),arrow=a.get('target'),src_arrow=a.get('source'),
            line=pl.find('y:LineStyle',NS).get('type'),path=p,pts=[(float(q.get('x')),float(q.get('y'))) for q in p.findall('y:Point',NS)],el=e))
    return out

# Approximate SBGN preview of a yEd graphml (judge the real look in yEd):
#   python3 render.py in.graphml out.png|out.svg [x0 y0 x1 y1]
# Needs: lxml, cairosvg (PNG only).
import sys, os, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ygml import *
import cairosvg
def render(path, out, box=None, scale=1.5):
    t,k=load(path); N=nodes(t,k); E=edges(t,k)
    xs=[d['geo'][0] for d in N.values()]+[d['geo'][0]+d['geo'][2] for d in N.values()]
    ys=[d['geo'][1] for d in N.values()]+[d['geo'][1]+d['geo'][3] for d in N.values()]
    x0,y0,x1,y1=box or (min(xs)-30,min(ys)-30,max(xs)+30,max(ys)+30)
    W,H=x1-x0,y1-y0
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*scale}" height="{H*scale}" viewBox="{x0} {y0} {W} {H}"><rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="white"/>',
       '<defs>',
       '<marker id="delta" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0L10,5L0,10z" fill="black"/></marker>',
       '<marker id="white_delta" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="11" markerHeight="11" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0L10,5L0,10z" fill="white" stroke="black"/></marker>',
       '<marker id="white_circle" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" orient="auto" markerUnits="userSpaceOnUse"><circle cx="5" cy="5" r="4.5" fill="white" stroke="black"/></marker>',
       '<marker id="t_shape" viewBox="0 0 4 12" refX="3" refY="6" markerWidth="4" markerHeight="12" orient="auto" markerUnits="userSpaceOnUse"><path d="M3,0L3,12" stroke="black" stroke-width="2"/></marker>',
       '</defs>']
    def depth(i): return i.count('::')
    for i,d in sorted(N.items(), key=lambda kv:(not kv[1].get('group'), depth(kv[0]))):
        x,y,w,h=d['geo']; c=d['cls']; f=(d['fill'] or '#fff')[:7]
        if c=='Complex':
            a=min(10,w/4,h/4)
            s.append(f'<path d="M{x+a},{y}H{x+w-a}L{x+w},{y+a}V{y+h-a}L{x+w-a},{y+h}H{x+a}L{x},{y+h-a}V{y+a}z" fill="{f}" stroke="black"/>')
        elif c=='Macromolecule': s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{f}" stroke="black"/>')
        elif c=='SimpleChemical': s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{f}" stroke="black"/>')
        elif c in ('Operator',): s.append(f'<circle cx="{x+w/2}" cy="{y+h/2}" r="{w/2}" fill="white" stroke="black"/>')
        elif c=='Process': s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="black"/>')
        else: s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}" stroke="red" stroke-dasharray="3"/>')
        if d['label'] and c!='Complex':
            lines=d['label'].split(' | ')
            for j,l in enumerate(lines[:1]):
                s.append(f'<text x="{x+w/2}" y="{y+h/2+4}" font-family="DejaVu Sans" font-size="11" text-anchor="middle">{html.escape(l)}</text>')
    for e in E:
        S,Tn=N[e['s']]['geo'],N[e['t']]['geo']; p=e['path']
        a=(S[0]+S[2]/2+float(p.get('sx')),S[1]+S[3]/2+float(p.get('sy')))
        b=(Tn[0]+Tn[2]/2+float(p.get('tx')),Tn[1]+Tn[3]/2+float(p.get('ty')))
        pts=[a]+e['pts']+[b]
        m=f' marker-end="url(#{e["arrow"]})"' if e['arrow']!='none' else ''
        s.append('<polyline points="%s" fill="none" stroke="black"%s/>'%(' '.join(f'{u},{v}' for u,v in pts),m))
    s.append('</svg>')
    if out.endswith('.svg'):
        open(out, 'w').write('\n'.join(s))
        return
    cairosvg.svg2png(bytestring='\n'.join(s).encode(), write_to=out)
if __name__=='__main__':
    box=tuple(map(float,sys.argv[3:7])) if len(sys.argv)>3 else None
    render(sys.argv[1],sys.argv[2],box)

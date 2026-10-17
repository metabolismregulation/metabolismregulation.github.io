# What a yEd map must keep to convert: the SBGN Process Description rules, with one exception
# (user, 2026-10-16): stimulation and inhibition may join two entities (also from a logic gate),
# CellDesigner's reduced notation in place of an Activity Flow map. yEd draws anything, so a map can look right and
# be wrong inside: a shape laid on a protein in place of a state variable, a node drawn inside
# a complex without being part of it, an arrow from another palette. Each problem is an
# element id and a reason; the element is left out of the conversion and marked red in a copy
# of the GraphML (mark).
#   python3 -m mapconv.rules <map.graphml> [<marked.graphml>]
import sys
from lxml import etree
from . import graphml
from .celldesigner import CLASS

PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess', 'Association', 'Dissociation')
MODIFIERS = ('catalysis', 'inhibition', 'modulation', 'stimulation', 'trigger')
REDUCED = ('stimulation', 'inhibition')  # allowed between two entities
RED = '#FF0000'


def problems(m):
    N, out = m.nodes, []
    ents = {i for i, d in N.items() if d.kind in CLASS}
    procs = {i for i, d in N.items() if d.kind in PROCESSES}
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    groups = {i for i, d in N.items() if d.kind == 'Compartment' or (d.kind == 'Complex' and any(e.parent == i for e in N.values()))}

    def up(i):  # the groups around i, nearest first
        q = N[i].parent
        while q in N:
            yield q
            q = N[q].parent
    inside = lambda a, b, t=1.0: (b[0] - t <= a[0] and a[0] + a[2] <= b[0] + b[2] + t and
                                  b[1] - t <= a[1] and a[1] + a[3] <= b[1] + b[3] + t)

    for i, d in N.items():
        if d.kind in ('StateVariable', 'UnitOfInformation'):
            out.append((i, 'a %s drawn as a node of its own: make it a label of its entity' % d.kind)); continue
        if i not in ents | procs | ops | groups and d.kind != 'Compartment':
            out.append((i, 'not an SBGN glyph (%s)' % d.kind)); continue
        if d.kind == 'SimpleChemical' and any(t.split('@')[0] for t, _, _ in d.states):
            out.append((i, 'a simple chemical carries no state variable'))
        p = N[d.parent] if d.parent in N else None
        if p is not None and not p.outline and not inside(d.box, p.box):  # an oval's members come from the drawing
            out.append((i, 'part of %s but drawn outside it' % (p.labels[0] if p.labels and p.labels[0] else p.kind)))
        if i in procs | ops:
            continue
        # the innermost group whose box holds this node on the drawing must be one it belongs to
        around = [g for g in groups if g != i and i not in up(g) and not N[g].outline and inside(d.box, N[g].box, 0)]
        if around:
            g = min(around, key=lambda g: N[g].box[2] * N[g].box[3])
            if g not in up(i) and (N[g].kind == 'Complex' or d.kind != 'Compartment'):
                out.append((i, 'inside %s on the drawing but not part of it' % (N[g].labels[0] if N[g].labels and N[g].labels[0] else N[g].kind)))
    # a smaller node laid on an entity it does not belong to, its centre on the entity's border
    # or inside it: a shape in place of a state variable (two nodes touching are layout)
    flagged = {i for i, _ in out}
    for a in (i for i in N if i not in groups and i not in flagged):
        x, y, w, h = N[a].box
        for b in ents - groups:
            bx, by, bw, bh = N[b].box
            if a != b and b not in up(a) and w * h < bw * bh and \
                    bx - 2 <= x + w / 2 <= bx + bw + 2 and by - 2 <= y + h / 2 <= by + bh + 2:
                out.append((a, 'laid on %s without being part of it' % (N[b].labels[0] or N[b].kind))); break

    bad = {i for i, _ in out}
    epn = ents
    for e in m.arcs:
        s, t, h = e.source, e.target, e.head
        if s in bad or t in bad:
            continue
        why = None
        if N[s].kind == 'Compartment' or N[t].kind == 'Compartment':
            why = 'an arc ends on a compartment (CellDesigner joins species only)'
        elif h is not None and h not in ('production',) + MODIFIERS:
            why = 'an arrow outside the SBGN palette (%s)' % h[6:]
        elif h is None:  # consumption, or a logic arc into an operator: drawn either way
            pair = {s, t}
            if not (pair & procs and pair & epn) and not (pair & ops and pair & (epn | ops)):
                why = 'a plain line must join an entity and a process (or a logic gate)'
        elif h == 'production':
            if s in epn and t in procs:
                why = 'a production arrow points away from its process'
            elif not (s in procs and t in epn):
                why = 'a production arrow must run from a process to an entity'
        elif s in epn | ops and t in epn:  # reduced notation, also from a logic gate
            if h not in REDUCED:
                why = 'a %s arc must end on a process (between entities only stimulation and inhibition)' % h
        elif not (s in epn | ops and t in procs):
            why = 'a %s arc must run from an entity (or a logic gate) to a process' % h
        if why:
            out.append((e.id, why))
    # a process needs something in and something out (reversible: products on both sides)
    ok = [e for e in m.arcs if e.id not in {i for i, _ in out}]
    for p in procs - bad:
        cons = sum(1 for e in ok if e.head is None and p in (e.source, e.target))
        prod = sum(1 for e in ok if e.head == 'production' and e.source == p)
        if not (cons and prod or prod >= 2):
            out.append((p, 'a process needs a reactant and a product (a source or sink when there is none)'))
    for o in ops - bad:
        # its output: a modifier arc (to a process, or reduced to an entity) or a plain line into another gate
        if not any(e.source == o and (e.head in MODIFIERS or e.head is None and e.target in ops) for e in ok):
            out.append((o, 'a logic gate needs an arc out of it'))
    return out


def lines(m, found):
    # each problem as one line, the element by its id and as it is found on the drawing: a node
    # by its label, an arc by its ends
    N, arcs = m.nodes, {e.id: e for e in m.arcs}
    lab = lambda n: ' '.join((N[n].labels[0] if N[n].labels and N[n].labels[0] else N[n].kind).split()) if n in N else n
    what = lambda i: lab(i) if i in N else 'arc %s → %s' % (lab(arcs[i].source), lab(arcs[i].target))
    return ['%s (%s): %s' % (i, what(i), r) for i, r in found]


def clean(m, found):
    # the map without the problem elements and the arcs at removed nodes
    from dataclasses import replace
    gone = {i for i, _ in found}
    nodes = {i: d for i, d in m.nodes.items() if i not in gone}
    return replace(m, nodes=nodes, arcs=[e for e in m.arcs if e.id not in gone and e.source in nodes and e.target in nodes])


def mark(path, found):
    # the GraphML with each problem element drawn red and its reason as its description
    # (yEd shows it on hover); nothing else changes
    NS, G = graphml.NS, '{%s}' % graphml.NS['g']
    t = etree.parse(path)
    root = t.getroot()
    keys = {(k.get('for'), k.get('attr.name')): k.get('id') for k in root.findall('g:key', NS)}
    why = dict(found)
    for tag, style in (('node', 'BorderStyle'), ('edge', 'LineStyle')):
        k = keys.get((tag, 'description'))
        if k is None:
            k = keys[tag, 'description'] = 'd_problem_' + tag
            root.insert(0, etree.Element(G + 'key', {'attr.name': 'description', 'attr.type': 'string', 'for': tag, 'id': k}))
        for x in root.iter(G + tag):
            if x.get('id') not in why:
                continue
            for s in x.iterfind('g:data//y:' + style, NS):
                s.set('color', RED); s.set('width', '3.0')
            d = x.find('g:data[@key="%s"]' % k, NS)
            if d is None:
                d = etree.Element(G + 'data', key=k); x.insert(0, d)
            d.text = why[x.get('id')]
    return etree.tostring(t, xml_declaration=True, encoding='UTF-8').decode('utf-8')


if __name__ == '__main__':
    m = graphml.read(sys.argv[1])
    found = problems(m)
    print('\n'.join(lines(m, found)))
    if len(sys.argv) > 2 and found:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(mark(sys.argv[1], found))

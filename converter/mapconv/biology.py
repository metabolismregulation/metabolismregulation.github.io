# The biology of a map (model.Biology) from its drawing: which glyphs draw one entity, and the
# reactions and influences between entities. The entity key (user, 2026-10-19; CLAUDE.md,
# "Restructuring"): two glyphs are one entity when they have the same identity, state,
# compartment and glyph class. Identity: an identifier where the glyph has one (proteins, genes,
# RNA: HGNC ID, else UniProt, else HGNC symbol; metabolites: ChEBI, conjugate acid and base
# joined), else the normalised label, which joins an annotated entity when it points to exactly
# one identifier. Complexes by their members, families by their members' identifiers. A chain
# length in the label (N:n, N:n+1) counts as the multimer count does.
import collections, json, os, re
from .celldesigner import CLASS, MOD, cd_class, plain_name, is_structural
from .graphml import EQUIV
from .annotation import units as hidden_units
from .model import HEADS, Annotation, Biology, Entity, Influence, Member, Reaction, StateVariable, UnitOfInformation

PROCESSES = ('Process', 'OmittedProcess', 'UncertainProcess')
# ChEBI IDs linked as conjugate acid and base, one group per molecule (tools/conjugates.py)
TABLE = os.path.join(os.path.dirname(__file__), 'conjugates.json')
CONJUGATE = {}
if os.path.exists(TABLE):
    with open(TABLE, encoding='utf-8') as f:
        CONJUGATE = {c: g[0] for g in json.load(f)['groups'] for c in g}


def label(d):
    return ' '.join(plain_name(d.labels[0]).split()) if d.labels else ''


def identifier(p, kind):
    # an entity's identifier from its properties (graphml node data, or read from MIRIAM)
    if kind == 'SimpleChemical':
        return ('chebi', CONJUGATE.get(p['ChEBI'], p['ChEBI'])) if p.get('ChEBI') else None
    for k in ('HGNC', 'UniProt', 'HGNC symbol'):
        if p.get(k):
            return (k.lower(), p[k])
    return None


def own_identity(d):
    # the identity a glyph's own annotation gives, or None
    if d.kind not in ('Macromolecule', 'NucleicAcidFeature', 'SimpleChemical'):
        return None
    if d.data.get('Member annotation'):  # a family: its members' identifiers
        ms = [identifier(dict(m['props']), d.kind) for m in json.loads(d.data['Member annotation'])]
        return ('family', tuple(sorted(ms))) if ms and all(ms) else None
    return identifier(d.data, d.kind)


# what a glyph states besides its entity key (user, 2026-10-22: a shape and its arcs are not all
# the biology a map conveys), as records (model.StateVariable, ...); node properties that are not
# biology: Orientation (yEd), notes
IDS = ('HGNC', 'HGNC symbol', 'UniProt', 'ChEBI')


def state_variables(d):
    # the drawn state variables, each with its site: on the variable (P@S505), or from the property
    # PTM (P@S505 per modified site, the Atlas maps), given to the unsited ones of that value in turn
    svs = [StateVariable(*txt.split('@', 1)) if '@' in txt else StateVariable(txt) for txt, _, _ in d.states]
    for s in (d.data.get('PTM') or '').split():
        v, site = s.split('@', 1) if '@' in s else (s, None)
        k = next((k for k, x in enumerate(svs) if x == StateVariable(v)), None)
        if k is None:
            svs.append(StateVariable(v, site))  # a site the drawing does not show
        else:
            svs[k] = StateVariable(v, site)
    return svs


def unit(u):
    return UnitOfInformation(u.split(':', 1)[1], 'ct') if u.startswith('ct:') else UnitOfInformation(u)


def annotations(p, qualifier='is'):
    return {Annotation(qualifier, k, ' '.join(p[k].split())) for k in IDS if p.get(k)}


def family_members(d):
    recs = json.loads(d.data.get('Member annotation') or '[]')
    if recs:
        return {Member(m.get('symbol'), tuple(sorted(annotations(dict(m['props']), 'hasVersion'))),
                       tuple(sorted((dict(m['props']).get('PTM') or '').split()))) for m in recs}
    return {Member(x.strip()) for x in (d.data.get('Members') or '').split(';') if x.strip()}


def build(m):
    N = m.nodes
    comps = {i for i, d in N.items() if d.kind == 'Compartment'}
    ents = [i for i, d in N.items() if d.kind in CLASS]
    is_ent = set(ents)
    members = collections.defaultdict(list)
    for i in ents:
        if N[i].parent in is_ent:
            members[N[i].parent].append(i)

    def comp(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return label(N[q]) if q else 'default'

    def state(i):
        d = N[i]; mods, lig = [], []
        if d.kind in ('Macromolecule', 'Complex'):
            for txt, _, _ in d.states:
                if is_structural(txt):
                    lig.append(txt)
                elif txt.split('@')[0]:
                    mods.append(txt.split('@')[0])
        return tuple(sorted(mods)), tuple(sorted(set(lig)))

    # glyph class: the class, the multimer count, a chain length written in the label (glycogen:
    # glucose (N:n) and (N:n+1): one ChEBI, two entities; user, 2026-10-19), a dashed border
    # (hypothetical, a property of the CellDesigner species), and the units of information not drawn (the property
    # Unit of information: two fragments of one protein, one identifier; user, 2026-10-29)
    cls = lambda i: (cd_class(N[i]), N[i].count) + tuple(re.findall(r'\(N:([^)]+)\)\s*$', label(N[i]))) + \
        (('hypothetical',) if N[i].dashed else ()) + tuple(sorted(hidden_units(N[i].data)))
    # identities: an identifier, or a label joining the one identifier it is given elsewhere
    ident = {i: own_identity(N[i]) for i in ents if N[i].kind != 'Complex'}
    seen = collections.defaultdict(set)
    for i, x in ident.items():
        if x: seen[label(N[i]), cls(i), state(i), comp(i)].add(x)
    notes = ['%s: %d identifiers (%s), %d entities' % (k[0], len(v), ', '.join(sorted(x[1] if isinstance(x[1], str) else x[0] for x in v)), len(v))
             for k, v in seen.items() if len(v) > 1 and k[0]]
    for i, x in ident.items():
        if x is None:
            v = seen.get((label(N[i]), cls(i), state(i), comp(i)), ())
            # a source or sink has no name: one per compartment
            ident[i] = next(iter(v)) if len(v) == 1 else ('label', '' if cls(i)[0] == 'DEGRADED' else label(N[i]))

    def inner(i):  # the key without the compartment: what a member adds to its complex
        if N[i].kind == 'Complex':
            ms = members.get(i)
            x = ('complex', tuple(sorted(inner(j) for j in ms))) if ms else ('label', label(N[i]))
        else:
            x = ident[i]
        return (x, cls(i), state(i))
    key = {i: (comp(i),) + inner(i) for i in ents}
    first = {}  # glyphs the file draws as one species are one entity, whatever their key
    for i in ents:
        if N[i].species:
            key[i] = first.setdefault(N[i].species, key[i])

    entities, glyph = {}, {}
    for i in ents:
        e = entities.get(key[i])
        if e is None:
            e = entities[key[i]] = Entity(id=i, key=key[i], glyphs=[])
        e.glyphs.append(i)
        d = N[i]
        svs = collections.Counter(state_variables(d))
        e.state_variables = tuple(sorted((collections.Counter(e.state_variables) | svs).elements(), key=lambda s: (s.value, s.variable or '')))
        e.names = e.names | ({label(d)} if label(d) else set())
        e.units = e.units | {unit(u) for u in d.units if not re.fullmatch(r'N:\d+', u)}  # N:x: the count, in the key
        e.annotations = e.annotations | annotations(d.data)
        e.family = e.family or d.data.get('Family')
        e.members = e.members | family_members(d)
        glyph[i] = e.id
    by_id = {e.id: e for e in entities.values()}
    for c, ms in members.items():
        for j in ms:
            by_id[glyph[j]].inside = glyph[c]

    reactions, influences = [], []
    other = lambda a, x: a.target if a.source == x else a.source
    for p, d in N.items():
        if d.kind not in PROCESSES:
            continue
        at = [a for a in m.arcs if p in (a.source, a.target)]
        cons = [glyph[other(a, p)] for a in at if a.head is None and other(a, p) in glyph]
        prod = [glyph[a.target] for a in at if a.source == p and a.head == 'production' and a.target in glyph]
        mods = [(glyph[a.source], a.head, a.dashed) for a in at if a.target == p and a.head in MOD and a.source in glyph]
        # a gate's inputs: the entities joined to it by plain arcs, either way
        gates = [(label(N[a.source]).upper(), [glyph[other(b, a.source)] for b in m.arcs if a.source in (b.source, b.target)
                  and b.head is None and other(b, a.source) in glyph], a.head, a.dashed)
                 for a in at if a.target == p and N[a.source].kind == 'Operator']
        reactions.append(Reaction(id=p, reactants=cons, products=prod, modifiers=mods, gates=gates))
    for a in m.arcs:
        s = N[a.source]
        if a.source in glyph and a.target in glyph and a.head in HEADS:
            influences.append(Influence(id=a.id, sources=[glyph[a.source]], target=glyph[a.target], head=a.head, dashed=a.dashed))
        elif s.kind == 'Operator' and label(s) == EQUIV and a.target in glyph and a.head is None:
            # an equivalence: the members, the generic entity
            ins = [other(b, a.source) for b in m.arcs if a.source in (b.source, b.target) and b is not a]
            influences.append(Influence(id=a.id, sources=[glyph[i] for i in ins if i in glyph], target=glyph[a.target],
                                        head=None, gate=EQUIV))
        elif s.kind == 'Operator' and a.target in glyph and a.head in HEADS:  # a gate on arcs between entities
            ins = [other(b, a.source) for b in m.arcs if a.source in (b.source, b.target) and b.head is None]
            influences.append(Influence(id=a.id, sources=[glyph[i] if i in glyph else (label(N[i]).upper(),) for i in ins],
                                        target=glyph[a.target], head=a.head, gate=label(s).upper(), dashed=a.dashed))
    def around(c):
        q = N[c].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return label(N[q]) if q else None
    return Biology(entities=by_id, reactions=reactions, influences=influences, glyph=glyph, notes=notes,
                   compartments={label(N[c]): around(c) for c in comps})

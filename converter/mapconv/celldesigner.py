# Write a CellDesigner 4.0 file (SBML L2V4 with the CellDesigner extension)
# from a map (model.py) read from a yEd SBGN map.
# - Every yEd entity node is a species with one alias at the yEd position
#   (all coordinates shifted so the map starts at MARGIN).
# - Proteins with the same label share one CellDesigner protein; its residues
#   come from the state variables (yEd icons: "P", "Ac@S516", empty = site
#   without a value), placed at the icon's position on the node border.
#   Nodes of one protein share a residue by site (S516), wherever the icon
#   sits; icons without a site share one by place. Site names are not
#   written: only the symbol in the circle (P, Ac, Me).
# - Nucleic acid features: genes, or RNAs when they carry ct:mRNA; one gene or
#   RNA per label; the ct: unit of information is kept (info prefix "ct").
# - Source/sink (EmptySet): a DEGRADED species, named after its id.
# - Every Process node is a reaction: consumption edges give the reactants,
#   production edges the products, modulation edges the modifiers. The main
#   line runs straight between the centres of the main reactant and product,
#   the square midway (CellDesigner's default); the other reactants and
#   products are added links. Where two processes join the same two species
#   (HMGCR <-> HMGCR-P), each line uses the quarter points on the facing sides.
# - Bend points only for long connectors that yEd draws as one L (cd_bends.py);
#   others the user adds by hand. Lines end at node centres. Main lines a few px off the vertical or
#   horizontal are straightened (cd_straighten.py); modifiers up to 15 px off
#   their square are moved onto it, if nothing overlaps after the move.
# - MIRIAM annotation from the map's node properties (annotation.py):
#   bqbiol:is for one entity, bqbiol:hasVersion for a family.
# - Metabolites become circles of CHEMICAL diameter on the yEd centre.
# - Complexes: complexSpeciesAlias; members are included species (aliases
#   with complexSpeciesAlias, RDF in their notes). An unlabelled complex is
#   named after its members (A:B).
# - Multimers: the count in the N:x unit of information becomes homodimer N
#   (yEd's mcount is only the number of shapes drawn, always 2); the unit
#   itself is not copied (MINERVA draws N:x at the top middle). The box grows
#   6 per unit beyond 2, top left kept (user's ASL tetramer, iNOS): 80x40 for
#   N:2, 92x52 for N:4.
# - A state variable without a modification state (cAMP) is a bound ligand:
#   one structural state per species, the same text twice written once.
# - A process with production arcs on both sides and no consumption arc is a
#   reversible reaction, the entities on the upper (or left) side as reactants.
# Checked by opening and saving in CellDesigner 4.4.2: no warning, nothing
# dropped (ChEBI must be urn:miriam:obo.chebi:CHEBI%3A...).
import math, os, re, sys
from dataclasses import replace
from struct import pack, unpack
from lxml import etree
from . import cd_straighten, cd_bends

MARGIN = 40
STRAIGHTEN = os.environ.get('STRAIGHTEN', '1') == '1'  # STRAIGHTEN=0: positions as in yEd
ALIGN = 15.0  # largest move of a modifier onto its square (px)
CHEMICAL = 36.0  # metabolites are drawn as circles of this diameter, centred on the yEd node
CD = 'http://www.sbml.org/2001/ns/celldesigner'
CLASS = {'Macromolecule': 'PROTEIN', 'SimpleChemical': 'SIMPLE_MOLECULE', 'NucleicAcidFeature': 'GENE',
         'UnspecifiedEntity': 'UNKNOWN', 'Complex': 'COMPLEX', 'Perturbation': 'PHENOTYPE', 'Phenotype': 'PHENOTYPE',
         'SourceAndSink': 'DEGRADED', 'EmptySet': 'DEGRADED',
         # CellDesigner has no submap: a phenotype (user's SREBP file, 2026-10-13)
         'Submap': 'PHENOTYPE'}
# arc between two entities (no process) -> CellDesigner reduced-notation reaction
# (user's SREBP file: submap -> submap and SREBP2 -> submap stimulation)
REDUCED = {'stimulation': 'PHYSICAL_STIMULATION'}
GATE = {'AND': 'BOOLEAN_LOGIC_GATE_AND', 'OR': 'BOOLEAN_LOGIC_GATE_OR', 'NOT': 'BOOLEAN_LOGIC_GATE_NOT'}
# glyph at the end of an arc into a process -> CellDesigner modification type
MOD = {'catalysis': 'CATALYSIS', 'inhibition': 'INHIBITION', 'modulation': 'MODULATION',
       'stimulation': 'PHYSICAL_STIMULATION', 'trigger': 'TRIGGER'}
STATE = {'P': 'phosphorylated', 'Ac': 'acetylated', 'Ub': 'ubiquitinated', 'Me': 'methylated',
         'OH': 'hydroxylated', 'G': 'glycosylated', 'My': 'myristoylated', 'Pa': 'palmytoylated',
         'Pr': 'prenylated', 'S': 'sulfated',
         # XML values checked through MINERVA (it shows H, *, ?; other spellings are rejected)
         'H': 'protonated', '*': "don't care", '?': 'unknown'}
# CellDesigner's modification circles (its symbol sheet, docs/components44-overview.png):
# a state variable with one of these symbols (or empty) is a residue, as many as the node has;
# any other text (active, cAMP, Ca) goes into the one free-text structural state of the species
NAME = [(' ', '_space_'), ('-', '_minus_'), ('/', '_slash_'), ('+', '_plus_'),
        ('α', '_alpha_'), ('β', '_beta_'), ('γ', '_gamma_'), ('δ', '_delta_'), ('ε', '_epsilon_'), ('ζ', '_zeta_'),
        ('η', '_eta_'), ('θ', '_theta_'), ('ι', '_iota_'), ('κ', '_kappa_'), ('λ', '_lambda_'), ('μ', '_mu_'),
        ('ν', '_nu_'), ('ξ', '_xi_'), ('π', '_pi_'), ('ρ', '_rho_'), ('σ', '_sigma_'), ('τ', '_tau_'),
        ('φ', '_phi_'), ('χ', '_chi_'), ('ψ', '_psi_'), ('ω', '_omega_')]


def cd_name(s):
    for a, b in NAME:
        s = s.replace(a, b)
    return s


def units_of_information(d):
    # the units of information other than the multimer count (that becomes homodimer N)
    return [u for u in d.units if ':' in u and not re.fullmatch(r'N:\d+', u)]


def cd_class(d):
    # a nucleic acid feature is an RNA when it carries ct:mRNA (or another ct:...RNA), else a gene
    if d.kind == 'NucleicAcidFeature' and any(u.split(':', 1)[1].lower().endswith('rna') for u in units_of_information(d)):
        return 'RNA'
    return CLASS[d.kind]


def is_structural(txt):
    # a state variable without a modification state (cAMP: a bound ligand)
    return bool(txt) and '@' not in txt and txt not in STATE


def border_angle(rx, ry):
    # CellDesigner's residue angle of a point on the node border, given as
    # offsets from the centre in node widths/heights (yEd nodeRatio, y down).
    # The angle runs linearly along the border: 0 east, pi/4 at the
    # north-east corner, pi/2 north, and so on (checked through MINERVA).
    q = math.pi / 4
    yy = -ry
    if abs(rx) >= abs(yy):
        a = q * yy / 0.5 if rx > 0 else math.pi - q * yy / 0.5
    else:
        a = math.pi / 2 - q * rx / 0.5 if yy > 0 else 3 * math.pi / 2 + q * rx / 0.5
    return a % (2 * math.pi)


# CellDesigner's quarter anchor points on a node box (Startup Guide, Appendix 2.3),
# used for two processes on the same two species
QUARTER = {'NNE': (.75, 0), 'ENE': (1, .25), 'ESE': (1, .75), 'SSE': (.75, 1),
           'SSW': (.25, 1), 'WSW': (0, .75), 'WNW': (0, .25), 'NNW': (.25, 0)}


def anchor_point(box, side, circle=False):
    x, y, w, h = box
    if not side:  # no anchor: the centre
        return (x + w / 2, y + h / 2)
    if circle:  # on a circle the points sit on it at 22.5 degree steps (checked through MINERVA)
        a = math.radians({'ENE': 22.5, 'NNE': 67.5, 'NNW': 112.5, 'WNW': 157.5, 'WSW': 202.5,
                          'SSW': 247.5, 'SSE': 292.5, 'ESE': 337.5}[side])
        return (x + w / 2 * (1 + math.cos(a)), y + h / 2 * (1 - math.sin(a)))
    fx, fy = QUARTER[side]
    return (x + fx * w, y + fy * h)


def write(diagram, ann, layout='direct'):
    # the CellDesigner file of a map (model.Map), with ann the MIRIAM annotation (annotation.py).
    # layout 'direct': the necessary minimum, simple and reliable, improved by hand in CellDesigner
    # (straight lines, squares midway); 'advanced': a layout that already looks good, squares and
    # modifier arcs where yEd draws them (F022 BCAA v04; names by the user, 2026-10-16)
    advanced = layout == 'advanced'
    N, E = diagram.nodes, diagram.arcs
    ents = {i: d for i, d in N.items() if d.kind in CLASS}
    procs = {i: d for i, d in N.items() if d.kind in ('Process', 'OmittedProcess', 'UncertainProcess', 'Association', 'Dissociation')}
    comps = {i: d for i, d in N.items() if d.kind == 'Compartment'}
    def comp_of(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return q
    other = set(N) - set(ents) - set(procs) - set(comps) - {i for i, d in N.items() if d.kind == 'Operator'}
    if other:
        print('not converted:', ', '.join(sorted('%s %s' % (i, N[i].kind) for i in other)))
    x0 = min(d.box[0] for d in N.values()) - MARGIN
    y0 = min(d.box[1] for d in N.values()) - MARGIN
    box = {i: (d.box[0] - x0, d.box[1] - y0, d.box[2], d.box[3]) for i, d in N.items()}
    W = max(b[0] + b[2] for b in box.values()) + MARGIN
    H = max(b[1] + b[3] for b in box.values()) + MARGIN
    # metabolites: circles, centre kept (the map size above keeps room for their labels)
    for i, d in N.items():
        if d.kind == 'SimpleChemical':
            x, y, w, h = box[i]
            box[i] = (x + w / 2 - CHEMICAL / 2, y + h / 2 - CHEMICAL / 2, CHEMICAL, CHEMICAL)
    # multimers of more than 2: the box grows 6 per extra unit, top left kept (yEd draws N:2's size)
    mult = {i: d.count for i, d in N.items() if d.kind in CLASS}
    for i, n in mult.items():
        if n > 2:
            x, y, w, h = box[i]
            box[i] = (x, y, w + 6 * (n - 2), h + 6 * (n - 2))
    label = {i: ' '.join(d.labels[0].split()) if d.labels else '' for i, d in ents.items()}
    # yEd ids of nested nodes (n3::n0) are no SBML ids: n3_n0 (a double underscore makes
    # MINERVA cut the id: re_n1__n28 and re_n1__n31 both became re_n1)
    sid = lambda i: re.sub(r'\W+', '_', i)
    members = {}
    for i, d in ents.items():
        if d.parent in ents:
            members.setdefault(d.parent, []).append(i)
    def name_complex(c):  # an unlabelled complex is named after its members, as CellDesigner does
        if not label[c]:  # (inner complexes first: PKA cat:PKA reg:cAMP:cAMP, not "PKA cat:")
            # each member once (user: PKA reg:cAMP, not PKA reg:cAMP:cAMP)
            label[c] = ':'.join(dict.fromkeys(name_complex(m) if m in members else label[m] for m in members[c]))
        return label[c]
    for c in members:
        name_complex(c)

    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    cen = lambda i: (box[i][0] + box[i][2] / 2, box[i][1] + box[i][3] / 2)
    def flows(p, quiet=False):
        # a process's arcs, the main reactant and product first
        # consumption arcs: no arrowhead, drawn either way in yEd (entity -> process or
        # process -> entity); turned to entity -> process
        ins = [e for e in E if e.target == p and e.source in ents and e.head is None]
        ins += [replace(e, source=e.target, target=p, points=e.points[::-1]) for e in E
                if e.source == p and e.target in ents and e.head is None and not e.tail]
        outs = [e for e in E if e.source == p and e.target in ents and e.head is not None]
        mods = [e for e in E if e.target == p and e.source in ents and e.head in MOD]
        gates = [e for e in E if e.target == p and e.source in ops and e.head in MOD]
        # reversible (SBGN: production arcs on both sides): the arcs on the upper (or left) side
        # are the reactants; an arc's side is that of its first bend, else of its entity
        reversible = not ins and len(outs) >= 2
        c = cen(p)
        if reversible:
            at = lambda e: (e.points[0][0] - x0, e.points[0][1] - y0) if e.points else cen(e.target)
            ax = 1 if max(abs(at(e)[1] - c[1]) for e in outs) >= max(abs(at(e)[0] - c[0]) for e in outs) else 0
            ins = [replace(e, source=e.target, target=p, points=e.points[::-1]) for e in outs if at(e)[ax] < c[ax]]
            outs = [e for e in outs if at(e)[ax] >= c[ax]]
        if not ins or not outs:
            if not quiet: print('process %s: no reactant or product, skipped' % p)
            return None
        # the main direction: the reactant and product that face each other through the
        # process, centre to centre; the others are extra links (CellDesigner: first one
        # source and one target, then more substrates and products; user, eNOS 2026-10-13)
        def through(a, b):
            (ax, ay), (bx, by) = cen(a), cen(b)
            L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1
            t_ = ((c[0] - ax) * (bx - ax) + (c[1] - ay) * (by - ay)) / L2
            d = abs((bx - ax) * (c[1] - ay) - (by - ay) * (c[0] - ax)) / math.sqrt(L2)
            return d + (0 if 0 < t_ < 1 else 1e6)  # the process between them
        # small molecules are side substrates: a main line between larger species first
        # (complex to complex; user, eNOS BH4/BH2 exchange 2026-10-13)
        small = lambda i: 1 if N[i].kind in ('SimpleChemical', 'EmptySet') else 0
        bi, bo = min(((a, b) for a in range(len(ins)) for b in range(len(outs))),
                     key=lambda ab: (small(ins[ab[0]].source) + small(outs[ab[1]].target),
                                     through(ins[ab[0]].source, outs[ab[1]].target), ab))
        ins = [ins[bi]] + ins[:bi] + ins[bi + 1:]; outs = [outs[bo]] + outs[:bo] + outs[bo + 1:]
        return ins, outs, mods, gates, reversible, c

    # straighten main lines a few pixels off the vertical or horizontal (cd_straighten.py)
    if STRAIGHTEN:
        fl = [flows(p, quiet=True) for p in procs]
        cd_straighten.straighten(box, [(f[0][0].source, f[1][0].target) for f in fl if f], members)
    # anchor points sit on the front shape of a multimer: CellDesigner draws it 6 smaller in
    # width and height (the user's glycolysis file: PFKFB2 dimer)
    front = {}
    for i, d in ents.items():
        k = 6 * (mult[i] - 1) if d.kind != 'SimpleChemical' else 0
        front[i] = (box[i][0], box[i][1], box[i][2] - k, box[i][3] - k)

    # the species each process joins by consumption and production arcs (twins: two processes, same species)
    joins = {p: frozenset(e.target if e.source == p else e.source for e in E if p in (e.source, e.target) and e.head not in MOD
                          and (e.source in ents or e.target in ents)) for p in procs}
    # yEd route points of an arc at process p, without the process ports (one process width from its centre)
    def route(p, pts):
        c = cen(p)
        return [(q[0] - x0, q[1] - y0) for q in pts if math.hypot(q[0] - x0 - c[0], q[1] - y0 - c[1]) > max(box[p][2], box[p][3]) + 3]

    def geometry(p, fl):
        # the main line of process p: its ends, anchors, bend, the square and the flow direction
        ins, outs, mods, gates, reversible, c = fl
        r_, q_ = ins[0].source, outs[0].target
        ra = qa = None  # line ends at the centres
        if any(q != p and joins[q] == joins[p] for q in procs):
            # two processes on the same two species (user's edit of mevalonate, HMGCR): each a
            # straight line between quarter points on the facing sides, on the side of the line
            # between the centres where yEd has the process (upper/lower, or left/right)
            (rx_, ry_), (qx_, qy_) = cen(r_), cen(q_)
            side = (qx_ - rx_) * (c[1] - ry_) - (qy_ - ry_) * (c[0] - rx_)  # >0: process right of r->q
            if abs(qx_ - rx_) >= abs(qy_ - ry_):  # side by side: E/W faces, upper or lower quarter
                v = 'N' if (side < 0) == (qx_ > rx_) else 'S'
                fr, fq = ('E', 'W') if qx_ > rx_ else ('W', 'E')
                ra, qa = fr + v + fr, fq + v + fq
            else:  # stacked: N/S faces, left or right quarter
                v = 'W' if (side > 0) == (qy_ > ry_) else 'E'
                fr, fq = ('S', 'N') if qy_ > ry_ else ('N', 'S')
                ra, qa = fr + fr + v, fq + fq + v
        A = anchor_point(front[r_] if ra else box[r_], ra, N[r_].kind == 'SimpleChemical')
        B = anchor_point(front[q_] if qa else box[q_], qa, N[q_].kind == 'SimpleChemical')
        # a significant bend on the main line: one long L on the reactant arc or on the product arc
        wr = cd_bends.turn([cen(r_)] + route(p, ins[0].points) + [c])
        wq = cd_bends.turn([cen(q_)] + route(p, outs[0].points)[::-1] + [c])
        bend = None
        if bool(wr) != bool(wq) and not ra:
            bend = cd_bends.corner(A, B, wr) if wr else cd_bends.corner(B, A, wq)
            if min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (A, B)) < cd_bends.EPS:
                bend = None  # the ends are already in line
        # the square (CellDesigner: midway on its segment; after the corner when yEd has the
        # process on the arc that bends from the reactant) and the flow direction through it
        P, Q = ((bend, B) if wr else (A, bend)) if bend else (A, B)
        sq = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
        L = math.hypot(Q[0] - P[0], Q[1] - P[1])
        f = ((Q[0] - P[0]) / L, (Q[1] - P[1]) / L)
        split = None
        if advanced and not bend:
            # the square where yEd has the process, if that is on the main line: two edit
            # points 8 px either side of it, the square on the segment between them
            u = ((c[0] - A[0]) * f[0] + (c[1] - A[1]) * f[1]) / L
            across = abs((c[0] - A[0]) * f[1] - (c[1] - A[1]) * f[0])
            if across < 3 and abs(u - 0.5) * L > 3 and 0.1 < u < 0.9:
                split = (u - 8 / L, u + 8 / L)
                sq = (A[0] + u * L * f[0], A[1] + u * L * f[1])
        return dict(r=r_, q=q_, ra=ra, qa=qa, A=A, B=B, wr=wr, bend=bend, sq=sq, f=f, split=split)

    def side(g, pt):  # the side of the square facing a point: 2 left of the flow, 3 right
        f, sq = g['f'], g['sq']
        return 2 if f[0] * (pt[1] - sq[1]) - f[1] * (pt[0] - sq[0]) < 0 else 3

    def lane(m, M, T, e):
        # advanced layout: the edit points of a modifier arc from M to T as yEd draws it, or
        # None for a straight arc from the centre
        pts = [(q[0] - x0, q[1] - y0) for q in e.points]
        if not pts:
            if e.source_at == (0.0, 0.0):
                return None
            # an off-centre start: straight across at the square's height, from just outside the node
            x, y, w, h = box[m]
            return [(x + w + 1 if T[0] > M[0] else x - 1, T[1])]
        # the yEd bends, each segment made horizontal or vertical, the last one ending on the square
        chain = [M] + pts
        for i in range(1, len(chain)):
            a, b = chain[i - 1], chain[i]
            chain[i] = (b[0], a[1]) if abs(b[1] - a[1]) < abs(b[0] - a[0]) else (a[0], b[1])
        last = chain[-1]
        chain[-1] = (last[0], T[1]) if abs(T[1] - last[1]) < abs(T[0] - last[0]) else (T[0], last[1])
        if len(chain) > 2:  # the point before keeps its segment straight
            a, b = chain[-2], chain[-1]
            if abs(a[0] - chain[-3][0]) < 0.5 and abs(a[1] - b[1]) < abs(a[0] - b[0]):
                chain[-2] = (a[0], b[1])
        # a metabolite's name is drawn across its circle: a lane leaving it sideways starts 12 px lower
        if N[m].kind == 'SimpleChemical' and abs(chain[1][1] - M[1]) < 0.5:
            sx = 1 if chain[1][0] > M[0] else -1
            chain[1:2] = [(M[0] + sx * 14, M[1] + 12), (chain[1][0], M[1] + 12)]
        return chain[1:]

    def crosses(a, b, r):  # the segment a-b runs through the box r (Liang-Barsky)
        t0, t1 = 0.0, 1.0
        for p_, q_ in ((a[0] - b[0], a[0] - r[0]), (b[0] - a[0], r[0] + r[2] - a[0]),
                       (a[1] - b[1], a[1] - r[1]), (b[1] - a[1], r[1] + r[3] - a[1])):
            if p_ == 0:
                if q_ < 0: return False
            elif p_ < 0: t0 = max(t0, q_ / p_)
            else: t1 = min(t1, q_ / p_)
        return t0 < t1

    def attach(g, pt):  # where an arc from pt meets the square: its side, 5 from the centre
        sgn = 1 if side(g, pt) == 2 else -1
        return (g['sq'][0] + sgn * 5 * g['f'][1], g['sq'][1] - sgn * 5 * g['f'][0])

    # modifiers onto their square: a small move so the arc meets the square straight (the
    # user's edits of the full set: 23 such moves). Only a move of at most ALIGN px along one
    # axis, the same for every reaction the modifier acts on, that keeps the main lines it
    # ends straight, keeps it in its compartment and makes it overlap nothing
    def overlap(a, b):
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
    geo = {p: geometry(p, fl) for p, fl in ((p, flows(p, quiet=True)) for p in procs) if fl}
    want = {}
    for p, g in geo.items():
        for e in flows(p, quiet=True)[2]:
            m = e.source
            if N[m].parent in ents or cd_bends.turn([cen(m)] + route(p, e.points) + [cen(p)]):
                continue  # complex members move with their complex; an L arc is straight already
            M, T = cen(m), attach(g, cen(m))
            ax = 0 if abs(M[0] - T[0]) < abs(M[1] - T[1]) else 1  # the axis with the small offset
            want.setdefault((m, ax), []).append(T[ax] - M[ax])
    ends = [(g['r'], g['q']) for g in geo.values()]
    for (m, ax), ds in sorted(want.items()):
        d = ds[0]
        if not 0.5 < abs(d) <= ALIGN or max(ds) - min(ds) > 1:
            continue
        if any(m in (a, b) and abs(cen(a)[ax] - cen(b)[ax]) < 1 for a, b in ends):
            continue  # it ends a main line that is straight on this axis
        moved = [m] + cd_straighten.descendants(m, members)
        new = {j: tuple(v + (d if k == ax else 0) for k, v in enumerate(box[j])) for j in moved}
        cm = comp_of(m)
        if cm and not (box[cm][0] <= new[m][0] and new[m][0] + new[m][2] <= box[cm][0] + box[cm][2]
                       and box[cm][1] <= new[m][1] and new[m][1] + new[m][3] <= box[cm][1] + box[cm][3]):
            continue
        if any(overlap(new[m], box[j]) for j in ents if j not in moved and N[j].parent not in moved
               and m not in cd_straighten.descendants(j, members)):
            continue
        box.update(new)
        for j in moved:
            front[j] = (box[j][0], box[j][1]) + front[j][2:]

    # proteins: one per label, residues from the state variables of all its nodes
    sv = {i: [(txt, border_angle(rx, ry)) for txt, rx, ry in d.states] for i, d in ents.items() if d.kind in ('Macromolecule', 'Complex')}
    # bound ligands: CellDesigner has one structural state per species; same text twice (two cAMP) is written once
    struct = {}
    for i in sv:
        st = [(txt, ang) for txt, ang in sv[i] if is_structural(txt)]
        if st:
            # counts dropped ("1:cAMP" and "2:cAMP" -> "cAMP", user's edit of estrogen v01);
            # placed where the icon with the highest count is
            name = lambda txt: re.sub(r'^\d+:', '', txt)
            cnt = lambda txt: int(re.match(r'^(\d+):', txt).group(1)) if re.match(r'^\d+:', txt) else 0
            struct[i] = ('/'.join(dict.fromkeys(name(txt) for txt, _ in st)), max(st, key=lambda q: cnt(q[0]))[1])
        sv[i] = [(txt, ang) for txt, ang in sv[i] if not is_structural(txt)]
        if ents[i].kind == 'Complex' and sv[i]:
            print('complex %s: state variables not converted' % i); sv[i] = []
    # a protein marked only by free text (Su, Glut: not in CellDesigner's menu) gets no empty
    # residues: the free-text state where it is marked, nothing where unmodified (user, 2026-10-16)
    free = {label[i] for i in struct} - {label[i] for i in sv if any(txt for txt, _ in sv[i])}
    for i in sv:
        if label[i] in free: sv[i] = []
    cls = {i: cd_class(d) for i, d in ents.items()}
    nucl = {'GENE': {}, 'RNA': {}}  # one gene / RNA per label, as one protein per label
    for i in sorted(ents, key=lambda i: [int(x) for x in re.findall(r'\d+', i)]):
        if cls[i] in nucl:
            nucl[cls[i]].setdefault(label[i], ('g_' if cls[i] == 'GENE' else 'r_') + sid(i))
    prot, res_of = {}, {}
    for i in sorted((i for i in sv if ents[i].kind == 'Macromolecule'), key=lambda i: [int(x) for x in re.findall(r'\d+', i)]):
        pid = prot.setdefault(label[i], 'pr_' + sid(i))
        sites = res_of.setdefault(pid, [])
        for k, (txt, ang) in enumerate(sv[i]):
            if txt.split('@')[0] and txt.split('@')[0] not in STATE:
                sys.exit('state variable %r on %s: unknown modification state' % (txt, label[i]))
            # the same site on another node of this protein: same site (Pa@26), wherever the
            # icon sits (eNOS: Pa@26 at three places gave three residues); no site: same place.
            # Site names are not written: CellDesigner and MINERVA show only the modification
            # symbol in the circle (P, Ac, Me); user's rule, glutaminase 2026-10-13
            site = txt.partition('@')[2]
            hit = next((s for s in sites if s['site'] == site and (site or abs(s['angle'] - ang) < 0.3)), None)
            if hit is None:
                hit = {'id': '%s_r%d' % (pid, len(sites) + 1), 'site': site, 'angle': ang}
                # the top middle stays free for MINERVA's N:x; state variables on the sides
                # (lower half) or at the corners (user's rule, 2026-10-13)
                if mult[i] > 1 and abs(ang - math.pi / 2) < math.pi / 8:
                    print('%s: state variable %r at the top middle, where N:%d goes' % (label[i], txt, mult[i]))
                sites.append(hit)
            sv[i][k] = (txt, hit['id'])

    def sub(p, tag, text=None, **a):
        e = etree.SubElement(p, '{%s}%s' % (CD, tag), {k.rstrip('_'): str(v) for k, v in a.items()})
        if text is not None: e.text = text
        return e

    sbml = etree.Element('sbml', nsmap={None: 'http://www.sbml.org/sbml/level2/version4', 'celldesigner': CD}, level='2', version='4')
    mid = re.sub(r'\W', '_', diagram.name)
    model = etree.SubElement(sbml, 'model', metaid=mid, id=mid)
    ext = sub(etree.SubElement(model, 'annotation'), 'extension')
    sub(ext, 'modelVersion', '4.0'); sub(ext, 'modelDisplay', sizeX=int(W), sizeY=int(H))
    inc = sub(ext, 'listOfIncludedSpecies') if members else None
    lco = sub(ext, 'listOfCompartmentAliases')
    depth = lambda i: 0 if comp_of(i) is None else 1 + depth(comp_of(i))
    for i in sorted(comps, key=lambda i: (depth(i), box[i][1], box[i][0])):  # outer ones first
        d = comps[i]; x, y, w, h = box[i]
        a = sub(lco, 'compartmentAlias', id='ca_' + sid(i), compartment='c_' + sid(i))
        sub(a, 'class', 'SQUARE'); sub(a, 'bounds', x=x, y=y, w=w, h=h)
        # the name where yEd has its label (top left of the label box)
        # CellDesigner's name point is the text baseline: 12.5 below the label top (its save of estrogen v01)
        lx, ly = d.label_at or (6, 0)
        sub(a, 'namePoint', x=x + lx, y=y + ly + 12.5)
        # as CellDesigner's own files (F021); colour: the yEd fill over white (yEd uses transparency)
        sub(a, 'doubleLine', thickness='12.0', outerWidth='2.0', innerWidth='1.0')
        fc = (d.fill or '#FFFFFF').lstrip('#'); al = int(fc[6:8], 16) / 255 if len(fc) == 8 else 1
        rgb = ''.join('%02x' % round(255 - al * (255 - int(fc[k:k + 2], 16))) for k in (0, 2, 4))
        sub(a, 'paint', color='ff' + rgb, scheme='Color'); sub(a, 'info', state='empty', angle='-1.5707963267948966')
    lca = sub(ext, 'listOfComplexSpeciesAliases')
    las = sub(ext, 'listOfSpeciesAliases')
    for i, d in ents.items():
        x, y, w, h = box[i]
        cx = d.parent if d.parent in ents else None
        if d.kind == 'Complex':
            a = sub(lca, 'complexSpeciesAlias', id='sa_' + sid(i), species='s_' + sid(i))
        else:
            a = sub(las, 'speciesAlias', id='sa_' + sid(i), species='s_' + sid(i))
        if cx: a.set('complexSpeciesAlias', 'sa_' + sid(cx))  # members carry no compartment (CellDesigner's files)
        elif comp_of(i): a.set('compartmentAlias', 'ca_' + sid(comp_of(i)))
        sub(a, 'activity', 'inactive'); sub(a, 'bounds', x=x, y=y, w=w, h=h)
        sub(a, 'font', size=12); sub(a, 'view', state='usual')
        if d.kind == 'Complex':
            sub(a, 'backupSize', w='0.0', h='0.0'); sub(a, 'backupView', state='none')
        if i in struct:
            sub(a, 'structuralState', angle=struct[i][1])
        for v in ('usualView', 'briefView'):
            u = sub(a, v)
            # members: the usual view sits at the offset in the complex (CellDesigner's own files)
            # in a compartment: the offset from the compartment's top left (CellDesigner's save of estrogen v01)
            cm = comp_of(i) if not cx else None
            ip = (x - box[cx][0], y - box[cx][1]) if cx and v == 'usualView' else \
                 (x - box[cm][0], y - box[cm][1]) if cm and v == 'usualView' else (0.0, 0.0)
            sub(u, 'innerPosition', x=ip[0], y=ip[1]); sub(u, 'boxSize', width=w, height=h)
            # CellDesigner keeps this one width as a float (107.45129863291555 -> 107.45130157470703)
            sub(u, 'singleLine', width=unpack("f", pack("f", w))[0] if d.kind == 'Complex' and v == 'briefView' else '1.0')
            sub(u, 'paint', color='ff' + (d.fill or '#FFFFFF').lstrip('#').lower(), scheme='Color')
        ct = [u for u in units_of_information(d) if u.startswith('ct:')]
        if ct:  # the old files: <info state="open" prefix="ct" label="gene"/> (angle as there)
            sub(a, 'info', state='open', prefix='ct', label=ct[0][3:], angle='-1.5707963267948966')
        else:
            sub(a, 'info', state='empty', angle='-1.5707963267948966')
    sub(ext, 'listOfGroups')
    lp = sub(ext, 'listOfProteins')
    for lab, pid in prot.items():
        p = sub(lp, 'protein', id=pid, name=cd_name(lab), type='GENERIC')
        if res_of[pid]:
            lr = sub(p, 'listOfModificationResidues')
            for s in res_of[pid]:
                sub(lr, 'modificationResidue', angle=s['angle'], id=s['id'], side='none')
    lg = sub(ext, 'listOfGenes')
    for lab, gid in nucl['GENE'].items(): sub(lg, 'gene', id=gid, name=cd_name(lab), type='GENE')
    lrn = sub(ext, 'listOfRNAs')
    for lab, rid in nucl['RNA'].items(): sub(lrn, 'RNA', id=rid, name=cd_name(lab), type='RNA')
    for tag in ('listOfAntisenseRNAs', 'listOfLayers', 'listOfBlockDiagrams'):
        sub(ext, tag)
    # the default units; without them CellDesigner warns when it opens the file
    units = etree.SubElement(model, 'listOfUnitDefinitions')
    for k, (name, kind, exp) in enumerate([('substance', 'mole', None), ('volume', 'litre', None),
                                           ('area', 'metre', '2'), ('length', 'metre', None), ('time', 'second', None)]):
        ud = etree.SubElement(units, 'unitDefinition', metaid=name, id=name, name=name)
        u = etree.SubElement(etree.SubElement(ud, 'listOfUnits'), 'unit', metaid='CDMT%05d' % (k + 1), kind=kind)
        if exp: u.set('exponent', exp)
    lcm = etree.SubElement(model, 'listOfCompartments')
    etree.SubElement(lcm, 'compartment', metaid='default', id='default', size='1', units='volume')
    for i in sorted(comps, key=lambda i: (depth(i), box[i][1], box[i][0])):
        nm = cd_name(' '.join(' | '.join(comps[i].labels).split()))
        cp = etree.SubElement(lcm, 'compartment', metaid='c_' + sid(i), id='c_' + sid(i), name=nm,
                              size='1', units='volume', outside='c_' + sid(comp_of(i)) if comp_of(i) else 'default')
        sub(sub(etree.SubElement(cp, 'annotation'), 'extension'), 'name', nm)  # CellDesigner adds it when it saves

    RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    BQ = 'http://biomodels.net/biology-qualifiers/'
    def miriam(parent, about, lab, abc=False):
        if lab not in ann: return
        fam, uris = ann[lab]
        # the namespaces CellDesigner declares, so its save changes nothing;
        # in the notes of included species it writes them in alphabetical order
        ns = {'rdf': RDF, 'dc': 'http://purl.org/dc/elements/1.1/', 'dcterms': 'http://purl.org/dc/terms/',
              'vCard': 'http://www.w3.org/2001/vcard-rdf/3.0#', 'bqbiol': BQ, 'bqmodel': 'http://biomodels.net/model-qualifiers/'}
        if abc: ns = dict(sorted(ns.items()))
        rdf = etree.SubElement(parent, '{%s}RDF' % RDF, nsmap=ns)
        d = etree.SubElement(rdf, '{%s}Description' % RDF, {'{%s}about' % RDF: '#' + about})
        bag = etree.SubElement(etree.SubElement(d, '{%s}%s' % (BQ, 'hasVersion' if fam else 'is')), '{%s}Bag' % RDF)
        for u in uris:
            etree.SubElement(bag, '{%s}li' % RDF, {'{%s}resource' % RDF: u})

    catalysed = {}
    for e in E:
        # CellDesigner lists every modifier here, not only catalysts (its save of glutaminase v01; F021)
        if e.target in procs and e.source in ents and e.head in MOD:
            catalysed.setdefault(e.source, []).append('re_' + sid(e.target))
    # logic gates (yEd Operator nodes): inputs are the entities joined to the operator by
    # plain arcs (either direction); the operator's modulation arc goes to a process
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    gate_in = {o: [e.source if e.target == o else e.target for e in E if o in (e.source, e.target) and e.head is None
                   and (e.source if e.target == o else e.target) in ents] for o in ops}
    for o in ops:  # left to right, as in the user's file
        gate_in[o].sort(key=lambda m: (N[m].box[0], N[m].box[1]))
    for e in E:
        if e.source in ops and e.target in procs and e.head in MOD:
            for m in gate_in[e.source]:  # CellDesigner lists the gate's inputs (user's mevalonate gate)
                catalysed.setdefault(m, []).append('re_' + sid(e.target))
    def identity(x, i):
        d = ents[i]
        si = sub(x, 'speciesIdentity'); sub(si, 'class', cls[i])
        if d.kind == 'Macromolecule':
            sub(si, 'proteinReference', prot[label[i]])
        elif cls[i] in nucl:
            sub(si, 'geneReference' if cls[i] == 'GENE' else 'rnaReference', nucl[cls[i]][label[i]])
        n = mult[i]
        if n > 1 or sv.get(i) or i in struct:
            st = sub(si, 'state')
            if n > 1: sub(st, 'homodimer', str(n))
            if sv.get(i):
                lm = sub(st, 'listOfModifications')
                for txt, rid in sv[i]:
                    m = txt.split('@')[0]
                    sub(lm, 'modification', residue=rid, state=STATE[m] if m else 'empty')
            if i in struct:
                sub(sub(st, 'listOfStructuralStates'), 'structuralState', structuralState=struct[i][0])
        if d.kind != 'Macromolecule' and cls[i] not in nucl:
            sub(si, 'name', name_of(i))

    # a source/sink is named after its id, as CellDesigner names a new degraded species (s48)
    name_of = lambda i: 's_' + sid(i) if cls[i] == 'DEGRADED' else cd_name(label[i])
    XH = 'http://www.w3.org/1999/xhtml'
    lsp = etree.SubElement(model, 'listOfSpecies')
    for i, d in ents.items():
        if d.parent in ents:
            # a complex member: an included species, its MIRIAM RDF in the notes (CellDesigner's convention)
            s = sub(inc, 'species', id='s_' + sid(i), name=cd_name(label[i]))
            h = etree.SubElement(sub(s, 'notes'), '{%s}html' % XH, nsmap={None: XH})
            etree.SubElement(etree.SubElement(h, '{%s}head' % XH), '{%s}title' % XH)
            miriam(etree.SubElement(h, '{%s}body' % XH), 's_' + sid(i), label[i], abc=True)
            x = sub(s, 'annotation'); sub(x, 'complexSpecies', 's_' + sid(d.parent))
            identity(x, i)
            continue
        s = etree.SubElement(lsp, 'species', metaid='s_' + sid(i), id='s_' + sid(i), name=name_of(i),
                             compartment='c_' + sid(comp_of(i)) if comp_of(i) else 'default', initialAmount='0')
        an = etree.SubElement(s, 'annotation'); x = sub(an, 'extension')
        sub(x, 'positionToCompartment', 'inside')
        identity(x, i)
        if i in catalysed:
            lc = sub(x, 'listOfCatalyzedReactions')
            for r in catalysed[i]: sub(lc, 'catalyzed', reaction=r)
        miriam(an, 's_' + sid(i), label[i])

    lr = etree.SubElement(model, 'listOfReactions')
    n_ref = [0]
    def ref(parent, tag, i):
        n_ref[0] += 1
        r = etree.SubElement(parent, tag, metaid='SR%d' % n_ref[0], species='s_' + sid(i))
        sub(sub(etree.SubElement(r, 'annotation'), 'extension'), 'alias', 'sa_' + sid(i))
    def line(k, n=1, **a):  # connect scheme with n segments
        ld = sub(sub(k, 'connectScheme', connectPolicy='direct', **a), 'listOfLineDirection')
        for j in range(n): sub(ld, 'lineDirection', index=j, value='unknown')
    for p in procs:
        fl = flows(p)
        if fl is None: continue
        ins, outs, mods, gates, reversible, c = fl
        g = geometry(p, fl)
        r_, q_, ra, qa, A, B, wr, bend, sq, f = (g[k] for k in ('r', 'q', 'ra', 'qa', 'A', 'B', 'wr', 'bend', 'sq', 'f'))
        side_of = lambda pt: side(g, pt)
        rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(p), id='re_' + sid(p))
        if not reversible: rx.set('reversible', 'false')  # true is the SBML default; CellDesigner then leaves it out
        x = sub(etree.SubElement(rx, 'annotation'), 'extension')
        sub(x, 'reactionType', 'STATE_TRANSITION')
        br = sub(sub(x, 'baseReactants'), 'baseReactant', species='s_' + sid(r_), alias='sa_' + sid(r_)); ra and sub(br, 'linkAnchor', position=ra)
        bp = sub(sub(x, 'baseProducts'), 'baseProduct', species='s_' + sid(q_), alias='sa_' + sid(q_)); qa and sub(bp, 'linkAnchor', position=qa)
        # added reactants and products: to the centre, no linkAnchor (as CellDesigner saves them)
        for lst, tag, attr, es, end, idx in (('listOfReactantLinks', 'reactantLink', 'reactant', ins[1:], 'source', '-1,0'),
                                             ('listOfProductLinks', 'productLink', 'product', outs[1:], 'target', '-1,1')):
            if es:
                l = sub(x, lst)
                for e in es:
                    k = sub(l, tag, **{attr: 's_' + sid(getattr(e, end))}, alias='sa_' + sid(getattr(e, end)), targetLineIndex=idx)
                    line(k); sub(k, 'line', width='1.0', color='ff000000', type='Straight')
        if bend:
            line(x, 2, rectangleIndex=1 if wr else 0)
            sub(x, 'editPoints', '%s,%s' % cd_bends.to_frame(A, B, bend))
        elif g['split']:
            line(x, 3, rectangleIndex=1)
            sub(x, 'editPoints', '%s,0.0 %s,0.0' % g['split'])
        else:
            line(x, rectangleIndex=0)
        sub(x, 'line', width='1.0', color='ff000000')
        if mods or gates:
            lm = sub(x, 'listOfModification')
            for e in mods:
                m = e.source; M = cen(m)
                T = attach(g, M)  # the arc's end on the square's side (the user's glycolysis v01 bends)
                pts = advanced and lane(m, M, T, e)
                if pts:
                    run = [M] + pts + [T]
                    for j in ents:
                        if j != m and N[j].parent not in ents and m not in cd_straighten.descendants(j, members) and \
                                any(crosses(a, b, box[j]) for a, b in zip(run, run[1:])):
                            print('%s: the arc from %s runs through %s' % (p, label[m] or m, label[j] or j))
                else:
                    # a significant bend: one long L from the modifier to that end
                    w = cd_bends.turn([cen(m)] + route(p, e.points) + [c])
                    bend = cd_bends.corner(M, T, w) if w else None
                    if bend and min(math.hypot(bend[0] - P[0], bend[1] - P[1]) for P in (M, T)) < cd_bends.EPS:
                        bend = None
                    pts = [bend] if bend else []
                # a line to the centre has no linkTarget (the user's CellDesigner edit of estrogen v01)
                k = sub(lm, 'modification', type=MOD[e.head], modifiers='s_' + sid(m), aliases='sa_' + sid(m),
                        targetLineIndex='-1,%d' % side_of(M))
                if pts:  # frame: origin the modifier's centre, x axis to the arc's end
                    k.set('editPoints', ' '.join('%s,%s' % cd_bends.to_frame(M, T, q) for q in pts))
                line(k, len(pts) + 1); sub(k, 'line', width='1.0', color='ff000000')
            # a gate (the user's CellDesigner file, mevalonate): one modification of type
            # BOOLEAN_LOGIC_GATE_* listing all inputs, the gate at editPoints (absolute; checked
            # through MINERVA), then one modification per input to the gate, centre (INACTIVE)
            for e in gates:
                o = e.source; inp = gate_in[o]
                gc = cen(o)
                k = sub(lm, 'modification', type=GATE[' | '.join(N[o].labels).strip().upper()], modifiers=','.join('s_' + sid(m) for m in inp),
                        aliases=','.join('sa_' + sid(m) for m in inp), modificationType=MOD[e.head],
                        targetLineIndex='-1,%d' % side_of(gc), editPoints='%s,%s' % gc)
                line(k)
                sub(k, 'line', width='1.0', color='ff000000')
                for m in inp:
                    # as CellDesigner saves it: targetLineIndex -1,0, no linkTarget (mevalonate, user's file)
                    k = sub(lm, 'modification', type=MOD[e.head], modifiers='s_' + sid(m), aliases='sa_' + sid(m), targetLineIndex='-1,0')
                    line(k)
                    sub(k, 'line', width='1.0', color='ff000000')
        lr_ = etree.SubElement(rx, 'listOfReactants')
        for e in ins: ref(lr_, 'speciesReference', e.source)
        lp_ = etree.SubElement(rx, 'listOfProducts')
        for e in outs: ref(lp_, 'speciesReference', e.target)
        if mods or gates:
            lm_ = etree.SubElement(rx, 'listOfModifiers')
            for e in mods: ref(lm_, 'modifierSpeciesReference', e.source)
            for e in gates:
                for m in gate_in[e.source]: ref(lm_, 'modifierSpeciesReference', m)
        left = [e for e in E if p in (e.source, e.target) and e.id not in {f.id for f in ins + outs + mods + gates}]
        if left: print('process %s: edges not converted: %s' % (p, ', '.join(e.id for e in left)))
    # arcs between two entities (no process: reduced notation, e.g. a stimulation of a phenotype)
    for e in E:
        if e.source in ents and e.target in ents and e.head in REDUCED:
            # straight from source to target, no process
            rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(e.id), id='re_' + sid(e.id), reversible='false')
            x = sub(etree.SubElement(rx, 'annotation'), 'extension')
            sub(x, 'reactionType', REDUCED[e.head])
            # both ends at the centre: no linkAnchor (CellDesigner's save of the SREBP and ACLY files)
            sub(sub(x, 'baseReactants'), 'baseReactant', species='s_' + sid(e.source), alias='sa_' + sid(e.source))
            sub(sub(x, 'baseProducts'), 'baseProduct', species='s_' + sid(e.target), alias='sa_' + sid(e.target))
            line(x)
            sub(x, 'line', width='1.0', color='ff000000')
            ref(etree.SubElement(rx, 'listOfReactants'), 'speciesReference', e.source)
            ref(etree.SubElement(rx, 'listOfProducts'), 'speciesReference', e.target)
        elif e.source in ents and e.target in ents:
            print('arc %s (%s -> %s, %s): no process, not converted' % (e.id, label[e.source] or e.source, label[e.target] or e.target, e.head))
    # written as CellDesigner writes it (no indentation, double-quoted declaration),
    # so a file opened and saved in CellDesigner can be compared line by line
    print('%s: %d species, %d proteins, %d reactions' % (diagram.name, len(ents), len(prot), len(lr)))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(sbml, encoding='UTF-8', pretty_print=True).decode('utf-8')
    return '\n'.join(l.lstrip() for l in xml.split('\n'))

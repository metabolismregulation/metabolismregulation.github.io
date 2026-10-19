# Write a CellDesigner 4.0 file (SBML L2V4 with the CellDesigner extension)
# from a map (model.py) read from a yEd SBGN map; read() at the end goes the other way.
# Where lines, squares and points go, and the tidy moves: cd_layout.py (the CellDesigner adapter);
# this module writes them.
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
# - Bend points only for long connectors that yEd draws as one L (layout.py);
#   others the user adds by hand. Lines end at node centres. Main lines a few px off the vertical or
#   horizontal are straightened (cd_straighten.py); modifiers up to 15 px off
#   their square are moved onto it, if nothing overlaps after the move.
# - MIRIAM annotation from the map's node properties (annotation.py):
#   bqbiol:is for one entity, bqbiol:hasVersion for a family.
# - Metabolites become circles of cd_layout.CHEMICAL diameter on the yEd centre.
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
from . import cd_layout, report
from .cd_layout import ANCHOR, SQUARE, anchor_point, from_frame, square_point, to_frame
from .layout import unbent
from .annotation import to_properties
from .graphml import EQUIV, without_delays
from .model import Map, Node, Arc

CD = 'http://www.sbml.org/2001/ns/celldesigner'
CLASS = {'Macromolecule': 'PROTEIN', 'SimpleChemical': 'SIMPLE_MOLECULE', 'NucleicAcidFeature': 'GENE',
         'UnspecifiedEntity': 'UNKNOWN', 'Complex': 'COMPLEX', 'Phenotype': 'PHENOTYPE',
         'SourceAndSink': 'DEGRADED', 'EmptySet': 'DEGRADED',
         # CellDesigner has no submap: a phenotype (user's SREBP file, 2026-10-13)
         'Submap': 'PHENOTYPE'}
# arc between two entities (no process) -> CellDesigner reduced-notation reaction
# (user's SREBP file: submap -> submap and SREBP2 -> submap stimulation)
REDUCED = {'stimulation': 'PHYSICAL_STIMULATION',
           'inhibition': 'NEGATIVE_INFLUENCE',
           'modulation': 'REDUCED_MODULATION', 'trigger': 'REDUCED_TRIGGER'}  # as the PD map (CellDesigner 4.4, autumn 2025)
# a logic gate on arcs between entities: a BOOLEAN_LOGIC_GATE reaction, its arc typed as in the PD map
GATE_ARC = {'stimulation': 'POSITIVE_INFLUENCE', 'inhibition': 'NEGATIVE_INFLUENCE'}
# a dashed arc (unknown) in CellDesigner's unknown types, where it has one (as the PD map)
UNKNOWN = {'CATALYSIS': 'UNKNOWN_CATALYSIS', 'INHIBITION': 'UNKNOWN_INHIBITION', 'NEGATIVE_INFLUENCE': 'UNKNOWN_NEGATIVE_INFLUENCE'}
REACTION = {'Process': 'STATE_TRANSITION', 'OmittedProcess': 'KNOWN_TRANSITION_OMITTED', 'UncertainProcess': 'UNKNOWN_TRANSITION'}
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


def plain_name(s):  # inverse of cd_name: _space_, _alpha_ back to text
    for a, b in NAME:
        s = s.replace(b, a)
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


def write(diagram, ann, layout='straight', move=True):
    # the CellDesigner file of a map (model.Map), with ann the MIRIAM annotation (annotation.py).
    # layout 'straight' (straight lines, as yEd calls them): the necessary minimum, simple and reliable, improved by hand in CellDesigner
    # (straight lines, squares midway); 'advanced': a layout that already looks good, squares and
    # modifier arcs where yEd draws them (F022 BCAA v04; names by the user, 2026-10-16).
    # move: the tidy moves (main lines straightened, an end onto a larger node's centre line, a
    # modifier onto its square), on unless the user forbids moving nodes (user, 2026-10-19); what
    # CellDesigner itself needs (circles, multimers, the complex name's room) is done either way
    advanced = layout == 'advanced'
    diagram = without_delays(diagram, 'CellDesigner')
    eq = [i for i, d in diagram.nodes.items() if d.kind == 'Operator' and d.labels[:1] == [EQUIV]]
    if eq:  # CellDesigner has no equivalence operator
        report.say('left out', 'equivalence operator: no CellDesigner form, left out (%s), its entities kept' % ', '.join(eq))
        diagram = replace(diagram, nodes={i: d for i, d in diagram.nodes.items() if i not in eq},
                          arcs=[a for a in diagram.arcs if a.source not in eq and a.target not in eq])
    N, E = diagram.nodes, diagram.arcs
    ents = {i: d for i, d in N.items() if d.kind in CLASS}
    procs = {i: d for i, d in N.items() if d.kind in ('Process', 'OmittedProcess', 'UncertainProcess')}
    comps = {i: d for i, d in N.items() if d.kind == 'Compartment'}
    def comp_of(i):
        q = N[i].parent
        while q is not None and q not in comps:
            q = N[q].parent
        return q
    other = set(N) - set(ents) - set(procs) - set(comps) - {i for i, d in N.items() if d.kind == 'Operator'}
    if other:
        report.say('left out', 'not converted: ' + ', '.join(sorted('%s %s' % (i, N[i].kind) for i in other)))
    mult = {i: d.count for i, d in N.items() if d.kind in CLASS}
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
    # where every line, square and point goes, the tidy moves included (cd_layout.py)
    drawing = cd_layout.draw(diagram, ents, members, label, advanced, move)
    box, cen = drawing.box, drawing.cen
    W, H = drawing.size

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
            report.say('left out', 'complex %s: state variables not converted' % i); sv[i] = []
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
                    report.say('warning', '%s: state variable %r at the top middle, where N:%d goes' % (label[i], txt, mult[i]))
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
        # an oval: a plain yEd ellipse read as a compartment (a cell, AsthMap)
        sub(a, 'class', 'OVAL' if d.outline == 'ShapeNode ellipse' else 'SQUARE'); sub(a, 'bounds', x=x, y=y, w=w, h=h)
        # the name where yEd has its label (top left of the label box)
        # CellDesigner's name point is the text baseline: 12.5 below the label top (its save of estrogen v01)
        lx, ly = d.label_at or (6, 0)
        sub(a, 'namePoint', x=x + lx, y=y + ly + 12.5)
        # as CellDesigner's own files (F021); colour: the yEd fill over white (yEd uses transparency)
        sub(a, 'doubleLine', thickness='12.0', outerWidth='2.0', innerWidth='1.0')
        fc = (d.fill or '#FFFFFF').lstrip('#'); al = int(fc[6:8], 16) / 255 if len(fc) == 8 else 1
        rgb = ''.join('%02x' % round(255 - al * (255 - int(fc[k:k + 2], 16))) for k in (0, 2, 4))
        sub(a, 'paint', color='ff' + rgb, scheme='Color'); sub(a, 'info', state='empty', angle='-1.5707963267948966')
    # one species per entity, each glyph an alias of it, as CellDesigner saves a molecule drawn
    # twice (the user's pyrimidine: ATP is species s11 with aliases n3 and n12; user, 2026-10-19);
    # a member's species belongs to its complex's species; a source or sink stays on its own (SBGN
    # does not clone the empty set)
    rep, first = {}, {}
    def rep_of(i):
        if i not in rep:
            d = ents[i]
            k = i if cls[i] == 'DEGRADED' else (rep_of(d.parent) if d.parent in ents else None, diagram.biology.glyph[i])
            rep[i] = first.setdefault(k, i)
        return rep[i]
    for i in ents: rep_of(i)
    spec = lambda i: 's_' + sid(rep[i])
    lca = sub(ext, 'listOfComplexSpeciesAliases')
    las = sub(ext, 'listOfSpeciesAliases')
    for i, d in ents.items():
        x, y, w, h = box[i]
        cx = d.parent if d.parent in ents else None
        if d.kind == 'Complex':
            a = sub(lca, 'complexSpeciesAlias', id='sa_' + sid(i), species=spec(i))
        else:
            a = sub(las, 'speciesAlias', id='sa_' + sid(i), species=spec(i))
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
        nm = cd_name(' '.join(' | '.join(x for x in comps[i].labels if x.strip()).split()))
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
        if d.dashed: sub(si, 'hypothetical', 'true')  # a dashed border (PD map: after the class)
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
    name_of = lambda i: spec(i) if cls[i] == 'DEGRADED' else cd_name(label[i])
    XH = 'http://www.w3.org/1999/xhtml'
    lsp = etree.SubElement(model, 'listOfSpecies')
    for i, d in ents.items():
        if rep[i] != i:
            continue
        if d.parent in ents:
            # a complex member: an included species, its MIRIAM RDF in the notes (CellDesigner's convention)
            s = sub(inc, 'species', id=spec(i), name=cd_name(label[i]))
            h = etree.SubElement(sub(s, 'notes'), '{%s}html' % XH, nsmap={None: XH})
            etree.SubElement(etree.SubElement(h, '{%s}head' % XH), '{%s}title' % XH)
            miriam(etree.SubElement(h, '{%s}body' % XH), spec(i), label[i], abc=True)
            x = sub(s, 'annotation'); sub(x, 'complexSpecies', spec(d.parent))
            identity(x, i)
            continue
        s = etree.SubElement(lsp, 'species', metaid=spec(i), id=spec(i), name=name_of(i),
                             compartment='c_' + sid(comp_of(i)) if comp_of(i) else 'default', initialAmount='0')
        an = etree.SubElement(s, 'annotation'); x = sub(an, 'extension')
        sub(x, 'positionToCompartment', 'inside')
        identity(x, i)
        cat = list(dict.fromkeys(r for j in ents if rep[j] == i for r in catalysed.get(j, ())))
        if cat:
            lc = sub(x, 'listOfCatalyzedReactions')
            for r in cat: sub(lc, 'catalyzed', reaction=r)
        miriam(an, spec(i), label[i])

    def typed(e, t):  # a dashed arc: CellDesigner's unknown type, or the type itself with a note
        if not e.dashed: return t
        if t not in UNKNOWN: report.say('changed', 'arc %s: dashed %s written solid (CellDesigner has no unknown form)' % (e.id, t))
        return UNKNOWN.get(t, t)
    lr = etree.SubElement(model, 'listOfReactions')
    n_ref = [0]
    def ref(parent, tag, i):
        n_ref[0] += 1
        r = etree.SubElement(parent, tag, metaid='SR%d' % n_ref[0], species=spec(i))
        sub(sub(etree.SubElement(r, 'annotation'), 'extension'), 'alias', 'sa_' + sid(i))
    def line(k, n=1, **a):  # connect scheme with n segments
        ld = sub(sub(k, 'connectScheme', connectPolicy='direct', **a), 'listOfLineDirection')
        for j in range(n): sub(ld, 'lineDirection', index=j, value='unknown')
    for p, fl in drawing.lines().items():
        if fl is None:
            report.say('left out', 'process %s: no reactant or product, skipped' % p); continue
        ins, outs, mods, gates, reversible, c = fl
        g = drawing.geometry(p, fl)
        r_, q_, ra, qa, A, B, sq, f = (g[k] for k in ('r', 'q', 'ra', 'qa', 'A', 'B', 'sq', 'f'))
        side_of = lambda pt: drawing.side(g, pt)
        rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(p), id='re_' + sid(p))
        if not reversible: rx.set('reversible', 'false')  # true is the SBML default; CellDesigner then leaves it out
        x = sub(etree.SubElement(rx, 'annotation'), 'extension')
        sub(x, 'reactionType', REACTION.get(N[p].kind, 'STATE_TRANSITION'))
        br = sub(sub(x, 'baseReactants'), 'baseReactant', species=spec(r_), alias='sa_' + sid(r_)); ra and sub(br, 'linkAnchor', position=ra)
        bp = sub(sub(x, 'baseProducts'), 'baseProduct', species=spec(q_), alias='sa_' + sid(q_)); qa and sub(bp, 'linkAnchor', position=qa)
        # added reactants and products: to the centre, no linkAnchor (as CellDesigner saves them)
        for lst, tag, attr, es, end, idx in (('listOfReactantLinks', 'reactantLink', 'reactant', ins[1:], 'source', '-1,0'),
                                             ('listOfProductLinks', 'productLink', 'product', outs[1:], 'target', '-1,1')):
            if es:
                l = sub(x, lst)
                for e in es:
                    k = sub(l, tag, **{attr: spec(getattr(e, end))}, alias='sa_' + sid(getattr(e, end)), targetLineIndex=idx)
                    line(k); sub(k, 'line', width='1.0', color='ff000000', type='Straight')
        line(x, len(g['ep']) + 1, rectangleIndex=g['k'])
        if g['ep']:
            sub(x, 'editPoints', ' '.join('%s,%s' % q for q in g['ep']))
        sub(x, 'line', width='1.0', color='ff000000')
        if mods or gates:
            lm = sub(x, 'listOfModification')
            for e in mods:
                m = e.source
                i, M, T, at, pts = drawing.modifier(p, g, e, len(mods) + len(gates) > 1)
                # a line to the centre has no linkTarget (the user's CellDesigner edit of estrogen v01)
                k = sub(lm, 'modification', type=typed(e, MOD[e.head]), modifiers=spec(m), aliases='sa_' + sid(m),
                        targetLineIndex='-1,%d' % i)
                if pts:  # frame: origin the modifier's centre (or its anchor), x axis to the arc's end
                    k.set('editPoints', ' '.join('%s,%s' % to_frame(M, T, q) for q in pts))
                line(k, len(pts) + 1)
                if at:  # as the PD map writes an anchored modifier
                    sub(sub(k, 'linkTarget', species=spec(m), alias='sa_' + sid(m)), 'linkAnchor', position=at)
                sub(k, 'line', width='1.0', color='ff000000')
            # a gate (the user's CellDesigner file, mevalonate): one modification of type
            # BOOLEAN_LOGIC_GATE_* listing all inputs, the gate at editPoints (absolute; checked
            # through MINERVA), then one modification per input to the gate, centre (INACTIVE)
            for e in gates:
                o = e.source; inp = gate_in[o]
                gc = cen(o)
                k = sub(lm, 'modification', type=GATE[' | '.join(N[o].labels).strip().upper()], modifiers=','.join(spec(m) for m in inp),
                        aliases=','.join('sa_' + sid(m) for m in inp), modificationType=MOD[e.head],
                        targetLineIndex='-1,%d' % side_of(gc), editPoints='%s,%s' % gc)
                line(k)
                sub(k, 'line', width='1.0', color='ff000000')
                for m in inp:
                    # as CellDesigner saves it: targetLineIndex -1,0, no linkTarget (mevalonate, user's file)
                    k = sub(lm, 'modification', type=MOD[e.head], modifiers=spec(m), aliases='sa_' + sid(m), targetLineIndex='-1,0')
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
        if left: report.say('left out', 'process %s: edges not converted: %s' % (p, ', '.join(e.id for e in left)))
    # arcs between two entities (no process: reduced notation, e.g. a stimulation of a phenotype)
    for e in E:
        if e.source in ents and e.target in ents and e.head in REDUCED:
            # straight from source to target, no process
            rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(e.id), id='re_' + sid(e.id), reversible='false')
            x = sub(etree.SubElement(rx, 'annotation'), 'extension')
            sub(x, 'reactionType', typed(e, REDUCED[e.head]))
            # both ends at the centre: no linkAnchor (CellDesigner's save of the SREBP and ACLY files)
            sub(sub(x, 'baseReactants'), 'baseReactant', species=spec(e.source), alias='sa_' + sid(e.source))
            sub(sub(x, 'baseProducts'), 'baseProduct', species=spec(e.target), alias='sa_' + sid(e.target))
            line(x)
            sub(x, 'line', width='1.0', color='ff000000')
            ref(etree.SubElement(rx, 'listOfReactants'), 'speciesReference', e.source)
            ref(etree.SubElement(rx, 'listOfProducts'), 'speciesReference', e.target)
        elif e.source in ents and e.target in ents:
            report.say('left out', 'arc %s (%s -> %s, %s): no process, not converted' % (e.id, label[e.source] or e.source, label[e.target] or e.target, e.head))
        elif e.source in ops and e.target in ents and e.head is not None:
            # (a plain line from a gate to an entity is one of the gate's inputs, drawn the other way)
            # a logic gate on arcs between entities (the PD map's coding): one reaction, the inputs
            # as base reactants, the gate at its edit point (absolute), then a gate member for the
            # gate and one per input
            o, inp = e.source, gate_in[e.source]
            kind = ' | '.join(N[o].labels).strip().upper()
            if e.head not in GATE_ARC or kind not in GATE or not inp or len(inp) < sum(1 for a in E if o in (a.source, a.target) and a.head is None):
                report.say('left out', 'arc %s (%s gate -> %s, %s): a logic gate on an arc between entities, not converted%s' % (
                    e.id, kind, label[e.target] or e.target, e.head, ' (a gate into a gate)' if inp else ''))
                continue
            gx, gy = cen(o)
            rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(e.id), id='re_' + sid(e.id), reversible='false')
            x = sub(etree.SubElement(rx, 'annotation'), 'extension')
            sub(x, 'reactionType', 'BOOLEAN_LOGIC_GATE')
            brs = sub(x, 'baseReactants')
            for m in inp:
                sub(brs, 'baseReactant', species=spec(m), alias='sa_' + sid(m))
            sub(sub(x, 'baseProducts'), 'baseProduct', species=spec(e.target), alias='sa_' + sid(e.target))
            sub(x, 'connectScheme', connectPolicy='direct')
            sub(x, 'editPoints', '%s,%s' % (gx, gy))
            sub(x, 'line', width='1.0', color='ff000000')
            gm = sub(x, 'listOfGateMember')
            g = sub(gm, 'GateMember', type=GATE[kind], aliases=','.join('sa_' + sid(m) for m in inp),
                    modificationType=GATE_ARC[e.head], editPoints='%s,%s' % (gx, gy))
            line(g); sub(g, 'line', width='1.0', color='ff000000')
            for m in inp:
                g = sub(gm, 'GateMember', type=GATE_ARC[e.head], aliases='sa_' + sid(m), targetLineIndex='-1,0')
                line(g); sub(g, 'line', width='1.0', color='ff000000')
            lr_ = etree.SubElement(rx, 'listOfReactants')
            for m in inp:
                ref(lr_, 'speciesReference', m)
            ref(etree.SubElement(rx, 'listOfProducts'), 'speciesReference', e.target)
    # written as CellDesigner writes it (no indentation, double-quoted declaration),
    # so a file opened and saved in CellDesigner can be compared line by line
    report.say('summary', '%s: %d species, %d proteins, %d reactions' % (diagram.name, len(ents), len(prot), len(lr)))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(sbml, encoding='UTF-8', pretty_print=True).decode('utf-8')
    return '\n'.join(l.lstrip() for l in xml.split('\n'))


# --- reading a CellDesigner file into the map model (rules: docs/CD-TO-SBGN.md)
SBML = 'http://www.sbml.org/sbml/level2/version4'
KIND = {'PROTEIN': 'Macromolecule', 'GENE': 'NucleicAcidFeature', 'RNA': 'NucleicAcidFeature',
        'ANTISENSE_RNA': 'NucleicAcidFeature', 'SIMPLE_MOLECULE': 'SimpleChemical', 'ION': 'SimpleChemical',
        'DRUG': 'SimpleChemical', 'UNKNOWN': 'UnspecifiedEntity', 'COMPLEX': 'Complex', 'PHENOTYPE': 'Phenotype',
        'DEGRADED': 'EmptySet'}
UNIT = {'GENE': 'ct:gene', 'RNA': 'ct:mRNA', 'ANTISENSE_RNA': 'ct:asRNA'}  # when the file has no ct: unit
PROCESS = {'KNOWN_TRANSITION_OMITTED': 'OmittedProcess', 'UNKNOWN_TRANSITION': 'UncertainProcess'}  # others: Process
PROCESSES = ('Process',) + tuple(PROCESS.values())
HEAD = {v: k for k, v in MOD.items()}
HEAD.update({'UNKNOWN_CATALYSIS': 'catalysis', 'UNKNOWN_INHIBITION': 'inhibition',
             'TRANSCRIPTIONAL_ACTIVATION': 'stimulation', 'TRANSLATIONAL_ACTIVATION': 'stimulation',
             'TRANSCRIPTIONAL_INHIBITION': 'inhibition', 'TRANSLATIONAL_INHIBITION': 'inhibition',
             'POSITIVE_INFLUENCE': 'stimulation', 'NEGATIVE_INFLUENCE': 'inhibition',
             'REDUCED_PHYSICAL_STIMULATION': 'stimulation', 'REDUCED_MODULATION': 'modulation',
             'REDUCED_TRIGGER': 'trigger'})
HEAD.update({'UNKNOWN_' + k: v for k, v in list(HEAD.items()) if k.startswith(('POSITIVE', 'NEGATIVE', 'REDUCED'))})
REDUCED_TYPES = {k for k in HEAD if 'INFLUENCE' in k or 'REDUCED' in k} | set(REDUCED.values())


def border_point(a):
    # inverse of border_angle: the point on the border at residue angle a, as offsets from
    # the centre in node widths and heights (y down)
    q = math.pi / 4
    a = (a + q) % (2 * math.pi) - q  # in [-pi/4, 7pi/4)
    if a < q:
        return 0.5, -0.5 * a / q
    if a < 3 * q:
        return 0.5 * (math.pi / 2 - a) / q, -0.5
    if a < 5 * q:
        return -0.5, -0.5 * (math.pi - a) / q
    return 0.5 * (a - 3 * math.pi / 2) / q, 0.5




def straight(m):
    # the map for straight SBGN-ML (user, 2026-10-18): CellDesigner's bends placed the process
    # square, and the arcs go straight, so each process midway between its main reactant and
    # product: its first consumption and first product (read() writes the main line first), or of
    # a reversible process (products only) its first two products
    ins, outs = {}, {}
    for a in m.arcs:
        if a.head is None and m.nodes[a.target].kind in PROCESSES:
            ins.setdefault(a.target, []).append(a.source)
        elif a.head == 'production':
            outs.setdefault(a.source, []).append(a.target)
    cen = lambda i: (m.nodes[i].box[0] + m.nodes[i].box[2] / 2, m.nodes[i].box[1] + m.nodes[i].box[3] / 2)
    for p, o in outs.items():
        e = ins.get(p, [])[:1] + o
        if len(e) > 1:
            (ax, ay), (bx, by), (x, y, w, h) = cen(e[0]), cen(e[1]), m.nodes[p].box
            m.nodes[p].box = ((ax + bx - w) / 2, (ay + by - h) / 2, w, h)
    return m


def points(s):
    return [tuple(float(v) for v in q.split(',')) for q in (s or '').split()]


def read(path):
    # a CellDesigner file as a map (model.Map), its own geometry kept (node sizes, arcs at its anchor
    # points as yEd ports, modifier arcs ending beside the square; user, 2026-10-16, PD02
    # eicosanoids); what does not convert is printed. The straight layout: layout.at_centres
    r = etree.parse(path).getroot()
    ns = {'cd': CD, 's': SBML, 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'bq': 'http://biomodels.net/biology-qualifiers/'}
    f = lambda x, q: x.find(q, ns)
    xs = lambda x, q: x.iterfind(q, ns)
    ext = f(r, 's:model/s:annotation/cd:extension')
    name = lambda s: ' '.join(plain_name(s or '').split())
    nodes, arcs = {}, []
    # compartments: a box with its name where CellDesigner has it
    comps = {c.get('id'): c for c in xs(r, './/s:listOfCompartments/s:compartment')}
    cname = {i: c.get('name') or i for i, c in comps.items()}
    calias = {a.get('compartment'): a.get('id') for a in xs(ext, 'cd:listOfCompartmentAliases/cd:compartmentAlias')}
    for a in xs(ext, 'cd:listOfCompartmentAliases/cd:compartmentAlias'):
        b = f(a, 'cd:bounds')
        if b is None:  # closeup compartments: a line, no box
            report.say('left out', 'compartment %s: %s, not converted' % (cname.get(a.get('compartment')), f(a, 'cd:class').text)); continue
        box = tuple(float(b.get(k)) for k in ('x', 'y', 'w', 'h'))
        np_ = f(a, 'cd:namePoint')
        nodes[a.get('id')] = Node(id=a.get('id'), kind='Compartment', box=box, labels=[name(cname.get(a.get('compartment')))],
                                  parent=calias.get(comps[a.get('compartment')].get('outside')), fill='#' + f(a, 'cd:paint').get('color')[2:].upper(),
                                  label_at=(float(np_.get('x')) - box[0], float(np_.get('y')) - box[1] - 12.5) if np_ is not None else None)
    # species: one node per alias; included species (complex members) as top-level ones
    species = {s.get('id'): (s, f(s, 's:annotation/cd:extension/cd:speciesIdentity'), f(s, 's:annotation'))
               for s in xs(r, 's:model/s:listOfSpecies/s:species')}
    species.update({s.get('id'): (s, f(s, 'cd:annotation/cd:speciesIdentity'), f(s, 'cd:notes'))
                    for s in xs(ext, 'cd:listOfIncludedSpecies/cd:species')})
    residues = {}
    for p in xs(ext, 'cd:listOfProteins/cd:protein'):
        for m in xs(p, 'cd:listOfModificationResidues/cd:modificationResidue'):
            residues[p.get('id'), m.get('id')] = (float(m.get('angle', 0)), m.get('name'))
    INV = {v: k for k, v in STATE.items()}
    aliases = list(xs(ext, 'cd:listOfComplexSpeciesAliases/cd:complexSpeciesAlias')) + \
        list(xs(ext, 'cd:listOfSpeciesAliases/cd:speciesAlias'))
    for a in aliases:
        s, si, an = species[a.get('species')]
        cls = f(si, 'cd:class').text
        if cls not in KIND:
            report.say('left out', 'species %s: class %s, not converted' % (s.get('name'), cls)); continue
        kind = KIND[cls]
        b = f(a, 'cd:bounds'); box = tuple(float(b.get(k)) for k in ('x', 'y', 'w', 'h'))
        n = int(f(si, 'cd:state/cd:homodimer').text) if f(si, 'cd:state/cd:homodimer') is not None else 1
        if n > 2:  # the box grew 6 per unit beyond 2 (forward rule), top left kept
            box = box[:2] + (box[2] - 6 * (n - 2), box[3] - 6 * (n - 2))
        states = []
        pref = f(si, 'cd:proteinReference')
        for m in xs(si, 'cd:state/cd:listOfModifications/cd:modification'):
            ang, site = residues.get((pref.text if pref is not None else None, m.get('residue')), (0.0, None))
            sym = '' if m.get('state') == 'empty' else INV.get(m.get('state'), m.get('state'))
            states.append((sym + ('@' + site if site else ''),) + border_point(ang))
        for st in xs(si, 'cd:state/cd:listOfStructuralStates/cd:structuralState'):
            sa = f(a, 'cd:structuralState')
            states.append((st.get('structuralState'),) + border_point(float(sa.get('angle')) if sa is not None else math.pi / 2))
        if (f(a, 'cd:activity').text if f(a, 'cd:activity') is not None else '') == 'active':
            states.append(('active', 0.5, -0.5))  # user, Q10
        info = f(a, 'cd:info')
        units = ['%s:%s' % (info.get('prefix'), info.get('label'))] if info is not None and info.get('state') != 'empty' else []
        if cls in UNIT and not any(u.startswith('ct:') for u in units):
            units.append(UNIT[cls])
        if n > 1:  # N:x as on every multimer of our yEd maps (N:2 included, user 2026-10-18)
            units.append('N:%d' % n)
        paint = f(a, 'cd:usualView/cd:paint')
        uris = [li.get('{%s}resource' % ns['rdf']) for li in xs(an, './/rdf:Description/*/rdf:Bag/rdf:li')] if an is not None else []
        fam = an is not None and f(an, './/rdf:Description/bq:hasVersion') is not None
        hyp = f(si, 'cd:hypothetical')
        nodes[a.get('id')] = Node(
            id=a.get('id'), kind=kind, box=box, labels=[name(s.get('name')) if cls != 'DEGRADED' else ''],
            parent=a.get('complexSpeciesAlias') or a.get('compartmentAlias'),
            fill=None if cls == 'DRUG' or paint is None else '#' + paint.get('color')[2:].upper(),
            states=states, units=units, count=n, data=to_properties(fam, uris) if uris else {},
            dashed=hyp is not None and hyp.text == 'true', species=a.get('species'))
    # an unlabelled complex in yEd is named after its members in CellDesigner: the name goes
    def member_names(c):
        return [m.labels[0] or ':'.join(member_names(m.id)) for m in nodes.values() if m.parent == c]
    for d in nodes.values():
        if d.kind == 'Complex' and set(d.labels[0].split(':')) == set(':'.join(member_names(d.id)).split(':')):
            d.labels = ['']
    alias_of = lambda x: x.get('alias') or x.get('aliases')
    cen = lambda i: (nodes[i].box[0] + nodes[i].box[2] / 2, nodes[i].box[1] + nodes[i].box[3] / 2)

    def end(e):  # where the main line meets an alias: its centre, or a quarter point
        b = f(e, 'cd:linkAnchor')
        d = nodes[alias_of(e)]
        if b is None or b.get('position') not in ANCHOR:
            return cen(d.id)
        return anchor_point(d.box, b.get('position'), d.kind in ('SimpleChemical', 'UnspecifiedEntity'))
    # an arc's port: where it meets its node, from the node's centre
    port = lambda i, P: (P[0] - cen(i)[0], P[1] - cen(i)[1])
    for rx in xs(r, 's:model/s:listOfReactions/s:reaction'):
        x = f(rx, 's:annotation/cd:extension')
        typ = f(x, 'cd:reactionType').text
        rid = rx.get('id')
        br, bp = list(xs(x, 'cd:baseReactants/cd:baseReactant')), list(xs(x, 'cd:baseProducts/cd:baseProduct'))
        if any(alias_of(e) not in nodes for e in br + bp):
            report.say('left out', 'reaction %s: an end is not converted, left out' % rid); continue
        if typ in REDUCED_TYPES:  # reduced notation: an arc between the entities (user, Q8)
            arcs.append(Arc(id=rid, source=alias_of(br[0]), target=alias_of(bp[0]), head=HEAD[typ],
                            points=[from_frame(cen(alias_of(br[0])), cen(alias_of(bp[0])), q) for q in points(x.findtext('cd:editPoints', namespaces=ns))],
                            dashed=typ.startswith('UNKNOWN_')))
            continue
        ep = f(x, 'cd:editPoints')
        pts = points(ep.text if ep is not None else '')
        if typ == 'BOOLEAN_LOGIC_GATE':
            # a logic gate on reduced arcs: the inputs (base reactants) into the gate at the edit
            # point (absolute), the gate's arc to the base product (PD map, Histamine signalling)
            g = f(x, 'cd:listOfGateMember/cd:GateMember')
            mt = g.get('modificationType')
            if mt not in HEAD or not pts:
                report.say('left out', 'reaction %s: logic gate with %s, not converted' % (rid, mt)); continue
            (gx, gy), op = pts[-1], rid + '_gate'
            nodes[op] = Node(id=op, kind='Operator', box=(gx - 15, gy - 15, 30, 30), labels=[g.get('type').rsplit('_', 1)[1]])
            for e in br:
                arcs.append(Arc(id='%s_%s' % (op, alias_of(e)), source=alias_of(e), target=op))
            arcs.append(Arc(id=op + '_out', source=op, target=alias_of(bp[0]), head=HEAD[mt], dashed=mt.startswith('UNKNOWN_')))
            continue
        if len(br) + len(bp) == 3:
            # a branched reaction (association: two reactants, dissociation, truncation: two
            # products) as one process at the branch point (user, Q5). The point: last edit
            # point, in the frame of the three species (origin the first, axes to the other two);
            # each branch's own edit points (num0, num1, num2) in the frame point -> its species
            # (cd2sbgnml, AssociationReactionModel)
            three = [alias_of(e) for e in br + bp]
            O, X, Y = (cen(i) for i in three)
            u, v = pts[-1]
            sq = (O[0] + u * (X[0] - O[0]) + v * (Y[0] - O[0]), O[1] + u * (X[1] - O[1]) + v * (Y[1] - O[1]))
            n = [int(ep.get('num%d' % k, 0)) for k in range(3)]
            arm = [pts[sum(n[:k]):sum(n[:k + 1])] for k in range(3)]
            ends = [end(e) for e in br + bp]
            bent = [[from_frame(sq, ends[k], q) for q in arm[k]] for k in range(3)]
            lines = [(three[k], k < len(br), bent[k][::-1] if k < len(br) else bent[k], port(three[k], ends[k])) for k in range(3)]
            Q = ends[2] if len(br) == 2 else ends[0]
            L = math.hypot(Q[0] - sq[0], Q[1] - sq[1]) or 1
            fl = ((Q[0] - sq[0]) / L, (Q[1] - sq[1]) / L) if len(br) == 2 else ((sq[0] - Q[0]) / L, (sq[1] - Q[1]) / L)
        elif len(br) == 1 and len(bp) == 1:
            # the main line: its ends, edit points, the square midway on segment rectangleIndex
            A, B = end(br[0]), end(bp[0])
            line = [A] + [from_frame(A, B, q) for q in pts] + [B]
            cs = f(x, 'cd:connectScheme')
            k = int(cs.get('rectangleIndex', 0)) if cs is not None else 0
            P, Q = line[k], line[k + 1]
            sq = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2)
            L = math.hypot(Q[0] - P[0], Q[1] - P[1]) or 1
            fl = ((Q[0] - P[0]) / L, (Q[1] - P[1]) / L)
            lines = [(alias_of(br[0]), True, line[1:k + 1], port(alias_of(br[0]), A)),
                     (alias_of(bp[0]), False, line[k + 1:-1], port(alias_of(bp[0]), B))]
        else:
            report.say('left out', 'reaction %s (%s): %d base reactants, %d base products, left out' % (rid, typ, len(br), len(bp))); continue
        S = 18.0  # the process size in our yEd maps
        nodes[rid] = Node(id=rid, kind=PROCESS.get(typ, 'Process'), box=(sq[0] - S / 2, sq[1] - S / 2, S, S), labels=[''])
        reversible = rx.get('reversible') != 'false'
        def flow(alias, into, pts=(), at=(0.0, 0.0)):  # a consumption arc into the process, or a production arc out of it
            if into and not reversible:
                arcs.append(Arc(id='%s_%s' % (rid, alias), source=alias, target=rid, points=list(pts), source_at=at))
            else:
                arcs.append(Arc(id='%s_%s' % (rid, alias), source=rid, target=alias, head='production', points=list(pts), target_at=at))
        for alias, into, bends, at in lines:
            flow(alias, into, bends, at)
        for tag, into in (('cd:listOfReactantLinks/cd:reactantLink', True), ('cd:listOfProductLinks/cd:productLink', False)):
            for l in xs(x, tag):
                if alias_of(l) in nodes:
                    if l.get('editPoints') or f(l, 'cd:editPoints') is not None:
                        report.say('left out', 'reaction %s: edit points of an added link left out' % rid)
                    flow(alias_of(l), into)
        # modifiers: the arc ends at the point of the square targetLineIndex names (a side middle or a
        # corner); in yEd at that point of the 18 px process (corners at 9, 9)
        gate_inputs, gates = set(), 0
        for m in xs(x, 'cd:listOfModification/cd:modification'):
            t = m.get('type')
            spot = SQUARE.get(int(m.get('targetLineIndex', '-1,2').split(',')[1]), SQUARE[3])
            T = square_point(sq, fl, *spot)
            if t.startswith('BOOLEAN_LOGIC_GATE'):
                op = '%s_gate%d' % (rid, gates); gates += 1
                gx, gy = points(m.get('editPoints'))[0]
                nodes[op] = Node(id=op, kind='Operator', box=(gx - 15, gy - 15, 30, 30), labels=[t.rsplit('_', 1)[1]])
                if t.endswith('UNKNOWN'):
                    report.say('changed', 'reaction %s: logic gate of unknown type kept as an operator "UNKNOWN"' % rid)
                for a_ in m.get('aliases').split(','):
                    if a_ in nodes:
                        arcs.append(Arc(id='%s_%s' % (op, a_), source=a_, target=op)); gate_inputs.add((a_, m.get('modificationType')))
                arcs.append(Arc(id=op + '_out', source=op, target=rid, head=HEAD.get(m.get('modificationType'), 'stimulation')))
                continue
            a_ = m.get('aliases')
            if (a_, t) in gate_inputs or a_ not in nodes:
                continue  # an input of a gate (listed once more by CellDesigner), or not converted
            if t not in HEAD:
                report.say('left out', 'reaction %s: modifier type %s, not converted' % (rid, t)); continue
            lt = f(m, 'cd:linkTarget')
            M = end(lt) if lt is not None else cen(a_)  # its anchor on the modifier, else the centre
            arcs.append(Arc(id='%s_%s_%s' % (rid, a_, t.lower()), source=a_, target=rid, head=HEAD[t],
                            points=[from_frame(M, T, q) for q in points(m.get('editPoints'))],
                            source_at=port(a_, M), target_at=square_point((0, 0), fl, *spot, S / 2),
                            dashed=t.startswith('UNKNOWN_')))
    for tag in ('cd:listOfLayers/cd:layer', 'cd:listOfGroups/cd:group'):
        k = sum(1 for _ in xs(ext, tag))
        if k: report.say('left out', '%d %s left out' % (k, tag.split(':')[-1] + 's'))
    # an edit point on the straight line between its neighbours is no bend in yEd (the advanced
    # layout's two points beside the square): left out
    for e in arcs:
        e.points = unbent([cen(e.source)] + e.points + [cen(e.target)])[1:-1]
    return Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs)

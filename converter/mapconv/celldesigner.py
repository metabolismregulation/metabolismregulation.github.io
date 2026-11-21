import math, os, re, sys
from dataclasses import replace
from struct import pack, unpack
from lxml import etree
from . import cd_layout, cd_tidy, report
from .cd_layout import ANCHOR, SQUARE, anchor_point, from_frame, square_point, to_frame
from .layout import exit_point, visible
from .annotation import from_notes, from_references, notes, references, to_properties
from .graphml import EQUIV, without_delays
from .model import Map, Node, Arc

CD = 'http://www.sbml.org/2001/ns/celldesigner'
CLASS = {'Macromolecule': 'PROTEIN', 'SimpleChemical': 'SIMPLE_MOLECULE', 'NucleicAcidFeature': 'GENE',
         'UnspecifiedEntity': 'UNKNOWN', 'Complex': 'COMPLEX', 'Phenotype': 'PHENOTYPE',
         'SourceAndSink': 'DEGRADED', 'EmptySet': 'DEGRADED',
         'Submap': 'PHENOTYPE'}
REDUCED = {'stimulation': 'REDUCED_PHYSICAL_STIMULATION',
           'inhibition': 'NEGATIVE_INFLUENCE',
           'modulation': 'REDUCED_MODULATION', 'trigger': 'REDUCED_TRIGGER'}
GATE_ARC = {'stimulation': 'REDUCED_PHYSICAL_STIMULATION', 'inhibition': 'NEGATIVE_INFLUENCE',
            'trigger': 'REDUCED_TRIGGER', 'modulation': 'REDUCED_MODULATION'}
UNKNOWN = {'CATALYSIS': 'UNKNOWN_CATALYSIS', 'INHIBITION': 'UNKNOWN_INHIBITION'}
UNKNOWN.update({t: 'UNKNOWN_' + t for t in ('NEGATIVE_INFLUENCE', 'REDUCED_PHYSICAL_STIMULATION',
                                             'REDUCED_MODULATION', 'REDUCED_TRIGGER')})
REACTION = {'Process': 'STATE_TRANSITION', 'OmittedProcess': 'KNOWN_TRANSITION_OMITTED', 'UncertainProcess': 'UNKNOWN_TRANSITION'}
GATE = {'AND': 'BOOLEAN_LOGIC_GATE_AND', 'OR': 'BOOLEAN_LOGIC_GATE_OR', 'NOT': 'BOOLEAN_LOGIC_GATE_NOT',
        '?': 'BOOLEAN_LOGIC_GATE_UNKNOWN'}
GATE_LABEL = {v: k for k, v in GATE.items()}
MOD = {'catalysis': 'CATALYSIS', 'inhibition': 'INHIBITION', 'modulation': 'MODULATION',
       'stimulation': 'PHYSICAL_STIMULATION', 'trigger': 'TRIGGER'}
STATE = {'P': 'phosphorylated', 'Ac': 'acetylated', 'Ub': 'ubiquitinated', 'Me': 'methylated',
         'OH': 'hydroxylated', 'G': 'glycosylated', 'My': 'myristoylated', 'Pa': 'palmytoylated',
         'Pr': 'prenylated', 'S': 'sulfated',
         'H': 'protonated', '*': "don't care", '?': 'unknown'}
NAME = [(' ', '_space_'), ('-', '_minus_'), ('/', '_slash_'), ('+', '_plus_'),
        ('α', '_alpha_'), ('β', '_beta_'), ('γ', '_gamma_'), ('δ', '_delta_'), ('ε', '_epsilon_'), ('ζ', '_zeta_'),
        ('η', '_eta_'), ('θ', '_theta_'), ('ι', '_iota_'), ('κ', '_kappa_'), ('λ', '_lambda_'), ('μ', '_mu_'),
        ('ν', '_nu_'), ('ξ', '_xi_'), ('π', '_pi_'), ('ρ', '_rho_'), ('σ', '_sigma_'), ('τ', '_tau_'),
        ('φ', '_phi_'), ('χ', '_chi_'), ('ψ', '_psi_'), ('ω', '_omega_')]


def cd_name(s):
    for a, b in NAME:
        s = s.replace(a, b)
    return s


def plain_name(s):
    for a, b in NAME:
        s = s.replace(b, a)
    return s


def units_of_information(d):
    return [u for u in d.units if not re.fullmatch(r'N:\d+', u)]


def cd_info(u):
    return ('ct', u[3:]) if u.startswith('ct:') else ('N', u[2:]) if re.fullmatch(r'N:\d+', u) else ('free input', u)


def cd_class(d):
    if d.kind == 'NucleicAcidFeature' and any(u.startswith('ct:') and u.lower().endswith('rna') for u in units_of_information(d)):
        return 'RNA'
    return CLASS[d.kind]


def is_structural(txt):
    return bool(txt) and '@' not in txt and txt not in STATE


def border_angle(rx, ry):
    q = math.pi / 4
    yy = -ry
    if abs(rx) >= abs(yy):
        a = q * yy / 0.5 if rx > 0 else math.pi - q * yy / 0.5
    else:
        a = math.pi / 2 - q * rx / 0.5 if yy > 0 else 3 * math.pi / 2 + q * rx / 0.5
    return a % (2 * math.pi)


def opened_ors(m):
    ops = {i for i, d in m.nodes.items() if d.kind == 'Operator'}
    opened, arcs = [], m.arcs
    for o in ops:
        if ' | '.join(m.nodes[o].labels).strip().upper() != 'OR':
            continue
        outs = [a for a in m.arcs if a.source == o and a.head is not None]
        ins = [a.target if a.source == o else a.source for a in m.arcs if o in (a.source, a.target) and a.head is None]
        if len(outs) == 1 and any(i in ops for i in ins):
            opened.append(o)
            arcs = [a for a in arcs if o not in (a.source, a.target)] + \
                   [replace(outs[0], id='%s_%s' % (outs[0].id, i), source=i, points=[], source_at=(0.0, 0.0)) for i in ins]
    if not opened:
        return m
    report.say('changed', 'OR gate fed by a gate: no CellDesigner form, its inputs joined to its target (%s)' % ', '.join(sorted(opened)))
    return replace(m, nodes={i: d for i, d in m.nodes.items() if i not in opened}, arcs=arcs)


LAYOUTS = ('straight', 'bends', 'advanced', 'drawn')


def write(diagram, ann, layout='straight'):
    advanced = layout != 'straight'
    diagram = opened_ors(without_delays(diagram, 'CellDesigner'))
    eq = [i for i, d in diagram.nodes.items() if d.kind == 'Operator' and d.labels[:1] == [EQUIV]]
    if eq:
        report.say('changed', 'equivalence operator written as CellDesigner\'s unknown gate ? (%s)' % ', '.join(eq))
        diagram = replace(diagram, nodes={i: replace(d, labels=['?']) if i in eq else d for i, d in diagram.nodes.items()},
                          arcs=[replace(a, head='stimulation', dashed=True) if a.source in eq else a for a in diagram.arcs])
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
    sid = lambda i: re.sub(r'\W+', '_', i)
    members = {}
    for i, d in ents.items():
        if d.parent in ents:
            members.setdefault(d.parent, []).append(i)
    def name_complex(c):
        if not label[c]:
            label[c] = ':'.join(dict.fromkeys(name_complex(m) if m in members else label[m] for m in members[c]))
        return label[c]
    for c in members:
        name_complex(c)
    drawing = cd_layout.draw(diagram, ents, members, label, advanced, layout == 'drawn')
    if layout == 'advanced':
        cd_tidy.tidy(diagram, drawing, ents, members, label)
    box, cen = drawing.box, drawing.cen
    W, H = drawing.size

    sv = {i: [(txt, border_angle(rx, ry)) for txt, rx, ry in d.states] for i, d in ents.items() if d.kind in ('Macromolecule', 'Complex')}
    struct = {}
    for i in sv:
        st = [(txt, ang) for txt, ang in sv[i] if is_structural(txt)]
        if st:
            name = lambda txt: re.sub(r'^\d+:', '', txt)
            cnt = lambda txt: int(re.match(r'^(\d+):', txt).group(1)) if re.match(r'^\d+:', txt) else 0
            struct[i] = ('/'.join(dict.fromkeys(name(txt) for txt, _ in st)), max(st, key=lambda q: cnt(q[0]))[1])
        sv[i] = [(txt, ang) for txt, ang in sv[i] if not is_structural(txt)]
        if ents[i].kind == 'Complex' and sv[i]:
            report.say('left out', 'complex %s: state variables not converted' % i); sv[i] = []
    free = {label[i] for i in struct} - {label[i] for i in sv if any(txt for txt, _ in sv[i])}
    for i in sv:
        if label[i] in free: sv[i] = []
    cls = {i: cd_class(d) for i, d in ents.items()}
    nucl = {'GENE': {}, 'RNA': {}}
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
            site = txt.partition('@')[2]
            hit = next((s for s in sites if s['site'] == site and (site or abs(s['angle'] - ang) < 0.3)), None)
            if hit is None:
                hit = {'id': '%s_r%d' % (pid, len(sites) + 1), 'site': site, 'angle': ang}
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
    for i in sorted(comps, key=lambda i: (depth(i), box[i][1], box[i][0])):
        d = comps[i]; x, y, w, h = box[i]
        a = sub(lco, 'compartmentAlias', id='ca_' + sid(i), compartment='c_' + sid(i))
        sub(a, 'class', 'OVAL' if d.outline == 'ShapeNode ellipse' else 'SQUARE'); sub(a, 'bounds', x=x, y=y, w=w, h=h)
        lx, ly = d.label_at or (6, 0)
        sub(a, 'namePoint', x=x + lx, y=y + ly + 12.5)
        sub(a, 'doubleLine', thickness='12.0', outerWidth='2.0', innerWidth='1.0')
        fc = (d.fill or '#FFFFFF').lstrip('#'); al = int(fc[6:8], 16) / 255 if len(fc) == 8 else 1
        seen = [round(255 - al * (255 - int(fc[k:k + 2], 16))) for k in (0, 2, 4)]
        rgb = (d.line[1:].lower() if d.line and band(d.line) == '#%02X%02X%02X' % tuple(seen) else
               ''.join('%02x' % max(0, round(255 - (255 - c) / BAND)) for c in seen))
        sub(a, 'paint', color='ff' + rgb, scheme='Color'); sub(a, 'info', state='empty', angle='-1.5707963267948966')
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
        if cx: a.set('complexSpeciesAlias', 'sa_' + sid(cx))
        elif comp_of(i): a.set('compartmentAlias', 'ca_' + sid(comp_of(i)))
        sub(a, 'activity', 'inactive'); sub(a, 'bounds', x=x, y=y, w=w, h=h)
        sub(a, 'font', size='%g' % (d.font or 12)); sub(a, 'view', state='usual')
        if d.kind == 'Complex':
            sub(a, 'backupSize', w='0.0', h='0.0'); sub(a, 'backupView', state='none')
        if i in struct:
            sub(a, 'structuralState', angle=struct[i][1])
        for v in ('usualView', 'briefView'):
            u = sub(a, v)
            cm = comp_of(i) if not cx else None
            ip = (x - box[cx][0], y - box[cx][1]) if cx and v == 'usualView' else \
                 (x - box[cm][0], y - box[cm][1]) if cm and v == 'usualView' else (0.0, 0.0)
            sub(u, 'innerPosition', x=ip[0], y=ip[1]); sub(u, 'boxSize', width=w, height=h)
            sub(u, 'singleLine', width=unpack("f", pack("f", w))[0] if d.kind == 'Complex' and v == 'briefView' else '1.0')
            sub(u, 'paint', color='ff' + (d.fill or '#FFFFFF').lstrip('#').lower(), scheme='Color')
        us = sorted(units_of_information(d), key=lambda u: not u.startswith('ct:'))
        if mult[i] > 2:
            us.insert(sum(u.startswith('ct:') for u in us), 'N:%d' % mult[i])
        if us:
            prefix, lab = cd_info(us[0])
            sub(a, 'info', state='open', prefix=prefix, label=lab, angle='-1.5707963267948966')
            if us[1:]: report.say('left out', '%s: units of information %s left out (CellDesigner keeps one)' % (label[i], ', '.join(us[1:])))
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
        sub(sub(etree.SubElement(cp, 'annotation'), 'extension'), 'name', nm)

    RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    BQ = 'http://biomodels.net/biology-qualifiers/'
    BQM = 'http://biomodels.net/model-qualifiers/'
    def description(parent, about, abc=False):
        ns = {'rdf': RDF, 'dc': 'http://purl.org/dc/elements/1.1/', 'dcterms': 'http://purl.org/dc/terms/',
              'vCard': 'http://www.w3.org/2001/vcard-rdf/3.0#', 'bqbiol': BQ, 'bqmodel': BQM}
        if abc: ns = dict(sorted(ns.items()))
        rdf = etree.SubElement(parent, '{%s}RDF' % RDF, nsmap=ns)
        return etree.SubElement(rdf, '{%s}Description' % RDF, {'{%s}about' % RDF: '#' + about})
    def bag(d, qualifier, uris):
        b = etree.SubElement(etree.SubElement(d, qualifier), '{%s}Bag' % RDF)
        for u in uris:
            etree.SubElement(b, '{%s}li' % RDF, {'{%s}resource' % RDF: u})
    def miriam(parent, about, lab, abc=False):
        if lab not in ann: return
        fam, uris = ann[lab]
        bag(description(parent, about, abc), '{%s}%s' % (BQ, 'hasVersion' if fam else 'is'), uris)
    def described(parent, about, d):
        uris = references(d.data.get('References'))
        if uris:
            desc = description(parent, about)
            for u in uris:
                bag(desc, '{%s}isDescribedBy' % BQM, [u])

    catalysed = {}
    for e in E:
        if e.target in procs and e.source in ents and e.head in MOD:
            catalysed.setdefault(e.source, []).append('re_' + sid(e.target))
    ops = {i for i, d in N.items() if d.kind == 'Operator'}
    gate_in = {o: [e.source if e.target == o else e.target for e in E if o in (e.source, e.target) and e.head is None
                   and (e.source if e.target == o else e.target) in ents] for o in ops}
    for o in ops:
        gate_in[o].sort(key=lambda m: (N[m].box[0], N[m].box[1]))
    for e in E:
        if e.source in ops and e.target in procs and e.head in MOD:
            for m in gate_in[e.source]:
                catalysed.setdefault(m, []).append('re_' + sid(e.target))
    def identity(x, i):
        d = ents[i]
        si = sub(x, 'speciesIdentity'); sub(si, 'class', cls[i])
        if d.dashed: sub(si, 'hypothetical', 'true')
        if d.kind == 'Macromolecule':
            sub(si, 'proteinReference', prot[label[i]])
        elif cls[i] in nucl:
            sub(si, 'geneReference' if cls[i] == 'GENE' else 'rnaReference', nucl[cls[i]][label[i]])
        n = mult[i]
        if n > 1 or sv.get(i) or i in struct:
            st = sub(si, 'state')
            if n > 1: sub(st, 'homodimer', '2')
            if sv.get(i):
                lm = sub(st, 'listOfModifications')
                for txt, rid in sv[i]:
                    m = txt.split('@')[0]
                    sub(lm, 'modification', residue=rid, state=STATE[m] if m else 'empty')
            if i in struct:
                sub(sub(st, 'listOfStructuralStates'), 'structuralState', structuralState=struct[i][0])
        if d.kind != 'Macromolecule' and cls[i] not in nucl:
            sub(si, 'name', name_of(i))

    name_of = lambda i: spec(i) if cls[i] == 'DEGRADED' else cd_name(label[i])
    XH = 'http://www.w3.org/1999/xhtml'
    lsp = etree.SubElement(model, 'listOfSpecies')
    for i, d in ents.items():
        if rep[i] != i:
            continue
        if d.parent in ents:
            s = sub(inc, 'species', id=spec(i), name=cd_name(label[i]))
            h = etree.SubElement(sub(s, 'notes'), '{%s}html' % XH, nsmap={None: XH})
            etree.SubElement(etree.SubElement(h, '{%s}head' % XH), '{%s}title' % XH)
            body = etree.SubElement(h, '{%s}body' % XH)
            body.text = ''.join(l + '\n' for l in notes(d.data)) or None
            miriam(body, spec(i), label[i], abc=True)
            x = sub(s, 'annotation'); sub(x, 'complexSpecies', spec(d.parent))
            identity(x, i)
            continue
        s = etree.SubElement(lsp, 'species', metaid=spec(i), id=spec(i), name=name_of(i),
                             compartment='c_' + sid(comp_of(i)) if comp_of(i) else 'default', initialAmount='0')
        if notes(d.data):
            h = etree.SubElement(etree.SubElement(s, 'notes'), '{%s}html' % XH, nsmap={None: XH})
            etree.SubElement(etree.SubElement(h, '{%s}head' % XH), '{%s}title' % XH)
            etree.SubElement(h, '{%s}body' % XH).text = '\n'.join(notes(d.data))
        an = etree.SubElement(s, 'annotation'); x = sub(an, 'extension')
        sub(x, 'positionToCompartment', 'inside')
        identity(x, i)
        cat = list(dict.fromkeys(r for j in ents if rep[j] == i for r in catalysed.get(j, ())))
        if cat:
            lc = sub(x, 'listOfCatalyzedReactions')
            for r in cat: sub(lc, 'catalyzed', reaction=r)
        miriam(an, spec(i), label[i])

    def typed(e, t):
        if not e.dashed: return t
        if t not in UNKNOWN: report.say('changed', 'arc %s: dashed %s written solid (CellDesigner has no unknown form)' % (e.id, t))
        return UNKNOWN.get(t, t)
    lr = etree.SubElement(model, 'listOfReactions')
    n_ref = [0]
    def ref(parent, tag, i):
        n_ref[0] += 1
        r = etree.SubElement(parent, tag, metaid='SR%d' % n_ref[0], species=spec(i))
        sub(sub(etree.SubElement(r, 'annotation'), 'extension'), 'alias', 'sa_' + sid(i))
    def line(k, n=1, **a):
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
        if not reversible: rx.set('reversible', 'false')
        an = etree.SubElement(rx, 'annotation')
        x = sub(an, 'extension')
        described(an, 're_' + sid(p), N[p])
        sub(x, 'reactionType', REACTION.get(N[p].kind, 'STATE_TRANSITION'))
        br = sub(sub(x, 'baseReactants'), 'baseReactant', species=spec(r_), alias='sa_' + sid(r_)); ra and sub(br, 'linkAnchor', position=ra)
        bp = sub(sub(x, 'baseProducts'), 'baseProduct', species=spec(q_), alias='sa_' + sid(q_)); qa and sub(bp, 'linkAnchor', position=qa)
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
                k = sub(lm, 'modification', type=typed(e, MOD[e.head]), modifiers=spec(m), aliases='sa_' + sid(m),
                        targetLineIndex='-1,%d' % i)
                if pts:
                    k.set('editPoints', ' '.join('%s,%s' % to_frame(M, T, q) for q in pts))
                line(k, len(pts) + 1)
                if at:
                    sub(sub(k, 'linkTarget', species=spec(m), alias='sa_' + sid(m)), 'linkAnchor', position=at)
                sub(k, 'line', width='1.0', color='ff000000')
            for e in gates:
                o = e.source; inp = gate_in[o]
                gc = cen(o)
                k = sub(lm, 'modification', type=GATE[' | '.join(N[o].labels).strip().upper()], modifiers=','.join(spec(m) for m in inp),
                        aliases=','.join('sa_' + sid(m) for m in inp), modificationType=MOD[e.head],
                        targetLineIndex='-1,%d' % side_of(gc), editPoints='%s,%s' % gc)
                line(k)
                sub(k, 'line', width='1.0', color='ff000000')
                for m in inp:
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
    for e in E:
        if e.source in ents and e.target in ents and e.head in REDUCED:
            rx = etree.SubElement(lr, 'reaction', metaid='re_' + sid(e.id), id='re_' + sid(e.id), reversible='false')
            x = sub(etree.SubElement(rx, 'annotation'), 'extension')
            sub(x, 'reactionType', typed(e, REDUCED[e.head]))
            sub(sub(x, 'baseReactants'), 'baseReactant', species=spec(e.source), alias='sa_' + sid(e.source))
            sub(sub(x, 'baseProducts'), 'baseProduct', species=spec(e.target), alias='sa_' + sid(e.target))
            line(x)
            sub(x, 'line', width='1.0', color='ff000000')
            ref(etree.SubElement(rx, 'listOfReactants'), 'speciesReference', e.source)
            ref(etree.SubElement(rx, 'listOfProducts'), 'speciesReference', e.target)
        elif e.source in ents and e.target in ents:
            report.say('left out', 'arc %s (%s -> %s, %s): no process, not converted' % (e.id, label[e.source] or e.source, label[e.target] or e.target, e.head))
        elif e.source in ops and e.target in ents and e.head is not None:
            o, inp = e.source, gate_in[e.source]
            kind = ' | '.join(N[o].labels).strip().upper()
            nested = len(inp) < sum(1 for a in E if o in (a.source, a.target) and a.head is None)
            if e.head not in GATE_ARC or kind not in GATE or not inp or nested:
                report.say('left out', 'arc %s (%s gate -> %s, %s): a logic gate on an arc between entities, not converted%s' % (
                    e.id, kind, label[e.target] or e.target, e.head, ' (a gate into a gate)' if nested else ''))
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
                    modificationType=typed(e, GATE_ARC[e.head]), editPoints='%s,%s' % (gx, gy))
            line(g); sub(g, 'line', width='1.0', color='ff000000')
            for m in inp:
                g = sub(gm, 'GateMember', type=UNKNOWN[GATE_ARC[e.head]] if e.dashed else GATE_ARC[e.head], aliases='sa_' + sid(m), targetLineIndex='-1,0')
                line(g); sub(g, 'line', width='1.0', color='ff000000')
            lr_ = etree.SubElement(rx, 'listOfReactants')
            for m in inp:
                ref(lr_, 'speciesReference', m)
            ref(etree.SubElement(rx, 'listOfProducts'), 'speciesReference', e.target)
    report.say('summary', '%s: %d species, %d proteins, %d reactions' % (diagram.name, len(ents), len(prot), len(lr)))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(sbml, encoding='UTF-8', pretty_print=True).decode('utf-8')
    return '\n'.join(l.lstrip() for l in xml.split('\n'))


SBML = 'http://www.sbml.org/sbml/level2/version4'
KIND = {'PROTEIN': 'Macromolecule', 'GENE': 'NucleicAcidFeature', 'RNA': 'NucleicAcidFeature',
        'ANTISENSE_RNA': 'NucleicAcidFeature', 'SIMPLE_MOLECULE': 'SimpleChemical', 'ION': 'SimpleChemical',
        'DRUG': 'SimpleChemical', 'UNKNOWN': 'UnspecifiedEntity', 'COMPLEX': 'Complex', 'PHENOTYPE': 'Phenotype',
        'DEGRADED': 'EmptySet'}
UNIT = {'GENE': 'ct:gene', 'RNA': 'ct:mRNA', 'ANTISENSE_RNA': 'ct:asRNA'}
PROCESS = {'KNOWN_TRANSITION_OMITTED': 'OmittedProcess', 'UNKNOWN_TRANSITION': 'UncertainProcess'}
PROCESSES = ('Process',) + tuple(PROCESS.values())
HEAD = {v: k for k, v in MOD.items()}
HEAD.update({'UNKNOWN_CATALYSIS': 'catalysis', 'UNKNOWN_INHIBITION': 'inhibition',
             'TRANSCRIPTIONAL_ACTIVATION': 'stimulation', 'TRANSLATIONAL_ACTIVATION': 'stimulation',
             'TRANSCRIPTIONAL_INHIBITION': 'inhibition', 'TRANSLATIONAL_INHIBITION': 'inhibition',
             'POSITIVE_INFLUENCE': 'stimulation', 'NEGATIVE_INFLUENCE': 'inhibition',
             'REDUCED_PHYSICAL_STIMULATION': 'stimulation', 'REDUCED_MODULATION': 'modulation',
             'REDUCED_TRIGGER': 'trigger'})
HEAD.update({'UNKNOWN_' + k: v for k, v in list(HEAD.items()) if k.startswith(('POSITIVE', 'NEGATIVE', 'REDUCED'))})
REDUCED_TYPES = {k for k in HEAD if 'INFLUENCE' in k or 'REDUCED' in k} | {'PHYSICAL_STIMULATION'}


BAND = 63 / 255


def band(c):
    return c and '#' + ''.join('%02X' % round(255 - BAND * (255 - int(c[k:k + 2], 16))) for k in (1, 3, 5))


def paint(c):
    return None if len(c) < 8 or c[:2] == '00' else '#' + c[2:].upper()


def border_point(a):
    q = math.pi / 4
    a = (a + q) % (2 * math.pi) - q
    if a < q:
        return 0.5, -0.5 * a / q
    if a < 3 * q:
        return 0.5 * (math.pi / 2 - a) / q, -0.5
    if a < 5 * q:
        return -0.5, -0.5 * (math.pi - a) / q
    return 0.5 * (a - 3 * math.pi / 2) / q, 0.5




def straight(m):
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
    r = etree.parse(path).getroot()
    ns = {'cd': CD, 's': SBML, 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'bq': 'http://biomodels.net/biology-qualifiers/',
          'bqm': 'http://biomodels.net/model-qualifiers/', 'xh': 'http://www.w3.org/1999/xhtml'}
    f = lambda x, q: x.find(q, ns)
    xs = lambda x, q: x.iterfind(q, ns)
    ext = f(r, 's:model/s:annotation/cd:extension')
    name = lambda s: ' '.join(plain_name(s or '').split())
    nodes, arcs = {}, []
    comps = {c.get('id'): c for c in xs(r, './/s:listOfCompartments/s:compartment')}
    cname = {i: c.get('name') or i for i, c in comps.items()}
    calias = {a.get('compartment'): a.get('id') for a in xs(ext, 'cd:listOfCompartmentAliases/cd:compartmentAlias')}
    for a in xs(ext, 'cd:listOfCompartmentAliases/cd:compartmentAlias'):
        b = f(a, 'cd:bounds')
        if b is None:
            report.say('left out', 'compartment %s: %s, not converted' % (cname.get(a.get('compartment')), f(a, 'cd:class').text)); continue
        box = tuple(float(b.get(k)) for k in ('x', 'y', 'w', 'h'))
        np_, c = f(a, 'cd:namePoint'), paint(f(a, 'cd:paint').get('color'))
        nodes[a.get('id')] = Node(id=a.get('id'), kind='Compartment', box=box, labels=[name(cname.get(a.get('compartment')))],
                                  parent=calias.get(comps[a.get('compartment')].get('outside')), fill=band(c), line=c,
                                  label_at=(float(np_.get('x')) - box[0], float(np_.get('y')) - box[1] - 12.5) if np_ is not None else None)
    species = {s.get('id'): (s, f(s, 's:annotation/cd:extension/cd:speciesIdentity'), f(s, 's:annotation'))
               for s in xs(r, 's:model/s:listOfSpecies/s:species')}
    species.update({s.get('id'): (s, f(s, 'cd:annotation/cd:speciesIdentity'), f(s, 'cd:notes'))
                    for s in xs(ext, 'cd:listOfIncludedSpecies/cd:species')})
    def note(s):
        return ''.join(t for q in ('s:notes/xh:html/xh:body', 'cd:notes/xh:html/xh:body') for b in xs(s, q) for t in b.xpath('text()'))
    residues = {}
    for p in xs(ext, 'cd:listOfProteins/cd:protein'):
        for m in xs(p, 'cd:listOfModificationResidues/cd:modificationResidue'):
            residues[p.get('id'), m.get('id')] = (float(m.get('angle', 0)), m.get('name'))
    INV = {v: k for k, v in STATE.items()}
    other = {}
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
        if n > 2:
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
            states.append(('active', 0.5, -0.5))
        info = f(a, 'cd:info')
        units = [info.get('label') if info.get('prefix') == 'free input' else '%s:%s' % (info.get('prefix'), info.get('label'))] \
            if info is not None and info.get('state') != 'empty' else []
        if cls in UNIT and not any(u.startswith('ct:') for u in units):
            units.append(UNIT[cls])
        cnt = [int(u[2:]) for u in units if re.fullmatch(r'N:\d+', u)]
        if n == 2 and cnt:
            n = cnt[0]
        elif n > 1:
            units.append('N:%d' % n)
        pv = f(a, 'cd:usualView/cd:paint')
        uris = [li.get('{%s}resource' % ns['rdf']) for li in xs(an, './/rdf:Description/*/rdf:Bag/rdf:li')] if an is not None else []
        for u in uris:
            db = u.rpartition(':')[0][len('urn:miriam:'):]
            if db not in ('hgnc', 'hgnc.symbol', 'uniprot', 'obo.chebi'): other.setdefault(db, set()).add(a.get('species'))
        fam = an is not None and f(an, './/rdf:Description/bq:hasVersion') is not None
        hyp = f(si, 'cd:hypothetical')
        font = f(a, 'cd:font')
        nodes[a.get('id')] = Node(
            id=a.get('id'), kind=kind, box=box, labels=[name(s.get('name')) if cls != 'DEGRADED' else ''],
            parent=a.get('complexSpeciesAlias') or a.get('compartmentAlias'),
            fill=None if cls == 'DRUG' or pv is None else paint(pv.get('color')), border=cls != 'UNKNOWN',
            states=states, units=units, count=n, data=from_notes(note(s), to_properties(fam, uris) if uris else {}),
            dashed=hyp is not None and hyp.text == 'true', species=a.get('species'),
            font=float(font.get('size')) if font is not None and font.get('size') else None)
    def member_names(c):
        return [m.labels[0] or ':'.join(member_names(m.id)) for m in nodes.values() if m.parent == c]
    for d in nodes.values():
        if d.kind == 'Complex' and set(d.labels[0].split(':')) == set(':'.join(member_names(d.id)).split(':')):
            d.labels = ['']
    alias_of = lambda x: x.get('alias') or x.get('aliases')
    cen = lambda i: (nodes[i].box[0] + nodes[i].box[2] / 2, nodes[i].box[1] + nodes[i].box[3] / 2)

    def end(e):
        b = f(e, 'cd:linkAnchor')
        d = nodes[alias_of(e)]
        if b is None or b.get('position') not in ANCHOR:
            return cen(d.id)
        circle = d.kind in ('SimpleChemical', 'UnspecifiedEntity')
        x_, y_, w_, h_ = d.box
        k = 6 if d.count > 1 and not circle else 0
        return anchor_point((x_, y_, w_ - k, h_ - k), b.get('position'), circle, d.kind == 'Phenotype')
    port = lambda i, P: (P[0] - cen(i)[0], P[1] - cen(i)[1])

    def rim(e, P, Q):
        b = f(e, 'cd:linkAnchor')
        if b is not None and b.get('position') in ANCHOR:
            return P
        d = nodes[alias_of(e)]
        if d.kind not in ('SimpleChemical', 'UnspecifiedEntity'):
            return exit_point(d.box, P, Q)
        dx, dy = Q[0] - P[0], Q[1] - P[1]
        t = min(1.0, 1 / (math.hypot(dx / (d.box[2] / 2), dy / (d.box[3] / 2)) or 1))
        return (P[0] + t * dx, P[1] + t * dy)
    refs = lambda rx: from_references([li.get('{%s}resource' % ns['rdf']) for q in ('bq', 'bqm')
                                       for li in xs(rx, 's:annotation/rdf:RDF/rdf:Description/%s:isDescribedBy/rdf:Bag/rdf:li' % q)])
    unplaced = []
    for rx in xs(r, 's:model/s:listOfReactions/s:reaction'):
        x = f(rx, 's:annotation/cd:extension')
        typ = f(x, 'cd:reactionType').text
        rid = rx.get('id')
        if typ in REDUCED_TYPES or typ == 'BOOLEAN_LOGIC_GATE':
            refs(rx) and unplaced.append(rid)
        br, bp = list(xs(x, 'cd:baseReactants/cd:baseReactant')), list(xs(x, 'cd:baseProducts/cd:baseProduct'))
        if any(alias_of(e) not in nodes for e in br + bp):
            report.say('left out', 'reaction %s: an end is not converted, left out' % rid); continue
        if typ in REDUCED_TYPES:
            A, B, s_, t_ = end(br[0]), end(bp[0]), alias_of(br[0]), alias_of(bp[0])
            arcs.append(Arc(id=rid, source=s_, target=t_, head=HEAD[typ],
                            points=[from_frame(A, B, q) for q in points(x.findtext('cd:editPoints', namespaces=ns))],
                            source_at=port(s_, A), target_at=port(t_, B), dashed=typ.startswith('UNKNOWN_')))
            continue
        ep = f(x, 'cd:editPoints')
        pts = points(ep.text if ep is not None else '')
        if typ == 'BOOLEAN_LOGIC_GATE':
            g = f(x, 'cd:listOfGateMember/cd:GateMember')
            mt = g.get('modificationType')
            if mt not in HEAD or not pts:
                report.say('left out', 'reaction %s: logic gate with %s, not converted' % (rid, mt)); continue
            (gx, gy), op = pts[-1], rid + '_gate'
            nodes[op] = Node(id=op, kind='Operator', box=(gx - 15, gy - 15, 30, 30), labels=[GATE_LABEL[g.get('type')]])
            for e in br:
                arcs.append(Arc(id='%s_%s' % (op, alias_of(e)), source=alias_of(e), target=op))
            arcs.append(Arc(id=op + '_out', source=op, target=alias_of(bp[0]), head=HEAD[mt], dashed=mt.startswith('UNKNOWN_')))
            continue
        if len(br) + len(bp) == 3:
            three = [alias_of(e) for e in br + bp]
            O, X, Y = (cen(i) for i in three)
            u, v = pts[-1]
            sq = (O[0] + u * (X[0] - O[0]) + v * (Y[0] - O[0]), O[1] + u * (X[1] - O[1]) + v * (Y[1] - O[1]))
            n = [int(ep.get('num%d' % k, 0)) for k in range(3)]
            arm = [pts[sum(n[:k]):sum(n[:k + 1])] for k in range(3)]
            ends = [end(e) for e in br + bp]
            bent = [[from_frame(sq, ends[k], q) for q in arm[k]] for k in range(3)]
            lines = [(three[k], k < len(br), bent[k][::-1] if k < len(br) else bent[k], port(three[k], ends[k])) for k in range(3)]
            joins = None
            Q = ends[2] if len(br) == 2 else ends[0]
            L = math.hypot(Q[0] - sq[0], Q[1] - sq[1]) or 1
            fl = ((Q[0] - sq[0]) / L, (Q[1] - sq[1]) / L) if len(br) == 2 else ((sq[0] - Q[0]) / L, (sq[1] - Q[1]) / L)
        elif len(br) == 1 and len(bp) == 1:
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
            P = rim(br[0], P, Q) if k == 0 else P
            Q = rim(bp[0], Q, P) if k == len(line) - 2 else Q
            joins = [(P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])) for t in (0.375, 0.625)]
        else:
            report.say('left out', 'reaction %s (%s): %d base reactants, %d base products, left out' % (rid, typ, len(br), len(bp))); continue
        S = 18.0
        nodes[rid] = Node(id=rid, kind=PROCESS.get(typ, 'Process'), box=(sq[0] - S / 2, sq[1] - S / 2, S, S), labels=[''],
                          data={'References': refs(rx)} if refs(rx) else {})
        reversible = rx.get('reversible') != 'false'
        def flow(alias, into, pts=(), at=(0.0, 0.0)):
            if into and not reversible:
                arcs.append(Arc(id='%s_%s' % (rid, alias), source=alias, target=rid, points=list(pts), source_at=at))
            else:
                arcs.append(Arc(id='%s_%s' % (rid, alias), source=rid, target=alias, head='production', points=list(pts), target_at=at))
        for alias, into, bends, at in lines:
            flow(alias, into, bends, at)
        for tag, into in (('cd:listOfReactantLinks/cd:reactantLink', True), ('cd:listOfProductLinks/cd:productLink', False)):
            for l in xs(x, tag):
                if alias_of(l) in nodes:
                    q, O = points(l.get('editPoints') or l.findtext('cd:editPoints', '', ns)), end(l)
                    if q and joins is None:
                        report.say('left out', 'reaction %s: edit points of an added link left out (a branched reaction)' % rid); q = []
                    J = joins[0 if into else 1] if joins else None
                    flow(alias_of(l), into, [from_frame(O, J, p) if into else from_frame(J, O, p) for p in q], port(alias_of(l), O))
        gate_inputs, gates = {}, 0
        for m in xs(x, 'cd:listOfModification/cd:modification'):
            t = m.get('type')
            spot = SQUARE.get(int(m.get('targetLineIndex', '-1,2').split(',')[1]), SQUARE[3])
            T = square_point(sq, fl, *spot)
            if t.startswith('BOOLEAN_LOGIC_GATE'):
                op = '%s_gate%d' % (rid, gates); gates += 1
                *bends, (gx, gy) = points(m.get('editPoints'))
                nodes[op] = Node(id=op, kind='Operator', box=(gx - 15, gy - 15, 30, 30), labels=[GATE_LABEL[t]])
                for a_ in m.get('aliases').split(','):
                    if a_ in nodes:
                        arcs.append(Arc(id='%s_%s' % (op, a_), source=a_, target=op)); gate_inputs[(a_, m.get('modificationType'))] = arcs[-1]
                arcs.append(Arc(id=op + '_out', source=op, target=rid, head=HEAD.get(m.get('modificationType'), 'stimulation'),
                                points=[from_frame((gx, gy), T, q) for q in bends]))
                continue
            a_ = m.get('aliases')
            lt = f(m, 'cd:linkTarget')
            if (a_, t) in gate_inputs:
                g = gate_inputs[(a_, t)]
                M = end(lt) if lt is not None else cen(a_)
                g.source_at, g.points = port(a_, M), [from_frame(M, cen(g.target), q) for q in points(m.get('editPoints'))]
                continue
            if a_ not in nodes:
                continue
            if t not in HEAD:
                report.say('left out', 'reaction %s: modifier type %s, not converted' % (rid, t)); continue
            M = end(lt) if lt is not None else cen(a_)
            arcs.append(Arc(id='%s_%s_%s' % (rid, a_, t.lower()), source=a_, target=rid, head=HEAD[t],
                            points=[from_frame(M, T, q) for q in points(m.get('editPoints'))],
                            source_at=port(a_, M), target_at=square_point((0, 0), fl, *spot, S / 2),
                            dashed=t.startswith('UNKNOWN_')))
    if unplaced:
        report.say('left out', 'references of %d reactions drawn as arcs (no process glyph to hold them): %s' % (len(unplaced), ', '.join(unplaced)))
    for tag in ('cd:listOfLayers/cd:layer', 'cd:listOfGroups/cd:group'):
        k = sum(1 for x in xs(ext, tag) if x.tag.endswith('group') or any(len(c) for c in x))
        if k: report.say('left out', '%d %s left out' % (k, tag.split(':')[-1] + 's'))
    if other:
        report.say('left out', 'identifiers other than HGNC, UniProt and ChEBI: %s' % ', '.join(
            '%s on %d species' % (db, len(sp)) for db, sp in sorted(other.items(), key=lambda x: (-len(x[1]), x[0]))))
    return visible(Map(name=os.path.basename(path).rsplit('.', 1)[0], nodes=nodes, arcs=arcs))

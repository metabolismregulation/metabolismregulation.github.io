// Port of sbgnml.py. Write a map (model.js) as SBGN-ML 0.3, the SBGN exchange format (Bergmann
// et al. 2020, doi:10.1515/jib-2020-0016; schema: libsbgn resources/SBGN.xsd). Colours as the SBML
// render extension on the map (the spec's Appendix B), annotation as RDF in each glyph's extension
// with identifiers.org links in Newt's form (db:id).
// read() at the end goes the other way, also for Newt's .nwt (SBGN-ML with its settings).
import { Dict, WS, dist, div, first, float, get, has, hypot, int, max, min, repr, reprList, sorted, split, strip, sum } from './py.js';
import { Element, SubElement, localname, parse, tostring } from './xml.js';
import * as report from './report.js';
import { from_graphml, to_properties } from './annotation.js';
import { bends, centre, compartment_of, decorations, unbent } from './layout.js';
import { for_newt, placed } from './newt_layout.js';
import { CHAR, DELAY, EQUIV, LINE, baseName, without_delays } from './graphml.js';
import { Arc, Diagram, Node, deepcopy } from './model.js';

const NS = 'http://sbgn.org/libsbgn/0.3';
const RENDER = 'http://www.sbml.org/sbml/level3/version1/render/version1';
const RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
const BQBIOL = 'http://biomodels.net/biology-qualifiers/';
const S = '{' + NS + '}', R = '{' + RENDER + '}', RD = '{' + RDF + '}';
const CLASS = { Macromolecule: 'macromolecule', SimpleChemical: 'simple chemical', NucleicAcidFeature: 'nucleic acid feature',
  UnspecifiedEntity: 'unspecified entity', Complex: 'complex',
  Phenotype: 'phenotype', SourceAndSink: 'source and sink', EmptySet: 'source and sink',
  Submap: 'submap', Compartment: 'compartment', Process: 'process', OmittedProcess: 'omitted process',
  UncertainProcess: 'uncertain process' };
const MULTIMER = ['Macromolecule', 'SimpleChemical', 'NucleicAcidFeature', 'Complex'];
const PROCESSES = ['Process', 'OmittedProcess', 'UncertainProcess'];
const OPERATORS = { and: 'AND', or: 'OR', not: 'NOT', equivalence: EQUIV, delay: DELAY };  // SBGN class -> yEd label (delay: Activity Flow)
const OPERATOR_CLASS = Object.fromEntries(Object.entries(OPERATORS).map(([k, v]) => [v, k]));
const ARC = { production: 'production', catalysis: 'catalysis', inhibition: 'inhibition', modulation: 'modulation',
  stimulation: 'stimulation', trigger: 'necessary stimulation' };
// urn:miriam:<db> -> Newt's identifiers.org prefix (annotations-handler.js, dbList)
const DB = { 'obo.chebi': 'CHEBI', hgnc: 'hgnc', 'hgnc.symbol': 'hgnc.symbol', uniprot: 'uniprot' };

const pmin = (a, b) => b < a ? b : a;
const pmax = (a, b) => b > a ? b : a;
const same = (p, q) => p[0] === q[0] && p[1] === q[1];

function xml_id(i) {
  // yEd's nested ids (n0::n1) are not XML ids
  return (/^[A-Za-z_]/.test(i) ? i : '_' + i).replace(/[^\p{L}\p{N}_.-]/gu, '_');
}

function border(d, p) {
  // where the line from the node's centre to p leaves its box
  const [cx, cy] = centre(d), [w, h] = d.box.slice(2);
  const [dx, dy] = [p[0] - cx, p[1] - cy];
  if (!dx && !dy) return [cx, cy];
  const t = pmin(dx ? w / 2 / Math.abs(dx) : Infinity, dy ? h / 2 / Math.abs(dy) : Infinity);
  return [cx + t * dx, cy + t * dy];
}

function leave(d, p, q, gap = 3) {
  // where the line from p (inside the node's box or on it) to q leaves the box, gap px beyond
  // (Newt loses an arc whose bend lies on the node's border)
  const [x, y, w, h] = d.box;
  const [dx, dy] = [q[0] - p[0], q[1] - p[1]];
  const ts = [dx > 0 ? (x + w - p[0]) / dx : dx < 0 ? (x - p[0]) / dx : null,
    dy > 0 ? (y + h - p[1]) / dy : dy < 0 ? (y - p[1]) / dy : null].filter(t => t !== null);
  const t = ts.length ? pmax(0.0, min(ts)) + gap / hypot(dx, dy) : 0.0;
  return [p[0] + t * dx, p[1] + t * dy];
}

function cuts(p, q, box, inset = 1) {
  // whether the segment p-q runs through the box's inside (Liang-Barsky)
  const [x, y, w, h] = box;
  let t0 = 0.0, t1 = 1.0;
  for (const [d, lo, hi, a] of [[q[0] - p[0], x + inset, x + w - inset, p[0]], [q[1] - p[1], y + inset, y + h - inset, p[1]]]) {
    if (!d) {
      if (!(lo < a && a < hi)) return false;
      continue;
    }
    const [r, s] = [(lo - a) / d, (hi - a) / d];
    const [u, v] = s < r ? [s, r] : [r, s];
    [t0, t1] = [pmax(t0, u), pmin(t1, v)];
  }
  return t0 < t1;
}

function bbox(parent, x, y, w, h) {
  SubElement(parent, S + 'bbox', { x: repr(x), y: repr(y), w: repr(w), h: repr(h) });
}

function shifted(diagram, margin = 20) {
  // the map moved so that it starts at the margin: SBGN-ML's origin is its top left corner,
  // yEd's anywhere
  const d = deepcopy(diagram);
  const dx = margin - min([...d.nodes.values()].map(n => n.box[0]));
  const dy = margin - min([...d.nodes.values()].map(n => n.box[1]));
  for (const n of d.nodes.values()) n.box = [n.box[0] + dx, n.box[1] + dy, ...n.box.slice(2)];
  for (const a of d.arcs) a.points = a.points.map(([x, y]) => [x + dx, y + dy]);
  return d;
}

export function write(diagram, layout = 'advanced') {
  // layout 'straight' (user, 2026-10-18): every arc straight from centre to centre (no bends, no
  // yEd ports, no process ports), the necessary minimum, improved by hand in Newt; 'advanced':
  // the drawing of the source kept (bends, arcs at yEd ports), the arcs of logic gates straight
  // (yEd's bend where the inputs meet lies past the gate's port: the line turns back, iNOS)
  diagram = for_newt(placed(without_delays(shifted(diagram), 'SBGN Process Description')), layout !== 'straight');
  const N = diagram.nodes;
  const ids = new Map([...N.keys()].map(i => [i, xml_id(i)]));
  const ann = from_graphml(diagram);
  const ops = new Set([...N].filter(([, d]) => d.kind === 'Operator').map(([i]) => i));
  const hubs = new Set([...N].filter(([, d]) => PROCESSES.includes(d.kind)).map(([i]) => i).concat([...ops]));
  const eq = new Set([...ops].filter(i => N.at(i).labels.length && N.at(i).labels[0] === EQUIV));  // its output, a plain line to the generic entity, keeps its direction

  // arcs in SBGN's direction: a consumption runs from the entity to the process (yEd maps
  // also draw it the other way), a logic arc from the entity into its gate
  // straight: an arc that shares its two ends with another keeps the source's bends, as Newt
  // curves two straight arcs between the same glyphs apart (iNOS: IFNGR consumed by the process
  // it stimulates; user, 2026-10-18)
  const pair = (s, t) => sorted([s, t]).join('\u0000');
  const pairs = new Map();
  for (const a of diagram.arcs) pairs.set(pair(a.source, a.target), (pairs.get(pair(a.source, a.target)) || 0) + 1);
  const arcs = [];
  for (const a of diagram.arcs) {
    let [s, t, pts, s_at, t_at] = [a.source, a.target, [...a.points], a.source_at, a.target_at];
    let cls;
    if (layout === 'straight' && pairs.get(pair(s, t)) === 1 || ops.has(s) || ops.has(t)) pts = [];
    if (layout === 'straight' || ops.has(s) || ops.has(t)) [s_at, t_at] = [[0.0, 0.0], [0.0, 0.0]];
    if (a.head === null) {
      if (hubs.has(s) && !eq.has(s) && !hubs.has(t)) [s, t, pts, s_at, t_at] = [t, s, [...pts].reverse(), t_at, s_at];
      cls = ops.has(t) || eq.has(s) ? 'logic arc' : 'consumption';
    } else {
      cls = get(ARC, a.head);
      if (cls === null) { report.say('left out', `arc ${a.id}: no SBGN arc for ${a.head}, left out`); continue; }
    }
    if (N.at(s).kind === 'Phenotype') {  // a perturbing agent, a submap or neither: not guessed (user, 2026-10-17)
      report.say('left out', `arc ${a.id}: leaves phenotype ${s} (${N.at(s).labels.length ? N.at(s).labels[0] : ''}), no SBGN Process Description equivalent, left out`); continue;
    }
    if (a.tail) report.say('left out', `arc ${a.id}: its arrow at the source has no place in SBGN-ML, dropped`);
    arcs.push([a, cls, s, t, pts, s_at, t_at]);
  }

  // a process or gate has two ports, on the line from its inputs to its outputs (the spec,
  // 2.10): port 1 where the consumptions (gate inputs) come in, port 2 where the products leave.
  // An arc comes in from its last bend (glycogen: IRS1 from the left, through a bend below)
  let ports = new Map();
  for (const p of hubs) {
    const ins = arcs.filter(([, c, , t]) => t === p && (c === 'consumption' || c === 'logic arc'))
      .map(([, , s, , pts]) => pts.length ? pts[pts.length - 1] : centre(N.at(s)));
    const outs = arcs.filter(([, c, s]) => s === p && (c === 'production' || ops.has(p)))
      .map(([, , , t, pts]) => pts.length ? pts[0] : centre(N.at(t)));
    const [cx, cy] = centre(N.at(p)), w = N.at(p).box[2], h = N.at(p).box[3];
    const mean = (q, d) => q.length ? [sum(q.map(([x]) => x)) / q.length, sum(q.map(([, y]) => y)) / q.length] : d;
    let a = mean(ins, [cx, cy]), b = mean(outs, [cx, cy]);
    if (same(a, b)) {  // reversible (products on both sides): the line through the first two
      const q = outs.length > 1 ? outs.slice(0, 2) : [[cx - 1, cy], [cx + 1, cy]];
      [a, b] = [q[0], q[1]];
    }
    const [vx, vy] = [b[0] - a[0], b[1] - a[1]];
    const horizontal = Math.abs(vx) >= Math.abs(vy);
    const k = (horizontal ? vx : vy) >= 0 ? 1 : -1;
    const one = horizontal ? [cx - k * w, cy] : [cx, cy - k * h];
    const two = horizontal ? [cx + k * w, cy] : [cx, cy + k * h];
    ports.set(p, [horizontal ? 'horizontal' : 'vertical', one, two]);
  }
  if (layout === 'straight') ports = new Map();  // no ports: every arc runs from centre to centre (user, 2026-10-18)

  const root = Element(S + 'sbgn', {}, [[null, NS]]);
  // language, not version: libsbgn's schema lists no PD version after 1.3
  const m = SubElement(root, S + 'map', { id: xml_id(diagram.name.replace(/-/g, '_')), language: 'process description' });

  // colours: one render style per fill
  const fills = new Map();
  for (const [i, d] of N) {
    if (d.fill) {
      const f = d.fill.toLowerCase();
      if (!fills.has(f)) fills.set(f, []);
      fills.get(f).push(ids.get(i));
    }
  }
  if (fills.size) {
    const ri = SubElement(SubElement(m, S + 'extension'), R + 'renderInformation', { id: 'renderInformation' }, [[null, RENDER]]);
    const cd = SubElement(ri, R + 'listOfColorDefinitions');
    SubElement(cd, R + 'colorDefinition', { id: 'black', value: '#000000' });
    const st = SubElement(ri, R + 'listOfStyles');
    [...fills].forEach(([f, members], k) => {
      SubElement(cd, R + 'colorDefinition', { id: 'color_' + k, value: f });
      const s = SubElement(st, R + 'style', { id: 'style_' + k, idList: members.join(' ') });
      SubElement(s, R + 'g', { stroke: 'black', fill: 'color_' + k });
      s.find(R + 'g').set('stroke-width', '1');
    });
  }

  const annotate = (g, i, d) => {
    const lab = d.labels.length ? split(d.labels[0]).join(' ') : '';
    if (!ann.has(lab) || !has(CLASS, d.kind) || PROCESSES.includes(d.kind)) return;
    const [family, urns] = ann.get(lab);
    const uris = [];
    for (const u of urns) {
      const rest = u.slice('urn:miriam:'.length), c = rest.lastIndexOf(':');
      const db = c < 0 ? '' : rest.slice(0, c), x = rest.slice(c + 1);
      if (has(DB, db)) uris.push(`http://identifiers.org/${DB[db]}:${x.replace(/%3A/g, ':').replace(/CHEBI:/g, '')}`);
    }
    if (!uris.length) return;
    const e = SubElement(g, S + 'extension');
    const r = SubElement(SubElement(e, S + 'annotation', {}, [[null, NS]]), RD + 'RDF', {}, [['rdf', RDF], ['bqbiol', BQBIOL]]);
    const desc = SubElement(r, RD + 'Description', { [RD + 'about']: '#' + ids.get(i) });
    const bag = SubElement(SubElement(desc, '{' + BQBIOL + '}' + (family ? 'hasVersion' : 'is')), RD + 'Bag');
    for (const u of uris) SubElement(bag, RD + 'li', { [RD + 'resource']: u });
  };

  const kids = new Map();
  for (const [i, d] of N) {
    const p = N.has(d.parent) ? d.parent : null;
    if (!kids.has(p)) kids.set(p, []);
    kids.get(p).push(i);
  }

  const glyph = (parent, i) => {
    const d = N.at(i);
    const [x, y, w, h] = d.box;
    let cls;
    if (d.kind === 'Operator') {
      cls = get(OPERATOR_CLASS, strip(d.labels.length ? d.labels[0] : '').toUpperCase());
      if (cls === null) { report.say('left out', `gate ${i}: label ${reprList(d.labels.slice(0, 1))} is not AND, OR, NOT or ${EQUIV}, left out`); return; }
    } else if (has(CLASS, d.kind)) {
      cls = CLASS[d.kind] + (d.count > 1 && MULTIMER.includes(d.kind) ? ' multimer' : '');
    } else {
      report.say('left out', `node ${i}: no SBGN glyph for ${d.kind}, left out`); return;
    }
    const g = SubElement(parent, S + 'glyph', { class: cls, id: ids.get(i) });
    const q = compartment_of(N, i);
    if (q && d.kind !== 'Compartment' && (d.parent === null || N.at(d.parent).kind !== 'Complex')) g.set('compartmentRef', ids.get(q));
    if (ports.has(i)) g.set('orientation', ports.get(i)[0]);
    annotate(g, i, d);
    const name = PROCESSES.includes(d.kind) || !d.labels.length ? '' : d.labels[0];  // a second label is a unit (N:2)
    if (d.kind !== 'Operator' && name) {
      const lab = SubElement(g, S + 'label', { text: name });
      if (d.kind === 'Compartment' && d.label_at) {
        const lines = name.split('\n');
        bbox(lab, x + d.label_at[0], y + d.label_at[1], max(lines.map(t => [...t].length)) * CHAR, lines.length * LINE);
      }
    } else if (d.kind === 'Operator' && cls !== 'equivalence') {  // the equivalence glyph has no label (the spec, 2.9.4)
      SubElement(g, S + 'label', { text: cls.toUpperCase() });
    }
    bbox(g, x, y, w, h);
    const [states, units] = decorations(d);
    d.states.slice(0, states.length).forEach(([txt], k) => {
      const at = txt.indexOf('@');
      const value = at < 0 ? txt : txt.slice(0, at), v = at < 0 ? '' : txt.slice(at + 1);
      const sv = SubElement(g, S + 'glyph', { class: 'state variable', id: `${ids.get(i)}_sv${k}` });
      const st = SubElement(sv, S + 'state', { value });
      if (v) st.set('variable', v);
      bbox(sv, ...states[k]);
    });
    units.forEach(([u, box], k) => {
      const ui = SubElement(g, S + 'glyph', { class: 'unit of information', id: `${ids.get(i)}_ui${k}` });
      SubElement(ui, S + 'label', { text: u });
      bbox(ui, ...box);
    });
    for (const j of d.kind === 'Complex' ? kids.get(i) || [] : []) glyph(g, j);
    if (ports.has(i)) {
      ports.get(i).slice(1).forEach(([px, py], k) => SubElement(g, S + 'port', { id: `${ids.get(i)}.${k + 1}`, x: repr(px), y: repr(py) }));
    }
  };

  // compartments first (drawn under the rest), then every node outside a complex
  const order = sorted([...N].filter(([, d]) => d.parent === null || N.at(d.parent).kind !== 'Complex').map(([i]) => i),
    i => N.at(i).kind !== 'Compartment');
  for (const i of order) glyph(m, i);

  const made = new Set([...m.iter(S + 'glyph')].map(g => g.get('id')));
  const crossed = (line, s, t) => {
    // the nodes a line runs through, besides its own ends and what holds them
    const ends = new Set([s, t]);
    for (let i of [s, t]) {
      while (N.at(i).parent !== null) { i = N.at(i).parent; ends.add(i); }
    }
    const segs = line.slice(1).map((q, k) => [line[k], q]);
    return new Set([...N].filter(([i, d]) => d.kind !== 'Compartment' && !ends.has(i) &&
      (d.parent === null || N.at(d.parent).kind === 'Compartment') && segs.some(([p, q]) => cuts(p, q, d.box))).map(([i]) => i));
  };
  const consumed = new Set(arcs.filter(([, c]) => c === 'consumption').map(([, , , y]) => y));
  for (const [a, cls, s, t, pts0, s_at, t_at] of arcs) {
    let pts = pts0;
    if (!made.has(ids.get(s)) || !made.has(ids.get(t))) continue;
    // the ends: a process's or gate's port on its flux side, else where the arc meets the
    // node's border (a yEd port: its own point)
    // a product leaves by port 2; of a reversible process (no consumption), by the nearer port
    let k = 2;
    if (ports.has(s) && !ops.has(s) && !consumed.has(s)) {
      const sq = q => { const c = centre(N.at(t)), dx = q[0] - c[0], dy = q[1] - c[1]; return dx * dx + dy * dy; };
      k = sq(ports.get(s)[1]) < sq(ports.get(s)[2]) ? 1 : 2;
    }
    const src = ports.has(s) ? `${ids.get(s)}.${k}` : ids.get(s);
    const tgt = ports.has(t) && (cls === 'consumption' || cls === 'logic arc') ? ids.get(t) + '.1' : ids.get(t);
    let p0 = ports.has(s) ? ports.get(s)[k] : null;
    let p1 = tgt.endsWith('.1') && ports.has(t) ? ports.get(t)[1] : null;
    const nxt = pts.length ? pts[0] : p1 ?? centre(N.at(t));
    const prv = pts.length ? pts[pts.length - 1] : p0 ?? centre(N.at(s));
    // Newt draws only the bends and aims the ends at the node's centre: an end at a yEd port
    // gets a bend where the arc leaves the node, so the line keeps yEd's course (eNOS: arcs
    // level with the process, at a complex's side)
    const any = v => v[0] !== 0 || v[1] !== 0;
    if (p0 === null) {
      p0 = any(s_at) ? [centre(N.at(s))[0] + s_at[0], centre(N.at(s))[1] + s_at[1]] : border(N.at(s), nxt);
      const q = leave(N.at(s), p0, nxt);
      if (any(s_at) && !hubs.has(s) && dist(q, border(N.at(s), nxt)) > 5) pts = [q, ...pts];
    }
    if (p1 === null) {
      p1 = any(t_at) ? [centre(N.at(t))[0] + t_at[0], centre(N.at(t))[1] + t_at[1]] : border(N.at(t), prv);
      const q = leave(N.at(t), p1, prv);
      if (any(t_at) && !hubs.has(t) && dist(q, border(N.at(t), prv)) > 5) pts = [...pts, q];
    }
    // key bends only (user, 2026-10-18): a bend stays if leaving it out moves the line by more
    // than 20 px (layout.bends, as for CellDesigner), or the line without it runs through a node
    // it does not run through now
    const line = [p0, ...pts, p1];
    let key = [p0, ...bends(line), p1];
    const now = crossed(line, s, t);
    if ([...crossed(key, s, t)].some(i => !now.has(i))) key = line;
    pts = key.slice(1, -1);
    // a bend on or near (5 px) the straight line between its neighbours, or on the one before,
    // is left out: SBGN-ML places the process itself (the bends that placed it in CellDesigner, and
    // the 3 px stubs at its anchor points, are not needed), and Newt loses an arc with two bends in
    // one place (iNOS, IRF1 mRNA; user, 2026-10-18). On the line as drawn and from where Newt aims
    // the ends (a port, else the node's centre)
    pts = unbent([p0, ...pts, p1], 5).slice(1, -1);
    pts = unbent([ports.has(s) ? p0 : centre(N.at(s)), ...pts, ports.has(t) ? p1 : centre(N.at(t))], 5).slice(1, -1);
    const e = SubElement(m, S + 'arc', { class: cls, id: xml_id(a.id), source: src, target: tgt });
    SubElement(e, S + 'start', { x: repr(p0[0]), y: repr(p0[1]) });
    for (const q of pts) SubElement(e, S + 'next', { x: repr(q[0]), y: repr(q[1]) });
    SubElement(e, S + 'end', { x: repr(p1[0]), y: repr(p1[1]) });
  }
  return tostring(root, true);
}


// --- reading SBGN-ML (and Newt's .nwt) into the map model (the converter's docs, SBGN-ML, "The way back")
const KIND = {};
for (const [k, v] of Object.entries(CLASS)) if (k !== 'SourceAndSink') KIND[v] = k;  // source and sink: yEd's EmptySet
Object.assign(KIND, { association: 'Process', dissociation: 'Process' });  // read as the generic process (MINERVA, Newt)
KIND['perturbing agent'] = 'Phenotype';  // as in CellDesigner; written back as a perturbing agent when an arc leaves it
const HEAD = { consumption: null, 'logic arc': null, production: 'production', catalysis: 'catalysis',
  inhibition: 'inhibition', modulation: 'modulation', stimulation: 'stimulation',
  'necessary stimulation': 'trigger' };
// Activity Flow (L1V1.2, read only; user, 2026-10-17): an activity is drawn as the entity it comes
// from, CellDesigner's way. Its unit of information's shape gives the glyph (none: a protein;
// perturbation: phenotype, as in CellDesigner), its label (the molecule's name) stays a unit; the
// influences are arcs between entities; a delay is an Operator labelled tau; a submap is a phenotype
// with its name, its terminals and the tags left out; an equivalence arc is a plain line (to a terminal:
// to the submap). In Newt's hybrid maps (PD and AF) an activity joined to its entity by a performance
// arc is that entity, as in CellDesigner's reduced notation, and "activity" at the end of an activity's
// label goes (user, 2026-10-19)
const ACTIVITY = { macromolecule: 'Macromolecule', 'nucleic acid feature': 'NucleicAcidFeature', 'simple chemical': 'SimpleChemical',
  'unspecified entity': 'UnspecifiedEntity', complex: 'Complex', perturbation: 'Phenotype' };
Object.assign(HEAD, { 'positive influence': 'stimulation', 'negative influence': 'inhibition', 'unknown influence': 'modulation' });
const URN = Object.fromEntries(Object.entries(DB).map(([k, v]) => [v, k]));
const W = '[\\p{L}\\p{N}_.]+';
const IDENTIFIERS = new RegExp('^https?://identifiers\\.org/(?:(' + W + ')/|(' + W + '):)?([^\\n]+)\\n?$', 'iu');
const ACTIVITY_END = new RegExp('[' + WS + ']activity[' + WS + ']*$', 'iu');
const ACTIVITY_CUT = new RegExp('[' + WS + ']+activity[' + WS + ']*$', 'iu');
const NX = /^N:\p{Nd}+$/u;

function urn(uri) {
  // an identifiers.org link (db:id, or the older db/id) or a MIRIAM URN as a MIRIAM URN
  if (uri.startsWith('urn:miriam:')) return uri;
  const m = uri.match(IDENTIFIERS);
  if (!m) return null;
  const db = m[1] || m[2] || null, x = m[3];
  if (db === null || db.toUpperCase() === 'CHEBI')
    return (db || x).toUpperCase().startsWith('CHEBI') ? 'urn:miriam:obo.chebi:CHEBI%3A' + x.split(':').pop() : null;
  return `urn:miriam:${get(URN, db, db.toLowerCase())}:${x}`;
}

function colour(c, defs) {
  // a render colour (an id or #RRGGBB[AA]) as yEd writes it: #RRGGBB, #RRGGBBAA when not opaque
  let v = defs.has(c) ? defs.get(c) : c;
  if (!v || !v.startsWith('#')) return null;
  v = v.toUpperCase();
  return v.length === 9 && v.endsWith('FF') ? v.slice(0, 7) : v;
}

export function read(path, content) {
  // the map in an SBGN-ML (or Newt) text; path gives its name
  const root = parse(content);
  for (const e of root.iter()) {  // libsbgn 0.1 and 0.2 files: the same elements in an older namespace
    if (e.tag.startsWith('{http://sbgn.org/libsbgn/')) e.tag = S + localname(e.tag);
  }
  const m = root.find(S + 'map');
  if (m === null) throw new TypeError("'NoneType' object has no attribute 'get'");
  const af = m.get('language') === 'activity flow';
  const defs = new Map([...m.iter(R + 'colorDefinition')].map(c => [c.get('id'), c.get('value')]));
  const fill = new Map(), font = new Map();
  for (const st of m.iter(R + 'style')) {
    const g = st.find(R + 'g');
    if (g === null) continue;
    for (const i of split(st.get('idList') || '')) fill.set(i, g.get('fill'));
  }
  for (const st of m.iter(R + 'style')) {
    const g = st.find(R + 'g');
    if (g === null || !g.get('font-size')) continue;
    for (const i of split(st.get('idList') || '')) font.set(i, float(g.get('font-size')));
  }
  const port = new Map();
  const nodes = new Dict(), skipped = new Map(), activities = new Set(), renamed = [];
  const skip = (what, id) => { if (!skipped.has(what)) skipped.set(what, []); skipped.get(what).push(id); };

  const text = g => {
    const lab = g.find(S + 'label');
    return lab !== null ? lab.get('text', '') : '';
  };

  const glyph = (g, parent) => {
    const [cls, i] = [g.get('class'), g.get('id')];
    const [x, y, w, h] = ['x', 'y', 'w', 'h'].map(k => float(g.find(S + 'bbox').get(k)));
    const base = cls.endsWith(' multimer') ? cls.slice(0, -' multimer'.length) : cls;
    let kind = has(OPERATORS, cls) ? 'Operator' : get(KIND, base);
    if (cls === 'biological activity') {
      const c0 = g.findall(S + 'glyph').find(c => c.get('class') === 'unit of information');
      const u = c0 ? c0.find(S + 'entity') : null;
      kind = get(ACTIVITY, (u !== null ? u.get('name') : '').replace(/ multimer/g, ''), 'Macromolecule');
      activities.add(i);
      if (ACTIVITY_END.test(text(g))) {  // the node is the molecule: "SHC activity" is SHC (user, 2026-10-19)
        g.find(S + 'label').set('text', text(g).replace(ACTIVITY_CUT, ''));
        renamed.push(g.get('id'));
      }
    }
    if (af && cls === 'submap') {  // a phenotype with the submap's name, no terminals or tags (user, 2026-10-17)
      kind = 'Phenotype';
      for (const c of g.findall(S + 'glyph')) if (c.get('class') === 'terminal') port.set(c.get('id'), i);
    }
    if (kind === null) { skip(cls, i); return; }  // tag, annotation and the other glyphs our maps do not draw
    for (const p of g.findall(S + 'port')) port.set(p.get('id'), i);
    const states = [], units = [];
    for (const c of g.findall(S + 'glyph')) {
      const cb = c.find(S + 'bbox');
      if (c.get('class') === 'state variable') {
        const st = c.find(S + 'state');
        const [v, vr] = st !== null ? [st.get('value') || '', st.get('variable') || ''] : ['', ''];
        const [cx, cy] = [float(cb.get('x')) + float(cb.get('w')) / 2, float(cb.get('y')) + float(cb.get('h')) / 2];
        states.push([v + (vr ? '@' + vr : ''), div(cx - x - w / 2, w), div(cy - y - h / 2, h)]);
      } else if (c.get('class') === 'unit of information' && (text(c) || cls !== 'biological activity')) {
        units.push(text(c));
      }
    }
    const n = units.filter(u => NX.test(u)).map(u => int(u.slice(2)));
    const lab = g.find(S + 'label');
    const lb = lab !== null ? lab.find(S + 'bbox') : null;
    const data = new Dict();
    for (const d of g.iter(RD + 'Description')) {
      for (const q of d.elements()) {
        const urns = [...q.iter(RD + 'li')].map(li => urn(li.get(RD + 'resource') || '')).filter(u => u);
        if (urns.length && ['is', 'hasVersion'].includes(localname(q.tag))) {
          for (const [k, v] of to_properties(localname(q.tag) === 'hasVersion', urns)) data.set(k, v);
        }
      }
      break;  // the glyph's own description
    }
    nodes.set(i, new Node({ id: i, kind, box: [x, y, w, h], parent,
      labels: kind === 'Operator' ? [OPERATORS[cls]] : [text(g)],
      fill: colour(fill.has(i) ? fill.get(i) : null, defs), states, units,
      count: cls.endsWith(' multimer') ? (n.length ? n[0] : 2) : 1,
      label_at: kind === 'Compartment' && lb !== null ? [float(lb.get('x')) - x, float(lb.get('y')) - y] : null,
      data, font: font.has(i) ? font.get(i) : null }));
    if (g.find(S + 'clone') !== null) skip('clone marker', i);
    for (const c of g.findall(S + 'glyph')) {
      if (!['state variable', 'unit of information'].includes(c.get('class'))) glyph(c, i);  // a complex's members
    }
  };

  for (const g of m.findall(S + 'glyph')) glyph(g, g.get('compartmentRef'));
  const arcs = [], performers = new Map();
  const head = af ? { ...HEAD, 'equivalence arc': null } : HEAD;  // AF: a plain line (user, 2026-10-17)
  for (const a of m.findall(S + 'arc')) {
    const cls = a.get('class');
    const [s, t] = ['source', 'target'].map(k => port.has(a.get(k)) ? port.get(a.get(k)) : a.get(k));
    if (cls === 'performance arc' && activities.has(t) && nodes.has(s) && !activities.has(s)) {
      if (!performers.has(t)) performers.set(t, []);
      performers.get(t).push([s, a.get('id')]);
      continue;
    }
    if (!has(head, cls) || !nodes.has(s) || !nodes.has(t)) {
      skip(!has(head, cls) ? cls + ' arc' : 'arc to a glyph left out', a.get('id'));
      continue;
    }
    arcs.push(new Arc({ id: a.get('id'), source: s, target: t, head: head[cls],
      points: a.findall(S + 'next').map(p => [float(p.get('x')), float(p.get('y'))]) }));
  }
  for (const [t, ps] of performers) {
    if (ps.length > 1) {  // which entity it stands for is not guessed
      for (const [, i] of ps) skip('performance arc', i);
      continue;
    }
    const s = ps[0][0];
    for (const a of arcs) {  // the activity's arcs start or end at its entity, straight
      if (a.source === t || a.target === t) {
        [a.source, a.target, a.points] = [a.source === t ? s : a.source, a.target === t ? s : a.target, []];
      }
    }
    report.say('changed', `activity of ${split(first(nodes.at(t).labels)).join(' ') || t}: drawn as ${split(first(nodes.at(s).labels)).join(' ') || s}, its entity (performance arc)`);
    nodes.delete(t);
  }
  const kept = renamed.filter(i => nodes.has(i)).map(i => split(first(nodes.at(i).labels)).join(' '));
  if (kept.length) report.say('changed', `"activity" cut from the label of: ${kept.join(', ')}`);
  for (const [what, ids] of skipped)
    report.say('left out', `${what}: ${ids.length} left out (${ids.slice(0, 5).join(', ') + (ids.length > 5 ? ' ...' : '')})`);
  return new Diagram({ name: baseName(path), nodes, arcs });
}

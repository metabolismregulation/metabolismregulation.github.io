// Port of rules.py. What a yEd map must keep to convert: the SBGN Process Description rules, with
// one exception (user, 2026-10-16): stimulation, inhibition, modulation and trigger may join two
// entities (from a logic gate stimulation and inhibition), CellDesigner's reduced notation in place
// of an Activity Flow map. yEd draws anything, so a map can look right and be wrong inside: a shape
// laid on a protein in place of a state variable, a node drawn inside a complex without being part
// of it, an arrow from another palette. Each problem is an element id and a reason; the element is
// left out of the conversion and marked red in a copy of the GraphML (mark).
// Python walks some of these sets in no fixed order; here they are walked in the order of the map,
// which only matters when two problems of one kind compete.
import { Dict, first, min, split } from './py.js';
import { Element, parse, tostring } from './xml.js';
import { NS, DELAY, EQUIV } from './graphml.js';
import { Diagram, replace } from './model.js';

// the glyphs CellDesigner has a species class for (the keys of celldesigner.py's CLASS)
export const ENTITIES = ['Macromolecule', 'SimpleChemical', 'NucleicAcidFeature', 'UnspecifiedEntity', 'Complex', 'Phenotype',
  'SourceAndSink', 'EmptySet', 'Submap'];
const PROCESSES = ['Process', 'OmittedProcess', 'UncertainProcess'];
const MODIFIERS = ['catalysis', 'inhibition', 'modulation', 'stimulation', 'trigger'];
const REDUCED = ['stimulation', 'inhibition', 'modulation', 'trigger'];  // allowed between two entities, also from a logic gate
const RED = '#FF0000';

export function problems(m) {
  const N = m.nodes, out = [];
  const ids = kind => new Set([...N].filter(([, d]) => kind(d)).map(([i]) => i));
  const ents = ids(d => ENTITIES.includes(d.kind));
  const procs = ids(d => PROCESSES.includes(d.kind));
  const ops = ids(d => d.kind === 'Operator');
  const groups = new Set([...N].filter(([i, d]) => d.kind === 'Compartment' ||
    (d.kind === 'Complex' && [...N.values()].some(e => e.parent === i))).map(([i]) => i));

  const up = i => {  // the groups around i, nearest first
    const out = [];
    let q = N.at(i).parent;
    while (N.has(q)) { out.push(q); q = N.at(q).parent; }
    return out;
  };
  const inside = (a, b, t = 1.0) => b[0] - t <= a[0] && a[0] + a[2] <= b[0] + b[2] + t &&
    b[1] - t <= a[1] && a[1] + a[3] <= b[1] + b[3] + t;
  const name = d => d.labels.length && d.labels[0] ? d.labels[0] : d.kind;

  for (const [i, d] of N) {
    if (d.kind === 'StateVariable' || d.kind === 'UnitOfInformation') {
      out.push([i, `a ${d.kind} drawn as a node of its own: make it a label of its entity`]); continue;
    }
    if (![ents, procs, ops, groups].some(s => s.has(i)) && d.kind !== 'Compartment') {
      out.push([i, `not an SBGN glyph (${d.kind})`]); continue;
    }
    if (d.kind === 'SimpleChemical' && d.states.some(([t]) => t.split('@')[0]))
      out.push([i, 'a simple chemical carries no state variable']);
    const p = N.has(d.parent) ? N.at(d.parent) : null;
    if (p !== null && !p.outline && !inside(d.box, p.box))  // an oval's members come from the drawing
      out.push([i, `part of ${name(p)} but drawn outside it`]);
    if (procs.has(i) || ops.has(i)) continue;
    // the innermost group whose box holds this node on the drawing must be one it belongs to
    const around = [...groups].filter(g => g !== i && !up(g).includes(i) && !N.at(g).outline && inside(d.box, N.at(g).box, 0));
    if (around.length) {
      const g = min(around, g => N.at(g).box[2] * N.at(g).box[3]);
      if (!up(i).includes(g) && (N.at(g).kind === 'Complex' || d.kind !== 'Compartment'))
        out.push([i, `inside ${name(N.at(g))} on the drawing but not part of it`]);
    }
  }
  // a smaller node laid on an entity it does not belong to, its centre on the entity's border
  // or inside it: a shape in place of a state variable (two nodes touching are layout)
  const flagged = new Set(out.map(([i]) => i));
  for (const a of [...N.keys()].filter(i => !groups.has(i) && !flagged.has(i))) {
    const [x, y, w, h] = N.at(a).box;
    for (const b of [...ents].filter(i => !groups.has(i))) {
      const [bx, by, bw, bh] = N.at(b).box;
      if (a !== b && !up(a).includes(b) && w * h < bw * bh &&
          bx - 2 <= x + w / 2 && x + w / 2 <= bx + bw + 2 && by - 2 <= y + h / 2 && y + h / 2 <= by + bh + 2) {
        out.push([a, `laid on ${first(N.at(b).labels) || N.at(b).kind} without being part of it`]); break;
      }
    }
  }

  const bad = new Set(out.map(([i]) => i));
  const epn = ents;
  for (const e of m.arcs) {
    const [s, t, h] = [e.source, e.target, e.head];
    if (bad.has(s) || bad.has(t)) continue;
    let why = null;
    if (N.at(s).kind === 'Compartment' || N.at(t).kind === 'Compartment') {
      why = 'an arc ends on a compartment (CellDesigner joins species only)';
    } else if (h !== null && !['production', ...MODIFIERS].includes(h)) {
      why = `an arrow outside the SBGN palette (${h.slice(6)})`;
    } else if (h === null) {  // consumption, or a logic arc into an operator: drawn either way
      const pair = [s, t];
      if (epn.has(s) && epn.has(t)) {  // an Activity Flow equivalence arc (to a submap) read into yEd
        why = 'a plain line between two entities (an equivalence arc) has no CellDesigner or SBGN PD form';
      } else if (!(pair.some(x => procs.has(x)) && pair.some(x => epn.has(x))) &&
                 !(pair.some(x => ops.has(x)) && pair.some(x => epn.has(x) || ops.has(x)))) {
        why = 'a plain line must join an entity and a process (or a logic gate)';
      }
    } else if (h === 'production') {
      if (epn.has(s) && procs.has(t)) why = 'a production arrow points away from its process';
      else if (!(procs.has(s) && epn.has(t))) why = 'a production arrow must run from a process to an entity';
    } else if ((epn.has(s) || ops.has(s)) && epn.has(t)) {  // reduced notation, between entities or from a logic gate
      if (!REDUCED.includes(h)) why = `a ${h} arc must end on a process`;
    } else if (!((epn.has(s) || ops.has(s)) && procs.has(t))) {
      why = `a ${h} arc must run from an entity (or a logic gate) to a process`;
    }
    if (why) out.push([e.id, why]);
  }
  // a process needs something in and something out (reversible: products on both sides)
  const gone = new Set(out.map(([i]) => i));
  const ok = m.arcs.filter(e => !gone.has(e.id));
  for (const p of [...procs].filter(i => !bad.has(i))) {
    const cons = ok.filter(e => e.head === null && (e.source === p || e.target === p)).length;
    const prod = ok.filter(e => e.head === 'production' && e.source === p).length;
    if (!(cons && prod || prod >= 2)) out.push([p, 'a process needs a reactant and a product (a source or sink when there is none)']);
  }
  for (const o of [...ops].filter(i => !bad.has(i))) {
    const lab = N.at(o).labels.slice(0, 1);
    if (lab.length && lab[0] === EQUIV) {
      // the equivalence operator (the spec, 2.9.4): entities in, one plain line out to the generic entity
      const ends = ok.filter(e => e.source === o || e.target === o).map(e => e.source === o ? e.target : e.source);
      if (ends.some(x => !epn.has(x))) out.push([o, 'an equivalence operator joins entities only']);
      else if (ok.filter(e => e.source === o).length !== 1 || ends.length < 3)
        out.push([o, 'an equivalence operator needs two or more entities in and one line out (drawn from it)']);
    } else if (!ok.some(e => e.source === o && (MODIFIERS.includes(e.head) || e.head === null && ops.has(e.target)))) {
      // its output: a modifier arc (to a process, or reduced to an entity) or a plain line into another gate
      out.push([o, 'a logic gate needs an arc out of it']);
    } else if (lab.length && lab[0] === DELAY && ok.filter(e => e.source === o || e.target === o).length !== 2) {
      out.push([o, 'a delay (Activity Flow) has one input and one arc out of it']);
    }
  }
  return out;
}

export function lines(m, found) {
  // each problem as one line, the element by its id and as it is found on the drawing: a node
  // by its label, an arc by its ends
  const N = m.nodes, arcs = new Dict(m.arcs.map(e => [e.id, e]));
  const lab = n => N.has(n) ? split(N.at(n).labels.length && N.at(n).labels[0] ? N.at(n).labels[0] : N.at(n).kind).join(' ') : n;
  const what = i => N.has(i) ? lab(i) : `arc ${lab(arcs.at(i).source)} → ${lab(arcs.at(i).target)}`;
  return found.map(([i, r]) => `${i} (${what(i)}): ${r}`);
}

export function clean(m, found) {
  // the map without the problem elements and the arcs at removed nodes; a removed complex takes
  // its members with it, what a removed compartment holds moves to the compartment around it
  const gone = new Set(found.map(([i]) => i)), N = m.nodes;
  const left_out = i => {  // a problem element, or a member of a complex that is one
    for (let q = i; N.has(q); q = N.at(q).parent) {
      if (gone.has(q) && (q === i || N.at(q).kind === 'Complex')) return true;
    }
    return false;
  };
  const kept = q => {  // the nearest enclosing node that stays
    while (gone.has(q)) q = N.at(q).parent;
    return q;
  };
  const nodes = new Dict([...N].filter(([i]) => !left_out(i))
    .map(([i, d]) => [i, kept(d.parent) === d.parent ? d : replace(d, { parent: kept(d.parent) })]));
  return new Diagram({ ...m, nodes, arcs: m.arcs.filter(e => !gone.has(e.id) && nodes.has(e.source) && nodes.has(e.target)) });
}

export function mark(content, found) {
  // the GraphML with each problem element drawn red and its reason as its description
  // (yEd shows it on hover); nothing else changes
  const G = '{' + NS.g + '}';
  const root = parse(content);
  const keys = new Map(root.findall('g:key', NS).map(k => [k.get('for') + '\u0000' + k.get('attr.name'), k.get('id')]));
  const why = new Map(found);
  for (const [tag, style] of [['node', 'BorderStyle'], ['edge', 'LineStyle']]) {
    let k = keys.get(tag + '\u0000description');
    if (k === undefined) {
      k = 'd_problem_' + tag;
      keys.set(tag + '\u0000description', k);
      root.insert(0, Element(G + 'key', { 'attr.name': 'description', 'attr.type': 'string', for: tag, id: k }));
    }
    for (const x of root.iter(G + tag)) {
      if (!why.has(x.get('id'))) continue;
      for (const s of x.findall('g:data//y:' + style, NS)) { s.set('color', RED); s.set('width', '3.0'); }
      let d = x.find(`g:data[@key="${k}"]`, NS);
      if (d === null) { d = Element(G + 'data', { key: k }); x.insert(0, d); }
      d.text = why.get(x.get('id'));
    }
  }
  return tostring(root);
}

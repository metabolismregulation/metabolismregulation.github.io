// Port of graphml.py: read a yEd GraphML map drawn with the SBGN palette into the map model, and
// write one.
import { Dict, KeyError, div, first, float, get, has, int, len, max, repr, round, sorted, strip } from './py.js';
import { Element, SubElement, cleanupNamespaces, deepcopy, localname, parse, tostring } from './xml.js';
import * as report from './report.js';
import { Arc, Diagram, Node, replace } from './model.js';
import { scale_of } from './style.js';
import TEMPLATE from './yed-template.js';

export const NS = { g: 'http://graphml.graphdrawing.org/xmlns', y: 'http://www.yworks.com/xml/graphml' };
const Y = '{' + NS.y + '}';
// yEd target arrow -> glyph at the arc's target (no arrow: null; any other arrow: production)
const HEAD = { white_circle: 'catalysis', t_shape: 'inhibition', white_diamond: 'modulation',
  white_delta: 'stimulation', white_delta_bar: 'trigger',
  crows_foot_one: 'inhibition' };  // a bar like t_shape, from yEd's other arrows (AsthMap)
// plain yEd shapes (not the SBGN palette) read by their outline (user, 2026-10-16; AsthMap):
// a plain ellipse holding other nodes is an oval compartment (a cell), one labelled AND, OR or
// NOT a logic gate
// yEd's SBGN palette has no omitted or uncertain process: a Process labelled \\ or ? (user's example)
const PROCESS_LABEL = { '\\\\': 'OmittedProcess', '?': 'UncertainProcess' };
const OUTLINE = { 'ShapeNode roundrectangle': 'Macromolecule', 'GenericNode com.yworks.flowchart.terminator': 'SimpleChemical',
  'ShapeNode ellipse': 'UnspecifiedEntity', 'ShapeNode rectangle': 'Phenotype', 'ShapeNode hexagon': 'Phenotype' };
const NX = /^N:\p{Nd}+$/u;

export const baseName = path => {
  // os.path.basename(path).rsplit('.', 1)[0]
  const b = path.split('/').pop(), k = b.lastIndexOf('.');
  return k < 0 ? b : b.slice(0, k);
};

export function realizer(n) {
  // the node's shape (GenericNode for the SBGN palette, ShapeNode and others from other
  // palettes), or the shown realizer of a group (complex, compartment)
  const gn = n.find('g:data/*[y:Geometry]', NS);
  return gn !== null ? gn : n.find('g:data/y:ProxyAutoBoundsNode/y:Realizers/*', NS);
}

function kind_of(n, gn) {
  // the SBGN glyph; a plain group is a compartment; anything else is named by its yEd shape
  // ("ShapeNode ellipse"), for the rules to report
  const conf = gn.get('configuration') || '';
  if (conf.startsWith('com.yworks.sbgn.')) return conf.slice('com.yworks.sbgn.'.length);
  if (n.find('g:graph', NS) !== null && localname(gn.tag) === 'GroupNode') return 'Compartment';
  const shape = gn.find('y:Shape', NS);
  return [localname(gn.tag), conf, shape !== null ? shape.get('type') : ''].filter(x => x).join(' ');
}

const text = r => strip([...r.iter(Y + 'NodeLabel')].map(x => x.text || '').join(''));

function states(gn, res) {
  // state variable icons: [text, rx, ry]; units of information are icons too, but not state variables
  const out = [];
  for (const l of gn.findall('y:NodeLabel', NS)) {
    const r = res.get(l.get('iconData'));
    if (r === undefined || r.find('.//y:GenericNode[@configuration="com.yworks.sbgn.StateVariable"]', NS) === null) continue;
    // the icon's text, or the label's own text drawn over a blank icon (glycogen IRS1/2 "P")
    const p = l.find('.//y:SmartNodeLabelModelParameter', NS);
    out.push([text(r) || strip(l.text || ''), float(p.get('nodeRatioX')), float(p.get('nodeRatioY'))]);
  }
  return out;
}

function units(gn, res) {
  // units of information (ct:gene, ct:mRNA, N:4): icons, or a second, boxed label (iNOS ASL: "N:4")
  const out = [];
  for (const l of gn.findall('y:NodeLabel', NS).slice(1)) {
    if (strip(l.text || '') && !l.get('iconData')) { out.push(strip(l.text)); continue; }
    const r = res.get(l.get('iconData'));
    // a plain box (iNOS) or yEd's SBGN unit of information glyph (ACLY ct:gene, ct:mRNA)
    if (r === undefined || (r.find('.//y:ShapeNode', NS) === null &&
        r.find('.//y:GenericNode[@configuration="com.yworks.sbgn.UnitOfInformation"]', NS) === null)) continue;
    out.push(text(r));
  }
  return out;
}

function count(gn, us) {
  // the multimer count: N in the N:x unit of information, else yEd's mcount (the number of
  // shapes drawn, always 2) for a multimer, 1 for a single unit
  const p = gn.find('y:StyleProperties/y:Property[@name="com.yworks.sbgn.style.mcount"]', NS);
  if (p === null) return 1;
  const n = us.filter(u => NX.test(u)).map(u => int(u.slice(2)));
  return n.length ? n[0] : int(p.get('value'));
}

function ovals(nodes) {
  // a plain ellipse with other nodes' centres inside it is an oval compartment; a node with no
  // parent belongs to the smallest one around it
  const cen = d => [d.box[0] + d.box[2] / 2, d.box[1] + d.box[3] / 2];
  const holds = (o, d) => {
    const [[cx, cy], [x, y]] = [cen(o), cen(d)];
    const a = div(x - cx, o.box[2] / 2), b = div(y - cy, o.box[3] / 2);
    return a * a + b * b <= 1;
  };
  const flat = [...nodes.values()].filter(d => d.parent === null);
  for (const o of flat.filter(d => d.outline === 'ShapeNode ellipse' && d.kind === 'UnspecifiedEntity')) {
    if (flat.some(d => d !== o && d.box[2] * d.box[3] < o.box[2] * o.box[3] && holds(o, d))) o.kind = 'Compartment';
  }
  const cells = flat.filter(d => d.kind === 'Compartment' && d.outline);
  for (const d of flat) {
    const around = cells.filter(o => o !== d && o.box[2] * o.box[3] > d.box[2] * d.box[3] && holds(o, d));
    if (around.length) d.parent = around.reduce((a, o) => o.box[2] * o.box[3] < a.box[2] * a.box[3] ? o : a).id;
  }
}

export function read(path, content) {
  // the map in a GraphML text; path gives its name
  const root = parse(content);
  const res = new Map([...root.iter(Y + 'Resource')].map(r => [r.get('id'), r]));
  const names = new Map(root.findall('g:key', NS).filter(k => k.get('for') === 'node' && k.get('attr.name'))
    .map(k => [k.get('id'), k.get('attr.name')]));
  const nodes = new Dict();
  for (const n of root.iter('{' + NS.g + '}node')) {
    const gn = realizer(n);
    if (gn === null) throw new TypeError("'NoneType' object has no attribute 'get'");
    let kind = kind_of(n, gn);
    const geo = gn.find('y:Geometry', NS);
    const labs = gn.findall('y:NodeLabel', NS);
    const fill = gn.find('y:Fill', NS);
    const p = n.getparent().getparent();
    const us = units(gn, res);
    // a compartment's name: the first label with text
    const l = labs.find(l => strip(l.text || '')) || null;
    const border = gn.find('y:BorderStyle', NS);
    if (kind === 'Process' && l !== null) kind = get(PROCESS_LABEL, strip(l.text), kind);
    const outline = has(OUTLINE, kind) ? kind : null;
    if (outline) kind = l !== null && ['AND', 'OR', 'NOT'].includes(strip(l.text)) && outline.includes('ellipse') ? 'Operator' : OUTLINE[outline];
    const data = new Dict();
    for (const x of n.findall('g:data', NS)) {
      if (names.has(x.get('key')) && strip(x.text || '')) data.set(names.get(x.get('key')), strip(x.text));
    }
    nodes.set(n.get('id'), new Node({
      id: n.get('id'), kind, outline, box: ['x', 'y', 'width', 'height'].map(a => float(geo.get(a))),
      labels: labs.filter(l => !l.get('iconData')).map(l => strip(l.text || '')),
      parent: p.tag.endsWith('node') ? p.get('id') : null,
      fill: fill !== null ? fill.get('color') : null,
      states: states(gn, res), units: us, count: count(gn, us),
      label_at: (kind === 'Compartment' || outline) && l !== null ? [float(l.get('x')), float(l.get('y'))] : null,
      data, dashed: border !== null && border.get('type') !== 'line' }));
  }
  ovals(nodes);
  for (const d of nodes.values()) if (d.kind !== 'Compartment') d.label_at = null;
  const arcs = [];
  for (const e of root.iter('{' + NS.g + '}edge')) {
    const pl = e.find('g:data/*[y:Path]', NS);  // PolyLineEdge in the SBGN palette; curves too
    const a = pl.find('y:Arrows', NS);
    const head = a.get('target');
    const yp = pl.find('y:Path', NS);
    arcs.push(new Arc({ id: e.get('id'), source: e.get('source'), target: e.get('target'),
      // another arrow is kept by its yEd name, for the rules to report
      head: head === 'none' || head === null ? null : get(HEAD, head, head === 'delta' ? 'production' : 'arrow ' + head),
      tail: !(a.get('source') === 'none' || a.get('source') === null),
      points: yp.findall('y:Point', NS).map(q => [float(q.get('x')), float(q.get('y'))]),
      source_at: [float(yp.get('sx')), float(yp.get('sy'))],
      target_at: [float(yp.get('tx')), float(yp.get('ty'))],
      dashed: pl.find('y:LineStyle', NS).get('type') !== 'line' }));
  }
  return new Diagram({ name: baseName(path), nodes, arcs });
}


// --- writing: every element is a copy of a template cut from our yEd files (yed.graphml)
const G = '{' + NS.g + '}';
const ARROW = Object.fromEntries(Object.entries(HEAD).filter(([k]) => k !== 'crows_foot_one').map(([k, v]) => [v, k]));  // AsthMap's bar is read, never written
ARROW.production = 'delta';
export const EQUIV = '≡';  // the equivalence operator's label in yEd's SBGN palette (user's file, 2026-10-17)
export const DELAY = 'τ';  // Activity Flow's delay: an Operator labelled tau, drawn as the equivalence (user, 2026-10-17)

export function without_delays(m, form) {
  // for a format with no delay (CellDesigner, SBGN PD): its input joined straight to its target,
  // with the type of the arc out of it. (Python iterates the delays as a set, in no fixed order;
  // here in the order of the nodes.)
  const ds = [...m.nodes].filter(([, d]) => d.kind === 'Operator' && d.labels.length && d.labels[0] === DELAY).map(([i]) => i);
  if (!ds.length) return m;
  report.say('changed', `delay: no ${form} form, its input joined to its target (${sorted(ds).join(', ')})`);
  let arcs = m.arcs.filter(a => !ds.includes(a.source) && !ds.includes(a.target));
  for (const d of ds) {
    const outs = m.arcs.filter(a => a.source === d && (a.head || m.nodes.at(a.target).kind === 'Operator'));
    const ins = m.arcs.filter(a => (a.source === d || a.target === d) && !outs.includes(a)).map(a => a.source === d ? a.target : a.source);
    arcs = arcs.concat(outs.flatMap(o => ins.map(i => replace(o, { id: `${o.id}_${i}`, source: i, points: [], source_at: [0.0, 0.0] }))));
  }
  return new Diagram({ ...m, nodes: new Dict([...m.nodes].filter(([i]) => !ds.includes(i))), arcs });
}

export const LINE = 16.5, CHAR = 9.5;  // a label line's height and a character's width at font size 14 (our maps)

function label(l, txt, w, h, k = 1.0) {
  // the label's text, its box estimated and centred (yEd measures it again when the text is edited);
  // k: the font size against our 14
  const lines = txt ? txt.split('\n') : [];
  const lw = Math.max(...(lines.length ? lines.map(len) : [0])) * CHAR * k, lh = lines.length * LINE * k + 4;
  l.text = txt || null;
  l.set('hasText', txt ? 'true' : 'false');
  for (const [a, v] of [['width', lw], ['height', lh], ['x', (w - lw) / 2], ['y', (h - lh) / 2]]) l.set(a, repr(v));
}

export function corrected(m) {
  // a map that looks like SBGN but is drawn with other shapes (read by their outline), redrawn
  // with the SBGN palette (user, 2026-10-17: <map>-corrected.graphml); null for a map already in it
  return [...m.nodes.values()].some(d => d.outline) ? write(m) : null;
}

export function write(diagram) {
  // the font follows the map's scale: 14 on our protein height (40), so Newt's 30 high gives 11
  const font = round(14 * scale_of(diagram) + 0.01);
  const t = parse(TEMPLATE);
  const tpl = new Map([...t.iter(G + 'node')].map(n => [n.get('id'), n]));
  const icon = tpl.get('IconLabel').find('.//y:NodeLabel', NS);
  const arc = t.iter(G + 'edge').next().value;
  const resTpl = new Map([...t.iter(Y + 'Resource')].map(r => [r.get('id'), r]));
  const N = diagram.nodes;
  const names = [...new Set([...N.values()].flatMap(d => [...d.data.keys()]))];
  const root = Element(G + 'graphml', {}, [[null, NS.g], ['y', NS.y], ['yed', 'http://www.yworks.com/xml/yed/3']]);
  names.forEach((name, k) => SubElement(root, G + 'key', { 'attr.name': name, 'attr.type': 'string', for: 'node', id: 'd' + k }));
  for (const [kid, f, y] of [['ng', 'node', 'nodegraphics'], ['res', 'graphml', 'resources'], ['eg', 'edge', 'edgegraphics']])
    SubElement(root, G + 'key', { for: f, id: kid, 'yfiles.type': y });
  const resources = [], rid = new Map();

  const resource = (kind, txt) => {  // one icon per kind and text, shared as yEd shares them
    const key = kind + '\u0000' + txt;
    if (!rid.has(key)) {
      const r = deepcopy(resTpl.get(kind));
      rid.set(key, String(rid.size + 1));
      r.set('id', rid.get(key));
      const gn = r.find('.//y:GenericNode', NS);
      gn.find('y:Geometry', NS).set('width', len(txt) <= 2 ? '15.0' : '45.0');  // as in our maps
      label(gn.find('y:NodeLabel', NS), txt, float(gn.find('y:Geometry', NS).get('width')), 15.0);
      resources.push(r);
    }
    return rid.get(key);
  };

  const kids = new Map();
  for (const [i, d] of N) {
    const p = N.has(d.parent) ? d.parent : null;
    if (!kids.has(p)) kids.set(p, []);
    kids.get(p).push(i);
  }

  const missing = new Map();
  const PROCESS_SIGN = Object.fromEntries(Object.entries(PROCESS_LABEL).map(([k, v]) => [v, k]));
  const node = (parent, i) => {
    const d = N.at(i);
    const group = (kids.get(i) || []).length > 0 || d.kind === 'Compartment';
    const name = group && d.kind === 'Complex' ? 'ComplexGroup' : Object.values(PROCESS_LABEL).includes(d.kind) ? 'Process' : d.kind;
    if (!tpl.has(name)) {  // a glyph none of our yEd files has: no template to copy
      if (!missing.has(d.kind)) missing.set(d.kind, []);
      missing.get(d.kind).push(i);
      return;
    }
    const n = deepcopy(tpl.get(name));
    n.set('id', i);
    parent.append(n);
    names.forEach((nm, k) => {
      if (d.data.get(nm)) {
        const x = Element(G + 'data', { key: 'd' + k });
        x.text = d.data.get(nm);
        n.insert(k, x);
      }
    });
    const gn = realizer(n);
    const [, , w, h] = d.box;
    ['x', 'y', 'width', 'height'].forEach((k, j) => gn.find('y:Geometry', NS).set(k, repr(d.box[j])));
    const fill = gn.find('y:Fill', NS);
    if (d.fill) fill.set('color', d.fill);
    else { fill.del('color'); fill.set('hasColor', 'false'); }  // no fill (aspirin's drugs)
    if (d.dashed) gn.find('y:BorderStyle', NS).set('type', 'dashed');
    const l = gn.find('y:NodeLabel', NS);
    const sign = get(PROCESS_SIGN, d.kind);
    if (!sign && font !== 14) l.set('fontSize', String(font));
    label(l, sign || d.labels.find(x => x) || '', w, h, font / 14);  // the name; a second label is a unit (N:4)
    if (d.kind === 'Operator' && [EQUIV, DELAY].includes(l.text)) {  // as yEd's palette draws the equivalence
      l.set('fontFamily', 'Monospaced'); l.set('fontSize', '18');
    }
    if (d.kind === 'Compartment') {  // its name where the source has it, else centred at the top (the template's place)
      const [lx, ly] = d.label_at || [float(l.get('x')), 0.0];
      l.set('x', repr(lx)); l.set('y', repr(ly));
    }
    if (d.count > 1) {  // yEd draws a multimer as two shapes; N:x says how many
      let sp = gn.find('y:StyleProperties', NS);
      if (sp === null) sp = SubElement(gn, Y + 'StyleProperties');  // the simple chemical template has none (a multimer Ca2+, O2)
      SubElement(sp, Y + 'Property', { class: 'java.lang.Integer', name: 'com.yworks.sbgn.style.mcount', value: '2' });
    }
    const us = d.units.concat(d.count > 2 && !d.units.some(u => NX.test(u)) ? ['N:' + d.count] : []);
    const icons = d.states.map(([txt, rx, ry]) => ['StateVariable', txt, rx, ry])
      .concat(us.map((u, k) => ['UnitOfInformation', u, (k + 1) / (us.length + 1) - 0.5, -0.5]));
    for (const [kind, txt, rx, ry] of icons) {
      const il = deepcopy(icon);
      il.set('iconData', resource(kind, txt));
      const p = il.find('.//y:SmartNodeLabelModelParameter', NS);
      p.set('nodeRatioX', repr(rx)); p.set('nodeRatioY', repr(ry));
      const ls = gn.findall('y:NodeLabel', NS);
      ls[ls.length - 1].addnext(il);
    }
    if (group) {
      const sub = n.find('g:graph', NS);
      sub.set('id', i + ':');
      for (const j of kids.get(i) || []) node(sub, j);
    }
  };

  const g = SubElement(root, G + 'graph', { edgedefault: 'directed', id: 'G' });
  for (const i of kids.get(null) || []) node(g, i);
  for (const [k, ids] of missing)
    report.say('left out', `no yEd template for ${k}: ${ids.length} nodes left out (${ids.map(i => first(N.at(i).labels) || i).join(', ')})`);
  const gone = new Set([...missing.values()].flat());
  for (const a of diagram.arcs) {
    if (gone.has(a.source) || gone.has(a.target)) continue;
    const e = deepcopy(arc);
    e.set('id', a.id); e.set('source', a.source); e.set('target', a.target);
    const pl = e.find('.//y:PolyLineEdge', NS);
    const yp = pl.find('y:Path', NS);
    ['sx', 'sy', 'tx', 'ty'].forEach((k, j) => yp.set(k, repr(a.source_at.concat(a.target_at)[j])));
    for (const q of a.points) SubElement(yp, Y + 'Point', { x: repr(q[0]), y: repr(q[1]) });
    if (a.dashed) pl.find('y:LineStyle', NS).set('type', 'dashed');
    if (a.head && !has(ARROW, a.head)) throw KeyError(a.head);
    pl.find('y:Arrows', NS).set('target', a.head ? ARROW[a.head] : 'none');
    pl.find('y:Arrows', NS).set('source', a.tail ? 'delta' : 'none');
    pl.find('y:BendStyle', NS).set('smoothed', 'true');  // soft bends on every arc (user, 2026-10-14)
    g.append(e);
  }
  const rs = SubElement(SubElement(root, G + 'data', { key: 'res' }), Y + 'Resources');
  rs.extend(resources);
  cleanupNamespaces(root);
  return tostring(root, true);
}

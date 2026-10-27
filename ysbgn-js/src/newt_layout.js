// Port of newt_layout.py, the Newt adapter: what an SBGN-ML map needs so Newt draws it as the
// source does. Every process and gate in a compartment, each compartment as large as Newt's
// padding needs, neighbours too close for it moved apart (the converter's docs, SBGN-ML).
import { Dict, formatD, min, sorted } from './py.js';
import * as report from './report.js';
import { PROCESSES, centre, compartment_of, decorations } from './layout.js';

// Python's min(a, b) and max(a, b): the first unless the second is smaller (larger)
const pmin = (a, b) => b < a ? b : a;
const pmax = (a, b) => b > a ? b : a;

export function placed(diagram) {
  // a process or gate outside any compartment put into the smallest one its centre lies in, else
  // into its first neighbour's, as Newt does (Newt puts it in a neighbour's and grows that
  // compartment over the others: iNOS, the transports across the plasma membrane; carnitine,
  // LKB1 out of the nucleus; user, 2026-10-18)
  const N = diagram.nodes;
  for (const d of N.values()) {
    if (['Operator', ...PROCESSES].includes(d.kind) && compartment_of(N, d.id) === null) {
      const [x, y] = centre(d);
      const at = [...N].filter(([, e]) => e.kind === 'Compartment' &&
        e.box[0] <= x && x <= e.box[0] + e.box[2] && e.box[1] <= y && y <= e.box[1] + e.box[3]).map(([c]) => c);
      const near = diagram.arcs.filter(a => a.source === d.id || a.target === d.id)
        .map(a => compartment_of(N, a.source === d.id ? a.target : a.source));
      d.parent = at.length ? min(at, c => N.at(c).box[2] * N.at(c).box[3]) : near.find(c => c) ?? d.parent;
    }
  }
  return diagram;
}

// Newt (sbgnml-to-cytoscape bboxProp): a compartment's padding, 24 (its 14 and the compound 10),
// with half a border and 1, 30 to be safe; a complex inside it stands out by its own padding
const NEWT_PAD = 30, COMPLEX_PAD = 20;

export function for_newt(diagram, ports = true) {
  // compartments as Newt keeps them (user, 2026-10-18): Newt keeps a compartment's box only when
  // its contents (state variables, units, a complex's padding, a process's port stubs) stay
  // NEWT_PAD inside every edge, else it wraps the contents and edges aligned in the source drift
  // apart or overlap. Each box is widened as its contents need; edges aligned in the source (within
  // 2 px) move together. Where two neighbours' contents are too close across their shared edge,
  // everything past that edge moves on by what is missing, so the edges stay aligned (printed).
  // Compartments side by side keep the gap the source has between them, up to NEWT_PAD (platelet
  // eicosanoids: 2.7 px apart in yEd, CYTOSOL grew into DENSE TUBULAR SYSTEM; user, 2026-10-19)
  const N = diagram.nodes;
  const comps = [...N].filter(([, d]) => d.kind === 'Compartment').map(([c]) => c);
  const value = (c, k) => N.at(c).box[k % 2] + (k > 1 ? N.at(c).box[2 + k % 2] : 0);
  // facing pairs: a before b along an axis, side by side on the other, neither around the other
  const within = (a, b) => [0, 1].every(k => value(a, k) >= value(b, k) - 1) && [2, 3].every(k => value(a, k) <= value(b, k) + 1);
  const facing = [];
  for (const a of comps) for (const b of comps) for (const ax of [0, 1]) {
    if (a !== b && !within(a, b) && !within(b, a) && value(a, ax + 2) - 2 <= value(b, ax) &&
        pmin(value(a, 3 - ax), value(b, 3 - ax)) - pmax(value(a, 1 - ax), value(b, 1 - ax)) > 0.5)
      facing.push([a, b, ax, pmin(NEWT_PAD, pmax(0.0, value(b, ax) - value(a, ax + 2)))]);
  }
  // a node outside every compartment that a compartment, once in place, grows over by more than
  // half is covered whole, so the edge does not stop inside it (SREBP from CellDesigner, straight:
  // the COPII vesicle grew to its process and cut the Sec23:Sec24 complex; user, 2026-10-20); one
  // the growth only grazes, or the source draws across the edge, stays as it is
  const free = [...N].filter(([i, d]) => d.kind !== 'Compartment' && d.parent === null && compartment_of(N, i) === null).map(([i]) => i);
  const covered = new Dict();
  const inside = (b, q) => pmax(0, pmin(b[0] + b[2], q[2]) - pmax(b[0], q[0])) * pmax(0, pmin(b[1] + b[3], q[3]) - pmax(b[1], q[1]));
  const key = (c, k) => c + '\u0000' + k;
  let bounds;
  for (let round = 0; round < 50; round++) {
    const ext = new Map(comps.map(c => [c, [Infinity, Infinity, -Infinity, -Infinity]]));
    for (const [i, d] of N) {
      const c = covered.has(i) ? covered.get(i) : compartment_of(N, i);
      if (c === null || d.parent !== null && N.at(d.parent).kind === 'Complex') continue;  // a member: inside its complex
      // a complex with its padding, a process or gate as Newt draws it (18 px: 51 with its
      // ports, 27 without)
      const e = d.kind === 'Complex' ? COMPLEX_PAD : d.kind === 'Compartment' ? NEWT_PAD - 4 :
        ['Operator', ...PROCESSES].includes(d.kind) ? (ports ? 17 : 5) : 0;
      const [states, units] = decorations(d);
      for (const [[x, y, w, h], ee] of [[d.box, e], ...states.concat(units.map(([, b]) => b)).map(b => [b, 0])]) {
        [x - ee, y - ee, x + w + ee, y + h + ee].forEach((v, k) => {
          ext.get(c)[k] = k < 2 ? pmin(ext.get(c)[k], v) : pmax(ext.get(c)[k], v);
        });
      }
    }
    const groups = [];
    for (const c of comps) for (let k = 0; k < 4; k++) {
      const g = groups.find(g => g[0][1] % 2 === k % 2 && Math.abs(value(...g[0]) - value(c, k)) <= 2);
      if (g) g.push([c, k]); else groups.push([[c, k]]);
    }
    bounds = groups.map(g => {
      const los = g.filter(([c, k]) => k > 1 && ext.get(c)[k] > -Infinity).map(([c, k]) => ext.get(c)[k] + NEWT_PAD);
      const his = g.filter(([c, k]) => k < 2 && ext.get(c)[k] < Infinity).map(([c, k]) => ext.get(c)[k] - NEWT_PAD);
      return [g, los.reduce(pmax, -Infinity), his.reduce(pmin, Infinity)];
    });
    // each edge where it ends up (an edge grows outward as its contents need); a facing pair
    // closer than its gap moves b's side on
    const end = new Map();
    for (const [g, lo, hi] of bounds) for (const [c, k] of g) end.set(key(c, k), k > 1 ? pmax(lo, value(c, k)) : pmin(hi, value(c, k)));
    const clash = sorted(
      bounds.filter(([, lo, hi]) => lo > hi + 0.5).map(([g, lo, hi]) => [value(...g[0]), g, lo - hi]).concat(
        facing.filter(([a, b, ax, gap]) => end.get(key(a, ax + 2)) + gap > end.get(key(b, ax)) + 0.5 &&
          Math.abs(value(a, ax + 2) - value(b, ax)) > 2)
          .map(([a, b, ax, gap]) => [value(b, ax), [[b, ax]], end.get(key(a, ax + 2)) + gap - end.get(key(b, ax))])),
      t => [t[1][0][1] % 2, t[0]]);
    if (!clash.length) {
      const grown = new Map(comps.map(c => [c, [0, 1, 2, 3].map(k => k < 2 ? pmin(value(c, k), ext.get(c)[k] - NEWT_PAD) : pmax(value(c, k), ext.get(c)[k] + NEWT_PAD))]));
      const hit = new Dict();
      for (const i of free) {
        if (covered.has(i)) continue;
        const b = N.at(i).box;
        for (const c of comps)
          if (0.5 * b[2] * b[3] < inside(b, grown.get(c)) && inside(b, grown.get(c)) < b[2] * b[3] &&
              !inside(b, [0, 1, 2, 3].map(k => value(c, k)))) hit.set(i, c);
      }
      if (!hit.size) break;
      for (const [i, c] of hit) covered.set(i, c);
      continue;
    }
    const [at, g, by] = clash[0];
    moved(diagram, g[0][1] % 2, at, by);
    const names = sorted(new Set(g.map(([c]) => N.at(c).labels.length ? N.at(c).labels[0] : c)));
    report.say('changed', `compartments ${names.join(', ')}: moved ${formatD(by)} px apart, so that Newt does not overlap them`);
  }
  for (const [g, lo, hi] of bounds) {
    const v = pmin(pmax(value(...g[0]), lo), hi);
    for (const [c, k] of g) {
      const d = N.at(c);
      const [x0, y0, x1, y1] = [d.box[0], d.box[1], d.box[0] + d.box[2], d.box[1] + d.box[3]].map((q, j) => j === k ? v : q);
      if (d.label_at && k < 2) d.label_at = [d.label_at[0] + d.box[0] - x0, d.label_at[1] + d.box[1] - y0];  // the name stays where it is
      d.box = [x0, y0, x1 - x0, y1 - y0];
    }
  }
  return diagram;
}

function moved(diagram, axis, at, by) {
  // everything past the line at (x or y, by axis) moved on by `by`: the compartments that start
  // there with their contents, the nodes outside any compartment, the bends; a compartment the
  // line runs through grows
  const N = diagram.nodes;
  const past = d => d.box[axis] >= at - 2;
  const shift = b => b.map((v, j) => j === axis ? v + by : v);
  for (const [i, d] of N) {
    const c = d.kind !== 'Compartment' ? compartment_of(N, i) : null;
    if (d.kind === 'Compartment') {
      if (past(d)) d.box = shift(d.box);
      else if (d.box[axis] + d.box[2 + axis] > at - 2) d.box = d.box.map((v, j) => j === 2 + axis ? v + by : v);
    } else if (c !== null && past(N.at(c)) || c === null && centre(d)[axis] > at) {
      d.box = shift(d.box);
    }
  }
  for (const a of diagram.arcs) a.points = a.points.map(p => p[axis] > at ? shift(p) : p);
}

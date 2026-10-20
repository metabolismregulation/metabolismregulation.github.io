// Port of the part of layout.py the SBGN-ML writer uses: centres, compartments, decorations, and
// the bends that shape a route. (main_lines, twins, route, turn, exit_point, visible, corner and
// at_centres serve CellDesigner only.)
import { hypot, max } from './py.js';

export const PROCESSES = ['Process', 'OmittedProcess', 'UncertainProcess'];

export function centre(d) {
  const [x, y, w, h] = d.box;
  return [x + w / 2, y + h / 2];
}

export function compartment_of(N, i) {
  // a node's enclosing compartment
  let q = N.at(i).parent;
  while (q !== null && N.at(q).kind !== 'Compartment') q = N.at(q).parent;
  return q;
}

const NX = /^N:\p{Nd}+$/u;

export function decorations(d) {
  // a node's state variables (their boxes) and units of information ([label, box]), as written
  const [x, y, w, h] = d.box;
  const [cx, cy] = [x + w / 2, y + h / 2];
  const states = d.states.map(([txt, rx, ry]) => {
    const sw = [...txt].length <= 2 ? 15.0 : 45.0;  // as yEd's icons on our maps
    return [cx + rx * w - sw / 2, cy + ry * h - 7.5, sw, 15.0];
  });
  const units = d.units.concat(d.count > 2 && !d.units.some(u => NX.test(u)) ? ['N:' + d.count] : []);
  const uw = units.map(u => Math.max(15.0, [...u].length * 7.0));
  return [states, units.map((u, k) => [u, [x + (k + 1) / (units.length + 1) * w - uw[k] / 2, y - 7.5, uw[k], 15.0]])];
}

// Bends (user, 2026-10-13): a yEd bend counts if leaving it out moves the line by more than EPS.
const EPS = 20.0;

export function off(p, a, b) {  // distance of p from the line through a and b
  const L = hypot(b[0] - a[0], b[1] - a[1]) || 1;
  return Math.abs((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / L;
}

function simplify(pts, eps) {
  // Ramer-Douglas-Peucker: keep only the points that shape the line
  if (pts.length < 3) return pts;
  const d = pts.slice(1, -1).map(p => off(p, pts[0], pts[pts.length - 1]));
  const i = max(d.keys(), k => d[k]);
  if (d[i] < eps) return [pts[0], pts[pts.length - 1]];
  return simplify(pts.slice(0, i + 2), eps).slice(0, -1).concat(simplify(pts.slice(i + 1), eps));
}

export function unbent(run, tol = 1) {
  // a polyline without the points that lie on the straight line between their neighbours
  // (between them, within tol px): no bend in either program
  run = [...run];
  let k = 1;
  while (k < run.length - 1) {
    const [[ax, ay], [bx, by], [qx, qy]] = [run[k - 1], run[k], run[k + 1]];
    if (off(run[k], run[k - 1], run[k + 1]) < tol &&
        Math.min(ax, qx) - tol <= bx && bx <= Math.max(ax, qx) + tol && Math.min(ay, qy) - tol <= by && by <= Math.max(ay, qy) + tol)
      run.splice(k, 1);
    else k += 1;
  }
  return run;
}

export function bends(route) {
  // the bends that shape a route (advanced layout), its ends left out
  return simplify(route, EPS).slice(1, -1);
}

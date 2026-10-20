// Port of style.py. Standard sizes (user, 2026-10-16), for a map from another drawing: proteins,
// genes and RNAs 80 x 40; metabolites (chemical()) 36 x 36 circles where the map draws them as
// circles, else stadiums 32 high, as wide as the name needs in steps of 10; centres kept. A map
// whose objects are clearly larger or smaller than ours (median protein height off 40 by more
// than 20%, e.g. a large font) is first scaled as a whole, distances included.
// The file with standard sizes is made when asked (the page's tick box, to harmonise a map) or
// when the map is drawn at another scale than usual (user, 2026-10-20): the median protein height
// off our 40, the median label font off the program's default, or, on a map without proteins, the
// median metabolite height off CHEMICAL, each by more than NOTICED.
import { Dict, div, formatG, get, len, max, median } from './py.js';
import { Diagram, replace } from './model.js';

export const PROTEIN = [80.0, 40.0];
const SIZE = { Macromolecule: PROTEIN, NucleicAcidFeature: PROTEIN };
const CIRCLE = [36.0, 36.0];  // the yEd metabolite glyph is a circle when square, else a stadium
const NOTICED = 1.2;  // a scale this far from 1 (either way) is rescaled
// the program's default label font: CellDesigner (all 926 labels of the website's CellDesigner
// files), Newt (its sample files)
const FONT = { CellDesigner: 12.0, Newt: 11.0 };
const CHEMICAL = [25.0, 40.0];  // usual metabolite heights: CellDesigner's 70 x 25 to Newt's 40 (ours 32 to 36; user, 2026-10-20)
const ENTITY = ['Macromolecule', 'NucleicAcidFeature', 'SimpleChemical', 'Complex', 'UnspecifiedEntity', 'Perturbation', 'Phenotype'];

export function chemical(d) {
  // a metabolite's size: a circle stays a circle; a stadium is 32 high and 60, 70, 80, ... wide,
  // about 7 px per character of its longest name line plus 14 (the user's maps: 60 for Pi,
  // 80 glutamate, 90 citrulline, 100 oxaloacetate, 180 alpha-keto-beta-methylvalerate)
  const [w, h] = d.box.slice(2);
  if (Math.abs(w - h) <= 0.1 * Math.max(w, h)) return CIRCLE;
  const name = max((d.labels.length ? d.labels[0] : '').split('\n'), len);
  return [Math.max(60.0, 10.0 * Math.ceil((7 * len(name) + 14) / 10)), 32.0];
}

export function scale_of(m) {
  const hs = [...m.nodes.values()].filter(d => d.kind === 'Macromolecule' && d.count === 1).map(d => d.box[3]);
  const s = hs.length ? median(hs) / PROTEIN[1] : 1.0;
  return s > NOTICED || s < 1 / NOTICED ? s : 1.0;
}

const off = (v, d) => v > d * NOTICED || v < d / NOTICED;

export function reasons(m, program) {
  // why the map is not at the usual scale, [] when it is
  const font = FONT[program];
  const med = vs => vs.length ? median(vs) : null;
  const ds = [...m.nodes.values()];
  const fonts = med(ds.filter(d => d.font && ENTITY.includes(d.kind)).map(d => d.font));
  const proteins = med(ds.filter(d => d.kind === 'Macromolecule' && d.count === 1).map(d => d.box[3]));
  const chems = med(ds.filter(d => d.kind === 'SimpleChemical' && d.count === 1).map(d => d.box[3]));
  const why = [];
  if (fonts && off(fonts, font))
    why.push(`Median font size ${formatG(fonts)}, ${program} default ${formatG(font)}.`);
  if (proteins && off(proteins, PROTEIN[1]))
    why.push(`Median protein height ${formatG(proteins)}, standard ${formatG(PROTEIN[1])}.`);
  if (!proteins && chems && (chems < CHEMICAL[0] / NOTICED || chems > CHEMICAL[1] * NOTICED))
    why.push(`Median metabolite height ${formatG(chems)}, usual range ${formatG(CHEMICAL[0])} to ${formatG(CHEMICAL[1])}.`);
  return why;
}

export function standard(m, program, asked = false) {
  // the map with standard node sizes when asked or drawn at another scale (reasons), else null
  if (!asked && !reasons(m, program).length) return null;
  return standardise(m);
}

export function standardise(m) {
  const s = scale_of(m);
  const nodes = new Dict(), ratio = new Dict();
  for (const [i, d] of m.nodes) {
    const [x, y, w, h] = d.box.map(v => div(v, s));
    let [W, H] = d.kind === 'SimpleChemical' ? chemical(d) : get(SIZE, d.kind, [w, h]);
    if (d.kind.endsWith('Process') || d.kind === 'Operator') [W, H] = [d.box[2], d.box[3]];  // glyphs of their own fixed size
    ratio.set(i, [w ? W / w : 1, h ? H / h : 1]);
    nodes.set(i, replace(d, { box: [x + w / 2 - W / 2, y + h / 2 - H / 2, W, H],
      label_at: d.label_at ? d.label_at.map(v => v / s) : null }));
  }
  // ports keep their place on the node's border; bends move with the map, and the bend next to
  // a port stays in line with it where it was (a straight run into the node stays straight)
  const cen = b => [b[0] + b[2] / 2, b[1] + b[3] / 2];
  const end = (i, at, nw) => {  // the arc's end point, before (scaled) and after
    const [cx, cy] = cen(m.nodes.at(i).box), [nx, ny] = cen(nodes.at(i).box);
    return [[(cx + at[0]) / s, (cy + at[1]) / s], [nx + nw[0], ny + nw[1]]];
  };
  const keep = (p, old, nw) => [Math.abs(p[0] - old[0]) < 0.5 ? nw[0] : p[0], Math.abs(p[1] - old[1]) < 0.5 ? nw[1] : p[1]];
  const arcs = m.arcs.map(e => {
    const sa = [e.source_at[0] / s * ratio.at(e.source)[0], e.source_at[1] / s * ratio.at(e.source)[1]];
    const ta = [e.target_at[0] / s * ratio.at(e.target)[0], e.target_at[1] / s * ratio.at(e.target)[1]];
    const pts = e.points.map(([px, py]) => [px / s, py / s]);
    if (pts.length) {
      pts[0] = keep(pts[0], ...end(e.source, e.source_at, sa));
      pts[pts.length - 1] = keep(pts[pts.length - 1], ...end(e.target, e.target_at, ta));
    }
    return replace(e, { points: pts, source_at: sa, target_at: ta });
  });
  return new Diagram({ ...m, nodes, arcs });
}

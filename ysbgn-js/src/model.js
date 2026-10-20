// Port of model.py: the map between a reader and a writer, SBGN glyphs and arcs with their
// geometry, independent of the file format. Coordinates are absolute, in the units of the source
// (yEd: one unit per pixel of a 1:1 export), y down. Python's tuples are arrays here, never
// changed in place; Python's Map is Diagram (Map is JavaScript's dict).
import { Dict } from './py.js';

// glyph at an arc's target: null (consumption, logic arc), or one of these
export const HEADS = ['production', 'catalysis', 'inhibition', 'modulation', 'stimulation', 'trigger'];

export class Node {
  constructor(f) {
    this.id = f.id;
    this.kind = f.kind;          // SBGN glyph: Macromolecule, SimpleChemical, Complex, Process, Operator, Compartment, ...
    this.box = f.box;            // [x, y, w, h]
    this.labels = f.labels;      // label texts, the name first
    this.parent = f.parent ?? null;  // enclosing complex or compartment
    this.fill = f.fill ?? null;  // '#RRGGBB' or '#RRGGBBAA'
    this.states = f.states ?? [];  // state variables: [text, rx, ry], place as offset from the centre in node widths and heights
    this.units = f.units ?? [];  // units of information: ct:gene, N:4, ...
    this.count = f.count ?? 1;   // multimer: number of units (2 when drawn as a multimer without N:x)
    this.label_at = f.label_at ?? null;  // compartment: top left of its name, relative to the box
    this.data = f.data ?? new Dict();  // yEd node data by name: url, annotation (HGNC symbol, UniProt, ...)
    this.dashed = f.dashed ?? false;  // dashed border: a hypothetical entity (CellDesigner)
    this.outline = f.outline ?? null;  // the plain yEd shape it was read from by its outline (not the SBGN palette)
    this.species = f.species ?? null;  // the entity the file says the glyph draws (CellDesigner species)
    this.font = f.font ?? null;  // its label's font size, where the file gives one (CellDesigner, Newt): style.reasons
  }
}

export class Arc {
  constructor(f) {
    this.id = f.id;
    this.source = f.source;
    this.target = f.target;
    this.head = f.head ?? null;  // see HEADS
    this.tail = f.tail ?? false;  // an arrowhead at the source as well
    this.points = f.points ?? [];  // bends
    this.source_at = f.source_at ?? [0.0, 0.0];  // where the arc leaves its source, from the source's centre
    this.target_at = f.target_at ?? [0.0, 0.0];  // where it meets its target, from the target's centre
    this.dashed = f.dashed ?? false;  // a dashed line: unknown catalysis, inhibition, influence (CellDesigner)
  }
}

export class Diagram {
  constructor(f) {
    this.name = f.name;
    this.nodes = f.nodes;  // Dict id -> Node, in the order of the file
    this.arcs = f.arcs;
  }
}

export function replace(obj, changes = {}) {
  // dataclasses.replace: a shallow copy with some fields changed
  return new obj.constructor({ ...obj, ...changes });
}

export function deepcopy(m) {
  // copy.deepcopy of a Diagram
  const nodes = new Dict();
  for (const [i, d] of m.nodes) {
    nodes.set(i, new Node({ ...d, box: [...d.box], labels: [...d.labels], states: d.states.map(s => [...s]),
      units: [...d.units], label_at: d.label_at && [...d.label_at], data: new Dict(d.data) }));
  }
  const arcs = m.arcs.map(a => new Arc({ ...a, points: a.points.map(p => [...p]), source_at: [...a.source_at], target_at: [...a.target_at] }));
  return new Diagram({ name: m.name, nodes, arcs });
}

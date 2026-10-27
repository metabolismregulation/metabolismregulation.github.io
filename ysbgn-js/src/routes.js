// Port of the GraphML and SBGN-ML part of routes.py: which files each input gives, with the
// Converter page's button labels; each file is made only when asked (made()).
//   GraphML: SBGN-ML straight and advanced; GraphML (corrected) for a map drawn with other
//            shapes; GraphML (marked) when it breaks a rule (the problems left out)
//   SBGN-ML, Newt: GraphML; GraphML (standard sizes) for a map drawn at another scale, or for
//            every map when standard (style.standard; user, 2026-10-20)
// (CellDesigner, both ways, is the Python converter's.)
import * as graphml from './graphml.js';
import * as report from './report.js';
import * as rules from './rules.js';
import * as sbgnml from './sbgnml.js';
import * as style from './style.js';

export const LAYOUTS = ['straight', 'advanced'];

export class Output {
  constructor(ending, label, make, red = false) {
    this.ending = ending;  // after the input's base name: -advanced.sbgn
    this.label = label;    // the page's button: SBGN-ML (advanced)
    this.make = make;      // () -> the file's text, or null when the input gives no such file
    this.red = red;        // the page's red button: the map with its problems marked
  }
}

function errorText(e) {
  // as Python prints an exception: its type and message
  if (e.type) return `${e.type}: ${e.message}`;
  return `${e.name}: ${e.message}`;
}

export function made(o) {
  // [text or null, messages]: the file and what the converter said making it, or why it failed,
  // each message [kind, text]
  const said = [];
  let text = null;
  report.collect(() => {
    try {
      text = o.make();
    } catch (e) {
      text = null;
      said.push(['left out', 'Not converted: ' + errorText(e)]);
    }
  }, said);
  return [text, said];
}

function standardised(read, program, asked) {
  // GraphML (standard sizes), null for a map at the usual scale unless asked; the reader's messages
  // are the plain GraphML's
  const [m] = report.collect(read);
  const t = style.standard(m, program, asked);
  return t ? graphml.write(t) : null;
}

export function outputs(path, content, standard = false) {
  // the outputs of one input file (its path, for its name and format, and its text)
  const ext = path.toLowerCase().split('.').pop();
  if (ext === 'graphml') {
    let found;
    try {
      [found] = report.collect(() => rules.problems(graphml.read(path, content)));
    } catch (e) {
      return [new Output('', '', () => rules.problems(graphml.read(path, content)))];  // made() says why
    }
    const read = () => rules.clean(graphml.read(path, content), found);  // a fresh copy for each file
    const marked = () => {
      const [m] = report.collect(() => graphml.read(path, content));
      for (const line of rules.lines(m, found)) report.say('problem', line);
      return rules.mark(content, found);
    };
    const out = LAYOUTS.map(l => new Output(`-${l}.sbgn`, `SBGN-ML (${l})`, () => sbgnml.write(read(), l)))
      .concat([new Output('-corrected.graphml', 'GraphML (corrected)', () => graphml.corrected(read()))]);
    return out.concat(found.length ? [new Output('-marked.graphml', 'GraphML (marked)', marked, true)] : []);
  }
  if (ext === 'sbgn' || ext === 'nwt') {
    return [new Output('.graphml', 'GraphML', () => graphml.write(sbgnml.read(path, content))),
      new Output('-standard.graphml', 'GraphML (standard sizes)', () => standardised(() => sbgnml.read(path, content), 'Newt', standard))];
  }
  return [];
}

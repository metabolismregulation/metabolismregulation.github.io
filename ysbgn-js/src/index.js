// ysbgn.js: yEd GraphML (SBGN palette) to SBGN-ML and back, in the browser or in Node, with no
// dependencies. A port of the GraphML and SBGN-ML routes of metabolismregulation's map converter
// (map-converter, Python), file for file the same output; upstream/VERSION names the commit.
//   outputs(path, text, standard) -> the files an input gives (Output: ending, label, make, red)
//   made(output) -> [text or null, messages], every message as Python says it (the tests compare them)
//   reported(messages) -> the problems and losses only, what a user needs to know (user, 2026-10-20)
import { made, outputs } from './routes.js';
import * as graphml from './graphml.js';
import * as sbgnml from './sbgnml.js';
import * as rules from './rules.js';
import * as report from './report.js';

export { made, outputs };

// the kinds a user is told: a rule the map breaks, and what the converted file lost (not converted,
// dropped); 'changed', 'warning' and 'summary' are development detail
export const REPORTED = ['problem', 'left out'];
export const reported = messages => messages.filter(([kind]) => REPORTED.includes(kind));

export function toSbgn(path, text, layout = 'advanced') {
  // a yEd GraphML map as SBGN-ML, the elements that break a rule left out: [text, problems and losses]
  const o = outputs(path, text).find(o => o.ending === `-${layout}.sbgn`) || outputs(path, text)[0];
  const [t, said] = made(o);
  return [t, reported(said)];
}

export function toGraphml(path, text, standard = false) {
  // an SBGN-ML or Newt map as yEd GraphML (with standard node sizes when asked): [text, problems and losses]
  const o = outputs(path, text, standard).find(o => o.ending === (standard ? '-standard.graphml' : '.graphml'));
  const [t, said] = made(o);
  return [t, reported(said)];
}

export { graphml, sbgnml, rules, report };

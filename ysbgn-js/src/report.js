// Port of report.py: the converter's messages, one list per conversion, each a kind and a text.
// Kinds: 'left out' (not converted, dropped), 'changed' (moved, joined, written another way),
// 'warning' (converted, worth a look), 'summary' (what a written file holds), 'problem' (a rule
// the map breaks, rules.js). Outside collect() a message is printed, as on the command line.

export const KINDS = ['left out', 'changed', 'warning', 'summary', 'problem'];
let messages = null;

export function say(kind, text) {
  if (!KINDS.includes(kind)) throw new Error('AssertionError: ' + kind);
  if (messages === null) console.log(text);
  else messages.push([kind, text]);
}

export function collect(f, said = []) {
  // f() with the messages said inside it collected (into said): [its result, the messages]
  const outer = messages;
  messages = said;
  try {
    return [f(), said];
  } finally {
    messages = outer;
  }
}

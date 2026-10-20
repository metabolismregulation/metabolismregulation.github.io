// Python's behaviour where JavaScript differs and the output depends on it: float printing
// (repr, %g, %d), round(), sum(), math.hypot and math.dist, string length and whitespace,
// ordering, dicts that keep any key in insertion order, the errors a conversion reports.
// Each function is named after the Python it stands for.

export class PyError extends Error {
  constructor(type, message) { super(message); this.type = type; }
}
export const KeyError = k => new PyError('KeyError', reprStr(String(k)));
export const ValueError = m => new PyError('ValueError', m);
export const ZeroDivisionError = () => new PyError('ZeroDivisionError', 'float division by zero');

// a dict: insertion order for every key (a JavaScript object puts integer-like keys first)
export class Dict extends Map {
  at(k) {  // d[k]
    if (!this.has(k)) throw KeyError(k);
    return this.get(k);
  }
  setdefault(k, v) {
    if (!this.has(k)) this.set(k, v);
    return this.get(k);
  }
}

// --- numbers

const BUF = new DataView(new ArrayBuffer(8));

export function frexp(x) {
  // [m, e] with x = m * 2**e, 0.5 <= |m| < 1 (x finite, not 0)
  BUF.setFloat64(0, x);
  let e = (BUF.getUint16(0) >> 4) & 0x7ff;
  if (e === 0) {  // subnormal
    const [m, k] = frexp(x * 2 ** 64);
    return [m, k - 64];
  }
  e -= 1022;
  BUF.setUint16(0, (BUF.getUint16(0) & 0x800f) | (1022 << 4));
  return [BUF.getFloat64(0), e];
}

function twoProduct(a, b) {
  // hi + lo == a * b exactly (Dekker), as Python's dl_mul
  const hi = a * b, SPLIT = 134217729;
  let t = SPLIT * a;
  const ah = t - (t - a), al = a - ah;
  t = SPLIT * b;
  const bh = t - (t - b), bl = b - bh;
  return [hi, ((ah * bh - hi) + ah * bl + al * bh) + al * bl];
}

function vectorNorm(vec, max, nan) {
  // CPython's vector_norm (Modules/mathmodule.c, 3.12 and later), correctly rounded in practice
  if (max === Infinity) return max;
  if (nan) return NaN;
  if (max === 0 || vec.length <= 1) return max;
  const maxE = frexp(max)[1];
  if (maxE < -1023) {
    const MIN = 2.2250738585072014e-308;
    return MIN * vectorNorm(vec.map(x => x / MIN), max / MIN, nan);
  }
  const scale = 2 ** -maxE;
  let csum = 1.0, frac1 = 0.0, frac2 = 0.0;
  for (let x of vec) {
    x *= scale;
    const [phi, plo] = twoProduct(x, x);
    const hi = csum + phi;
    frac2 += (csum - hi) + phi;
    csum = hi;
    frac1 += plo;
  }
  let h = Math.sqrt(csum - 1.0 + (frac1 + frac2));
  const [phi, plo] = twoProduct(-h, h);
  const hi = csum + phi;
  frac2 += (csum - hi) + phi;
  csum = hi;
  frac1 += plo;
  const x = csum - 1.0 + (frac1 + frac2);
  h += x / (2.0 * h);
  return h / scale;
}

function norm(xs) {
  let max = 0, nan = false;
  const vec = xs.map(x => {
    x = Math.abs(x);
    if (Number.isNaN(x)) nan = true;
    if (x > max) max = x;
    return x;
  });
  return vectorNorm(vec, max, nan);
}

export const hypot = (...xs) => norm(xs);  // math.hypot
export const dist = (p, q) => norm(p.map((v, k) => v - q[k]));  // math.dist

export function sum(xs) {
  // sum() of floats: Neumaier's compensated summation (CPython 3.12 and later)
  let total = 0, c = 0, first = true;
  for (const x of xs) {
    if (first) { total = x === 0 ? 0 : x; first = false; continue; }
    const t = total + x;
    c += Math.abs(total) >= Math.abs(x) ? (total - t) + x : (x - t) + total;
    total = t;
  }
  return c !== 0 && Number.isFinite(c) ? total + c : total;
}

export function round(x) {
  // round(x) to an int, halves to even
  const f = Math.floor(x), d = x - f;
  return d > 0.5 || (d === 0.5 && f % 2 !== 0) ? f + 1 : f;
}

export function div(a, b) {
  // a / b, ZeroDivisionError as Python
  if (b === 0) throw ZeroDivisionError();
  return a / b;
}

export function median(xs) {  // statistics.median
  const s = [...xs].sort((a, b) => a - b), n = s.length;
  if (!n) throw new PyError('StatisticsError', 'no median for empty data');
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

function shortest(x) {
  // the shortest digits that read back as x, and the decimal exponent of the first digit
  const [m, e] = Math.abs(x).toExponential().split('e');
  return [m.replace('.', ''), Number(e)];
}

export function repr(x) {
  // repr(float(x))
  if (Number.isNaN(x)) return 'nan';
  if (!Number.isFinite(x)) return x > 0 ? 'inf' : '-inf';
  if (x === 0) return Object.is(x, -0) ? '-0.0' : '0.0';
  const sign = x < 0 ? '-' : '';
  const [d, e] = shortest(x);
  if (e < -4 || e >= 16) {
    const exp = (e < 0 ? '-' : '+') + String(Math.abs(e)).padStart(2, '0');
    return sign + d[0] + (d.length > 1 ? '.' + d.slice(1) : '') + 'e' + exp;
  }
  if (e < 0) return sign + '0.' + '0'.repeat(-e - 1) + d;
  const int = d.slice(0, e + 1).padEnd(e + 1, '0'), frac = d.slice(e + 1);
  return sign + int + '.' + (frac || '0');
}

export function formatG(x) {
  // '%g' % x
  if (Number.isNaN(x)) return 'nan';
  if (!Number.isFinite(x)) return x > 0 ? 'inf' : '-inf';
  if (x === 0) return Object.is(x, -0) ? '-0' : '0';
  // six significant digits, rounded half to even on the exact value (toExponential rounds halves up)
  const [m, es] = Math.abs(x).toExponential(100).split('e');
  const all = m.replace('.', '');
  let d = all.slice(0, 6), e = Number(es);
  const rest = all.slice(6);
  if (rest[0] > '5' || rest[0] === '5' && (/[1-9]/.test(rest.slice(1)) || d[5] % 2 === 1)) {
    d = String(Number(d) + 1);
    if (d.length > 6) { d = d.slice(0, 6); e += 1; }
  }
  const sign = x < 0 ? '-' : '';
  const trim = s => s.replace(/0+$/, '');
  if (e < -4 || e >= 6) {
    const f = trim(d.slice(1));
    return sign + d[0] + (f ? '.' + f : '') + 'e' + (e < 0 ? '-' : '+') + String(Math.abs(e)).padStart(2, '0');
  }
  if (e < 0) return sign + '0.' + '0'.repeat(-e - 1) + trim(d);
  const f = trim(d.slice(e + 1));
  return sign + d.slice(0, e + 1) + (f ? '.' + f : '');
}

export const formatD = x => String(Math.trunc(x));  // '%d' % x

const FLOAT = /^[+-]?(?:(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?|inf|infinity|nan)$/i;

export function float(s) {
  // float(s) of a string
  const t = strip(s);
  if (!FLOAT.test(t)) throw ValueError('could not convert string to float: ' + reprStr(s));
  const u = t.replace(/_/g, '').toLowerCase();
  if (u.endsWith('nan')) return NaN;
  if (u.endsWith('inf') || u.endsWith('infinity')) return u[0] === '-' ? -Infinity : Infinity;
  return Number(u);
}

export function int(s) {
  // int(s) of a string of digits
  const t = strip(s);
  if (!/^[+-]?\d(_?\d)*$/.test(t)) throw ValueError("invalid literal for int() with base 10: " + reprStr(s));
  return Number(t.replace(/_/g, ''));
}

// --- strings

// Python's whitespace (str.split(), str.strip(), \s in re)
export const WS = '\\t\\n\\v\\f\\r\\x1c-\\x20\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const LEAD = new RegExp('^[' + WS + ']+'), TRAIL = new RegExp('[' + WS + ']+$'), RUN = new RegExp('[' + WS + ']+');

export const strip = s => s.replace(LEAD, '').replace(TRAIL, '');
export const split = s => { const t = strip(s); return t ? t.split(RUN) : []; };  // s.split()
export const len = s => { let n = 0; for (const _ of s) n++; return n; };  // code points, not UTF-16 units

export function cmp(a, b) {
  // Python's order of two values: numbers, booleans, strings by code point, tuples (arrays) item by item
  if (Array.isArray(a)) {
    for (let k = 0; k < Math.min(a.length, b.length); k++) {
      const c = cmp(a[k], b[k]);
      if (c) return c;
    }
    return a.length - b.length;
  }
  if (typeof a === 'string') {
    const x = [...a], y = [...b];
    for (let k = 0; k < Math.min(x.length, y.length); k++) {
      const c = x[k].codePointAt(0) - y[k].codePointAt(0);
      if (c) return c;
    }
    return x.length - y.length;
  }
  return a < b ? -1 : a > b ? 1 : 0;
}

export const sorted = (xs, key = x => x) => [...xs].sort((a, b) => cmp(key(a), key(b)));  // stable, as Python's

export function min(xs, key = x => x) {
  // the first smallest, ValueError on none
  let best, bk, first = true;
  for (const x of xs) {
    const k = key(x);
    if (first || cmp(k, bk) < 0) { best = x; bk = k; first = false; }
  }
  if (first) throw ValueError('min() iterable argument is empty');
  return best;
}

export function max(xs, key = x => x) {
  // the first largest
  let best, bk, first = true;
  for (const x of xs) {
    const k = key(x);
    if (first || cmp(k, bk) > 0) { best = x; bk = k; first = false; }
  }
  if (first) throw ValueError('max() iterable argument is empty');
  return best;
}

export function reprStr(s) {
  // repr(str): single quotes unless the text has one and no double quote
  const q = s.includes("'") && !s.includes('"') ? '"' : "'";
  let out = q;
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (ch === q || ch === '\\') out += '\\' + ch;
    else if (ch === '\n') out += '\\n';
    else if (ch === '\r') out += '\\r';
    else if (ch === '\t') out += '\\t';
    else if (c < 0x20 || c === 0x7f) out += '\\x' + c.toString(16).padStart(2, '0');
    else if (c >= 0x80 && c <= 0xa0 || c === 0xad) out += '\\x' + c.toString(16).padStart(2, '0');
    else out += ch;
  }
  return out + q;
}

export const reprList = xs => '[' + xs.map(reprStr).join(', ') + ']';  // repr of a list of strings

export function jsonDumps(v) {
  // json.dumps(v, ensure_ascii=False): ', ' and ': ' between items
  if (v === null) return 'null';
  if (Array.isArray(v)) return '[' + v.map(jsonDumps).join(', ') + ']';
  if (typeof v === 'object') return '{' + Object.entries(v).map(([k, x]) => jsonStr(k) + ': ' + jsonDumps(x)).join(', ') + '}';
  if (typeof v === 'string') return jsonStr(v);
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : repr(v);
  return String(v);
}

function jsonStr(s) {
  const esc = { '"': '\\"', '\\': '\\\\', '\n': '\\n', '\r': '\\r', '\t': '\\t', '\b': '\\b', '\f': '\\f' };
  return '"' + s.replace(/["\\\x00-\x1f]/g, c => esc[c] || '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')) + '"';
}

// a constant table (a JavaScript object) read with a key from a file: own keys only
export const has = (o, k) => k !== null && k !== undefined && Object.hasOwn(o, k);
export const get = (o, k, d = null) => has(o, k) ? o[k] : d;

export function first(xs) {
  // xs[0], IndexError on an empty list
  if (!xs.length) throw new PyError('IndexError', 'list index out of range');
  return xs[0];
}

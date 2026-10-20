// The part of lxml the converter uses, with lxml's output byte for byte: a parser, elements with
// text and tail, namespaces as libxml2 keeps them (each element points to the declaration it
// uses), ElementPath (find, findall, iter), copying, moving, cleanup_namespaces, and tostring
// with libxml2's pretty printing (an element whose children include text is written as it is).

export const XML_NS = 'http://www.w3.org/XML/1998/namespace';
const XML_DECL = { prefix: 'xml', uri: XML_NS };

const uriOf = tag => tag[0] === '{' ? tag.slice(1, tag.indexOf('}')) : null;
export const localname = tag => tag[0] === '{' ? tag.slice(tag.indexOf('}') + 1) : tag;

export class Node {
  // an element ('element'), comment or processing instruction; text: an element's text before its
  // first child, a comment's or PI's content; tail: the text after the node, up to its next sibling
  constructor(type, tag) {
    this.type = type;
    this.tag = tag;
    this.ns = null;            // the declaration ({prefix, uri}) the element's name uses
    this.attrib = new Map();   // name ('{uri}local' or 'local') -> value, in order
    this.attrNs = new Map();   // name -> declaration, for a namespaced attribute
    this.nsDecls = [];         // the declarations made on this element, in order
    this.text = null;
    this.tail = null;
    this.children = [];
    this.parent = null;
    this.target = null;        // a PI's target
  }

  get(name, d = null) { return this.attrib.has(name) ? this.attrib.get(name) : d; }

  set(name, value) {
    if (name[0] === '{') {
      const uri = uriOf(name);
      this.attrNs.set(name, uri === XML_NS ? XML_DECL : findOrBuild(this, uri, true));
    }
    this.attrib.set(name, String(value));
  }

  del(name) {  // del el.attrib[name]
    if (!this.attrib.has(name)) throw new Error('KeyError: ' + name);
    this.attrib.delete(name);
    this.attrNs.delete(name);
  }

  getparent() { return this.parent; }
  elements() { return this.children.filter(c => c.type === 'element'); }

  *iter(tag = null) {  // this element and its descendants, in document order
    if (this.type === 'element' && (tag === null || tag === this.tag)) yield this;
    for (const c of this.children) if (c.type === 'element') yield* c.iter(tag);
  }

  find(path, ns = {}) { return select(this, path, ns)[0] || null; }
  findall(path, ns = {}) { return select(this, path, ns); }

  append(el) { attach(this, el, this.children.length); }
  extend(els) { for (const e of els) this.append(e); }
  insert(index, el) { attach(this, el, Math.min(index, this.children.length)); }
  addnext(el) { attach(this.parent, el, this.parent.children.indexOf(this) + 1); }
}

// --- namespaces

function inScope(node) {
  // the declarations visible at node, nearest first
  const out = [];
  for (let n = node; n; n = n.parent) out.push(...n.nsDecls);
  return out;
}

function searchByPrefix(node, prefix) {
  if (prefix === 'xml') return XML_DECL;
  return inScope(node).find(d => d.prefix === prefix) || null;
}

function searchByHref(node, uri, attribute = false) {
  // the nearest declaration of uri whose prefix no nearer declaration hides (libxml2's
  // xmlSearchNsByHref; an attribute needs a prefix)
  if (uri === XML_NS) return XML_DECL;
  for (const d of inScope(node))
    if (d.uri === uri && !(attribute && d.prefix === null) && searchByPrefix(node, d.prefix) === d) return d;
  return null;
}

function findOrBuild(node, uri, attribute = false) {
  // lxml's _findOrBuildNodeNs: an existing declaration, else a new one on node, prefix ns0, ns1, ...
  const d = searchByHref(node, uri, attribute);
  if (d) return d;
  let k = 0;
  while (searchByPrefix(node, 'ns' + k)) k++;
  const nd = { prefix: 'ns' + k, uri };
  node.nsDecls.push(nd);
  return nd;
}

function setNs(node, nsmap) {
  // nsmap ([[prefix or null, uri], ...]) declared on node unless the prefix is bound to the uri
  // already; the node's name in the first of them with its uri, else in the nearest declaration
  // of it (lxml's _setNodeNamespaces)
  const uri = uriOf(node.tag);
  let own = null;
  for (const [prefix, href] of nsmap) {
    let d = searchByPrefix(node, prefix);
    if (!d || d.uri !== href) node.nsDecls.push(d = { prefix, uri: href });
    if (href === uri && !own) own = d;
  }
  node.ns = own || (uri === null ? null : findOrBuild(node, uri));
}

function* subtree(n) {
  yield n;
  for (const c of n.children) yield* subtree(c);
}

function remap(root, from, to) {
  for (const n of subtree(root)) {
    if (n.ns === from) n.ns = to;
    for (const [k, d] of n.attrNs) if (d === from) n.attrNs.set(k, to);
  }
}

function attach(parent, el, index) {
  // el moved under parent at index (its tail with it); its declarations that parent's scope
  // already has (by uri) are dropped, as lxml's moveNodeToDocument does
  if (el.parent) el.parent.children.splice(el.parent.children.indexOf(el), 1);
  parent.children.splice(index, 0, el);
  el.parent = parent;
  for (const d of [...el.nsDecls]) {
    const found = searchByHref(parent, d.uri);
    if (found) {
      el.nsDecls.splice(el.nsDecls.indexOf(d), 1);
      remap(el, d, found);
    }
  }
}

// --- making elements

function initAttrib(el, attrib) {
  for (const [k, v] of Object.entries(attrib || {})) el.set(k, v);
}

export function Element(tag, attrib = {}, nsmap = []) {
  // etree.Element(tag, attrib, nsmap): nsmap as [[prefix or null, uri], ...]
  const el = new Node('element', tag);
  setNs(el, nsmap);
  initAttrib(el, attrib);
  return el;
}

export function SubElement(parent, tag, attrib = {}, nsmap = []) {
  const el = new Node('element', tag);
  parent.children.push(el);
  el.parent = parent;
  setNs(el, nsmap);
  initAttrib(el, attrib);
  return el;
}

export function deepcopy(el) {
  // copy.deepcopy(el): a new tree, its tail kept, the declarations it uses from outside (and those
  // of its ancestors) declared on its root, as lxml does
  const decls = new Map();
  const copy = n => {
    const c = new Node(n.type, n.tag);
    c.text = n.text; c.tail = n.tail; c.target = n.target;
    c.nsDecls = n.nsDecls.map(d => { const nd = { ...d }; decls.set(d, nd); return nd; });
    c.attrib = new Map(n.attrib);
    c.children = n.children.map(k => { const kc = copy(k); kc.parent = c; return kc; });
    c.ns = n.ns; c.attrNs = new Map(n.attrNs);
    return c;
  };
  const root = copy(el);
  const outside = new Map();
  for (const d of inScope(el.parent)) {
    if (!root.nsDecls.some(x => x.prefix === d.prefix) && !outside.has(d.prefix)) {
      const nd = { ...d };
      root.nsDecls.push(nd);
      outside.set(d.prefix, nd);
    }
  }
  const map = d => d === null || d === XML_DECL ? d : decls.get(d) || outside.get(d.prefix) || d;
  for (const n of subtree(root)) {
    n.ns = map(n.ns);
    for (const [k, d] of n.attrNs) n.attrNs.set(k, map(d));
  }
  return root;
}

export function cleanupNamespaces(root) {
  // etree.cleanup_namespaces: the declarations no element or attribute uses are dropped
  const used = new Set();
  for (const n of subtree(root)) {
    used.add(n.ns);
    for (const d of n.attrNs.values()) used.add(d);
  }
  for (const n of subtree(root)) n.nsDecls = n.nsDecls.filter(d => used.has(d));
}

// --- ElementPath: tags (prefix:local, {uri}local, *), / and //, predicates [@a="v"] and [tag]

function select(start, path, ns) {
  const qname = t => {
    if (t === '*' || t[0] === '{') return t;
    const k = t.indexOf(':');
    return k < 0 ? t : '{' + ns[t.slice(0, k)] + '}' + t.slice(k + 1);
  };
  // steps and separators; a {uri} holds slashes of its own
  let nodes = [start], deep = path.startsWith('.//');
  const tokens = path.replace(/^\.\/\/?/, '').match(/\/\/?|(?:\{[^}]*\}|[^/{])+/g);
  for (const tok of tokens) {
    if (tok === '/') { deep = false; continue; }
    if (tok === '//') { deep = true; continue; }
    if (tok === '' || tok === '.') continue;
    const m = tok.match(/^([^[]+)((?:\[[^\]]*\])*)$/);
    const tag = qname(m[1]);
    const preds = [...m[2].matchAll(/\[([^\]]*)\]/g)].map(p => p[1]);
    const ok = el => (tag === '*' || el.tag === tag) && preds.every(p => {
      const a = p.match(/^@([^=]+)=["'](.*)["']$/);
      if (a) return el.get(qname(a[1])) === a[2];
      const t = qname(p);
      return el.elements().some(c => c.tag === t);
    });
    const next = [], seen = new Set();
    for (const n of nodes) {
      const pool = deep ? [...n.iter()].slice(1) : n.elements();
      for (const el of pool) if (ok(el) && !seen.has(el)) { seen.add(el); next.push(el); }
    }
    nodes = next;
    deep = false;
  }
  return nodes;
}

// --- parsing

const ENT = { lt: '<', gt: '>', amp: '&', quot: '"', apos: "'" };

function unescape(s, where) {
  // where: () -> where in the text, for the error
  if (!s.includes('&')) return s;
  return s.replace(/&(#x[0-9a-fA-F]+|#[0-9]+|\w+);/g, (m, e) => {
    if (e[0] === '#') return String.fromCodePoint(e[1] === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
    if (e in ENT) return ENT[e];
    throw new Error('XMLSyntaxError: Entity \'' + e + '\' not defined' + where());
  });
}

export function parse(text) {
  // etree.parse(...).getroot() of an XML text; the comments and PIs around the root in .before, .after
  text = text.replace(/^﻿/, '').replace(/\r\n?/g, '\n');
  let i = 0, root = null, cur = null, last = null;
  const before = [], after = [];
  const where = () => ', line ' + (text.slice(0, i).split('\n').length);
  const addText = s => {
    if (!cur) return;
    if (last) last.tail = (last.tail || '') + s;
    else cur.text = (cur.text || '') + s;
  };
  const addNode = n => {
    if (cur) { n.parent = cur; cur.children.push(n); last = n; }
    else (root ? after : before).push(n);
  };
  const pending = [];  // [element, raw prefix, [[raw name, value]]] until its declarations are known
  while (i < text.length) {
    const lt = text.indexOf('<', i);
    if (lt < 0) { addText(unescape(text.slice(i), where)); break; }
    if (lt > i) addText(unescape(text.slice(i, lt), where));
    i = lt;
    if (text.startsWith('<!--', i)) {
      const e = text.indexOf('-->', i);
      const c = new Node('comment', null); c.text = text.slice(i + 4, e);
      addNode(c); i = e + 3;
    } else if (text.startsWith('<![CDATA[', i)) {
      const e = text.indexOf(']]>', i);
      addText(text.slice(i + 9, e)); i = e + 3;
    } else if (text.startsWith('<?', i)) {
      const e = text.indexOf('?>', i);
      const body = text.slice(i + 2, e);
      const m = body.match(/^(\S+)\s*([\s\S]*)$/);
      if (m[1] !== 'xml') {
        const p = new Node('pi', null); p.target = m[1]; p.text = m[2];
        addNode(p);
      }
      i = e + 2;
    } else if (text.startsWith('<!DOCTYPE', i)) {
      let depth = 0, k = i;
      for (; k < text.length; k++) {
        if (text[k] === '[') depth++;
        else if (text[k] === ']') depth--;
        else if (text[k] === '>' && depth === 0) break;
      }
      i = k + 1;
    } else if (text[i + 1] === '/') {
      const e = text.indexOf('>', i);
      last = cur; cur = cur.parent; i = e + 1;
      if (!cur) last = null;
    } else {
      const m = /^<([^\s/>]+)/.exec(text.slice(i, i + 300));
      i += m[0].length;
      const attrs = [];
      const re = /\s*([^\s=/>]+)\s*=\s*("([^"]*)"|'([^']*)')|\s*(\/?>)/y;
      let end;
      for (;;) {
        re.lastIndex = i;
        const a = re.exec(text);
        if (!a) throw new Error('XMLSyntaxError: bad tag' + where());
        i = re.lastIndex;
        if (a[5]) { end = a[5]; break; }
        // attribute values: literal tabs and newlines become spaces, references are kept
        const raw = (a[3] ?? a[4]).replace(/[\t\n]/g, ' ');
        attrs.push([a[1], unescape(raw, where)]);
      }
      const el = new Node('element', m[1]);
      for (const [n, v] of attrs) {
        if (n === 'xmlns') el.nsDecls.push({ prefix: null, uri: v });
        else if (n.startsWith('xmlns:')) el.nsDecls.push({ prefix: n.slice(6), uri: v });
      }
      if (cur) addNode(el);
      else root = el;
      // the name and attributes in their namespaces
      const resolve = (qn, attribute) => {
        const k = qn.indexOf(':');
        const prefix = k < 0 ? null : qn.slice(0, k);
        if (attribute && prefix === null) return [qn, null];
        const d = searchByPrefix(el, prefix);
        if (!d) {
          if (prefix === null) return [qn, null];
          throw new Error('XMLSyntaxError: Namespace prefix ' + prefix + ' not defined' + where());
        }
        return ['{' + d.uri + '}' + (k < 0 ? qn : qn.slice(k + 1)), d];
      };
      [el.tag, el.ns] = resolve(m[1], false);
      for (const [n, v] of attrs) {
        if (n === 'xmlns' || n.startsWith('xmlns:')) continue;
        const [name, d] = resolve(n, true);
        el.attrib.set(name, v);
        if (d) el.attrNs.set(name, d);
      }
      if (end === '>') { cur = el; last = null; }
      else { last = el; }
    }
  }
  root.before = before;
  root.after = after;
  return root;
}

// --- writing (lxml's tostring, encoding UTF-8 with the XML declaration)

const escText = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\r/g, '&#13;');
const escAttr = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
  .replace(/\n/g, '&#10;').replace(/\r/g, '&#13;').replace(/\t/g, '&#9;');

const qn = (d, local) => d && d.prefix ? d.prefix + ':' + local : local;

function write(n, out, level, format) {
  // libxml2's xmlNodeDumpOutput: with format, each child on its own line, indented two spaces a
  // level, unless an element's children include text (then that element is written as it is)
  const indent = () => { if (format) out.push('  '.repeat(Math.min(level, 30))); };
  if (n.type === 'comment') { indent(); out.push('<!--' + n.text + '-->'); return; }
  if (n.type === 'pi') { indent(); out.push('<?' + n.target + (n.text ? ' ' + n.text : '') + '?>'); return; }
  indent();
  let s = '<' + qn(n.ns, localname(n.tag));
  for (const d of n.nsDecls) s += ' xmlns' + (d.prefix ? ':' + d.prefix : '') + '="' + escAttr(d.uri) + '"';
  for (const [k, v] of n.attrib) s += ' ' + qn(n.attrNs.get(k) || null, localname(k)) + '="' + escAttr(v) + '"';
  const hasText = n.text !== null || n.children.some(c => c.tail !== null);
  if (!n.children.length && n.text === null) { out.push(s + '/>'); return; }
  const inner = format && !hasText;
  out.push(s + '>');
  if (inner) out.push('\n');
  if (n.text !== null) out.push(escText(n.text));
  for (const c of n.children) {
    write(c, out, level + 1, inner);
    if (c.tail !== null) out.push(escText(c.tail));
    if (inner) out.push('\n');
  }
  if (inner) indent();
  out.push('</' + qn(n.ns, localname(n.tag)) + '>');
}

export function tostring(root, pretty = false) {
  // etree.tostring(root or its tree, pretty_print=pretty, xml_declaration=True, encoding='UTF-8')
  const out = ["<?xml version='1.0' encoding='UTF-8'?>\n"];
  const sep = pretty ? '\n' : '';
  for (const n of root.before || []) { write(n, out, 0, false); out.push(sep); }
  write(root, out, 0, pretty);
  for (const n of root.after || []) { out.push(sep); write(n, out, 0, false); }
  if (pretty) out.push('\n');
  return out.join('');
}

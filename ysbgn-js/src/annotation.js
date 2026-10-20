// Port of annotation.py. MIRIAM annotation of a map's labels: label -> [family, [urn]]. A family
// is written as bqbiol:hasVersion, one entity as bqbiol:is.
// Read from the GraphML's node properties as annotate.py writes them (HGNC symbol, HGNC,
// UniProt, ChEBI; Member annotation for a family). A map without them (not annotated):
// from the node links to ChEBI and UniProt.
import { Dict, jsonDumps, split } from './py.js';

const LINK = [[/chebiId=(CHEBI:\p{Nd}+)/u, x => ['urn:miriam:obo.chebi:' + x.replace(/:/g, '%3A')]],
  [/uniprot(?:kb)?\/([\p{L}\p{N}_]+)/u, x => ['urn:miriam:uniprot:' + x]]];

function miriam(p) {
  // the URNs of one entity's properties
  if (p.get('ChEBI')) return ['urn:miriam:obo.chebi:' + p.get('ChEBI').replace(/:/g, '%3A')];  // CellDesigner drops other ChEBI forms when it saves
  const out = p.get('HGNC symbol') ? ['urn:miriam:hgnc.symbol:' + p.get('HGNC symbol')] : [];  // CellDesigner: UniProt alone
  if (p.get('HGNC')) out.push('urn:miriam:hgnc:' + p.get('HGNC').replace(/HGNC:/g, ''));
  if (p.get('UniProt')) out.push('urn:miriam:uniprot:' + p.get('UniProt'));
  return out;
}

export function from_graphml(diagram) {
  const out = new Dict();
  const ds = [...diagram.nodes.values()];
  const links = !ds.some(d => ['ChEBI', 'HGNC symbol', 'Member annotation'].some(k => d.data.get(k)));
  for (const d of ds) {
    const lab = d.labels.length ? split(d.labels[0]).join(' ') : '';
    if (!lab || out.has(lab)) continue;
    const p = d.data;
    if (p.get('Member annotation')) {
      out.set(lab, [true, JSON.parse(p.get('Member annotation')).flatMap(m => miriam(new Dict(m.props)))]);
    } else if (p.get('ChEBI') || p.get('HGNC symbol')) {
      out.set(lab, [false, miriam(p)]);
    } else if (links) {
      for (const [pat, urns] of LINK) {
        const hit = (p.get('url') || '').match(pat);
        if (hit) { out.set(lab, [false, urns(hit[1])]); break; }
      }
    }
  }
  return out;
}

export function to_properties(family, uris) {
  // inverse of miriam(): node properties from an entity's URNs; a family's URNs are its
  // members' one after another, each starting with an HGNC symbol or a ChEBI id
  const members = [];
  const KEY = { 'urn:miriam:hgnc.symbol': 'HGNC symbol', 'urn:miriam:hgnc': 'HGNC', 'urn:miriam:uniprot': 'UniProt',
    'urn:miriam:obo.chebi': 'ChEBI' };
  for (const u of uris) {
    const c = u.lastIndexOf(':');
    const db = c < 0 ? '' : u.slice(0, c), x = u.slice(c + 1);
    if (db === 'urn:miriam:hgnc.symbol' || db === 'urn:miriam:obo.chebi' || !members.length) members.push(new Dict());
    const k = Object.hasOwn(KEY, db) ? KEY[db] : null;
    if (k) members[members.length - 1].set(k, k === 'HGNC' ? 'HGNC:' + x : x.replace(/%3A/g, ':'));
  }
  if (!family) return members.length ? members[0] : new Dict();
  const order = ['HGNC', 'HGNC symbol', 'UniProt', 'ChEBI'];  // as annotate.py lists them
  return new Dict([
    ['Members', members.map(m => m.get('HGNC symbol') ?? m.get('ChEBI') ?? '').join('; ')],
    ['Member annotation', jsonDumps(members.map(m => ({ symbol: m.get('HGNC symbol') ?? '',
      props: order.filter(k => m.has(k)).map(k => [k, m.get(k)]) })))]]);
}

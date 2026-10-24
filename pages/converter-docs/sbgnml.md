---
layout: converter-docs
title: "GraphML -> SBGN-ML"
permalink: /converter/docs/sbgnml/
sitemap: false
noindex: true
---
{% raw %}

`mapconv/sbgnml.py` writes a map as SBGN-ML 0.3 (Bergmann et al. 2020, J Integr Bioinform
17:20200016, doi:10.1515/jib-2020-0016), the exchange format Newt, MINERVA, CellDesigner and
cd2sbgnml read. First direction (user, 2026-10-17): from yEd GraphML; then the way back.

    python3 -m mapconv <map.graphml> <out.sbgn>
    python3 -m mapconv <map.sbgn|map.nwt> <out.graphml|out.xml> [--standard]   (also <out>-standard.graphml for a map at another scale, or always with --standard)

## Rules

- Glyphs: our yEd glyphs by name (`CLASS`); a multimer (yEd's mcount) is `<class> multimer`,
  its N:x a unit of information; EmptySet is `source and sink`; a gate is `and`, `or`, `not`
  from its label; an arc leaving a phenotype is left out, the phenotype kept (see the way back).
- Complex members are child glyphs of the complex. An entity in a compartment gets its
  `compartmentRef` (the nearest compartment around it); compartments come first, drawn under
  the rest. A compartment's label keeps its place (label bbox from the yEd label).
- State variables: `P@S455` is value `P`, variable `S455` (the spec's own example: P@T286),
  placed where yEd has the icon. Units of information along the top edge, as the GraphML writer.
- Processes and gates get the two ports the spec asks for (2.10), on the line from the inputs
  (consumptions, gate inputs) to the outputs, one process width from the centre; the
  orientation follows. A reversible process (no consumption) sends each product out by the
  nearer port.
- Arcs in SBGN's direction: a consumption from the entity to port 1 (yEd maps also draw it
  from the process), a logic arc from the entity into its gate, products from port 2, a
  modifier to the process glyph. `trigger` is `necessary stimulation`. Bends are `next`
  points; an end at a port is the port, a yEd port is its own point, any other end is where
  the line meets the node's box.
- A bend on or near (5 px) the straight line between its neighbours is left out: it draws nothing
  (user, 2026-10-18).
- Two layouts, as for CellDesigner (user, 2026-10-18): `straight`, every arc straight from centre
  to centre (no bends, no yEd ports, no process ports), simple and reliable, improved by hand in
  Newt; `advanced`, the drawing of the source kept, except the arcs of logic gates, straight in both (user,
  2026-10-18: yEd's bend where the inputs meet lies past the gate's port). From CellDesigner, straight puts each process midway between
  its main reactant and product (`celldesigner.straight`: in CellDesigner the bends placed the
  process glyph), the gates where CellDesigner has them; advanced reads CellDesigner's own geometry
  (`celldesigner.read(path)`).
- Key bends only (user, 2026-10-18): a bend stays if leaving it out moves the line by more than
  20 px (`layout.bends`, as for CellDesigner), or the line without it runs through a node it does not
  run through now; then those within 5 px of the line through their neighbours go. Straight: an
  arc that shares its two ends with another keeps its bends (two straight arcs between the same
  glyphs would lie on each other; Newt curves them apart).
- A CellDesigner homodimer gets its N:x unit, N:2 included, as on every multimer of our yEd maps
  (user, 2026-10-18; found by comparing CellDesigner -> SBGN-ML with GraphML -> SBGN-ML of the
  same map). It goes into the GraphML from CellDesigner too.
- The map is moved to start at (20, 20): SBGN-ML's origin is the top left corner.
- Colours: the SBML render extension on the map (the spec's Appendix B), one colour
  definition and style per fill.
- Annotation: RDF in each glyph's extension, `bqbiol:is` (a family: `bqbiol:hasVersion`),
  identifiers.org links in Newt's form (`http://identifiers.org/uniprot:P53396`, `CHEBI:16947`,
  `hgnc:115`, `hgnc.symbol:ACLY`), from the same annotation as the CellDesigner writer.
- The map has `language="process description"`, not `version`: libsbgn's schema lists no PD
  version after 1.3.

### For Newt

Each SBGN-ML file also comes adjusted for Newt (user, 2026-10-21: "SBGN-ML (for Newt)",
`<map>-newt.sbgn`; `-straight-newt.sbgn`; `--newt`; the Converter's Newt buttons open these), made
by the Newt adapter `newt_layout.py`: `sbgnml.write(..., newt=True)` runs `adjust` on the map and
draws the arcs as Newt aims them. The plain file is the SBGN-ML of the source, its compartments
as drawn: Newt draws a compartment about 12 px larger on every side than its bbox (its compound
padding), so compartments that touch or stand close in yEd overlap there (estrogen).
- Arc ends: Newt draws only the bends and aims each end at the node's centre (sbgnviz): an end
  at a yEd port off the line to the centre (more than 5 px apart on the border) gets a bend 3 px
  outside the node where yEd's line leaves it, so the line keeps its course (user, eNOS: lines
  level with the process at a complex's side; `leaving`). Not at a process or gate (Newt aims at
  their ports). On the border itself Newt loses the arc.
- A bend within 5 px of the line from where Newt aims the ends (a port, else the node's centre)
  is left out too: Newt loses an arc with two bends in one place (user, 2026-10-18, iNOS: the IRF1
  mRNA arcs; `unaimed`).
- Processes and gates outside every compartment carry the compartment their centre lies in, else
  their first neighbour's, as Newt does (Newt otherwise puts them in a neighbour's and grows it
  over the others; `placed`).
- Compartments as Newt keeps them (user, 2026-10-18, `for_newt`): Newt keeps a compartment's box
  only when what it draws inside stays its padding inside every edge (24: the compartment's 14 and
  the compound 10, with half a border; 30 to be safe), counting state variables and units at their
  size and a process or gate with its ports (12 px more; sbgnml-to-cytoscape `bboxProp`,
  `calculateElementPadding`). Measured in Newt (2026-10-22, QUALITY.md): a complex needs no more
  than a node (until then 20 px more), a process without ports none (until then 5), and Newt never
  grows a compartment for a compartment inside it (until then 56 px kept around it). Otherwise it wraps the
  contents in that direction, and edges aligned in the source drift apart or overlap. Each box is
  widened as its contents need, and edges aligned in the source (within 2 px) move together. Where
  two neighbours' contents are too close across their shared edge, everything past that edge
  (compartments, their contents, bends) moves on by what is missing, so the edges stay aligned
  (printed). Compartments side by side (neither around the other) keep the gap they have in the
  source, up to 30 px, the same way (user, 2026-10-19, eicosanoids platelet: CYTOSOL and DENSE
  TUBULAR SYSTEM 2.7 px apart in yEd, too far for one edge, and CYTOSOL grew into its neighbour). Processes are placed (above)
  before the boxes are fitted. A node outside every compartment that a
  compartment, once in place, grows over by more than half is covered whole, with the padding, so the
  edge does not stop inside it; one the growth only grazes, or the source draws across the edge,
  stays as it is (user, 2026-10-20: SREBP straight, the COPII vesicle grew to its process and its edge
  cut the Sec23:Sec24 complex; advanced covered it by its larger process margin). Checked by loading every map in Newt and
  comparing its compartments with the file's.

## The way back: SBGN-ML -> map model

`sbgnml.read` reads SBGN-ML and Newt's .nwt (SBGN-ML with Newt's settings in
`nwt:mapProperties`, ignored) into the map model; `graphml.write` or `celldesigner.write`
then write it. Examples: our own SBGN-ML of every test map, and files saved by Newt
(`tests/external/newt/pd/`).

- Glyphs back by class (`KIND`, the inverse of `CLASS`); `source and sink` is yEd's EmptySet;
  a multimer gets count N from its N:x unit, else 2; a gate keeps AND, OR, NOT as its label.
- Parents: a complex's child glyphs; else `compartmentRef`.
- State variables: value and variable back to `P@S455`, placed by the centre of their bbox.
- Colours from the render extension (a colour id or the value itself; MINERVA writes the value).
- Annotation: `bqbiol:is` (one entity) and `bqbiol:hasVersion` (a family) from identifiers.org
  links (db:id, the older db/id) or MIRIAM URNs, into the node properties `annotation.py` reads.
- Arcs: ports back to their glyph, bends from `next` points; the ends at the centres (ports
  0, 0, our yEd convention); `necessary stimulation` is `trigger`.
- Left out and printed: what our maps do not draw (tag and equivalence arc, annotation
  glyphs, clone markers), and arcs of other classes. Association and dissociation are read as the
  generic process (MINERVA, Newt).
- Perturbing agent and phenotype (user, 2026-10-17): our maps have one glyph for both, the
  phenotype, as CellDesigner has (PHENOTYPE), which also stands for a submap. A perturbing agent is
  read as a phenotype, and so is yEd's Submap glyph (user, 2026-10-21: SREBP's "Transcription of target
  genes" and "Cholesterol biosynthesis", submaps in SBGN-ML before; the palette offers the glyph, the
  map means a phenotype). Written to SBGN-ML, an arc leaving a phenotype is left out and printed: an
  SBGN phenotype takes no outgoing arc, and whether it is a perturbing agent, a submap or neither is
  not guessed (user, 2026-10-17). The phenotype stays, with the arcs into it (user, 2026-10-20: SREBP
  from CellDesigner lost "Transcription of target genes" and SREBP2's stimulation of it; until then
  the phenotype went with all its arcs).

### Activity Flow (read only, user 2026-10-17)

SBGN AF Level 1 Version 1.2 (Mi et al. 2015, doi:10.1515/jib-2015-265; copy in maps-workbench
`notes/activity-flow/`). An activity is drawn as the entity it comes from, CellDesigner's way: its
unit of information's shape gives the glyph (macromolecule, nucleic acid feature, simple chemical,
unspecified entity, complex; perturbation as a phenotype, as in CellDesigner; no unit: a protein), the
unit's label (the molecule's name) stays a unit of information. Positive, negative and unknown influence
become stimulation, inhibition and modulation between entities; necessary stimulation, logic arcs,
AND, OR, NOT, phenotype and compartments as in PD. A delay is a yEd Operator labelled τ, drawn as the
equivalence operator (user's file `tests/yed/delay.graphml`, 2026-10-17): one plain line in, one arc out (an
influence). CellDesigner and SBGN PD have no delay: there its input is joined to its target with the type of
the arc out of it (`graphml.without_delays`). A submap is a phenotype with its name (user, 2026-10-17); its
terminals and tags are left out (named on the console). An equivalence arc is a plain line, yEd's
consumption arc (user, 2026-10-17); one to a submap terminal joins the activity to the submap's phenotype,
one to a tag is left out with the tag. Onwards (CellDesigner, SBGN PD) the check marks it red: no form there.
No Activity Flow output. Test: `tests/external/newt/af/` (Newt's TGF-beta map).

Hybrid PD-AF maps (Newt's `hybrid pd-af`, `hybrid sbgn`; user, 2026-10-19): an activity joined to a
PD entity by a performance arc is that entity, as in CellDesigner's reduced notation (one node for the
molecule and its activity): the activity box goes, its arcs start or end at the entity, straight, and a
message names both. An activity with two performance arcs is kept, its performance arcs left out (which
entity it stands for is not guessed). The rest of a hybrid map is read as PD: activities as above,
submaps as submaps. Tests: Newt's EGFR-PI3K/AKT-MAPK and insulin receptor samples in
`tests/external/newt/repository/`.

Activity labels (AF and hybrid; user, 2026-10-19): "activity" at the end of an activity's label goes
("SHC activity" is SHC), since the node is the molecule; a message lists them.

### Equivalence operator (PD 2.9.4)

yEd's SBGN palette draws it as an Operator labelled ≡ (Monospaced 18; the user's file
`tests/yed/equivalence-operator.graphml`), the members joined to it by plain lines, one plain line
drawn from it to the generic entity. SBGN-ML: class `equivalence`, logic arcs in and one out, no label.
CellDesigner has no equivalence: left out there, with a message, the entities kept.

## Checks

`python3 -m unittest` converts every map in `tests/maps/` to its `expected.sbgn`, reads it
back to the same meaning (`mapconv.check`), and validates it against libsbgn's schema (`tests/sbgnml/`, libsbgn commit 2aae05b, LGPL 2.1 or
Apache 2.0). libsbgn's semantic rules for PD (`validation/rules/sbgn_pd.sch`, XSLT 2) run
with Java and its Saxon jar:

    java -cp saxon9he.jar net.sf.saxon.Transform -s:sbgn_pd.sch -xsl:iso_schematron_message_xslt2.xsl -o:pd.xsl allow-foreign=true
    java -cp saxon9he.jar net.sf.saxon.Transform -s:<map>.sbgn -xsl:pd.xsl

(`iso_schematron_message_xslt2.xsl` is inside libsbgn's `validation/lib/ant-schematron.jar`.)
On the test maps of 2026-10-17 they find the maps' own departures from SBGN PD, not
conversion errors: entities outside every compartment on a map that has compartments
(carnitine, glutaminase, eicosanoids, urea cycle, SREBP, BCAA SLC25A44, nNOS Ca2+), and
SREBP's stimulation arcs to and between submaps (reduced notation).

The user checks the files in Newt on the website's hidden page /converter/sbgn/
(https://metabolismregulation.github.io/converter/sbgn/; links to Newt, ours next to MINERVA's
export; no SBGN-ML files to download, user 2026-10-17), and the way back there as GraphML for yEd.
`tests/external/newt/pd/` also holds the samples as Newt saves them in CellDesigner and GPML, for later. After a change
that is for the user to check: `sh tools/sbgn_test.sh <website repository>` and push the
website to master.

## Notes (user, 2026-10-22)

A glyph's `<notes>` (XHTML body) carries the family name and the members' sites, the same lines as in
CellDesigner (docs/CELLDESIGNER.md, Notes); read back into Family and Member annotation.
An arc drawn dashed (CellDesigner's unknown catalysis, inhibition and the other unknown types; SBGN PD has
no unknown arc) carries the note "Unknown (a dashed arc)" and is read back dashed (user, 2026-10-22).

## Compared with momapy and SBGN PD 2.1 (2026-10-22)

What our biology model (model.py) records was compared with momapy 0.16.1 (A. Rougny; `sbgn/pd/model.py`,
`celldesigner/model.py`) and with SBGN PD Level 1 Version 2.1 (Balci, Rougny et al. 2026,
doi:10.1515/jib-2025-0018; source github.com/sbgn/process-descriptions, commit 1558ba5). Kept for when
it is needed:
- Recorded as momapy does: names, state variables with sites, units of information, annotations
  (qualifier, resource), complex members with their own states, multimer count, family and members,
  logic gates, equivalence, source and sink, reversible processes, nested compartments.
- Not recorded, by decision (user, 2026-10-22): stoichiometry (momapy's FluxRole.stoichiometry, SBGN's
  cardinality; arc labels such as 2 O2 in eNOS, not read), the kind of process (omitted, uncertain;
  read and written, not compared). Dashed arcs recorded and compared since this date.
- In momapy, not on our maps: CellDesigner protein types (receptor, ion channel, truncated), gene and
  RNA regions, CellDesigner reaction types (transport, transcription, translation, heterodimer
  association, truncation), units of information on compartments, tags and terminals.
- SBGN PD 2.1 (changes from 2.0: wording of must and should, a state variable with only a name, a unit
  of information rule, connectivity table, empty set without clone marker): duplicated entity pool
  nodes are allowed only with a clone marker (Duplication rules), which our SBGN-ML does not write
  (287 entities drawn more than once on the 28 reference GraphML maps; not needed, user 2026-10-22: tools
  add them automatically, and if the converter ever writes them, it does so automatically, never as an
  option); the rule that a state variable
  on one EPN is on all its equivalent EPNs holds on all 28 maps.

{% endraw %}

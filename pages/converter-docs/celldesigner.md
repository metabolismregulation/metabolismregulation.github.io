---
layout: converter-docs
title: "CellDesigner files: conventions"
permalink: /converter/docs/celldesigner/
sitemap: false
noindex: true
---
{% raw %}

Moved from `maps-workbench/tools/CELLDESIGNER.md` (2026-10-16). Paths below are those of
the workbench at the time. Here the converter is `mapconv/graphml.py` (reader), `model.py`
and `celldesigner.py` (writer), and the symbol sheet is `docs/components44-overview.png`.

Removed 2026-10-13 (user: only efficient and elegant code): the side connection point
mode (`CENTRE=0`, yEd port offsets, the 16-point snapping), the `--bends`
mode (yEd bends as edit points, port detection, coordinate frames for main
lines and modifiers), the antenna for twin processes and the `TWIN` switch.
The sections below that mention them are history. The last version with
them: commit `2516243` (`git show 2516243:tools/to_celldesigner.py`). Output of the
current defaults unchanged (all 18 maps byte-identical).

What `tools/to_celldesigner.py` follows, learned from the 19 CellDesigner
files on the website (2026-10-13), the user's CellDesigner 4.4.2 check of
the eicosanoids pilot, and calibration through MINERVA's converter.

## When a convention is unclear

Do not guess. Ask the user to draw a small test diagram of the case in
CellDesigner and upload the saved file (it goes into the map's `sources/`);
read the convention from it. Checks through MINERVA's converter are fine for
geometry, but CellDesigner's own file is the reference.

## Versions

Every CellDesigner file that goes to the user carries a version:
`<map>/celldesigner/<map>-vNN.xml` (v01, v02, ...). The user checks every
file in CellDesigner; that is the check. MINERVA's converter is only a tool
for working out geometry (absolute positions from SBGN-ML); do not report
MINERVA results to the user and do not make MINERVA renders for new
versions (older `-minerva.png` files stay). Files the user returns keep the version they
were made from in their name (`sources/<map>-vNN-cd442-....xml`). The map
README has a table of the versions and what changed.

## Round trip

Goal (user, 2026-10-13): CellDesigner opens the file without warnings and
saves it without dropping anything. Small numeric differences after a save
(e.g. last-digit rounding of modifier edit points, glycolysis v05) do not
matter: do not chase them. A diff with a returned file is for finding real
changes (dropped or rewritten content, moved elements).

The converter writes the file the way CellDesigner 4.4.2 saves it (numbers
with .0, the full set of RDF namespaces, no indentation, double-quoted XML
declaration). Eicosanoids v03 is byte-identical to v02 opened and saved in
CellDesigner, so `diff` against a returned file shows only real changes.

## Annotation (MIRIAM, in the species' `<annotation>` after the extension)

- One entity: `bqbiol:is`. A family (one node, several genes): `bqbiol:hasVersion`
  listing every member. All 19 old files keep this rule (678 `is`, 1198
  `hasVersion` entries; never `is` with several proteins or `hasVersion`
  with one).
- Proteins: `urn:miriam:hgnc.symbol:X` and `urn:miriam:uniprot:Y`, in member
  pairs. The old files have no HGNC numeric ID; the converter adds
  `urn:miriam:hgnc:N` (CellDesigner keeps it).
- Metabolites: `urn:miriam:obo.chebi:CHEBI%3A12345`. Other forms are dropped
  by CellDesigner on saving, without a message.
- References on a reaction: `bqmodel:isDescribedBy` with
  `urn:miriam:pubmed:N` in the reaction's annotation (F021 has three).
- Species inside a complex (`listOfIncludedSpecies` in the model extension)
  carry their MIRIAM RDF inside `celldesigner:notes/html/body`, not in an
  annotation element: CellDesigner's own convention for included species.
- Model `<notes>`: some old files hold conversion warnings ("Invalid element
  id", "requires thickness to be at least 2.5"). Leave model notes empty.

## Required for a clean open in CellDesigner 4.4.2

- The five unit definitions (substance, volume, area, length, time) and
  `units="volume"` on the compartments; without them a warning on opening.
- Compartment double line thickness at least 2.5.

## Geometry (checked through MINERVA)

- Residue angle: runs linearly along the box border; 0 east, pi/4 north-east
  corner, pi/2 north, pi west, 3pi/2 south. Sites without a value need
  `state="empty"`, else they are not drawn.
- Reaction edit points: frame with origin = reactant connection point, x axis =
  product connection point - reactant connection point, y axis = x axis turned 90 degrees (screen
  coordinates). The process glyph sits mid-segment `rectangleIndex`.
- Modifier `targetLineIndex="-1,2"` = left of the reaction flow, `-1,3` =
  right (side middles); `-1,4`/`-1,5` the left corners, upstream/downstream, `-1,6`/`-1,7`
  the right ones (MINERVA's `getAnchorPointOnReactionRect`; confirmed by MINERVA's SBGN-ML of
  the user's PDH edit, which uses 6 and 7).
- Modifier edit points: attribute `editPoints="u,v ..."` on the
  `modification` element, one `lineDirection` per segment. Frame: origin =
  the modifier's connection point, x axis = to the arc's end on the process
  glyph's side (process glyph 10 wide: centre +- 5 across the flow), y axis = x
  axis turned 90 degrees. Found from the user's bends in glycolysis v01 and
  MINERVA's SBGN-ML (match to 1e-7).
- Multimers: lines attach to the front shape, the box 6 smaller in width and
  height per unit beyond 1. Confirmed for N:4 by the user's ASL edit (iNOS,
  `F007-inos/sources/F007-inos-asl-tetramer-cd442-edited.xml`): homodimer
  2 -> 4 made CellDesigner grow the box 80x40 -> 92x52, top left kept, so
  the front shape stays 74x34.
- Antenna (two edit points around the process glyph, `rectangleIndex="1"`): only
  where two processes join the same species, so the two reactions do not
  fall on one line; otherwise a straight line with the process glyph midway
  (`rectangleIndex="0"`). User's rule (glycolysis, 2026-10-13).
- Bends on extra reactant/product links: not needed (user, 2026-10-13).
- Metabolites: 40x40 circles, centre kept (36x36 until 2026-10-23, user).

## Complexes, multimers, bound ligands (in the converter since glycolysis v01)

Taken from F012-camp, a file saved by CellDesigner, and checked through
MINERVA (glycolysis v01).

- Complex: `complexSpeciesAlias` in `listOfComplexSpeciesAliases`, with
  `backupSize w="0.0" h="0.0"` and `backupView state="none"` after `view`;
  brief view `singleLine` width = box width. The complex species (class
  COMPLEX) is in `listOfSpecies` with a name (members joined by `:` when the
  yEd complex has no label; CellDesigner draws it at the bottom of the box).
- Members: `speciesAlias` with `complexSpeciesAlias="<complex alias>"`, usual
  view `innerPosition` = offset from the complex's top left corner. The
  species go into `listOfIncludedSpecies` (`celldesigner:species`, MIRIAM RDF
  in `celldesigner:notes/html/body`, `celldesigner:annotation` with
  `complexSpecies` and `speciesIdentity`), not into the SBML species list.
- Multimers: `<celldesigner:homodimer>` first in `state`; the count from the yEd N:x unit of
  information (an icon, or a second boxed label as iNOS ASL "N:4"); yEd's `mcount` is only the number of
  shapes drawn (always 2), used only when there is no N:x. Until 2026-10-13 the converter took `mcount`:
  NOSTRIN N:3, HMGCR and ACAT2 N:4, ASL N:4 came out as 2. Since 2026-10-24 (user, the SBGN way) every
  multimer is written as homodimer 2 at the yEd size, and a count beyond 2 as the unit
  `<celldesigner:info state="open" prefix="N" label="3"/>` (after a ct: unit, before other free text; one info
  per alias), so a tetramer does not grow 18 px and reach its neighbours. The form is AsthmaMap's
  (PD01 Mast Cell: N:4 and N:3 on homodimer 2), shown as "N:3"; free input would add "free input:" in
  MINERVA (user, 2026-10-24: not that). The reader takes N:x on a dimer
  as its count; a file with homodimer 3 or more (CellDesigner's own, the box grown 6 per unit) is read as
  before. MINERVA draws N:x at the top middle: keep it free; state
  variables go on the sides (lower half) or at the corners (user's rule).
  The converter warns when a residue of a multimer sits there (none in the
  current maps).
- Bound ligands (yEd state variable "cAMP"): one `structuralState` per
  species (`listOfStructuralStates`, after the modifications), plus
  `<celldesigner:structuralState angle="..."/>` on the alias after `view`.
  All old files do the same (cAMP, AMP, ATP, Ca2+). Two cAMP icons become one
  "cAMP": CellDesigner has one structural state per species. F018 writes
  "1:cAMP" and "2:cAMP" for different counts.
- Reversible reaction: no `reversible` attribute (true is the SBML default;
  CellDesigner drops `reversible="true"` on saving and keeps
  `reversible="false"`); MINERVA draws arrowheads at both ends.
- Learned from the user's save of glycolysis v01: in the notes of included
  species CellDesigner writes the RDF namespaces in alphabetical order (bqbiol,
  bqmodel, dc, dcterms, rdf, vCard); the complex's brief-view `singleLine`
  width is stored as a float (107.45129863291555 -> 107.45130157470703);
  extra reactant and product links get a `connectScheme` (direct, one line
  direction "unknown") between `linkAnchor` and `line`.
- Names: commas stay as they are (no `_comma_`; MINERVA does not decode it,
  the old files keep the comma).

## Modifications, genes, RNAs, source/sink (glutaminase v01, 2026-10-13)

- Residue sites carry no name: the converter writes only the modification
  state, so CellDesigner shows the symbol in the circle (P, Ac, Ub, Me, ...)
  and no site label. User's rule: site names (S314) are left out because
  MINERVA does not show them. Nodes of one protein share one residue when
  the icons name the same site (Pa@26), wherever they sit; icons without a
  site share one by place. Until 2026-10-13 only by place: eNOS had 4 sites
  drawn at 7 places, so 7 residues (Pa@26 at 165, 179 and 195 degrees), and
  the SBGN-ML export showed 7 state variables, 3 of them empty; EGFR
  (phosphoinositides) 2 for one site.
- CellDesigner 4.4 Startup Guide (user's PDF, pp. 39-40, 84): the
  modification menu offers phosphorylated, palmytoylated, acetylated,
  prenylated, ubiquitinated, protonated, methylated, sulfated, hydroxylated,
  empty, glycosylated, don't care, myristoylated, unknown. A residue's name
  is optional (the residue dialog has id, name, type, side, angle). Genes and
  RNAs only take phosphorylated, acetylated, methylated, unknown, don't care.
  XML values for protonated, don't care and unknown: "protonated", "don't
  care", "unknown" (MINERVA, 2026-10-13).
- Nucleic acid feature: GENE, or RNA when it carries a ct:...RNA unit of
  information (ct:mRNA). One `gene` / `RNA` per label in `listOfGenes` /
  `listOfRNAs`; the species points to it with `geneReference` /
  `rnaReference`. The ct unit stays as
  `<info state="open" prefix="ct" label="gene" angle="-1.5707963267948966"/>`
  (the old files' form).
- Source/sink (yEd EmptySet): class DEGRADED, one species per yEd node, named
  after its id (CellDesigner names a new one s48 and the like). yEd size kept.
- Transcription and translation stay as drawn in yEd: STATE_TRANSITION from
  a source with a TRIGGER from the gene (or the mRNA). CellDesigner also has
  TRANSCRIPTION and TRANSLATION reaction types (gene -> RNA -> protein
  lines); not used.
- `listOfCatalyzedReactions` on a species lists every reaction it modifies
  (catalysis, trigger, stimulation, inhibition), not only catalysis:
  CellDesigner's save of glutaminase v01 added the trigger and stimulation
  ones; F021 (made in CellDesigner) lists an inhibitor.
- Greek letters in names: `_epsilon_` and the rest of the alphabet, as
  `_alpha_`.

## CellDesigner symbols vs. our yEd maps (2026-10-13)

`notes/celldesigner/components44-overview.png`: the user's picture of
CellDesigner's symbol sheet (`<CellDesigner folder>/samples/components44.xml`).
Our yEd SBGN is mostly a subset of it. Scan of all 14 annotated maps:

- Modification states used: empty (81), P (79), Pa (22), My (11), Ac (2).
  All in CellDesigner's menu.
- State variables without a modification: active (13), inactive (9), cAMP,
  Ca, Ca2+, AMP, ATP, cGMP, 1:cAMP, 2:cAMP. The converter writes them as a
  structural state, as the old website files do (13 "active", 9 "inactive"
  there). No node has two of them.
- Units of information: ct:gene (4), ct:mRNA (7) only.
- Arcs into processes: consumption 274, catalysis 94, stimulation 18,
  necessary stimulation (trigger) 10, inhibition 1.
- Not yet converted: logic operators (6, with 12 input arcs; CellDesigner
  boolean gates), submaps (2; no CellDesigner symbol), a stimulation arc to
  a phenotype (1; CellDesigner draws it as a reduced stimulation),
  compartments.

## Compartments, bends, connection points (estrogen and eNOS v01, 2026-10-13)

- Compartments: yEd group nodes without an SBGN class. `compartmentAlias`
  class SQUARE at the yEd box, `namePoint` at the top left of the yEd label,
  `doubleLine thickness="12.0" outerWidth="2.0" innerWidth="1.0"` (as F021,
  made in CellDesigner), colour: the yEd fill blended over white (yEd fills
  are transparent). SBML `compartment` with `outside` = the enclosing
  compartment or `default` (nesting: F018 nucleus and mitochondria in the
  cytoplasm). Outer compartments first in both lists. Species and complex
  aliases carry `compartmentAlias`, species `compartment`; complex members
  carry neither (F021). Checked through MINERVA: boxes land on the yEd boxes.
- Main line bends (only with `--bends` since 2026-10-13): the yEd bends of the base reactant and base product arcs
  become edit points: reactant bends, the two process ports, product bends;
  `rectangleIndex` = the segment between the ports (number of reactant
  bends + 1). yEd ports sit at the tips of the process arms, one process
  width from the centre; points there are ports, not bends. Without bends
  the old rules hold (straight, or the antenna for twin processes), so the
  antenna is the case with no bends.
- Consumption arcs drawn in yEd from the process to the reactant (no
  arrowhead; F008 has five): reactants. Production = an arc from the process
  with an arrowhead.
- Line ends off the node centre in yEd (port offset, e.g. a line leaving a
  complex at its bottom left): the nearest of CellDesigner's 16 connection
  points (N, NNE, NE, ENE, E, ...; corners, side centres and quarter points;
  Startup Guide Appendix 2.3). Positions of the quarter points assumed at
  1/4 and 3/4 of the side; MINERVA places them there. Not for metabolites:
  their yEd box was wider than the circle (stadiums, until 2026-10-23), so the offset points
  nowhere useful.

## Centre position and other lessons from the user's estrogen edit (2026-10-13)

`F018-estrogen/sources/F018-estrogen-v01-cd442-edited.xml` (user's edit and save
of v01):

- Centre position: a base reactant/product without `linkAnchor`, a modifier
  without `linkTarget`, an extra link without `linkAnchor`: the line goes to
  the node centre (cut at the border). User: preferred as the default; it is
  yEd's default port (offset 0,0). The converter writes it for central
  yEd ports and for ports at the middle of a side; other offsets get the
  nearest of the 16 connection points. `CENTRE=0` gives the old side connection points.
- Edit point frame with a centre end: origin the node centre (checked
  through MINERVA: bends land on the yEd points). For a multimer, the centre
  of the whole box, not of the front shape (eNOS NOSTRIN).
- Bound ligands: one structural state "cAMP", no counts ("1:cAMP/2:cAMP" was
  confusing). Placed at the icon with the highest count (user's placement).
- CellDesigner on saving: compartment `namePoint` 12.5 lower (the text
  baseline); a `celldesigner:name` in each compartment's annotation; the
  usual-view `innerPosition` of an alias in a compartment = its offset from
  the top left of its (innermost) compartment. The converter writes all three.

## How CellDesigner builds a reaction; no bends (user, eNOS 2026-10-13)

`F008-enos/sources/F008-enos-v01-cd442-isolated.xml`: one reaction redrawn by
the user (HSP90 + CAV1:CaM:eNOS -> CaM:HSP90:CAV1:eNOS + CaM).

- CellDesigner builds a reaction in two steps: first the main direction,
  one source and one target (here complex centre to complex centre), then
  further substrates and products as extra links. The converter picks as
  base reactant and product the pair that faces each other through the
  process (the process between their centres, least off their line); the
  others become reactant/product links. Before, the first yEd arc was the
  base and bends were needed to make it fit.
- Main vs additional: `baseReactants`/`baseProducts` are the main source and
  target (the base line through the process glyph); `listOfReactantLinks`/
  `listOfProductLinks` are the added ones, attached to the base line
  (`targetLineIndex` -1,0 reactant side, -1,1 product side). Only layout:
  SBML `listOfReactants`/`listOfProducts` make no difference.
- Choosing the main pair: first avoid metabolites (simple molecules,
  source/sink) as long as larger species are there (complex to complex;
  user's edit of eNOS v03, BH4/BH2 exchange), then the pair the process sits
  between, least off their centre line.
- No bend points by default, on main lines, extra links and modifiers. User:
  bends only for a few long connectors, added by hand; working out many
  bends to fit the yEd look is not wanted. `--bends` copies the yEd bends
  (glycolysis v05 was made with them: `CENTRE=0 ... --bends` reproduces it).
  The twin antenna (two processes on the same species) stays.
- Every line end at the centre, whatever port offset yEd has (offsets come from
  the yEd layout; user on eNOS v03: DNM2 joining should go from complex centre
  to complex centre, not ENE to N). The 16 connection points are used only with
  `CENTRE=0`.
- Extra link to a node centre: `linkAnchor position="INACTIVE"` (base links:
  no linkAnchor; modifiers: no linkTarget).
- Reaction ids: yEd's `n0::n17` is no SBML id; `re_n0__n17`.

## Logic gates, submaps, arcs without a process (user's files, 2026-10-13)

- Gate (`F003-mevalonate/sources/F003-mevalonate-v01-cd442-gate-example.xml`):
  in the reaction's `listOfModification`, one `modification` with
  `type="BOOLEAN_LOGIC_GATE_OR"` (AND, NOT), `modifiers` and `aliases` listing
  the inputs (comma separated, left to right), `modificationType` = the arc
  from the gate to the process (CATALYSIS, TRIGGER, ...), `targetLineIndex`,
  and `editPoints="x,y"` = the gate's absolute position (MINERVA puts the gate
  there). The gate can sit anywhere (user): the converter uses the yEd
  operator's position. A gate CellDesigner saved with bends (PD map histamine signalling,
  Osteoarthritis pd65; read since 2026-10-25): the gate is the last point of `editPoints`, the points
  before it the bends of the line gate -> process, in the frame gate -> process; each input's
  modification carries its connection point (`linkTarget`) and its bends in the frame input -> gate. Then one `modification` per input, of the
  modificationType, with `linkTarget` connection point INACTIVE and no targetLineIndex.
  Any number of inputs (the user's file `tests/celldesigner/gate-or-multiple.xml`, 2026-10-26: an OR of
  five on a catalysis, the gate's line at targetLineIndex -1,2): every input in `modifiers` and `aliases`,
  one modification each; AND and the unknown gate ? are read and written the same way.
  Every input is a modifierSpeciesReference and lists the reaction in its
  listOfCatalyzedReactions. yEd: Operator node, inputs joined by plain arcs
  in either direction.
- Gate between entities (reduced notation, no process; the user's file
  `tests/celldesigner/gate-trigger-modulation.xml`, 2026-10-19): a reaction of type
  BOOLEAN_LOGIC_GATE, the inputs as base reactants, the target as base product, a
  GateMember of the gate's type with `modificationType` the arc out of it
  (REDUCED_TRIGGER, REDUCED_MODULATION; REDUCED_PHYSICAL_STIMULATION for a
  stimulation, NEGATIVE_INFLUENCE for inhibition; the PD map's POSITIVE_INFLUENCE is read), then one GateMember per input of
  that type. All four are written and read.
- Unknown gate (`BOOLEAN_LOGIC_GATE_UNKNOWN`, the question mark; pd65 of the Osteoarthritis map, 2026-10-25): the
  yEd Operator **?**, both ways, as a modification gate and between entities; an equivalence operator is written as
  it (D19).
- Unknown (dashed) reduced arcs (the user's file `tests/celldesigner/unknown-reduced.xml`,
  2026-10-20): UNKNOWN_ before the type, between entities (UNKNOWN_POSITIVE_INFLUENCE,
  UNKNOWN_NEGATIVE_INFLUENCE, UNKNOWN_REDUCED_PHYSICAL_STIMULATION, UNKNOWN_REDUCED_MODULATION,
  UNKNOWN_REDUCED_TRIGGER) and out of a gate (its modificationType and each input's
  GateMember). There is no UNKNOWN_PHYSICAL_STIMULATION: a dashed stimulation between
  entities is written UNKNOWN_REDUCED_PHYSICAL_STIMULATION, the same head as our solid one.
- A gate into a gate has no CellDesigner form (user, 2026-10-19). When the second
  gate (the one nearer the target) is OR, it goes: each of its inputs, entity or
  gate, points at its target with the type of its arc out, since several arcs onto
  one target read as any of them (Newt's TGF-beta: AND into OR into Gene
  transcription). When it is AND, the arc is left out with a message.
- Submap: no CellDesigner symbol; a PHENOTYPE at the yEd box (user's SREBP
  file `F005-srebp/sources/F005-srebp-v01-cd442-phenotype.xml`).
- Arc between two entities without a process (stimulation of a phenotype or
  submap): a reaction with `reactionType` PHYSICAL_STIMULATION (since 2026-10-20, user:
  REDUCED_PHYSICAL_STIMULATION, also out of a logic gate, its white arrowhead SBGN's;
  POSITIVE_INFLUENCE, an open arrow with no SBGN equivalent, is read as a stimulation and
  never written; onto a process the PHYSICAL_STIMULATION modifier), base reactant
  and base product only, both `linkAnchor position="INACTIVE"`, no process,
  `reversible="false"`. Only the yEd stimulation arrow (white_delta) is
  mapped; other arrows get a warning.
- Added link's edit points (the user's file `tests/celldesigner/added-link-bends.xml`,
  2026-10-20; checked through MINERVA on all 22 such links of PD map autophagy and
  histamine signalling, exact): a frame as for modifiers, from the link's species end
  (its connection point, else its centre) to the point where the link joins the main line, or the
  other way for a product (join -> species). The join is on the segment with the process glyph
  (rectangleIndex), at 3/8 of it for a reactant, 5/8 for a product, the segment's ends
  where CellDesigner draws them (a species' connection point, else its border). Read; the writer
  still writes added links straight.
- Added reactant/product links to a centre: no linkAnchor (CellDesigner's
  save of mevalonate v01 dropped the INACTIVE written there before).

## Twin processes by quarter connection points; gate inputs as saved (2026-10-13)

From the user's edit of mevalonate v03 without the twin rule
(`F003-mevalonate/sources/F003-mevalonate-v03-without-twin-rule-cd442-edited.xml`):

- Two processes on the same two species (phosphorylation and
  dephosphorylation of HMGCR): no edit points. Each is a straight line
  between quarter connection points on the facing sides of the two boxes: the
  process above the line between the centres uses the upper quarters (ENE /
  WNW), the one below the lower (ESE / WSW); for boxes stacked vertically the
  left (NNW / SSW) or right (NNE / SSE) quarters. Which side: where yEd has
  the process. Replaces the antenna (two edit points around the process glyph),
  which stays only with `CENTRE=0`.
- Gate inputs: `targetLineIndex="-1,0"` and no `linkTarget` (as CellDesigner
  saved them).
- Regulatory arcs: attached to the side of the process glyph facing the modifier
  (targetLineIndex -1,2 / -1,3, a one-line test). Arcs that cross another
  line because of where the modifier sits are left to the manual pass
  (avoiding them needs routing).

## Straightening slightly-off main lines (user's glycolysis edit, 2026-10-13)

`F001-glycolysis/sources/F001-glycolysis-v08-cd442-edited-orthogonal.xml`: the
PKA complexes and PKA cat put on one vertical line by hand. Until 2026-10-24 the converter did it
(`cd_tidy.py`): nodes joined by a main line at most 10 px off the vertical got one common x, off the
horizontal one common y. Across all maps such lines are 0-5 px off and the next ones 20+ px (intended
diagonals). Removed (user, 2026-10-24: no node moved in conversion): it belongs to the source map, the
layout skill's `standardise.py`, if wanted.

## Significant bends (in the converter since 2026-10-13, `mapconv/layout.py`, bends)

From the user's edits (glycolysis v08: two PFKFB2 catalysis arcs; aspirin
v02: arachidonate -> 15R-HETE), one corner each, matching the yEd elbow.

- Found in yEd: the route of an arc (node centre, bends without the process
  ports, process centre), simplified (Ramer-Douglas-Peucker, 20 px); a bend
  counts when exactly one corner remains and the route is at least 150 px
  long. From yEd only the way the L turns (horizontal or vertical first).
- Corner built from the CellDesigner file: x of one end, y of the other.
  Main line: ends at the reactant and product centres; one bend on the
  reactant arc or on the product arc (not both); the process glyph goes on the
  segment where yEd has the process (after the corner for a reactant-arc
  bend: `rectangleIndex` 1). Modifier: from its centre to the arc's end on
  the process glyph's side (5 px from the process glyph centre); frame origin the modifier
  centre, x axis to that end (checked through MINERVA: the corner lands
  exactly).
- Quarter points on circles (metabolites) sit on the circle at 22.5 degree
  steps (ENE = 22.5 degrees), not at the box quarters (found here: twin
  process glyphs between metabolites were 2 px off).
- Result over the full set: 24 bends, every corner a right angle (within
  0.5 px, MINERVA).
- Added reactant/product links stay straight (user: not needed).

## The user's edits of the full set (2026-10-13)

`<map>/sources/<file>-cd442-edited.xml` (zip `celldesigner-all-edited`). Same
species and reactions everywhere; geometry only; iNOS and glycogen liver
unchanged. Published on the website as they are (17 maps; glycogen liver
from the muscle edits, `F004-glycogen/build_liver_from_muscle_edits.py`).

What the edits show:
- Modifiers moved so their arc meets the process glyph straight: 23 times
  (offsets 2-15 px, once 45); never the other way. In the converter since
  2026-10-13 (user: automatic if the move is small and nothing overlaps):
  after straightening, a modifier is moved up to 15 px (ALIGN) along one axis
  so its arc meets the process glyph straight; the same move for every reaction it
  acts on; not if it ends a main line straight on that axis, not if it would
  leave its compartment or overlap another node; complex members move with
  their complex; L-shaped arcs are left alone. Against the user's edits: of
  the modifiers it moves, 29 of 45 are aligned in the user's files too (the
  user often moved the other end instead), 16 the user had left.
- Lines through other nodes: 5 in the full set, the user fixed 3 by hand.
  User: no reports wanted, only the best automatic conversion.
- Bends: most changed values are CellDesigner recomputing the edit points
  after moves; the converter's bends were kept. New by hand: 3 (a modifier
  in mevalonate, a main line in glycogen muscle, a modifier in
  phosphoinositides); removed by hand: 2 (TAG stimulation arcs). No rule.
- Stimulations without a process: CellDesigner drops the INACTIVE connection points;
  the converter now writes none (SREBP, ACLY).
- Modifier attachment: CellDesigner also uses targetLineIndex -1,5 (TAG);
  the Startup Guide's figure numbers the process glyph's points 2-4 (top) and 5-7
  (bottom). The converter keeps 2/3, except in the advanced layout (section "Advanced layout:
  the rules now", modifier arcs).
- Many moves are spacing (blocks shifted, room for labels): no rule.
- iNOS (sent separately, `F007-inos/sources/F007-inos-v05-cd442-edited.xml`):
  three urea-cycle reactions redrawn so the main line follows the cycle
  (arginine -> citrulline, citrulline -> argininosuccinate,
  argininosuccinate -> arginine), side metabolites (O2, NO, aspartate,
  fumarate) as added links. Tested "backbone first" (prefer species that
  also take part in another process), first and as a tie-breaker after
  "avoid metabolites": it fixes two of the three but breaks others (eNOS
  ADMA -> DMA becomes H2O -> citrulline, arginine -> NO becomes O2 -> NO).
  Not built: which metabolite is the main one is a biological choice.
  Possible exact route (proposed to the user): a marker on the main arcs in
  yEd (custom property or line width) that the converter reads.

## SBML through MINERVA; ids and complex names (2026-10-13)

- SBML and SBGN-ML downloads (website `atlas-downloads/`): `tools/minerva_exports.py <website repo>/atlas-downloads [maps]` (or `/downloads` for the official copies)
  (MINERVA's conversion service). MINERVA cuts ids at a double underscore:
  `re_n1__n28` and `re_n1__n31` both became `re_n1`, and the SBML export
  failed ("Problem with exporting bioEntity"; glycogen, eNOS, iNOS, estrogen,
  ...). The script sends reaction ids with single underscores; the converter
  now writes all ids that way (`n1::n28` -> `n1_n28`).
- Unnamed complexes inside unnamed complexes were named before their inner
  complex had a name ("PKA cat:", ":", "ADCY:" in glycogen); now inner first,
  each member once (user: "PKA reg:cAMP", not "PKA reg:cAMP:cAMP").
- Checked over all maps: these changes alter only ids and complex names.

## Seen in the old files, not yet in the converter

- Extra reactants/products: `listOfReactantLinks` / `listOfProductLinks`
  with their own connection point, connect scheme and line.
- (Boolean gates: in the converter since 2026-10-13. TRIGGER, PHYSICAL_STIMULATION,
  INHIBITION modifiers are written; TRIGGER and PHYSICAL_STIMULATION first
  checked with glutaminase v01.)
- Classes used: PROTEIN, SIMPLE_MOLECULE, COMPLEX, RNA, GENE, ION, DEGRADED,
  PHENOTYPE (RNA, GENE, DEGRADED in the converter since glutaminase v01).
- States used: phosphorylated, palmytoylated (CellDesigner's spelling),
  myristoylated, acetylated, ubiquitinated, empty.

## Units of information: two yEd glyphs (2026-10-13)

yEd draws a unit of information either as a plain box icon (ShapeNode: iNOS,
estrogen, glutaminase, the N:x of most maps) or as its SBGN glyph (GenericNode
com.yworks.sbgn.UnitOfInformation: ACLY ct:gene/ct:mRNA, glycogen, SREBP), or
as a second boxed text label (iNOS ASL "N:4"). The converter reads all three.
Before, only the box: ACLY's mRNA became a gene.

## State patch of the published files (2026-10-13)

`tools/cd_fix_states.py <published.xml> <converter output.xml> <out.xml>`
gives each protein the converter's residues and each species its identity
(class, protein/gene/RNA reference, state; the published name kept), the gene
and RNA lists and each alias's unit of information (ct:) follow the converter; a multimer whose count changes grows 6 per unit,
top left kept. Nothing else changes (the published files are the user's
edits). Applied to the website `atlas-downloads/` (all 18 maps run; changed:
mevalonate, iNOS, eNOS, phosphoinositides; iNOS equals the user's ASL edit),
SBML and SBGN-ML regenerated with `tools/minerva_exports.py`. Grown boxes
checked: no overlaps, NOSTRIN still inside its complexes.

## SBGN within CellDesigner (user's rules, 2026-10-13)

- CellDesigner offers more classes and reaction types than SBGN; we use only
  the SBGN ones. Reactions: STATE_TRANSITION (also across compartments, e.g.
  cholesterol cytoplasm -> mitochondria; no TRANSPORT), PHYSICAL_STIMULATION
  for arcs without a process. No ION: every metabolite is SIMPLE_MOLECULE
  (SBGN has only simple chemical); an ION in a file is an error to fix. The
  converter writes none of the others (atlas set checked: classes PROTEIN,
  COMPLEX, SIMPLE_MOLECULE, GENE, RNA, PHENOTYPE, DEGRADED only).
  The old official `downloads/` files still break it (to be replaced when the
  user says): ION Ca2+ in glycogen liver and muscle; HETERODIMER_ASSOCIATION
  (mevalonate), UNKNOWN_TRANSITION (estrogen), REDUCED_PHYSICAL_STIMULATION (ACLY).
- Bound ligand as structural state: written once ("cAMP"), no counts.
  CellDesigner has one free-text structural state per species, nothing else
  can carry a ligand, so the yEd icons collapse to one: CaM with four "Ca"
  icons (mevalonate) -> structural state "Ca"; two "cAMP" (glycolysis, TAG)
  -> "cAMP". The yEd maps stay as they are (user, 2026-10-13: the problem
  is CellDesigner's, not the GraphML's).
- The rule (user, from `notes/celldesigner/components44-overview.png`): a state
  variable that is one of CellDesigner's modification circles (P, Pa, Ac, Pr,
  Ub, H, Me, S, OH, G, My, empty, * don't care, ? unknown) is a residue, as
  many as the node has; anything else (active, inactive, cAMP, Ca, ATP, ...)
  goes into the one free-text structural state (different texts joined by
  "/"; none in the current maps). The converter does this for all of them;
  XML values for H, * and ?: "protonated", "don't care", "unknown" (checked
  through MINERVA, which shows H, *, ? and rejects other spellings).

## Reversible processes with several arcs; free-text-only proteins (2026-10-16)

- A reversible process (production arcs on both sides, no consumption arc) with more than two
  arcs (BCAT2 in F022: leucine + alpha-ketoglutarate <-> alpha-ketoisocaproate + glutamate):
  the arcs on the upper (or left) side of the process are the reactants. An arc's side is that
  of its first yEd bend, else of its entity; the axis is the one along which the arcs spread
  most. Then the main pair is chosen as for any reaction. Before, only two arcs were handled
  and BCAT2 was skipped. All other maps byte-identical.
- A protein whose marks are all free text (Su, Glut: not in CellDesigner's menu; CPS1 in F021)
  gets no residues: its empty circles (OVAV in yEd) are dropped, the marked nodes get the
  free-text structural state, unmodified nodes nothing (user, 2026-10-16). All other maps
  byte-identical.

## Layout transfer from the user's GraphML (F022 BCAA v04, 2026-10-16)

On the user's request ("layout better, as in the GraphML"), a map-specific script
(`F022-bcaa/cd_layout_v04.py`) post-processes the converter output:
- Modifier arcs with yEd bends or an off-centre start get edit points (frame of `cd_layout.to_frame`),
  snapped orthogonal against the CellDesigner positions; an off-centre start becomes one point 1 px
  outside the node at the process glyph's height.
- A process glyph where yEd has the process: two edit points on the straight main line, 8 px either side,
  `rectangleIndex="1"`, three line directions.
- Lanes leave a metabolite circle 12 px below its centre, so they do not cross the name.
Since 2026-10-16 in the converter as `--layout advanced` (user: two modes. `direct` (since 2026-10-17 `straight`), the default,
is the necessary minimum: simple rules, a basic and reliable conversion improved by hand.
`advanced` gives a layout that already looks good in CellDesigner). Differences from the script:
- The process glyph is placed before the modifiers are aligned onto it, so the small alignment moves
  (up to 15 px) aim at the process glyph where yEd has it. On the 24 test maps every node this
  changes ends up closer to its yEd position (49 nodes).
- No node is moved for a route. A routed arc that runs through another node is reported
  ("n1::n38: the arc from α-ketoisocaproate runs through PPM1K:Mn2+"), for the user to move in
  CellDesigner (the script moved PPM1K:Mn2+ 20 px; the user's check moved it 36 px right instead).
- Lanes left a metabolite (SimpleChemical) 12 px lower (the script recognised it by its 36 px width); since 2026-10-16 replaced by the connection points in "Metabolite circles: where lines meet them".
BCAA: identical to v04 except the 20 px move (process glyphs, edit points, line directions compared).

## Metabolite circles: where lines meet them (advanced)

A metabolite is a circle with its name drawn across the middle. In the advanced layout a line
meets it where the name is not (user, 2026-10-16, from PD02 eicosanoids: 85 of 104 lines from
above or below at N or S, sideways lines mostly at ESE or WSW): at N or S when it leaves up or
down, at ESE or WSW (the lower quarter of the side) when it leaves sideways. The way it leaves:
the first leg of an L, else towards the process; for a modifier, towards its first bend or the
process glyph. Main lines get linkAnchor, modifiers a linkTarget with linkAnchor (as the PD map), the
modifier's first bend in line with that point. Two processes on the same two species keep their
quarter points. The straight layout keeps lines at the centres. (Replaces the earlier rule that a
lane leaving a metabolite sideways starts 12 px lower.)

## Advanced layout: the rules now (2026-10-17)

Worked out on PD02 eicosanoids (CellDesigner -> GraphML -> CellDesigner, `test_round_trip`) and
the user's CellDesigner edits of pyrimidine (v05-v08), iNOS (v07, v08), urea cycle (v02), BCAA
(checked v04). Principle (user): write a connection point or edit point only where it changes the drawing,
and move a node before adding bend points; points that change nothing make relayout by hand
harder. When the converter already has a line straight, keep it: CellDesigner's view can show it
a few px off (the user's moves of ERK1/2, 6 px, and SIRT5, 4 px, made lines the converter had
level 3-4 px off by its reading).

Main line of a process with several reactants or products, in order: larger species before
metabolites; never a pair whose midway process glyph would sit on another node; a pair drawn straight
through the process in yEd (3 px); a pair on a cycle, the product leading back to the reactant
through other processes (iNOS: arginine, citrulline, argininosuccinate main, O2, NO, fumarate,
aspartate added; urea cycle ASS1, was ATP -> PPi); the pair nearest the process.

Geometry of a main line:
- Edit points: one long L keeps the corner rule (x of one end, y of the other); the L is read
  with the yEd bend at the process's port, which says from which side the line comes in (iNOS
  ASL, ASS1). An L whose bend is more than 20 px from that corner keeps its slanting leg; other
  routes keep every bend that moves the line by more than 20 px (`layout.bends`: PD02's Z
  routes and detours round other nodes).
- Connection points: where the yEd arc meets the entity's border (nearest of CellDesigner's 16; on a
  metabolite E and W become ESE and WSW), else on a metabolite where its name is not (section
  above). Kept only if it moves the line more than 2 px from the line to the centre.
- Two processes on the same two species, both drawn straight: quarter points.
- The process glyph where yEd has the process (user, 2026-10-24: no node moved), when that is more
  than 3 px from midway on its segment (`SHIFT`; also on a bent line), within 12 px of the line (a
  metabolite's line leaves 10 px off its centre, under its name) and between 0.1 and 0.9 of it: two edit
  points half way from the process glyph to the nearer end on either side, at least 3 px outside the end
  nodes and at the same distance from the process glyph (user, 2026-10-24: 90 points inside a node before),
  so the arcs keep visible antennas (8 px beside the process glyph looked as if the arcs ran into it; the user's CAD edit: about
  0.6 of that way). On the line, so CellDesigner draws nothing more. Else midway (CellDesigner's own
  rule). 3 px: the yEd offsets run on without a gap (0-5 px 23 processes, 5-10 px 39, of 168 placed on
  the 28 Atlas maps), and below 3 px two points per reaction would add clutter for nothing seen.
- A main line yEd draws level into a larger node through an end point beside its centre (more than 3 px):
  one edit point on the line, 3 px outside that node (`EDGE`), the line on to the centre from there (no
  connection point). Under the node (first try, 2026-10-24) it showed: CellDesigner draws lines over nodes, so the
  line ran to the centre (user, 2026-10-24; iNOS CaM -> CaM:iNOS 23.6 px, mevalonate
  AMPK 14.4 px, glycolysis extended IRS1 22 px, SREBP 4.5 px, cAMP 3.7 px). Until 2026-10-24 the other end
  was moved onto the centre line.

The rules above are for CellDesigner (as drawn), `-drawn.xml` (user, 2026-10-24; D18). CellDesigner
(straight & bends), `-bends.xml`, has the drawing below without the moves. CellDesigner (advanced) keeps the
tidy moves (`cd_tidy.py`; D17, D18): main lines up to 10 px off straightened,
the end of a level line into a larger node beside its centre moved onto that node's centre line (iNOS CaM
23.6 px; the user moved it 25 px twice), a modifier up to 15 px onto its process glyph, on a drawing with the
process glyph placed only for a modifier straight across that could not be moved. Straight line moves no
node.

Modifier arcs: the end on the process glyph. A process with several modifier arcs, one of which yEd
ends off the process's centre (more than 2 px): that arc ends at the process glyph's point nearest its yEd
port (a corner, `-1,4` to `-1,7`, or a side middle), so the arcs do not merge into one line
(user, PDH 2026-10-17: PDK, pyruvate and dichloroacetate on the PDK step, acetyl-CoA and NADH on
PDH; the user's own CellDesigner edit of PDH has the same points). Else the side facing the
modifier, as before. A modifier arc counts as straight across when it is in line with its yEd port
or with the process's centre. Changed: TAG (2 arcs), BCAA (4), PDH (6; PDK 5 px left onto its
corner). Back to yEd (advanced) the arc ends at the same point of the 18 px process: corners at
(9, 9), side middles at (0, 9) across the flow (user, 2026-10-17), so GraphML -> CellDesigner ->
GraphML -> CellDesigner gives PDH's drawing twice (`test_repeat`).
The route: the yEd route made orthogonal; from an off-centre yEd port a lane at the process glyph's
height from just outside the node, only if the port is off the line from the centre by more than
2 px; a slanting straight arc from a port on the border takes that connection point. No edit point on a
straight line between its neighbours (`layout.unbent`, also used on the way back).

Both layouts: CellDesigner writes a complex's name at the bottom inside it. Its members move up to
leave NAME_ROOM (14 px) below their outline (a state variable on the bottom edge reaches 8.5 px
below the node, yEd's second shape of a multimer 6 px), as far as 8 px above them allows; the
complex grows down for the rest. 14 px is the bottom of the complex packing rule of the
sbgn-human-like-layout skill (`complex_pack.py`), so a packed GraphML keeps its geometry in
CellDesigner (user, 2026-10-18). MINERVA writes the name about 3.6-12.5 px above the complex's
bottom edge, so it stays about 1.5 px clear of a bottom state variable. Before: 25 px below the
node boxes (the user's pyrimidine edits, 2026-10-16: RAS up 12 px, GDP/GTP 6 px), which moved
members of packed complexes up and pushed N:2 through the complex's top.

Results: PD02 round trip every process glyph within 38 px (553 before); pyrimidine and iNOS advanced equal
the user's last edits apart from rounding and the antenna length; urea cycle v02 needed only
SIRT5 4 px and CPS1 1 px; BCAA looks as checked. Squares placed by edit points: BCAA 8, iNOS 4,
pyrimidine 1, mevalonate 1, glycolysis and nNOS none.

Open:
- Move a whole subpathway in place of bend points (the user moved RAF1, MEK1/2 and ERK1/2
  together, keeping equal distances). Needs knowing what a subpathway is; separately.
- What remains on CellDesigner's own maps: the yEd-oriented moves (modifiers onto process glyphs,
  straightened main lines) also act on them; metabolites become 40 px circles.

## Hidden bends, reading CellDesigner (user, 2026-10-19)

CellDesigner draws its nodes over the arcs, so a file holds edit points nobody sees: inside the
arc's own source or target (on influence arcs and modifiers above all), or on the straight line
between their neighbours. yEd and Newt draw them (an arrow folded back inside its target). The
reader keeps only the bends CellDesigner shows (`layout.visible`): the run of points at the start
of an arc inside its source and at its end inside its target is left out, and the arc's port goes
to where CellDesigner's line crosses the node's border, when a line from the old port would differ
(a process or operator keeps its port); then the points on the straight line, measured from the
ports (before: from the centres). Points of an arc that leaves a node and crosses it again are
seen in CellDesigner and kept. Measured on 97 CellDesigner files (official, PD map, AsthmaMap,
ACSN): 1186 of 18509 edit points left out, inside an end node 1151 -> 10 (QUALITY.md).

## Free-text units of information (user's example, 2026-10-22)

CellDesigner saves a unit of information with free text on the species alias as
`<celldesigner:info state="open" prefix="free input" label="exampletext" angle="..."/>`
(`tests/celldesigner/free-text-unit.xml`, saved by the user), the same element as ct:gene with
another prefix. The writer gives every unit other than ct: and N:x this form (SREBP "precursor",
"processed form", "mature form"; before, they were left out without a message); the reader takes the
label alone. One info per alias: a node with more units keeps a ct: unit first, the rest is
reported left out. CellDesigner shows the label alone ("example..." cut to the box); MINERVA (22.0.1)
draws and exports "free input:precursor", the prefix with the label.

## Notes: family name and members' sites (user, 2026-10-22)

What MIRIAM cannot hold goes into the species' SBML notes (XHTML body, CellDesigner's notes panel,
MINERVA's notes), one line each: "Family: PKA regulatory subunits" and "MAPK3: P@T202 P@Y204" per
family member with sites (`annotation.notes`, read back by `annotation.from_notes`). An included
species (complex member) has the lines before its RDF in the same body. The entity's own sites stay in
the GraphML property PTM only (user, 2026-10-22: until a case needs them on the drawing).

{% endraw %}

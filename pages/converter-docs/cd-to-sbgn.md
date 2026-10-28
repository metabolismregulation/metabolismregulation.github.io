---
layout: converter-docs
title: "CellDesigner to SBGN PD (yEd): the rule table"
permalink: /converter/docs/cd-to-sbgn/
sitemap: false
noindex: true
---
{% raw %}

Rules for the backward direction (CellDesigner -> GraphML), 2026-10-16, all answered by the
user. Implemented in `celldesigner.read` + `graphml.write` (`python3 -m mapconv <map.xml> <out.graphml>`),
first for what our own CellDesigner files hold (user: our maps first, as a
round trip), then for CellDesigner's own files: the PD map (autumn 2025, 41 files, user)
reads without error. Branched reactions (association, dissociation, truncation) become one
process at the branch point: the last edit point in the frame of the three species (origin
the first, axes to the other two), each branch's edit points (num0, num1, num2) in the frame
branch point -> its species (cd2sbgnml, AssociationReactionModel). Logic gates on reduced arcs
are BOOLEAN_LOGIC_GATE reactions (inputs as base reactants, the gate at the edit point,
absolute; GateMember list) both ways; CellDesigner has no gate feeding a gate. Inhibition
between entities: NEGATIVE_INFLUENCE (forward); modulation and trigger between entities:
REDUCED_MODULATION, REDUCED_TRIGGER (forward, 2026-10-17, so they come back as they went). From a
gate only stimulation and inhibition (a CellDesigner file with a gate's trigger would settle more). Not yet: binding regions and gene/RNA regions
(Q11), edit points of added reactant/product links (drawn straight), closeup compartments, yEd
Checked against the user's small files (2026-10-16): a reversible reaction is marked only by
leaving out reversible="false" (both ways as before); yEd draws an omitted or uncertain process
as its Process labelled \\ or ? (no glyph of its own; read and written so, CellDesigner
KNOWN_TRANSITION_OMITTED, UNKNOWN_TRANSITION); unspecified entity template from the user's file.
Dashed (unknown) arcs: UNKNOWN_CATALYSIS, UNKNOWN_INHIBITION, UNKNOWN_NEGATIVE_INFLUENCE; others
written solid with a note. Dashed border: hypothetical. Stimulation between entities stays
PHYSICAL_STIMULATION, the triangle (user: closest to SBGN; POSITIVE_INFLUENCE is an open arrow). Seeded from
**cd2sbgnml** (github.com/sbgn/cd2sbgnml, commit a35eff8: `model/ReactantModel.java`,
`model/Process.java`, `model/LinkModel.java`, `CD2SBGNML.java`, wiki page "Limitations"),
the CellDesigner <-> SBGN-ML converter by Ludovic Roy (Institut Curie), made with this
group (Balaur et al. 2020). Where our own forward converter (`celldesigner.py`) already
decides a case, the table follows it, so a round trip comes back unchanged.

Coverage test: CellDesigner's own component sheet (`docs/components44-overview.png`; its
CellDesigner file `components44.xml` ships with cd2sbgnml in `samples/`) holds every glyph
CellDesigner 4.4 can draw: 13 classes, 4 protein types, 20 reaction types, 13 modifier types,
gene/RNA regions, hypothetical and active species, layers. Every element on it must convert
or give a warning.

Columns: **CellDesigner** element, **cd2sbgnml** (what it writes in SBGN-ML), **proposal**
for our yEd maps, **?** = a choice for the user (questions at the end). The yEd glyph names
are those of the yEd SBGN palette (`model.py` kinds).

## Species

| CellDesigner | cd2sbgnml | proposal | ? |
|---|---|---|---|
| PROTEIN, generic | macromolecule | Macromolecule | |
| PROTEIN, receptor | macromolecule + unit of information "receptor" | **Macromolecule** (user: Q1) | |
| PROTEIN, ion channel | macromolecule + unit "ion channel", state variable "open"/"closed" (CellDesigner active/inactive) | **Macromolecule + state variable "open"/"closed"** (user: Q1, Q2) | |
| PROTEIN, truncated | macromolecule + unit "truncated" | **Macromolecule** (user: Q1) | |
| GENE | nucleic acid feature | NucleicAcidFeature + unit "ct:gene" (our maps' form) | |
| RNA | nucleic acid feature + unit "RNA" | NucleicAcidFeature + unit "ct:mRNA" (our maps' form) | |
| ANTISENSE_RNA | nucleic acid feature + unit "asRNA" | NucleicAcidFeature + unit "ct:asRNA" | |
| SIMPLE_MOLECULE | simple chemical | SimpleChemical | |
| ION | simple chemical | **SimpleChemical** (user: Q3) | |
| DRUG | simple chemical + unit "drug" | **SimpleChemical, white fill** to tell it apart (user: Q3) | |
| UNKNOWN | unspecified entity | UnspecifiedEntity | |
| COMPLEX | complex | Complex, members inside | |
| PHENOTYPE | phenotype | **Phenotype**. In our yEd maps the Phenotype glyph stands for phenotype, perturbation and submap alike, so the maps stay compatible with CellDesigner (user: Q4). Nothing becomes Perturbation or Submap | |
| DEGRADED | source and sink | SourceAndSink | |
| homodimer N | "... multimer" + unit "N:N" | the glyph as multimer + unit "N:N" (our maps' form) | |
| hypothetical species (dashed border) | | **the glyph with a dashed border**, and a warning (user: Q9) | |
| active species (dotted outer border, "activated") | | **state variable "active"** (user: Q10) | |
| complex in brief view (members hidden) | complex | Complex with its members (from the species), drawn as in usual view | |
| PROTEIN residue, binding region | state variable / unit | residue: state variable; **binding region: unit of information with its name** (user: Q11) | |
| GENE/RNA regions: modification site, coding region, regulatory region, transcription starting site | | modification site: state variable; **others: unit of information with the name** (user: Q11) | |

## States and units

| CellDesigner | cd2sbgnml | proposal | ? |
|---|---|---|---|
| modification residue, state phosphorylated, acetylated, ubiquitinated, methylated, hydroxylated, glycosylated, myristoylated, palmytoylated, prenylated, protonated, sulfated, don't care, unknown | state variable P, Ac, Ub, Me, OH, G, My, Pa, Pr, H, S, *, ? | the same symbols, placed at the residue's angle on the border (inverse of `border_angle`) | |
| residue, state empty | empty state variable | empty state variable | |
| structural state (free text: cAMP, active, Su) | state variable with that text | state variable with that text (our bound-ligand and free-text form) | |
| info unit ("ct:gene" etc.) | unit of information | unit of information, same text | |

## Reactions (the process glyph)

| CellDesigner | cd2sbgnml | proposal | ? |
|---|---|---|---|
| STATE_TRANSITION | process | Process | |
| KNOWN_TRANSITION_OMITTED | omitted process | OmittedProcess | |
| UNKNOWN_TRANSITION | uncertain process | UncertainProcess | |
| TRANSPORT (translocation) | process | Process | |
| TRANSCRIPTION | process | Process | |
| TRANSLATION | process | Process | |
| HETERODIMER_ASSOCIATION | association | **Process** (user: our maps use no association or dissociation glyphs, Q5) | |
| DISSOCIATION | dissociation | **Process** (user, Q5) | |
| TRUNCATION | dissociation (Limitations page) | **Process** (user, Q5) | |
| reactants, products, added reactant/product links | consumption, production | consumption, production arcs | |
| homodimer formation (STATE_TRANSITION to a multimer), degradation (to DEGRADED) | process | Process; nothing special | |
| bidirectional reaction (reversible="true", arrows on both ends) | production on both sides | production on both sides | |
| reversible="true" without a consumption side | production on both sides | production on both sides (our forward rule, inverted) | |

## Modifiers (arcs into a process)

| CellDesigner | cd2sbgnml | proposal | ? |
|---|---|---|---|
| CATALYSIS | catalysis | catalysis | |
| UNKNOWN_CATALYSIS | catalysis | **catalysis, dashed** (user: Q6) | |
| INHIBITION | inhibition | inhibition | |
| UNKNOWN_INHIBITION | inhibition | **inhibition, dashed** (user: Q6) | |
| PHYSICAL_STIMULATION | stimulation | stimulation | |
| MODULATION | modulation | modulation | |
| TRIGGER | necessary stimulation | necessary stimulation (trigger) | |
| TRANSCRIPTIONAL_ACTIVATION, TRANSLATIONAL_ACTIVATION | production (marked TODO in cd2sbgnml) | **stimulation** (user, Q7) | |
| TRANSCRIPTIONAL_INHIBITION, TRANSLATIONAL_INHIBITION | production (TODO) | **inhibition** (user, Q7) | |
| BOOLEAN_LOGIC_GATE_AND, _OR, _NOT | logic operator + logic arcs | Operator AND/OR/NOT + logic arcs (our forward rule, inverted) | |
| BOOLEAN_LOGIC_GATE_UNKNOWN | gate dropped, its inputs go straight to the process (Limitations page) | GraphML: Operator **?** (D19); SBGN-ML: the gate and its arcs left out, with a message (no SBGN glyph) | |

## Reduced notation (arcs between entities, no process)

cd2sbgnml writes them as arcs straight from entity to entity, which SBGN PD does not allow
(an Activity Flow idea inside a PD map). **Decision (user, Q8): kept as in CellDesigner**, entity
to entity: not a one-language map, but nothing is lost and the way back is possible. Our forward converter already writes one such case:
a yEd stimulation arc between two entities becomes PHYSICAL_STIMULATION in reduced notation
(SREBP, ACLY).

Geometry (2026-10-28): such an arc starts and ends at the connection points CellDesigner names (`linkAnchor` of its
base reactant and product) and its bends come from its edit points in the frame between those two points, as a
reaction's main line ([CellDesigner files](/converter/docs/celldesigner/)). Before, the frame ran between the node
centres, which shifted every bend and broke the shared lanes of a map drawn with them (ExposomeMap-PM: 15 of 492
segments level or upright, now 280, as CellDesigner draws them).

| CellDesigner | cd2sbgnml | proposal | ? |
|---|---|---|---|
| POSITIVE_INFLUENCE, UNKNOWN_POSITIVE_INFLUENCE | stimulation, entity to entity | stimulation arc, entity to entity (UNKNOWN_: dashed, as Q6) |  |
| NEGATIVE_INFLUENCE, UNKNOWN_NEGATIVE_INFLUENCE | inhibition, entity to entity | inhibition arc, entity to entity (UNKNOWN_: dashed, as Q6) |  |
| REDUCED_PHYSICAL_STIMULATION (+ UNKNOWN_) | stimulation | stimulation arc (UNKNOWN_: dashed, as Q6) |  |
| REDUCED_MODULATION (+ UNKNOWN_) | modulation | modulation arc (UNKNOWN_: dashed, as Q6) |  |
| REDUCED_TRIGGER (+ UNKNOWN_) | necessary stimulation | trigger arc (UNKNOWN_: dashed, as Q6) |  |
| a link pointing at another link | omitted (Limitations page) | omitted, with a warning | |
| logic gate on a reduced arc (trigger 1 AND trigger 2 -> B) | logic arcs | Operator + logic arcs, then the reduced arc from the operator | |
| a reduced arc ending on a reduced arc (c inhibits A -> B) | omitted | omitted, with a warning | |

## Compartments, geometry

| CellDesigner | proposal |
|---|---|
| compartment alias (SQUARE, OVAL) | yEd group node with the name, fill as in CellDesigner |
| closeup compartments (SQUARE_CLOSEUP_*: a border line, no box) | a warning; drawn as a box to the map's edge | 
| alias bounds | node box (metabolite circles back to the yEd size 60 x 32, centre kept; multimers shrink 6 per unit beyond 2: inverse of the forward rules) |
| reaction | Process 18 x 18 (our maps' size) where CellDesigner draws the process glyph: midway on the main line's segment `rectangleIndex` |
| edit points of a reaction or modifier | yEd bends (sharp, as CellDesigner draws them; within 3 px of one line aligned on it, [D22](/converter/docs/design/#d22-bends-from-celldesigner-aligned-within-3-px-drawn-sharp)), from the edit point frame (inverse of `cd_layout.to_frame`); a modifier's frame ends at the point of the process glyph `targetLineIndex` names (side middle, 5 px beside the centre, or corner) |
| arc ends | node centres (ports 0,0; CellDesigner's quarter connection points only place the process glyph); advanced: connection points as ports, a modifier at the point of the 18 px process `targetLineIndex` names (corners at 9, 9, side middles at 0, 9 across the flow) |
| MIRIAM annotation | node properties as `mapconv.annotate` writes them (HGNC symbol, HGNC, UniProt, ChEBI; a family's Members and Member annotation) |
| references on a reaction (`isDescribedBy`, bqbiol or bqmodel: PubMed, DOI, PMC, Reactome) | the process glyph's node property References, `prefix:id` separated by spaces (`pubmed:27260166 doi:10.1016/j.jaci.2020.12.155`); back to CellDesigner as `bqmodel:isDescribedBy`, one bag each ([D21](/converter/docs/design/#d21-references-on-a-process-as-the-node-property-references)) |

## Not converted

| CellDesigner | proposal |
|---|---|
| layers (free text, lines, shapes, layer comments) | left out, with a warning listing them; empty layers (CellDesigner's default two) say nothing |
| style variation (gradient fill, line width) | left out: our yEd style |
| colours of species | kept as fill (as the forward direction) |
| references on a reaction drawn as an arc (reduced notation, influences, a logic gate between entities) | left out, with a message naming the reactions: an arc holds no properties ([Issues](/converter/docs/issues/)) |
| reaction annotation other than `isDescribedBy` (`bqmodel:is` with a PMID, Reactome `hasVersion`) | left out, no message yet |
| species identifiers other than HGNC, HGNC symbol, UniProt, ChEBI (Entrez, Ensembl, RefSeq, InChI, PubChem, GO) | left out, with one message naming each database and the number of species (2026-10-28) |
| species notes (MINERVA's Name, Synonyms, Charge text) | left out but for a family's lines (`annotation.from_notes`) |
| line colours, font sizes (a 30 pt title on a 12 pt map) | left out: our yEd style, the map's one font size |

## The forward direction (GraphML -> CellDesigner) stays with our symbols

User, 2026-10-16: going from GraphML to CellDesigner never brings back CellDesigner's extra
kinds (receptor, ion channel, truncated, transport, association, ion, drug class...): our
glyphs are written as CellDesigner's plain ones (generic protein, state transition, simple
molecule). The backward direction is a one-way normalisation of those kinds onto our set.
Only arcs between entities (reduced notation) need CellDesigner's reduced types, for maps
that mix Activity Flow into Process Description. One SBGN stimulation arc in yEd stands
for both POSITIVE_INFLUENCE and REDUCED_PHYSICAL_STIMULATION in CellDesigner; written back as
REDUCED_PHYSICAL_STIMULATION, the SBGN arrowhead (user, 2026-10-20, docs/CELLDESIGNER.md). Rules, not training: the
converter needs one example of each case (the component sheet has them) and real mixed maps
only to check against.

## Questions for the user

All answered 2026-10-16 (in the rows above): the table is settled.

- **Q1** Receptor, ion channel, truncated protein: a macromolecule with a unit of information
  naming it (as cd2sbgnml, so the kind survives a round trip back to CellDesigner), or a
  plain macromolecule?
- **Q2** Ion channel open/closed as a state variable (cd2sbgnml), or left out?
- **Q3** ION and DRUG: simple chemical, with a "drug" unit for drugs (cd2sbgnml)? Our drug
  maps (aspirin) draw drugs as plain simple chemicals.
- **Q4** Phenotype comes back as Phenotype. Should anything become Perturbation or Submap
  (e.g. by a name or note)?
- **Q5** Truncation: Dissociation (cd2sbgnml) or a plain Process with the truncated protein
  as product?
- **Q6** Unknown catalysis/inhibition (dashed in CellDesigner): the plain arc, or the arc
  dashed in yEd to keep the "unknown"?
- **Q7** Transcriptional/translational activation and inhibition: stimulation and inhibition
  arcs (proposal; cd2sbgnml left a TODO)?
- **Q8** Reduced notation: keep the entity-to-entity arcs (as cd2sbgnml, and as our forward
  converter for stimulation), draw each through an added omitted process to stay valid PD,
  or leave them out with a warning?
- **Q9** Hypothetical species (dashed border in CellDesigner): dashed border in yEd, or a
  plain glyph with a warning?
- **Q10** Active species ("activated", dotted outer border): a state variable "active" (as
  our maps mark activity), or left out?
- **Q11** Protein binding regions and gene/RNA regions (coding, regulatory, transcription
  starting site): units of information with the region's name, or left out? Modification
  sites become state variables in any case.

## Known faults, not fixed yet

Found 2026-10-18 by the routing experiment (in the working repository of the maps), on the PD map
submaps in `tests/external/pd-map/submaps/` and AsthmaMap's PD02 in `tests/external/asthmap/submaps/`:

- **Added links lose their bends**: "edit points of an added link left out" (pd-autophagy 16
  links, pd-histamine-signalling 2). Needs a small CellDesigner file with an added reactant or
  product link drawn with bends, saved by CellDesigner, before the format is read.
- **SBGN-ML writer stops on a family member without an HGNC symbol** (pd-autophagy):
  `annotation.miriam` reads `p['HGNC symbol']`, KeyError. The website's converter page fails
  the same way on this file (CellDesigner -> SBGN-ML). Fix: a member without the symbol gives
  only the identifiers it has.

{% endraw %}

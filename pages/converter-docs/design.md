---
layout: converter-docs
title: "Design principles"
permalink: /converter/docs/design/
sitemap: false
noindex: true
---
{% raw %}

The decisions that shape the converter, one record each: when it was taken, why, what follows from it.
A record is never deleted. When a later decision replaces one, its status says so and names the new
record. Questions still open are in [Open questions](/converter/docs/decisions/), the criteria for
judging a decision there too.

## D1. Maps only

**2026-10-19, accepted.** **Context**: some formats carry a drawing (yEd, CellDesigner, SBGN-ML, SBML
with layout), some only the biology (BioPAX, SBML without layout). **Decision**: every route starts from
a map. Formats without a drawing are written, never read. Making a map from them is the work of the
human-like layout project. **Consequences**: no layout algorithm in the converter. SBML with layout is
read and written, SBML without layout and BioPAX are export only.

## D2. Biology and drawing apart

**2026-10-19, accepted.** **Context**: v1 had only the drawing, one node per alias, joined again by label
when CellDesigner was written, so a molecule drawn twice came back as two species. CellDesigner, SBML
layout and BioPAX all keep biology and drawing apart. **Decision**: the model holds the biology
(entities, reactions, annotation) and the drawing (boxes, arcs, bends), each glyph pointing to what it
draws. **Consequences**: one CellDesigner species per entity, each drawn box an alias of it. The biology
alone is what a BioPAX or SBML export writes.

## D3. The entity key

**2026-10-19, accepted.** **Context**: yEd and SBGN-ML hold only a drawing, so the entities must be
found in it. **Decision**: two boxes are one entity when they share identity, state, compartment and
glyph class, the principle of SBGN's clone markers. Identity is the identifier where there is one (HGNC,
UniProt, ChEBI), else the label. ChEBI's conjugate acids and bases are joined from a table kept in the
repository. **Consequences**: identifiers take over from labels (ERK1 and MAPK3 with one UniProt are one
entity). A substance under two unlinked identifiers stays two (an open issue).

## D4. Readers read only what the file says

**2026-10-19, accepted; extended 2026-10-24.** **Context**: a reader that guesses what the file meant,
or recovers what a program changed, ties the converter to one program's behaviour. **Decision**: a reader
reads the file as it is. A file saved by Newt, CellDesigner or yEd is read as any file of its format,
whatever made it, and what the program changed stays changed (2026-10-24, for Newt). **Consequences**: no
recovery of the original map on the way back. The files for Newt are made so that Newt has little to
move, and that loop is measured.

## D5. Layout in one place, an adapter per target, writers that only write

**2026-10-19, accepted.** **Context**: in v1 the layout rules sat inside the CellDesigner writer, so
nothing could be reused or tested on its own. **Decision**: what every format shares is in
`layout.py`, what one target needs in its adapter (`style.py` for yEd, `cd_layout.py` for CellDesigner,
`newt_layout.py` for Newt), and the writers only write. **Consequences**: each rule is sorted as generic
or for one target. A new target is one more adapter and writer.

## D6. Conversion translates, tidying is an add-on

**2026-10-24, accepted; the add-on replaced by [D14](#d14-no-node-moved-the-process-glyph-and-ports-by-hidden-edit-points) the same day.** **Context**: moves made during conversion do not last over trips between yEd,
CellDesigner and Newt: the process glyph rule moved the iNOS receptor complexes 5 px on every pass.
**Decision**: adapters change sizes, ports, bends and arc ends, never a node's centre. Two exceptions,
each in the messages: the room for a complex's name in CellDesigner and Newt's margin (files for Newt
only). The moves that tidy lines are an add-on after the adapter (`cd_tidy.py`), CellDesigner only.
**Consequences**: the CellDesigner process glyph is to be held where yEd has the process by hidden edit
points (advanced layout). The tidy moves are to settle after one trip. Their default is open.

## D7. Two layouts: advanced and straight line

**2026-10-18, accepted; names 2026-10-19.** **Context**: one file that keeps the drawing, one that is
easy to lay out by hand. **Decision**: advanced keeps the input's drawing (ports and the bends that
matter) and is the recommended file. Straight line draws every arc from centre to centre. SBGN-ML
straight line from yEd keeps yEd's process positions (placing each process midway turned 50 of 350
Atlas processes, drawn as Ls in yEd, into diagonals). **Consequences**: the straight layout stays the
simple fallback, with no tricks: a modifier's arc may slant.

## D8. Plain SBGN-ML and SBGN-ML for Newt

**2026-10-21, accepted.** **Context**: Newt redraws compartments and aims every arc at a node's centre,
so a plain file changes when Newt opens it. **Decision**: the plain SBGN-ML is the SBGN-ML of the source,
compartments as drawn. Everything Newt needs is in the files for Newt only (`newt_layout.py`).
**Consequences**: two SBGN-ML files per layout. The file for Newt is the recommended one for now.

## D9. One report of messages

**2026-10-19, accepted.** **Context**: messages were printed by each writer in its own way. **Decision**:
every message has a kind (problem, left out, changed, warning, summary) and goes into one report per
file, read by the page, the command line and the tests. **Consequences**: a loss that is not in the
messages is a bug. Which kinds the page shows is open.

## D10. Offline and in the browser

**2026-10-16, accepted.** **Decision**: the converter runs in the browser (Pyodide) on the Converter
page, from a copy of the code, and needs no network: tables it needs (ChEBI conjugates, yEd templates)
are kept in the repository. **Consequences**: no web service is called during conversion. A table is
remade by hand when maps with new identifiers come in.

## D11. Rules from files the programs saved

**2026-10-13, accepted.** **Decision**: no file format is guessed. A convention comes from a small file
saved by the program itself (CellDesigner, Newt, yEd), and a rule is preferably read from a file drawn
by hand. **Consequences**: some issues wait on an example file.

## D12. Every change checked against the reference files

**2026-10-19, accepted.** **Decision**: every Atlas map, every official CellDesigner and SBGN-ML file and
every test file went through every route with v1 and is kept with its messages. A change compares them.
A change meant to alter output remakes them in the same commit and names what changed and why.
**Consequences**: the restructuring kept every file the same apart from changes named one by one.

## D13. Clone markers not written

**2026-10-22, accepted.** **Context**: 287 entities are drawn more than once on the 28 Atlas maps, and
the tools that show a map add clone markers themselves. **Decision**: the converter does not write them.
If it ever does, it does so always, never as an option. **Consequences**: a clone marker in an SBGN-ML
input is left out, with a message.

## D14. No node moved: the process glyph and ports by hidden edit points

**2026-10-24, accepted; as the default replaced by [D17](#d17-tidy-moves-the-default-again-no-move-in-development) the same day, the rules kept for "no move".** **Context**: D6 kept the tidy moves as an add-on. Once the process glyph sits
where yEd has the process and a line can reach a large node beside its centre, the two moves for those
cases have nothing left to do, and straightening a line a few px off level changes the source map, which
is the layout skill's work. **Decision**: the converter moves no node (the add-on `cd_tidy.py` and the
option to forbid moves removed). In the advanced layout CellDesigner gets edit points it draws over or
along, so nothing more shows: two points on the main line around the process glyph, where yEd has the
process further than 3 px from midway (`cd_layout.SHIFT`); one point level with a main line that yEd
draws into a larger node beside its centre, also more than 3 px off. Every added point lies at least 3 px
outside the nodes (`EDGE`; user, 2026-10-24: a point under a node showed the line running to its centre,
as CellDesigner draws lines over nodes), and the two around a process glyph at the same distance from it. **Consequences**: a line a few px
off level in yEd stays so in CellDesigner. GraphML -> CellDesigner -> GraphML moves 5 nodes of 438 by more
than 1 px (58 before, at most 3 px), and a second trip none (13 before). The way back drops the points
(`layout.visible`). The straight layout stays without them (D7). Room for a complex's name stays the one
exception in CellDesigner. The tidy moves stay as an option to compare ([D16](#d16-tidy-moves-as-an-option-to-compare)).

## D15. Multimers drawn as dimers, the count as a unit

**2026-10-24, accepted.** **Context**: CellDesigner draws a multimer as one shape per unit, the box 6 px
larger per unit beyond 2, so a tetramer grew and could reach its neighbours. **Decision**: the SBGN way:
every multimer is drawn as a dimer at yEd's size (homodimer 2), and a count beyond 2 is the unit of
information N:x on the alias (prefix N, label 3: AsthmaMap's form, never "free input"). The reader takes
N:x on a dimer as its count. **Consequences**: no node grows. MINERVA reads homodimer 2, and its drawing
of the unit is to be seen on upload.

## D16. Tidy moves as an option to compare

**2026-10-24, accepted; replaced by [D17](#d17-tidy-moves-the-default-again-no-move-in-development) the same day.** **Context**: the user found the advanced CellDesigner file with the tidy moves
close to what they do by hand, and wants to compare it with the files that move no node. **Decision**:
`cd_tidy.py` is back as an option, "CellDesigner (tidy)" (`-advanced-tidy.xml`, `--tidy`): the advanced
drawing as it was before D14 (the process glyph placed only for a modifier straight across, no added point
at a node) with the tidy moves. The default moves no node. **Consequences**: the option gives the files of
before D14 byte for byte, apart from multimers (D15). One more output per GraphML and SBGN-ML input.

## D17. Tidy moves the default again, no move in development

**2026-10-24, accepted; the modes and their names replaced by [D18](#d18-four-celldesigner-modes-named-for-what-they-do) the same day.** **Context**: the advanced file with the tidy moves gives the Metabolism Regulation
maps the look the user wants in CellDesigner and MINERVA, though the moves add up over round trips. Moving
no node is the aim, still being developed. **Decision**: CellDesigner (advanced) has the tidy moves again,
as before D14. "CellDesigner (no move)" (`-advanced-nomove.xml`, `--no-move`) is the advanced file that
moves no node (D14's rules), worked on until it can take over. Straight line moves no node either.
Multimers stay dimers with N:x (D15) in every file. **Consequences**: the advanced files are those of before
D14 byte for byte, apart from multimers. The no-move steps, each a file to compare: straight (no bends),
the advanced drawing without the moves (yEd's key bends, connection points, modifier routes; the "positions kept"
file of 2026-10-20 to 2026-10-24, not offered now), and no move (that drawing with process glyphs and ports
held by edit points).

## D18. Four CellDesigner modes, named for what they do

**2026-10-24, accepted, built.** **Context**: the modes compared on the 28 Atlas maps (orthogonal look one
way, round trips, edit points; QUALITY.md). **Decision**: four CellDesigner files from a GraphML or
SBGN-ML map, all kept: straight (lines between node centres), straight & bends (the input's key bends,
connection points and modifier routes), advanced (moved nodes: the tidy moves, the blue button), as drawn
(multi-bends: process glyphs and ports held by edit points). Only advanced moves entity nodes. Roles
(user, 2026-10-24): advanced is the main file, for a one-time conversion and as the base a CellDesigner
user keeps working on (a map developed in yEd, then edited in CellDesigner); straight & bends the fallback,
straight the simplest fallback; as drawn only for going back and forth between editors repeatedly.
**Consequences**: four buttons and `--layout straight|bends|advanced|drawn` (CellDesigner only for bends
and drawn). As drawn writes about 450 more edit points on the Atlas maps than the others (555 against
196-248, visible bends about the same), which a CellDesigner user has to clean when changing a reaction.
Developed only as far as its purpose needs (user, 2026-10-24: one person keeps one editor, so round trips
matter for two people in two editors, or a map returned to its CellDesigner owners): its process glyph
drift over round trips fixed (trip 2: 17 process glyphs on 10 maps, up to 27 px, then 6 on 6 maps, up to 10
px), then frozen. Not built until a real exchange shows the need: the points at large complexes for modifier
arcs and slanting lines. Advanced is where one-way quality is improved.

## D19. CellDesigner's unknown gate as ?, and the equivalence operator written as it

**2026-10-25, accepted, built.** **Context**: CellDesigner has a fourth logic gate, `BOOLEAN_LOGIC_GATE_UNKNOWN`,
drawn with a question mark (Osteoarthritis pd65: ten opioids into Opioid peptide, twice); the reader labelled its
yEd operator UNKNOWN, which no writer took back. SBGN and yEd's SBGN palette have no such gate; CellDesigner has
no equivalence operator, so that was left out of CellDesigner files. **Decision** (user, 2026-10-25): the unknown
gate is a yEd Operator labelled **?**, read and written both ways with CellDesigner (on a reaction's modifiers and
between entities). An equivalence operator (≡) is written to CellDesigner as the unknown gate, the best fit, its
line to the generic entity a dashed stimulation (`UNKNOWN_REDUCED_PHYSICAL_STIMULATION`, as for every dashed
stimulation out of a gate). **Consequences**: a ≡ that goes to CellDesigner comes back as ?, not ≡ (the file keeps
no mark of it). SBGN-ML has no glyph for ?: the gate and its arcs are left out with a message (an open question,
[Issues](/converter/docs/issues/)).

## D20. A complex's name at the bottom in GraphML

**2026-10-25, accepted, built.** **Context**: the GraphML writer copied yEd's complex template, which puts the name
at the top inside the complex, while CellDesigner writes it at the bottom. **Decision** (user, 2026-10-25): in every
GraphML the converter writes, a complex with members has its name at the bottom inside it (yEd's internal label
model, position bottom, no border distance, as close to the border as CellDesigner draws it). A complex without
members keeps its name in the middle. **Consequences**: CellDesigner files keep about 20 px under the lowest member,
enough for the name (82 of 88 named complexes in the reference files). SBGN-ML and Newt files keep 12 to 15 px
there, so the name touches the lowest member in 155 of 269 (it touched the top member before too). The
conversion leaves that as it is (user, 2026-10-25: a conversion changes as little as possible; the one deliberate
exception is the small moves of the advanced CellDesigner file, which save fixing by hand): the layout skill's
complex packing (`standardise.py`) gives the name its room at the bottom.


{% endraw %}

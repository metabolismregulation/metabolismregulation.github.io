# The map between a reader and a writer: SBGN glyphs and arcs with their geometry,
# independent of the file format. Coordinates are absolute, in the units of the source
# (yEd: one unit per pixel of a 1:1 export), y down.
from dataclasses import dataclass, field
from functools import cached_property

# glyph at an arc's target: None (consumption, logic arc), or one of these
HEADS = ('production', 'catalysis', 'inhibition', 'modulation', 'stimulation', 'trigger')


@dataclass
class Node:
    id: str
    kind: str          # SBGN glyph: Macromolecule, SimpleChemical, Complex, Process, Operator, Compartment, ...
    box: tuple         # x, y, w, h
    labels: list       # label texts, the name first
    parent: str = None  # enclosing complex or compartment
    fill: str = None   # '#RRGGBB' or '#RRGGBBAA'
    states: list = field(default_factory=list)  # state variables: (text, rx, ry), place as offset from the centre in node widths and heights
    units: list = field(default_factory=list)   # units of information: ct:gene, N:4, ...
    count: int = 1     # multimer: number of units (2 when drawn as a multimer without N:x)
    label_at: tuple = None  # compartment: top left of its name, relative to the box
    data: dict = field(default_factory=dict)  # yEd node data by name: url, annotation (HGNC symbol, UniProt, ...)
    dashed: bool = False  # dashed border: a hypothetical entity (CellDesigner)
    outline: str = None  # the plain yEd shape it was read from by its outline (not the SBGN palette)
    species: str = None  # the entity the file says the glyph draws (CellDesigner species), if it says one
    font: float = None  # its label's font size, where the file gives one (CellDesigner, Newt): style.reasons


@dataclass
class Arc:
    id: str
    source: str
    target: str
    head: str = None    # see HEADS
    tail: bool = False  # an arrowhead at the source as well
    points: list = field(default_factory=list)  # bends
    source_at: tuple = (0.0, 0.0)  # where the arc leaves its source, from the source's centre
    target_at: tuple = (0.0, 0.0)  # where it meets its target, from the target's centre
    dashed: bool = False  # a dashed line: unknown catalysis, inhibition, influence (CellDesigner)


@dataclass
class Map:
    name: str
    nodes: dict  # id -> Node, in the order of the file
    arcs: list

    @cached_property
    def biology(self):  # what the drawing means (biology.py); a changed map is a new Map
        from .biology import build
        return build(self)


# The biology a map draws (biology.build): entities and what happens to them, each pointing
# to the glyphs (Node and Arc ids above) that draw it. An entity is a node with properties and
# property records, as SBGN PD describes an entity pool and momapy models it (sbgn.pd.model: a
# StateVariable(value, variable), a UnitOfInformation(prefix, value), subunits; annotations beside
# the model as qualifier and resource): what a conversion must keep (check.content, user 2026-10-22).
@dataclass(frozen=True, order=True)
class StateVariable:
    value: str                 # P, Ac, active, or '' for a site drawn unmodified
    variable: str = None       # the site: S505 (a state variable P@S505, or the property PTM)


@dataclass(frozen=True, order=True)
class UnitOfInformation:
    value: str                 # gene, mRNA, precursor; the multimer count N:x is the key's cardinality
    prefix: str = None         # ct; None for free text


@dataclass(frozen=True, order=True)
class Annotation:
    qualifier: str             # is (the entity's own identifier), hasVersion (a family member's)
    database: str              # HGNC, HGNC symbol, UniProt, ChEBI
    id: str


@dataclass(frozen=True, order=True)
class Member:                  # a family member: its name, identifiers and sites
    label: str
    annotations: tuple = ()
    sites: tuple = ()


@dataclass
class Entity:
    id: str
    key: tuple         # (compartment, identity, class, state): two glyphs with one key draw one entity
    glyphs: list       # the nodes drawing it
    inside: str = None  # the complex entity it is a member of
    names: frozenset = frozenset()          # its glyphs' labels
    state_variables: tuple = ()              # StateVariable, sorted, as many as a glyph draws
    units: frozenset = frozenset()           # UnitOfInformation
    annotations: frozenset = frozenset()     # Annotation
    family: str = None                       # a family's name (property Family)
    members: frozenset = frozenset()         # Member, a family's members


@dataclass
class Reaction:
    id: str            # the process node
    reactants: list    # entity ids; a reversible process has none, its products are both sides
    products: list
    modifiers: list    # (entity id, head)
    gates: list        # (operator label, [entity ids], head): a logic gate on the process


@dataclass
class Influence:       # an arc between entities, with or without a logic gate
    id: str            # the arc
    sources: list      # entity ids, or (operator label,) for a gate inside the gate
    target: str
    head: str          # see HEADS; None for an equivalence
    gate: str = None   # operator label (AND, OR, NOT, ≡)


@dataclass
class Biology:
    entities: dict     # id -> Entity
    reactions: list
    influences: list
    glyph: dict        # node id -> entity id
    notes: list        # what the entity key could not settle (one label, two identifiers)
    compartments: dict = None  # compartment name -> the compartment around it (SBML's outside; None: none)

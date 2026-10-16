# The map between a reader and a writer: SBGN glyphs and arcs with their geometry,
# independent of the file format. Coordinates are absolute, in the units of the source
# (yEd: one unit per pixel of a 1:1 export), y down.
from dataclasses import dataclass, field

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

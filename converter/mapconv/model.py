from dataclasses import dataclass, field
from functools import cached_property

HEADS = ('production', 'catalysis', 'inhibition', 'modulation', 'stimulation', 'trigger')


@dataclass
class Node:
    id: str
    kind: str
    box: tuple
    labels: list
    parent: str = None
    fill: str = None
    line: str = None
    weight: float = None
    states: list = field(default_factory=list)
    units: list = field(default_factory=list)
    count: int = 1
    label_at: tuple = None
    data: dict = field(default_factory=dict)
    dashed: bool = False
    border: bool = True
    outline: str = None
    species: str = None
    font: float = None
    small: float = None


@dataclass
class Arc:
    id: str
    source: str
    target: str
    head: str = None
    tail: bool = False
    points: list = field(default_factory=list)
    source_at: tuple = (0.0, 0.0)
    target_at: tuple = (0.0, 0.0)
    dashed: bool = False


@dataclass
class Map:
    name: str
    nodes: dict
    arcs: list

    @cached_property
    def biology(self):
        from .biology import build
        return build(self)


@dataclass(frozen=True, order=True)
class StateVariable:
    value: str
    variable: str = None


@dataclass(frozen=True, order=True)
class UnitOfInformation:
    value: str
    prefix: str = None


@dataclass(frozen=True, order=True)
class Annotation:
    qualifier: str
    database: str
    id: str


@dataclass(frozen=True, order=True)
class Member:
    label: str
    annotations: tuple = ()
    sites: tuple = ()


@dataclass
class Entity:
    id: str
    key: tuple
    glyphs: list
    inside: str = None
    names: frozenset = frozenset()
    state_variables: tuple = ()
    units: frozenset = frozenset()
    annotations: frozenset = frozenset()
    family: str = None
    members: frozenset = frozenset()


@dataclass
class Reaction:
    id: str
    reactants: list
    products: list
    modifiers: list
    gates: list


@dataclass
class Influence:
    id: str
    sources: list
    target: str
    head: str
    gate: str = None
    dashed: bool = False


@dataclass
class Biology:
    entities: dict
    reactions: list
    influences: list
    glyph: dict
    notes: list
    compartments: dict = None

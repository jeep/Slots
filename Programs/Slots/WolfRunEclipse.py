from dataclasses import dataclass, field

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


@dataclass(repr=False, eq=False)
class WolfRunEclipsePlay(StateHelperPlay):
    """State helper for WRE"""
    machine: Machine = Machine("Wolf Run Eclipse", "Wolf Run Eclipse/Cats Run Serengeti")
    state_data: dict = field(init=False, default_factory = lambda: {"mega": None, "major": None, "minor": None, "mini": None})
    _state: str = field(init=False)

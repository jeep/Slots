from dataclasses import dataclass, field

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


@dataclass(repr=False, eq=False)
class RegalLinkPlay(StateHelperPlay):
    """State helper for Regal Link"""
    machine: Machine = Machine("Regal Link", "Regal Link")
    state_data: dict = field(init=False, default_factory = lambda: {
        "Diamond": None, "Emerald": None, "Amethyst": None, "Sapphire": None, "Amber": None, 
        "Gray Cash Wilds": None})
    _state: str = field(init=False)

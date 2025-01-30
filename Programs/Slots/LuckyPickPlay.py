from dataclasses import dataclass, field

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


@dataclass(repr=False, eq=False)
class LuckyPickPlay(StateHelperPlay):
    machine: Machine = Machine("Lucky Pick", "Lucky Pick")
    state_data: dict = field(init=False,
                             default_factory=lambda: {"+1fg": None, "+2fg": None, "+3fg": None, "+1wild": None,
                                                      "+1mult": None})
    _state: str = field(init=False)

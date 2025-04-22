from dataclasses import dataclass, field

from .Machine import Machine
from Programs.Slots.Play import Play


@dataclass(repr=False, eq=False)
class FreePlay(Play):
    """To add free play"""
    machine: Machine = Machine("Free Play", "Non-AP")
    play_type: str = field(default='Non-Play', init=False)
    _start_image: str = field(default=None, init=False)
    _addl_images: list[str] = field(default=None, init=False)
    _end_image: str = field(default=None, init=False)

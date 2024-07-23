import ttkbootstrap as ttk
import tkinter as tk


from dataclasses import dataclass, field
import json
from .EntryField import EntryField
from .Machine import Machine
from .Play import Play

@dataclass(repr=False, eq=False)
class PinwheelPrizesPlay(Play):
    machine: Machine = Machine("Pinwheel Prizes", "Pinwheel Prizes")
    state_data: dict = field(init=False, default_factory = lambda: {"Golds": None, "10:1s": None})
    _state: str = field(init=False)

    def get_entry_fields(self) -> list:
        return [EntryField(label='Golds G->R', callback=self.set_fs), 
                EntryField(label='10:1 G->R', callback=self.set_large),
                ]

    def set_fs(self, val: int) -> None:
        self.state_data["Golds"] = val

    def set_large(self, val: int) -> None:
        self.state_data["10:1s"] = val

    @property
    def state(self) ->str:
        rv = ""
        if self._state:
            rv = f"{self._state}; " 
        if self.state_data["Golds"]:
            individual = [int(i) for i in list(self.state_data["Golds"])]
            tot = sum(individual)
            rv = f'{rv}{tot} {self.state_data["Golds"]}'
        if self.state_data["10:1s"]:
            rv = f'{rv}/{self.state_data["10:1s"]}'
        return rv

    @state.setter
    def state(self, state):
        self._state = state

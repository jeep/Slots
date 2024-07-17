from dataclasses import dataclass, field
import json
from .EntryField import EntryField
from .Machine import Machine
from .Play import Play

@dataclass(repr=False, eq=False)
class LuckyWealthCatPlay(Play):
    machine: Machine = Machine("Lucky Wealth Cat", "Lucky Buddha/Lucky Wealth Cat")
    state_data: dict = field(init=False, default_factory = lambda: {"7xCat": None, "6xFish": None, "5xTree": None, "3xA": None, "3xK": None, "3xQ": None})
    _state: str = field(init=False)

    def __post_init__(self):
        print("Made a LWC play:", self.machine, " ", type(self.machine))

    
    def get_entry_fields(self) -> list:
        return [EntryField(label='7xCat', callback=self.set_cat_data),
                EntryField(label='6xFish', callback=self.set_fish_data),
                EntryField(label='5xTree', callback=self.set_tree_data),
                EntryField(label='3xA', callback=self.set_a_data),
                EntryField(label='3xK', callback=self.set_k_data),
                EntryField(label='3xQ', callback=self.set_q_data)]

    def set_cat_data(self, val: int) -> None:
        self.state_data["7xCat"] = val

    def set_fish_data(self, val: int) -> None:
        self.state_data["6xFish"] = val

    def set_tree_data(self, val: int) -> None:
        self.state_data["5xTree"] = val

    def set_a_data(self, val: int) -> None:
        self.state_data["3xA"] = val

    def set_k_data(self, val: int) -> None:
        self.state_data["3xK"] = val

    def set_q_data(self, val: int) -> None:
        self.state_data["3xQ"] = val

    @property
    def state(self) ->str:
        rv = {k: v for k,v in self.state_data.items() if v is not None}
        if not len(rv):
            return self._state

        if self._state:
            return ";".join([self._state, json.dumps(rv)])
        return json.dumps(rv)

    @state.setter
    def state(self, state):
        self._state = state

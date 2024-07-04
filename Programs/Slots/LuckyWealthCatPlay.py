import json
from Programs.Slots.EntryField import EntryField
from Programs.Slots.Machine import Machine
from Programs.Slots.Play import Play


class LuckyWealthCatPlay(Play):
    def __init__(self) -> None:
        super().__init__(Machine("Lucky Wealth Cat", "Lucky Buddha/Lucky Wealth Cat"))
        self._state_data={"7xCat": None, "6xFish": None, "5xTree": None, "3xA": None, "3xK": None, "3xQ": None}

    def get_entry_fields(self) -> list:
        return [EntryField(label='7xCat', field_type="int", val=self.cat_data),
                EntryField(label='6xFish', field_type="int", val=self.fish_data),
                EntryField(label='5xTree', field_type="int", val=self.tree_data),
                EntryField(label='3xA', field_type="int", val=self.a_data),
                EntryField(label='3xK', field_type="int", val=self.k_data),
                EntryField(label='3xQ', field_type="int", val=self.q_data)]

    def cat_data(self, val: int) -> None:
        self._state_data["7xCat"] = val

    def fish_data(self, val: int) -> None:
        self._state_data["6xFish"] = val

    def tree_data(self, val: int) -> None:
        self._state_data["5xTree"] = val

    def a_data(self, val: int) -> None:
        self._state_data["3xA"] = val

    def k_data(self, val: int) -> None:
        self._state_data["3xK"] = val

    def q_data(self, val: int) -> None:
        self._state_data["3xQ"] = val

    @property
    def state(self) ->str:
        rv = {}
        for k,v in self._state_data.items():
            if v is None:
                continue
            rv[k] = v
        if len(rv) > 0:
            if len(self._state):
                return ";".join([self._state, json.dumps(rv)])
            return json.dumps(rv)
        return self._state
    @state.setter
    def state(self, state):
        self._state = state

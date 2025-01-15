import json
from dataclasses import dataclass, field

from .EntryField import EntryField
from .Play import Play


@dataclass(repr=False, eq=False)
class StateHelperPlay(Play):
    """constructor"""
    _state: str = field(init=False)
    state_data: dict = None

    def get_entry_fields(self) -> list:
        rv = []
        for k in self.state_data.keys():
            cb = self.make_setter(k)
            rv.append(EntryField(label=k, callback=cb))
        return rv

    def make_setter(self, key):
        """make the setter"""
        def s():
            return key

        return lambda val: self.set_val(s(), val)

    def set_val(self, key, val):
        """set the value of of the key in state data"""
        self.state_data[key] = val

    @property
    def state(self) -> str:
        """return the state as a string"""
        rv = {k: v for k, v in self.state_data.items() if v and v != ""}
        if not len(rv):
            return self._state

        if self._state.strip() != "":
            return "; ".join([self._state.strip(), json.dumps(rv)])
        return json.dumps(rv)

    @state.setter
    def state(self, state):
        self._state = state.strip()

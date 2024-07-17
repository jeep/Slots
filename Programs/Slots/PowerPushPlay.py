from dataclasses import dataclass, field
import json
from .EntryField import EntryField
from .Machine import Machine
from .Play import Play

@dataclass(repr=False, eq=False)
class PowerPushPlay(Play):
    machine: Machine = Machine("Power Push", "Power Push")
    state_data: dict = field(init=False, default_factory = lambda: {"Stacks": None, "Diamonds": None, "Gems": None, "Royals": None, "Majors": None, "Minors": None, "Free Spins": None, "Minis": None, "Balls": None, "Pearls": None, "+2 Pushes": None})
    _state: str = field(init=False)

    def get_entry_fields(self) -> list:
        return [EntryField(label='Stacks', callback=self.set_stacks),
                EntryField(label='Diamonds', callback=self.set_diamonds),
                EntryField(label='Emerald/Rubys', callback=self.set_gems),
                EntryField(label='Royals', callback=self.set_royals),
                EntryField(label='Majors', callback=self.set_majors),
                EntryField(label='Minors', callback=self.set_minors),
                EntryField(label='Free Spins', callback=self.set_free_spins),
                EntryField(label='Minis', callback=self.set_minis),
                EntryField(label='Balls', callback=self.set_balls),
                EntryField(label='Pearls', callback=self.set_pearls),
                EntryField(label='+2 Pushes', callback=self.set_pushes)]

    def set_stacks(self, val: int) -> None:
        self.state_data["Stacks"] = val

    def set_diamonds(self, val: int) -> None:
        self.state_data["Diamonds"] = val

    def set_gems(self, val: int) -> None:
        self.state_data["Gems"] = val

    def set_royals(self, val: int) -> None:
        self.state_data["Royals"] = val

    def set_majors(self, val: int) -> None:
        self.state_data["Majors"] = val

    def set_minors(self, val: int) -> None:
        self.state_data["Minors"] = val

    def set_free_spins(self, val: int) -> None:
        self.state_data["Free Spins"] = val

    def set_minis(self, val: int) -> None:
        self.state_data["Minis"] = val

    def set_balls(self, val: int) -> None:
        self.state_data["Balls"] = val

    def set_pearls(self, val: int) -> None:
        self.state_data["Pearls"] = val

    def set_pushes(self, val: int) -> None:
        self.state_data["Pushes"] = val

    def _append_tray_value_to_state(orig, str_to_append):
        if orig == "":
            return str_to_append
        else:
            if orig[-1] != ';':
                return ', '.join([orig, str_to_append])
            else: 
                return f'{orig} {str_to_append}'


    @property
    def state(self) ->str:
        filtered = {k: v for k,v in self.state_data.items() if v and k != 'Stacks'}
        stacks = self.state_data['Stacks'] if self.state_data['Stacks'] else '?'
        rv = f"{stacks} Stacks;"
        if not len(filtered):
            return self._state

        if self._state:
            rv = f"{self._state}; {rv}" 
        for k, v in filtered.items():
            rv = PowerPushPlay._append_tray_value_to_state(rv, f'{v} {k}')
        
        return rv

    @state.setter
    def state(self, state):
        self._state = state

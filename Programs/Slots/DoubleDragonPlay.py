from dataclasses import dataclass, field

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


@dataclass(repr=False, eq=False)
class DoubleDragonPlay(StateHelperPlay):
    machine: Machine = Machine("Double Dragon Jin Long Jin Bao", "Double Dragon Jin Long Jin Bao")

    valid_multipliers = ["x1", "x2", "x3", "x5", "x10"]
    state_data: dict = field(init=False,
                             default_factory=lambda: {
                                 "Top Spins": None, "Top x1": None, "Top x2": None,
                                 "Top x3": None, "Top x5": None, "Top x10": None,
                                 "Bot Spins": None, "Bot x1": None, "Bot x2": None,
                                 "Bot x3": None, "Bot x5": None, "Bot x10": None})

    @property
    def state(self) -> str:
        rv = {k: v for k, v in self.state_data.items() if v and v != ""}
        if not len(rv):
            return self._state

        rv = ""
        if self._state.strip() != "":
            rv = self._state.strip()

        for area in ["Top", "Bot"]:
            if rv.strip() != "":
                rv += "; "

            spins = self.state_data[f'{area} Spins']
            if spins is None:
                spins = "?"
            rv+= f"{area}({spins}): "

            for m in self.valid_multipliers:
                area_mult = f"{area} {m}"
                if area_mult in self.state_data and self.state_data[area_mult]:
                    if rv[-1] != " ":
                        rv += ", "
                    rv += f" {self.state_data[area_mult]} {m}"

        return rv

    @state.setter
    def state(self, state):
        self._state = state.strip()

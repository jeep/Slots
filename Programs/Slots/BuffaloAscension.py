import json
from dataclasses import dataclass, field

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


ascensions_str = "Ascensions (ex. 333 is max)"
r2_str = "Top of R2 (S, SS, FG)"
r3_str = "Top of R3"
r4_str = "Top of R4"

@dataclass(repr=False, eq=False)
class BuffaloAscensionPlay(StateHelperPlay):
    machine: Machine = Machine("Buffalo Ascension", "Buffalo Ascension")
    state_data: dict = field(init=False,
                             default_factory=lambda: {ascensions_str: None, r2_str: None, 
                                                      r3_str: None, r4_str: None})

    @property
    def state(self) -> str:
        rv = {k: v for k, v in self.state_data.items() if v and v != ""}
        if not rv:
            return self._state

        ascensions = self.state_data[ascensions_str]
        if not ascensions:
            ascensions = "?"

        ways = 16
        if (len(ascensions) == 3 and ascensions.isdigit()):
            for r in list(ascensions):
                ways = ways * (4 + int(r))
        else:
            ways = "?"

        prizes = f"{self.state_data[r2_str]}-{self.state_data[r3_str]}-{self.state_data[r4_str]}"
        rv = {"ways": ways,
              "ascensions": self.state_data[ascensions_str], 
              "prizes": prizes} 

        if self._state.strip() != "":
            return "; ".join([self._state.strip(), json.dumps(rv)])

        return json.dumps(rv)

    @state.setter
    def state(self, state):
        self._state = state.strip()

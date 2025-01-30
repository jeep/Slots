import json
from dataclasses import dataclass, field
from decimal import Decimal

from ttkbootstrap.dialogs import Messagebox

from .Machine import Machine
from .StateHelperPlay import StateHelperPlay


@dataclass(repr=False, eq=False)
class FrankensteinPlay(StateHelperPlay):
    """Class which includes Frankenstein state helper"""
    machine: Machine = Machine("Frankenstein", "Frankenstein")
    state_data: dict = field(init=False,
                             default_factory=lambda: {"tl": None, "tm": None, "tr": None, "ml": None, "mm": None,
                                                      "mr": None, "bl": None, "bm": None, "br": None})
    ev_mult: list = field(default_factory=lambda: [0.09416, 0.32996, 0.56598,
                                                   0.50230, 0.83143, 0.57439,
                                                   0.29475, 0.27778, 0.21183,
                                                   0.16668, 0.18126, 0.16008])
    base_head_ev = 4.18942

    @staticmethod
    def d(in_str):
        two_places = Decimal(10) ** -2
        return Decimal(in_str).quantize(two_places)

    labels = {
        (d("0.6"), "1cent"): [1000, 500, 300, 200, 150, 125, 100, 75, 60],
        (d("1.2"), "1cent"): [2000, 1000, 600, 400, 300, 250, 200, 150, 120],
        (d("1.8"), "1cent"): [3000, 1500, 900, 600, 450, 375, 300, 225, 180],
        (d("3"), "1cent"): [5000, 2500, 1500, 1000, 750, 625, 500, 375, 300],
        (d("6"), "1cent"): [10000, 5000, 3000, 2000, 1500, 1250, 1000, 750, 600],
        (d("1.2"), "2cent"): [1000, 500, 300, 200, 150, 125, 100, 75, 60],
        (d("2.4"), "2cent"): [2000, 1000, 600, 400, 300, 250, 200, 150, 120],
        (d("3.6"), "2cent"): [3000, 1500, 900, 600, 450, 375, 300, 225, 180],
        (d("6"), "2cent"): [5000, 2500, 1500, 1000, 750, 625, 500, 375, 300],
        (d("12"), "2cent"): [10000, 5000, 3000, 2000, 1500, 1250, 1000, 750, 500],
        (d("1.5"), "5cent"): [500, 250, 150, 100, 75, 60, 50, 40, 30],
        (d("3"), "5cent"): [1000, 500, 300, 200, 150, 120, 100, 60, 90],
        (d("4.5"), "5cent"): [1500, 750, 450, 300, 225, 180, 150, 120, 90],
        (d("7.5"), "5cent"): [2500, 1250, 750, 500, 375, 300, 250, 200, 150],
        # (d("max"), "5cent"): {},
        (d("3"), "10cent"): [500, 250, 150, 100, 75, 60, 50, 40, 30],
        (d("6"), "10cent"): [1000, 500, 300, 200, 150, 120, 100, 80, 60],
        (d("9"), "10cent"): [1500, 750, 450, 300, 225, 180, 150, 120, 90],
        (d("15"), "10cent"): [2500, 1250, 750, 500, 375, 300, 250, 200, 150],
        # (d("max"), "10cent"): {},
        (d("5"), "$1"): [75, 40, 25, 20, 15, 10, 8, 6, 5],
        (d("10"), "$1"): [150, 80, 50, 40, 30, 20, 16, 12, 10],
        (d("15"), "$1"): [225, 120, 75, 60, 45, 30, 24, 18, 15],
        (d("20"), "$1"): [300, 160, 100, 80, 60, 40, 32, 24, 20],
        (d("25"), "$1"): [375, 200, 125, 100, 75, 50, 40, 30, 25],
        # (d("min"), "$2"): {},
        # (d("min2"), "$2"): {},
        (d("10"), "$2"): [150, 80, 50, 40, 30, 20, 16, 12, 10],
        (d("20"), "$2"): [160, 100, 80, 60, 40, 32, 24, 20],
        (d("50"), "$2"): [750, 400, 250, 200, 150, 100, 80, 60, 50],
    }

    def get_state_data(self):
        if not self.denom or not self.bet:
            Messagebox.show_error("You must set both the denom and bet first")
            return False
        if (FrankensteinPlay.d(self.bet), self.denom) not in self.labels:
            Messagebox.show_error(f"This combination of {self.bet} bet and {self.denom} denom is not known")
            return False

        state_labels = ["Maxi", "Minor", "Mini"]
        state_labels.extend(self.labels[(FrankensteinPlay.d(self.bet), self.denom)])
        self.state_data = dict(zip(state_labels, [None] * 12))
        return True

    def get_entry_fields(self) -> list:
        if self.get_state_data():
            return super().get_entry_fields()
        return []

    @property
    def state(self) -> str:
        ev = self.d(sum([mult * int(value if value is not None and value != "" else 1) for mult, value in
                         zip(self.ev_mult, self.state_data.values())]) / self.base_head_ev)
        rv = {k: int(v) for k, v in self.state_data.items() if v and v != ""}
        if not len(rv):
            return self._state

        john = sum(rv.values())
        dave = sum(rv.values()) + (9 - len(rv.keys()))

        if self._state.strip() != "":
            return "; ".join([self._state.strip(), json.dumps(rv), f" [j:{john}; d:{dave}; ev-Jan-2025:{ev}]"])
        return "; ".join([json.dumps(rv), f" [j:{john}; d:{dave}, ev-Jan-2025: {ev}]"])

    @state.setter
    def state(self, state):
        self._state = state.strip()

from dataclasses import dataclass, field
from Programs.Slots.Machine import Machine
from babel.numbers import format_currency 
from typing import Optional
from decimal import Decimal
import datetime
import pathlib

@dataclass(repr=False, eq=False)
class Play:
    machine: str 
    casino: str = None 
    start_time: datetime = datetime.MINYEAR
    _cash_in: list[Decimal] = field(default_factory=lambda: [])
    _bet: Decimal = None
    _play_type: str = None
    _state: str = ""
    note: str = None
    start_image: str = None
    addl_images: list[str] = field(default_factory=lambda: [])
    end_image: str = None
    _cash_out: Decimal = Decimal(0.0)

    @property
    def bet(self) -> Decimal:
        return self._bet
    @bet.setter
    def bet(self, bet: Decimal) -> None:
        self._bet = bet

    @property
    def state(self) -> str:
        return self._state
    @state.setter
    def state(self, state: str) -> None:
        self._state = state

    @property
    def play_type(self) -> Decimal:
        return self._play_type
    @play_type.setter
    def play_type(self, play_type: str) -> None:
        self._play_type = play_type

    @property 
    def initial_cash_in(self) -> Decimal:
        return self._cash_in[0]

    @property
    def cash_in(self) -> Decimal:
        return sum(self._cash_in)

    @property
    def cash_out(self) -> Decimal:
        return self._cash_out
    @cash_out.setter
    def cash_out(self, cash_out: Decimal) -> None:
        self._cash_out = cash_out

    @property
    def pnl(self) -> Decimal:
        return self.cash_out - self.cash_in

    def add_cash(self, cash: Decimal) -> None:
        self._cash_in.append(cash)
    
    def add_image(self, img: pathlib.Path) -> None:
        self.addl_images.append(img)

    def add_images(self, imgs: list[pathlib.Path]) -> None:
        self.addl_images.extend(imgs)

    def __str__(self):
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        images = [str(pathlib.PureWindowsPath(f)) for f in self.addl_images]
        return f"{self.casino},{start_date},{self.machine.get_name()},{format_currency(self.cash_in, 'USD', locale='en_US')},{format_currency(self.bet, 'USD', locale='en_US')},{self.play_type},\"{self.state}\",{format_currency(self.cash_out, 'USD', locale='en_US')},{format_currency(self.pnl, 'USD', locale='en_US')},\"{self.note}\",{self.machine.get_family()},{self.start_image},{self.end_image},{images}"
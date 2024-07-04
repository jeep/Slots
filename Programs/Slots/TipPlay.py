from dataclasses import dataclass, field
from Programs.Slots.Machine import Machine
from Programs.Slots.Play import Play
from babel.numbers import format_currency 
from typing import Optional
from decimal import Decimal
import datetime
import pathlib

@dataclass(repr=False, eq=False)
class TipPlay(Play):
    machine: Machine = field(default = Machine('Tip', 'Non-AP'), init = False)
    _bet: Decimal = field(default = None, init = False)
    _play_type: str =field(default = 'Tip', init = False)
    _cash_out: Decimal =field(default = Decimal(0.0), init = False)
    _state: str =field(default = "", init = False)
    _start_image: str =field(default = None, init = False)
    _addl_images: list[str] = field(default = None, init = False)
    _end_image: str =field(default =  None, init = False)

    @property
    def bet(self) -> Decimal:
        return self._bet

    @property
    def state(self) -> str:
        return self._state

    @property
    def play_type(self) -> Decimal:
        return self._play_type

    @property 
    def initial_cash_in(self) -> Decimal:
        return self._cash_in[0]

    @property
    def cash_out(self) -> Decimal:
        return self._cash_out

    def __str__(self):
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        note = f'"{self.note}"' if self.note else ""
        return f"{self.casino},{start_date},{self.machine.get_name()},{format_currency(self.cash_in, 'USD', locale='en_US')},,{self.play_type},,{format_currency(self.cash_out, 'USD', locale='en_US')},{format_currency(self.pnl, 'USD', locale='en_US')},{note},{self.machine.get_family()},,,"
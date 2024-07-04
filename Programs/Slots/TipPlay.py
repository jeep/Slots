from dataclasses import dataclass
from Programs.Slots.Machine import Machine
from Programs.Slots.Play import Play
from babel.numbers import format_currency 
from typing import Optional
from decimal import Decimal
import datetime
import pathlib

@dataclass
class TipPlay(Play):
    _casino: str
    _start_time: datetime
    _note: str = None
    _start_image: str = None
    _end_image: str = None
    _machine = Machine('Tip', 'Non-AP')
    _cash_in: list[Decimal] = [Decimal(0.00)]
    _cash_out: Decimal = Decimal(0.0)
    _state: str = ""
    _play_type: str = 'Tip'
    _bet: Decimal = None
    _addl_images: list[str] = []

    @property
    def bet(self) -> Decimal:
        return self._bet

    @property
    def state(self) -> str:
        return self._state

    @property
    def note(self) -> str:
        return self._note
    @note.setter
    def note(self, note: str) -> None:
        self._note = note

    @property
    def play_type(self) -> Decimal:
        return self._play_type

    @property 
    def initial_cash_in(self) -> Decimal:
        return self._cash_in[0]

    @property
    def cash_out(self) -> Decimal:
        return self._cash_out

    @property
    def start_image(self) -> str:
        return self._start_image
    @start_image.setter
    def start_image(self, start_image: str) -> None:
        self._start_image = start_image

    @property
    def end_image(self) -> str:
        return self._end_image
    @end_image.setter
    def end_image(self, end_image: str) -> None:
        self._end_image = end_image

    @property
    def addl_images(self) -> list[str]:
        return self._addl_images

    @property
    def pnl(self) -> Decimal:
        return self.cash_out - self.cash_in
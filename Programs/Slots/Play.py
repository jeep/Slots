from Programs.Slots.Machine import Machine
from babel.numbers import format_currency 
from typing import Optional
from decimal import Decimal
import datetime
import pathlib

class Play:
    _casino: str = None
    _start_time: datetime = datetime.MINYEAR
    _bet: Decimal = None
    _play_type: str = None
    _state: str = ""
    _note: str = None
    _start_image: str = None
    _end_image: str = None
    _cash_out: Decimal = Decimal(0.0)

    def __init__(self, machine : Machine) -> None:
        self._machine = machine
        self._cash_in: list[Decimal] = []
        self._addl_images: list[str] = []

    @property
    def casino(self) -> str:
        return self._casino
    @casino.setter
    def casino(self, casino: str) ->None:
        self._casino=casino

    @property
    def start_time(self) -> datetime.datetime:
        return self._start_time
    @start_time.setter
    def start_time(self, dt: datetime.datetime) -> None:
        self._start_time = dt

    @property
    def machine(self) -> Machine:
        return self._machine

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
    def note(self) -> str:
        return self._note
    @note.setter
    def note(self, note: str) -> None:
        self._note = note

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

    def add_cash(self, cash: Decimal) -> None:
        self._cash_in.append(cash)
    
    def add_image(self, img: pathlib.Path) -> None:
        self._addl_images.append(img)

    def add_images(self, imgs: list[pathlib.Path]) -> None:
        self._addl_images.extend(imgs)

    def __str__(self):
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        images = [str(pathlib.PureWindowsPath(f)) for f in self.addl_images]
        return f"{self._casino},{start_date},{self.machine.get_name()},{format_currency(self.cash_in, 'USD', locale='en_US')},{format_currency(self.bet, 'USD', locale='en_US')},{self.play_type},\"{self.state}\",{format_currency(self.cash_out, 'USD', locale='en_US')},{format_currency(self.pnl, 'USD', locale='en_US')},\"{self.note}\",{self.machine.get_family()},{self.start_image},{self.end_image},{images}"
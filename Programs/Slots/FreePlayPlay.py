from dataclasses import dataclass, field

from babel.numbers import format_currency

from Programs.Slots.Play import Play


@dataclass(repr=False, eq=False)
class FreePlay(Play):
    """To add free play"""
    play_type: str = field(default='Non-Play', init=False)
    _start_image: str = field(default=None, init=False)
    _addl_images: list[str] = field(default=None, init=False)
    _end_image: str = field(default=None, init=False)

    def __str__(self):
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        note = f'"{self.note}"' if self.note else ""
        return (f"{self.casino},{start_date},{self.machine.get_name()},"
                f"{format_currency(0.00, 'USD', locale='en_US')},,{self.play_type},,"
                f"{format_currency(self.cash_out, 'USD', locale='en_US')},"
                f"{format_currency(self.pnl, 'USD', locale='en_US')},{note},"
                f"{self.machine.get_family()},,,")

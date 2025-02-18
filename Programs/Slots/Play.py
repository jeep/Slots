import datetime
import pathlib
from dataclasses import dataclass, field
from decimal import Decimal

from babel.numbers import format_currency

from .Machine import Machine
from .Bonus import Bonus


def d(in_str):
    two_places = Decimal(10) ** -2
    return Decimal(in_str).quantize(two_places)


@dataclass
class HandPay:
    pay_amount: Decimal
    tip_amount: Decimal
    image: str = None
    addl_images: list[str] = field(default_factory=list)
    taxable: bool = True
    tax_rate: Decimal = d(0.27)

    @property
    def tax(self):
        tax = "0.00"
        if self.taxable:
            tax = d(self.tax_rate * self.pay_amount)
        return tax


@dataclass(repr=False, eq=False, kw_only=True)
class Play:
    machine: Machine
    casino: str = None
    session_date: datetime = None
    start_time: datetime = datetime.MINYEAR
    end_time: datetime = datetime.MINYEAR
    _cash_in: list[Decimal] = field(default_factory=list)
    bet: Decimal = None
    play_type: str = None
    denom: str = None
    state: str = ""
    note: str = None
    bonuses: list[Bonus] = field(default_factory=list)
    start_image: pathlib.Path = None
    addl_images: list[pathlib.Path] = field(default_factory=list)
    end_image: pathlib.Path = None
    cash_out: Decimal = Decimal(0.0)
    hand_pays: list[HandPay] = field(default_factory=list)

    @property
    def identifier(self) -> str:
        return f"{self.machine.get_name().replace(' ', '_')}-{self.bet}-{self.start_time.strftime('%Y-%m-%d-%H:%M:%S')}"

    @identifier.setter
    def identifier(self, ident):
        pass

    @property
    def initial_cash_in(self) -> Decimal:
        if self._cash_in:
            return self._cash_in[0]
        return Decimal(0.00)

    @property
    def cash_in(self) -> Decimal:
        return Decimal(sum(self._cash_in))

    @cash_in.setter
    def cash_in(self, val: Decimal) -> None:
        # JEEP: Why do I need to do this?
        if type(val) is Decimal:
            self._cash_in = [val]
        else:
            self._cash_in = [Decimal(0.00)]

    @property
    def pnl(self) -> Decimal:
        hps = sum(hp.pay_amount for hp in self.hand_pays)
        return self.cash_out + hps - self.cash_in


    def get_cash_entries(self):
        return self._cash_in

    
    def get_cash_entries_for_csv(self):
        """Get the string to use for cashin for CSV"""
        if len(self._cash_in) <=1:
            return f"{self.cash_in:.2f}"

        rv = "="
        rv += "+".join(str(ci) for ci in self.get_cash_entries())
        return rv

    def add_cash(self, cash: Decimal) -> None:
        if len(self._cash_in) == 1 and self._cash_in[0] == Decimal(0):
            self._cash_in[0] = cash
        else:
            self._cash_in.append(cash)

    def clear_cash_in(self) -> None:
        """Clears cash in"""
        self._cash_in.clear()

    def get_total_cash_out(self):
        rv = Decimal(0.0)
        for hp in self.hand_pays:
            rv += hp.pay_amount
        rv += self.cash_out
        return rv

    def cash_out_str(self):
        rv = ""
        if len(self.hand_pays):
            rv = "="
            hps = "+".join(str(hp.pay_amount) for hp in self.hand_pays)
            rv += hps
            rv += "+"
        rv += str(self.cash_out)
        return rv

    def add_image(self, img: pathlib.Path) -> None:
        if img not in self.addl_images:
            self.addl_images.append(img)

    def add_images(self, imgs: list[pathlib.Path]) -> None:
        for img in imgs:
            self.add_image(img)

    def make_hand_pay(self, payment, tip, image=None, addl_images=None):
        if not addl_images:
            addl_images = []
        self.hand_pays.append(HandPay(payment, tip, image, addl_images))

    def add_hand_pay(self, handpay: HandPay):
        self.hand_pays.append(handpay)

    def get_entry_fields(self):
        return None


    def get_csv_dict(self):
        """In progress, not working now. Get the output in CSV format"""
        return
        note = f"{self.note}"
        if len(self.bonuses) > 0:
            note += f"; {str(self.bonuses)}"

        # JEEP: This doesn't belong in this class
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        images = [str(pathlib.PureWindowsPath(f)) for f in self.addl_images]

        fieldnames = ['session id', 'casino', 'start time', 'machine', 'cash in', 'bet', 'play_type', 'denom', 'state', 'cash out', 'pnl', 'note', 'family', 'start image', 'end image', 'addl images', 'end time']

        session_id = self.session_date.strftime(r"%m/%d/%Y") 
        data=[{'session id': session_id,
               'casino': self.casino, 
               'start time': self.start_time, 
               'machine': self.machine.get_name(), 
               'cash in': self.get_cash_entries_for_csv(),
               'bet': format_currency(self.bet, 'USD', locale='en_US'), 
               'play type': self.play_type,
               'denom': self.denom,
               'state': self.state,
               'cash out': self.cash_out,
               'pnl': format_currency(self.pnl, 'USD', locale='en_US'),
               'note': note,
               'family': self.machine.get_family(), 
               'start image': self.start_image,
               'end image': self.end_image,
               'addl images': images,
               'end time': self.end_time
               }]

        for hp in self.hand_pays:
            if hp.tax > 0:
                tax = format_currency(hp.tax, 'USD', locale='en_US')
                images = hp.addl_images if hp.addl_images else ""
                rows.append((self.session_date.strftime(r"%m/%d/%Y"), self.casino, start_date, self.machine.get_name(),
                             tax, "", "Tax Consequence", self.denom,
                             format_currency(hp.pay_amount, 'USD', locale="en_US"), "", -1 * tax, tax,
                             self.machine.get_family(), hp.image, "", images, ""))
            if hp.tip_amount > 0:
                rows.append((self.session_date.strftime(r"%m/%d/%Y"), self.casino, start_date, self.machine.get_name(),
                             format_currency(hp.tip_amount, 'USD', locale='en_US'), "", "Tip", "", "",
                             format_currency(0.00, 'USD', locale='en_US'),
                             format_currency(-1 * hp.tip_amount, 'USD', locale='en_US'), "", self.machine.get_family(),
                             "", "", "", ""))
        return rows

    def get_csv_rows(self):
        """Get the output in CSV format"""
        note = f"{self.note}"
        if len(self.bonuses) > 0:
            note += f"; {str(self.bonuses)}"

        # JEEP: This doesn't belong in this class
        start_date = self.start_time.strftime(r"%m/%d/%Y")
        images = [str(pathlib.PureWindowsPath(f)) for f in self.addl_images]

        rows = [(self.session_date.strftime(r"%m/%d/%Y"), self.casino, self.start_time,
                 self.machine.get_name(), self.get_cash_entries_for_csv(),
                 format_currency(self.bet, 'USD', locale='en_US'), self.play_type, self.denom,
                 self.state, self.cash_out_str(),format_currency(self.pnl, 'USD', locale='en_US'),
                 note, self.machine.get_family(), self.start_image, self.end_image, images, self.end_time)]
        for hp in self.hand_pays:
            if hp.tax > 0:
                tax = format_currency(hp.tax, 'USD', locale='en_US')
                images = hp.addl_images if hp.addl_images else ""
                rows.append((self.session_date.strftime(r"%m/%d/%Y"), self.casino, start_date, self.machine.get_name(),
                             tax, "", "Tax Consequence", self.denom,
                             format_currency(hp.pay_amount, 'USD', locale="en_US"), "", -1 * tax, tax,
                             self.machine.get_family(), hp.image, "", images, ""))
            if hp.tip_amount > 0:
                rows.append((self.session_date.strftime(r"%m/%d/%Y"), self.casino, start_date, self.machine.get_name(),
                             format_currency(hp.tip_amount, 'USD', locale='en_US'), "", "Tip", "", "",
                             format_currency(0.00, 'USD', locale='en_US'),
                             format_currency(-1 * hp.tip_amount, 'USD', locale='en_US'), "", self.machine.get_family(),
                             "", "", "", ""))
        return rows

    def __str__(self):
        if self.start_time != datetime.MINYEAR:
            start_date = self.start_time.strftime(r"%m/%d/%Y")
        else:
            start_date = "??"
        images = [str(pathlib.PureWindowsPath(f)) for f in self.addl_images]
        note = f"{self.note}"
        if len(self.bonuses) > 0:
            note += f"; {str(self.bonuses)}"

        output_string = (f"{self.identifier},{self.casino},{start_date},{self.machine.get_name()},"
                         f"{self.get_cash_entries_for_csv()},"
                         f"{format_currency(self.bet, 'USD', locale='en_US')},{self.play_type},"
                         f"{self.denom},\"{self.state}\",{self.cash_out_str()},"
                         f"{format_currency(self.pnl, 'USD', locale='en_US')},\"{note}\","
                         f"{self.machine.get_family()},{self.start_image},{self.end_image},{images}")
        for hp in self.hand_pays:
            if hp.tax > 0:
                tax = format_currency(hp.tax, 'USD', locale='en_US')
                images = hp.addl_images if hp.addl_images else ""
                output_string += (f"\n{self.identifier},{self.casino},{start_date},{self.machine.get_name()},{tax},,"
                                  f"Tax Consequence,{self.denom},{format_currency(hp.pay_amount, 'USD', 
                                                                                  locale='en_US')},,-{tax},{tax},"
                                  f"{self.machine.get_family()},{hp.image},,{images}")
            if hp.tip_amount > 0:
                output_string += (f"\n{self.identifier},{self.casino},{start_date},{self.machine.get_name()},"
                                  f"{format_currency(hp.tip_amount, 'USD', locale='en_US')},,Tip,,,"
                                  f"{format_currency(0.00, 'USD', locale='en_US')},"
                                  f"{format_currency(-1 * hp.tip_amount, 'USD', locale='en_US')},,"
                                  f"{self.machine.get_family()},,,")
        return output_string

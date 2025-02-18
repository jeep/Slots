import datetime

from decimal import Decimal
import ttkbootstrap as ttk

from Scripts.LabelPairs.ComboboxLabel import ComboboxLabel
from Scripts.LabelPairs.EntryLabel import EntryLabel
from Scripts.LabelPairs.MoneyEntryLabel import MoneyEntryLabel
from Scripts.LabelPairs.LabelLabel import LabelLabel
from Scripts.LabelPairs.LargeEntryLabel import LargeEntryLabel
from Scripts.LabelPairs.DateEntryLabel import DateEntryLabel
from Scripts.StateEntryHelperWindow import StateEntryHelperWindow

from Slots.Play import HandPay


def _no_tab(_, parent):
    # focuses on the next wigit
    parent.focus_get().tk_focusNext().focus()
    return 'break'


def _no_shift_tab(_, parent):
    # focuses on the previous wigit
    parent.focus_get().tk_focusPrev().focus()
    return 'break'


class EntryWigits(ttk.Frame):
    def __init__(self, parent, window):
        super().__init__(master=parent)
        self._window = window

        self.total_cash_out = ttk.StringVar()
        self.total_cash_in = ttk.StringVar()

        self._create_entries()
        self._place_entries()

    def _create_entries(self):
        self._create_header()

        self._create_machine()

        self._create_date()
        self._create_end_datetime()

        self._create_bet()
        self._create_denom()
        self._create_play_type()

        self._create_cashin()
        self._create_cashout()

        self._create_total_ci()
        self._create_total_co()
        self._create_profit_loss()

        self._create_cash_in_table()
        self._create_hp_table()

        self._create_initial_state()
        self._create_state_val()

        self._create_note()

        self._create_start_entry()
        self._create_end_entry()
        self._create_image_table()

    def _create_header(self):
        self._header = ttk.Label(self, text="Play Information", anchor='center')

    def _create_machine(self):
        self.machine_cb = ComboboxLabel(self, '', self._window.dropdown_data.machine_values)
        self.machine_cb.combobox.configure(width=30)
        self.machine_cb.combobox.set("Select Machine")
        self.machine_cb.combobox.bind("<<ComboboxSelected>>", lambda _: self._create_play(self.machine_cb.var.get()))

    def _create_play(self, machine):
        self._window.create_play(machine)

    def _create_date(self):
        self.dt = DateEntryLabel(self, 'Start Time', dateformat=r'%Y-%m-%d %H:%M:%S')
        #self.dt.var.set(self._window.default_dt)

    def play_start_datetime_is_valid(self):
        "Checks if start datetime is valid"
        return self.dt.var.get() != "" and self.dt.var.get() != self._window.default_dt

    def get_play_start_datetime(self) -> datetime.datetime:
        """Gets the start date in the proper format"""
        fmt = "%Y-%m-%d %H:%M:%S"
        if not self.play_start_datetime_is_valid():
            return '1900-01-01 01:01:01'
        if len(self.dt.var.get()) == 10:
            fmt = "%Y-%m-%d"
        return datetime.datetime.strptime(self.dt.var.get(), fmt)

    def set_play_start_datetime(self, start_datetime):
        """Set the start time of the play"""
        fmt = "%Y-%m-%d %H:%M:%S"
        self.dt.var.set(start_datetime.strftime(fmt))

    def clear_play_start_datetime(self):
        """Clears the start time for the play"""
        self.dt.var.set("")

    def _create_play_type(self):
        self.play_type = ComboboxLabel(self, 'Play Type', self._window.dropdown_data.play_types)
        self.play_type.var.set("AP")
        self.play_type.bind("<<ComboboxSelected>>", self._window.update_play_type)

    def _create_denom(self):
        self.denom_cb = ComboboxLabel(self, 'Denom', self._window.dropdown_data.denom_values)
        self.denom_cb.combobox.current(0)
        self.denom_cb.combobox.bind("<<ComboboxSelected>>", self._window.update_denom)

    def _create_bet(self):
        self.bet = MoneyEntryLabel(self, 'Bet')
        self.bet.bind("<FocusOut>", self._window.update_bet)

    def _create_cashin(self):
        self.cashin = MoneyEntryLabel(self, 'Cash In')
        self.cashin.bind("<FocusOut>", self.add_cash)

    def _create_cashout(self):
        self.cashout = MoneyEntryLabel(self, 'Cash Out')
        self.cashout.bind("<FocusOut>", self._window.update_cashout)

    def _create_total_ci(self):
        self.total_ci = LabelLabel(self, 'Total Cash In', label_var=self.total_cash_in)

    def _create_total_co(self):
        self.total_co = LabelLabel(self, 'Total Cash Out', label_var=self.total_cash_out)

    def _create_profit_loss(self):
        self.profit_loss = LabelLabel(self, 'Profit/Loss', 0.00)

    def _create_end_datetime(self):
        self.end_dt = LabelLabel(self, 'End time', "")

    def play_end_datetime_is_valid(self):
        return self.end_dt.var.get() != "" and self.end_dt.var.get() != 1

    def get_play_end_datetime(self) -> datetime.datetime:
        fmt = "%Y-%m-%d %H:%M:%S"
        if not self.play_end_datetime_is_valid():
            return '1900-01-01 01:01:01'
        if len(self.end_dt.var.get()) == 10:
            fmt = "%Y-%m-%d"
        return datetime.datetime.strptime(self.end_dt.var.get(), fmt)

    def set_play_end_datetime(self, end_datetime):
        if end_datetime == "" or end_datetime == 1:
            return

        fmt = "%Y-%m-%d %H:%M:%S"
        self.end_dt.var.set(end_datetime.strftime(fmt))

    def clear_play_end_datetime(self):
        self.end_dt.var.set("")

    def _open_state_helperwin(self, _):
        """second param is 'parent'"""
        #Shouldn't need to reach in this deep
        if 'disabled' in self._window.image_buttons.state_button.config('state'):
            return
        if self._window.get_current_play() is not None:
            StateEntryHelperWindow(play=self._window.get_current_play())
        else:
            print("No helper available")

    def _create_initial_state(self):
        self.initial_state = LargeEntryLabel(self, 'Initial State')
        self.initial_state.label.bind('<Button-1>', lambda _: self._open_state_helperwin(self._window))
        self.initial_state.label.bind('<Return>', lambda _: self._open_state_helperwin(self._window))
        self.initial_state.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        self.initial_state.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))
        self.initial_state.text.bind('<FocusOut>', self._update_state)

    def _update_state(self, _):
        if self._window.get_current_play():
            self._window.get_current_play().state = self.initial_state.text.get(1.0, 'end')
            self._window.ttk_state.set(self._window.get_current_play().state)
        else:
            self._window.ttk_state.set(self.initial_state.text.get(1.0, 'end'))

    def _create_state_val(self):
        self.state_val = LabelLabel(self, 'State', '', self._window.ttk_state)

    def _create_note(self):
        self.note = LargeEntryLabel(self, 'Note')
        self.note.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        self.note.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))

    def _create_start_entry(self):
        self.start_entry = EntryLabel(self, 'Start Image', self._window.start_img, state='readonly')
        self.start_entry.label.bind('<Button-1>', self._window.jump_to_start_image)

    def _create_end_entry(self):
        self.end_entry = EntryLabel(self, 'End Image', self._window.end_img, state='readonly')
        self.end_entry.label.bind('<Button-1>', self._window.jump_to_end_image)

    def _jump_to_selection(self, _):
        if not self.image_table.selection():
            return
        self._window.jump_to_image(self.image_table.item(self.image_table.selection(), 'values')[0])

    def _create_image_table(self):
        self.image_table = ttk.Treeview(self, columns='imgs', show='headings')
        self.image_table.heading('imgs', text='Images')
        self.image_table.bind('<Double-Button-1>', self._jump_to_selection)

    def _create_hp_table(self):
        self.hp_table = ttk.Treeview(self, columns=('hp', 'tip'), show='headings', height=4)
        self.hp_table.heading('hp', text='Hand Pay')
        self.hp_table.heading('tip', text='Tip')
        self.hp_table.bind('<Delete>', self._hp_delete)


    def add_cash(self, _=None):
        """Add cash from entry field to the play"""
        if not self.cashin.var.get():
            return
        ci = Decimal(self.cashin.var.get())
        if ci and ci > Decimal(0.0):
            success = self._window.add_cash_to_play(ci)
            if success:
                self.cashin.var.set("")
        self.update_cash_in_table(self._window)


    def _create_cash_in_table(self):
        self.ci_table = ttk.Treeview(self, columns=('ci'), show='headings', height=4)
        self.ci_table.heading('ci', text='Cash in')
        self.ci_table.bind('<Delete>', self._ci_delete)

    def update_table(self, parent):
        """update the table of images"""
        self.image_table.delete(*self.image_table.get_children())
        # self.image_table.insert(parent='', index=ttk.END, values=parent.play_imgs)
        # return
        for item in parent.play_imgs:
            self.image_table.insert(parent='', index=ttk.END, values=f"{{{item}}}")

    def update_hand_pay_table(self, parent):
        """Update the handpay display table"""
        self.hp_table.delete(*self.hp_table.get_children())
        for item in parent.hand_pay:
            self.hp_table.insert(parent='', index=ttk.END,
                                 values=(item.pay_amount, item.tip_amount))
        parent.update_handpays()

    def update_cash_in_table(self, parent):
        """Update the cash in display table to match the values from the play"""
        self.ci_table.delete(*self.ci_table.get_children())
        total = Decimal(0.0)
        for item in parent.get_cash_in():
            self.ci_table.insert(parent='', index=ttk.END, values=item)
            total += item
        self.total_cash_in.set('{:2f}'.format(total))

    def _ci_delete(self, _):
        for item in self.ci_table.selection():
            self.ci_table.delete(item)
        success = True
        self._window.update_cash_in()

    def get_cash_in(self):
        values = []
        for i in self.ci_table.get_children():
            values.append(Decimal(self.ci_table.item(i, 'values')[0]))
        return values

    def _hp_delete(self, _):
        for item in self.hp_table.selection():
            self.hp_table.delete(item)
        self._window.hand_pay.clear()
        for item in self.hp_table.get_children():
            values = self.hp_table.item(item)['values']
            self._window.hand_pay.append(HandPay(Decimal(values[0]), Decimal(values[1])))

    def clear_all_widgets(self):
        self.clear_play_start_datetime()
        self.clear_play_end_datetime()
        self.bet.var.set(0)
        self.cashout.var.set(0)
        self.initial_state.clear()
        self.note.clear()
        self.start_entry.var.set("")
        self.end_entry.var.set("")

        self.update_table(self._window)
        self.ci_table.delete(*self.ci_table.get_children())
        self.update_hand_pay_table(self._window)


    def _place_entries(self):
        self.columnconfigure((0, 1, 2), weight=1, uniform='b')
        row = 0
        self._header.grid(row=row, column=0, columnspan=3)

        row = 1
        self.machine_cb.grid(row=row, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        row=2
        self.dt.grid(row=row, column=0, columnspan=2, sticky='we', padx=5, pady=5)
        self.end_dt.grid(row=row, column=1, sticky='we', padx=5, pady=5)

        row = 3
        self.bet.grid(row=row, column=0, sticky='we', padx=5, pady=5)
        self.denom_cb.grid(row=row, column=1, sticky='we', padx=5, pady=5)
        self.play_type.grid(row=row, column=2, sticky='we', padx=5, pady=5)

        row += 1
        self.total_ci.grid(row=row, column=0, sticky='we')
        self.total_co.grid(row=row, column=1, sticky='we')
        self.profit_loss.grid(row=row, column=2, sticky='we')

        row += 1
        self.cashin.grid(row=row, column=0, sticky='we', padx=5, pady=5)
        self.cashout.grid(row=row, column=1, sticky='we', padx=5, pady=5)

        row += 1
        self.ci_table.grid(row=row, column=0, columnspan=1, sticky='we', padx=5, pady=5)
        self.hp_table.grid(row=row, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        row += 1
        self.initial_state.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row += 1
        self.state_val.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row += 1
        self.note.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row += 1
        self.start_entry.grid(row=row, column=0, sticky='we', padx=5, pady=5)
        self.image_table.grid(row=row, column=1, columnspan=2, rowspan=2, sticky='we', padx=5, pady=5)

        row += 1
        self.end_entry.grid(row=row, column=0, sticky='we', padx=5, pady=5)

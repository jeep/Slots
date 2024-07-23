import ttkbootstrap as ttk

from Scripts.LabelPairs.ComboboxLabel import ComboboxLabel
from Scripts.LabelPairs.EntryLabel import EntryLabel
from Scripts.LabelPairs.MoneyEntryLabel import MoneyEntryLabel
from Scripts.LabelPairs.LabelLabel import LabelLabel
from Scripts.LabelPairs.LargeEntryLabel import LargeEntryLabel

from Slots.Play import HandPay
from decimal import Decimal

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
        # initializes the frame
        super().__init__(master=parent)
        # creates a 'private' window variable
        self._window = window
        
        self._create_entries()
        self._place_entries()
    
    def _create_entries(self):
        self._create_header()
        self._create_machine()
        self._create_date()
        self._create_bet()
        self._create_play_type()
        self._create_denom()
        self._create_cashin()
        self._create_cashout()
        self._create_profit_loss()
        self._create_initial_state()
        self._create_state_val()
        self._create_note()
        self._create_start_entry()
        self._create_end_entry()
        self._create_image_table()
        self._create_hp_table()
    
    def _create_header(self):
        self._header = ttk.Label(self, text="Play Information", anchor='center')
    
    def _create_machine(self):
        self.machine_cb = ComboboxLabel(self, '', self._window.machine_values)
        self.machine_cb.combobox.set("Select Machine")
        self.machine_cb.combobox.bind("<<ComboboxSelected>>", lambda _: self._create_play(self.machine_cb.var.get()))

    def _create_play(self, machine):
        print(f"Creating play for {machine}") 
        self._window.create_play(machine)

    def _create_date(self):
        self.dt = EntryLabel(self, 'Date')
        self.dt.var.set("Auto / YYYY-MM-DD")
    
    def _create_play_type(self):
         self.play_type = ComboboxLabel(self, 'Play Type', self._window.play_types)
         self.play_type.var.set("AP")

    def _create_denom(self):
        self.denom_cb = ComboboxLabel(self, '', self._window.denom_values, auto=False)
        self.denom_cb.combobox.current(0)

    def _create_bet(self):
        self.bet = MoneyEntryLabel(self, 'Bet')
    
    def _create_cashin(self):
        self.cashin = MoneyEntryLabel(self, 'Cash In')

    def _create_cashout(self):
        self.cashout = MoneyEntryLabel(self, 'Cash Out')

    def _create_profit_loss(self):
        self.profit_loss = LabelLabel(self, 'Profit/Loss', 0.00)
        # binds pressing any key to updateing the label
        self._window.bind('<Key>', lambda _: self.profit_loss.var.set(f'{(Decimal(self.cashout.get_var()) - Decimal(self.cashin.get_var())):.2f}'))

    def _create_initial_state(self):
        self.initial_state = LargeEntryLabel(self, 'Initial State')
        self.initial_state.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        self.initial_state.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))
        self.initial_state.text.bind('<FocusOut>', self._update_state)

    def _update_state(self, _):
        if self._window._current_play:
            self._window.ttk_state.set(self._window._current_play.state)
        else: 
            self._window.ttk_state.set(self.initial_state.text.get(1.0))

    def _create_state_val(self):
        self.state_val = LabelLabel(self, 'State', '', self._window.state)

    def _create_note(self):
        self.note = LargeEntryLabel(self, 'Note')
        self.note.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        self.note.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))
    
    def _create_start_entry(self):
        self.start_entry = EntryLabel(self, 'Start Image', self._window.start_img, state='readonly')
    
    def _create_end_entry(self):
        self.end_entry = EntryLabel(self, 'End Image', self._window.end_img, state='readonly')
    
    def _create_image_table(self):
        self.image_table = ttk.Treeview(self, columns='imgs', show='headings')
        self.image_table.heading('imgs', text='Images')
    
    def _create_hp_table(self):
        self.hp_table = ttk.Treeview(self, columns=('hp', 'tip'), show='headings')
        self.hp_table.heading('hp', text='Hand Pay')
        self.hp_table.heading('tip', text='Tip')
        #self.hp_table.bind('<Delete>', self._hp_delete)
        
    def update_table(self, parent):
        # removes all elements of the table
        self.image_table.delete(*self.image_table.get_children())
        # places all items in the play_imgs list onto the table
        for item in parent.play_imgs:
            self.image_table.insert(parent='', index=ttk.END, values=item)
    
    def update_hand_pay_table(self, parent):
        self.hp_table.delete(*self.hp_table.get_children())
        
        for item in parent.hand_pay:
            self.hp_table.insert(parent='', index=ttk.END, values=(item.pay_amount, item.tip_amount))
    

#    def _hp_delete(self, _):
#        for item in self.hp_table.selection():
#            values = self.hp_table.item(item)['values']
#            self._window.hand_pay.remove(Handpay(float(values[0]), float(values[1]), None))
#            self.hp_table.delete(item)

    def _place_entries(self):

        self.columnconfigure((1,2,3), weight=1, uniform='b')
        row = 0
        self._header.grid(row=row, column=0, columnspan=3)

        row = 1
        self.machine_cb.grid(row=row, column=0, sticky='we', padx=5, pady=5)
        self.dt.grid(row=row, column=1, columnspan=2, sticky='we', padx=5, pady=5)

        row = 2
        self.bet.grid(row=row, column=0, sticky='we',  padx=5, pady=5)
        self.play_type.grid(row=row, column=1, sticky='we', padx=5, pady=5)
        self.denom_cb.grid(row=row, column=2, sticky='we' ,padx=5, pady=5)

        row = 3
        self.cashin.grid(row=row, column=0, sticky='we', padx=5, pady=5)
        self.cashout.grid(row=row, column=1, sticky='we', padx=5, pady=5)
        self.profit_loss.grid(row=row, column=2, sticky='we', columnspan=2)

        row = 4
        self.initial_state.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row = 5
        self.state_val.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row = 6
        self.note.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

        row = 7
        self.start_entry.grid(row=row, column=0,  sticky='we', padx=5, pady=5)
        self.image_table.grid(row=row, column=1, columnspan=2, rowspan=2, sticky='we', padx=5, pady=5)

        row = 8
        self.end_entry.grid(row=row, column=0, sticky='we', padx=5, pady=5)

        row = 9
        self.hp_table.grid(row=row, column=0, columnspan=3, sticky='we', padx=5, pady=5)

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
        
        # creates the entry fields
        self._create_entries()
        # places the entry fields onto the frame
        self._place_entries()
    
    def _create_entries(self):
        self._create_session_date()
        self._create_casino()
        self._create_date()
        self._create_machine()
        self._create_cashin()
        self._create_bet()
        self._create_play_type()
        self._create_initial_state()
        self._create_cashout()
        self._create_profit_loss()
        self._create_note()
        self._create_start_entry()
        self._create_end_entry()
        self._create_table()
        self._create_hp_table()
    
    def _place_entries(self):
        self.session_date.pack(fill='x')
        self.casino.pack(fill='x')
        self.date.pack(fill='x')
        self.machine.pack(fill='x')
        self.cashin.pack(fill='x')
        self.bet.pack(fill='x')
        self.play_type.pack(fill='x')
        self.initial_state.pack(fill='x')
        self.cashout.pack(fill='x')
        self.profit_loss.pack(fill='x')
        self.note.pack(fill='x')
        self.start_entry.pack(fill='x')
        self.end_entry.pack(fill='x')
        self.table.pack(fill='x')
        self.hp_table.pack(fill='x')
    
    def _create_session_date(self):
        self.session_date = LabelLabel(self, 'Session Date', label_var=self._window.session_date)

    def _create_casino(self):
        self.casino = ComboboxLabel(self, 'Casino', self._window.casino_values, state='readonly')
    
    def _create_date(self):
        self.date = EntryLabel(self, 'Date', state='readonly')
    
    def _create_machine(self):
        self.machine = ComboboxLabel(self, 'Machine', self._window.machine_values)
    
    def _create_cashin(self):
        self.cashin = MoneyEntryLabel(self, 'Cash In')
    
    def _create_bet(self):
        self.bet = MoneyEntryLabel(self, 'Bet')
    
    def _create_play_type(self):
        self.play_type = ComboboxLabel(self, 'Play Type', self._window.play_type)
    
    def _create_initial_state(self):
        self.initial_state = LargeEntryLabel(self, 'Initial State')
        # binds pressing tab to moving to the next wigit
        self.initial_state.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        # binds pressing shift and tab to moving to the previous wigit
        self.initial_state.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))

    def _create_cashout(self):
        self.cashout = MoneyEntryLabel(self, 'Cash Out')
    
    def _create_profit_loss(self):
        self.profit_loss = LabelLabel(self, 'Profit/Loss', 0.00)
        # binds pressing any key to updateing the label
        self._window.bind('<Key>', lambda _: self.profit_loss.var.set(f'{(Decimal(self.cashout.get_var()) - Decimal(self.cashin.get_var())):.2f}'))
    
    def _create_note(self):
        self.note = LargeEntryLabel(self, 'Note', height=8)
        # binds pressing tab to moving to the next wigit
        self.note.text.bind('<Tab>', lambda _: _no_tab(_, self._window))
        # binds pressing shift and tab to moving to the previous wigit
        self.note.text.bind('<Shift-Tab>', lambda _: _no_shift_tab(_, self._window))
    
    def _create_start_entry(self):
        self.start_entry = EntryLabel(self, 'Start Image', self._window.start_img, state='readonly')
    
    def _create_end_entry(self):
        self.end_entry = EntryLabel(self, 'End Image', self._window.end_img, state='readonly')
    
    def _create_table(self):
        self.table = ttk.Treeview(self, columns='imgs', show='headings')
        self.table.heading('imgs', text='Images')
    
    def _create_hp_table(self):
        self.hp_table = ttk.Treeview(self, columns=('hp', 'tip'), show='headings')
        self.hp_table.heading('hp', text='Hand Pay')
        self.hp_table.heading('tip', text='Tip')
        #self.hp_table.bind('<Delete>', self._hp_delete)
        
    def update_table(self, parent):
        # removes all elements of the table
        self.table.delete(*self.table.get_children())
        # places all items in the play_imgs list onto the table
        for item in parent.play_imgs:
            self.table.insert(parent='', index=ttk.END, values=item)
    
    def update_hand_pay_table(self, parent):
        self.hp_table.delete(*self.hp_table.get_children())
        
        for item in parent.hand_pay:
            self.hp_table.insert(parent='', index=ttk.END, values=(item.pay_amount, item.tip_amount))
    
#    def _hp_delete(self, _):
#        for item in self.hp_table.selection():
#            values = self.hp_table.item(item)['values']
#            self._window.hand_pay.remove(Handpay(float(values[0]), float(values[1]), None))
#            self.hp_table.delete(item)
import ttkbootstrap as ttk


import tkinter as tk

from Scripts.LabelPairs.EntryLabel import EntryLabel
from Slots.Play import Play
from decimal import Decimal


class StateEntryHelperWindow(tk.Toplevel):
    def __init__(self, *args, play: Play, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('State Entry')
        self.minsize(300, 300)
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        self.fields = play.get_entry_fields()
        if self.fields is None:
            print("This should be a dialog, but there are not fields for this machine.")

        self.entries = []
        for f in self.fields:
            l = EntryLabel(self, f.label, callback=f.callback)
            self.entries.append(l)
            l.pack()

        self.okay_button = ttk.Button(
            self,
            text="Okay",
            command=self.button_okay_pressed
        )
        self.okay_button.pack()
        self.cancel_button = ttk.Button(
            self,
            text="Cancel",
            command=self.button_cancel_pressed
        )
        self.cancel_button.pack()
        self.focus()

    def button_okay_pressed(self):
        for e in self.entries:
            e.execute()

        self.destroy()

    def button_cancel_pressed(self):
        self.destroy()
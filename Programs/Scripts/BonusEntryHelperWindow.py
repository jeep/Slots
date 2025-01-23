import tkinter as tk

import ttkbootstrap as ttk

from Slots.Play import Play
from Scripts.LabelPairs.EntryLabel import EntryLabel
from Scripts.LabelPairs.LargeEntryLabel import LargeEntryLabel


class BonusEntryHelperWindow(tk.Toplevel):
    """Bonus Entry Window"""
    def __init__(self, *args, play: Play, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Bonus Entry')
        self.minsize(300, 300)
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))

        self._name = EntryLabel(self, 'Bonus Type')
        self._sub_bonuses = LargeEntryLabel(self, 'Sub Bonuses')
        self._notable_event = LargeEntryLabel(self, 'Event')
        self._value = EntryLabel(self, "Value")

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
        """If okay pressed, return"""
        for e in self.entries:
            e.execute()
        self.destroy()

    def button_cancel_pressed(self):
        """cancel"""
        self.destroy()

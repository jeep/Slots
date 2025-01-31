import csv
from os.path import splitext, exists, join, dirname
from collections import namedtuple

from ttkbootstrap import Querybox

DropdownDataDefaults = namedtuple("Dropdown_data", ["filename", "defaults"])
externals = {'play_type': DropdownDataDefaults("playtype_entry_values.csv",
                                               ["AP", "Gamble", "Misplay", "Non-play", "Science", "Tip"], ),
             'casino': DropdownDataDefaults("casino_entry_values.csv", ["ilani", "Spirit Mountain"]),
             'denom': DropdownDataDefaults("denom_entry_values.csv",
                                           ["1cent", "2cent", "5cent", "10cent", "25cent", "$1", "$2"], ),
             'machine': DropdownDataDefaults("machine_entry_values.csv",
                                             ["Frankenstein", "Pinwheel Prizes", "Power Push"], )}


class DropdownData:
    """Class for managing the dropdown data"""

    def __init__(self):
        self.denom_values = DropdownData.get_entry_values(externals["denom"])
        self.casino_values = DropdownData.get_entry_values(externals["casino"])
        self.play_types = DropdownData.get_entry_values(externals["play_type"])
        self._machine_file = externals["machine"].filename
        self.machine_values = DropdownData.get_entry_values(externals["machine"])

    def add_denom(self):
        """Add a new denomination"""
        new = Querybox.get_string(prompt="Enter a denomination", title="Denom Entry")
        if (new is not None) and (new not in self.denom_values):
            self.denom_values.append(new)

    def add_casino(self):
        """add a new casino"""
        new_casino = Querybox.get_string(prompt="Enter a casino", title="Casino Entry")
        if (new_casino is not None) and (new_casino not in self.casino_values):
            self.casino_values.append(new_casino)

    def add_machine(self):
        """Add a new machine"""
        new_machine = Querybox.get_string(
            prompt="Enter a machine", title="Machine Entry"
        )
        if (new_machine is not None) and (new_machine not in self.machine_values):
            self.machine_values.append(new_machine)

    def add_playtype(self):
        """Add a new playtype"""
        new = Querybox.get_string(prompt="Enter a play type", title="PlayType Entry")
        if (new is not None) and (new not in self.play_types):
            self.play_types.append(new)

    def update_machine_dd(self, casino):
        """update the machines based on casino"""
        # TODO save machine data on switch
        if casino is None:
            return
        fn = externals["machine"].filename

        (base, ext) = splitext(fn)
        casino = casino.replace(" ", "_")
        casino_fn = f"{base}-{casino}{ext}"
        if exists(casino_fn):
            fn = casino_fn

        if fn == self._machine_file:
            return

        self._machine_file = fn
        dd = DropdownDataDefaults(fn, externals["machine"].defaults)
        self.machine_values.clear()
        self.machine_values.extend(DropdownData.get_entry_values(dd))

    def save_externals(self):
        """Save the csv files for entry drop-downs"""
        external_csvs = {
            "casino_entry_values.csv": self.casino_values,
            self._machine_file: self.machine_values,
            "denom_entry_values.csv": self.denom_values,
            "playtype_entry_values.csv": self.play_types,
        }
        for f, var in external_csvs.items():
            file_path = join(dirname(dirname(__file__)), f)
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for item in var:
                    writer.writerow([item])

    @staticmethod
    def get_entry_values(dd_data: DropdownDataDefaults):
        """Read an external file to get values to use"""
        fn = dd_data.filename
        if exists(fn):
            with open(fn, "r") as csvfile:
                values = list(csv.reader(csvfile))
                values = [
                    val.strip()
                    for sublist in values
                    for val in sublist
                    if (val.strip() != "")
                ]
                return values

        msg = f"{dd_data.filename} not found."
        if dd_data.defaults:
            print(msg, " Using defaults.")
            return dd_data.defaults

        return []
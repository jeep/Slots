import copy
import csv
import datetime
from collections import namedtuple
from decimal import Decimal
from enum import Flag, auto
from os import makedirs, remove, startfile
from os.path import basename, dirname, exists, join, splitext
from shutil import move
from tkinter.constants import DISABLED, NORMAL
from tkinter.filedialog import askdirectory

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from pillow_heif import register_heif_opener
from Scripts.EntryWigits import EntryWigits
from Scripts.get_imgs_data import multi_get_img_data
from Scripts.HandPayWindow import HandPayWindow
from Scripts.ImageButtons import ImageButtons
from Scripts.ImageDisplay import ImageDisplay
from Scripts.SessionFrame import SessionFrame
from Scripts.SessionTable import SessionTable
from Scripts.StateEntryHelperWindow import StateEntryHelperWindow
from Slots.PlayFactory import PlayFactory
from ttkbootstrap.dialogs import Messagebox, Querybox

register_heif_opener(decode_threads=8, thumbnails=False)

DropdownData = namedtuple("Dropdown_data", ["filename", "defaults"])
externals = {
    "play_type": DropdownData(
        "playtype_entry_values.csv",
        ["AP", "Gamble", "Misplay", "Non-play", "Science", "Tip"],
    ),
    "casino": DropdownData("casino_entry_values.csv", ["ilani", "Spirit Mountain"]),
    "denom": DropdownData(
        "denom_entry_values.csv",
        ["1cent", "2cent", "5cent", "10cent", "25cent", "$1", "$2"],
    ),
    "machine": DropdownData(
        "machine_entry_values.csv",
        ["Frankenstein", "Lucky Wealth Cat", "Pinwheel Prizes", "Power Push"],
    ),
}

class App(ttk.Window):
    """Starting point"""
    def __init__(self):
        super().__init__()

        self.title("Slot Data Entry")
        self.minsize(450, 705)
        self.geometry("1450x1000")
        self.iconphoto(False, ttk.PhotoImage(file=r"Programs\Icon\slot_machine_icon.png"))
        self._loaded_play_id = None
        self._current_index = None
        self.imgs = []
        self.play_imgs = []
        self.hand_pay = []
        self.plays = {}
        self._current_play = None
        self.machine_values = None
        self.machine_file = None
        self.start_datetime = datetime.MINYEAR

        self.get_dropdown_data()

        self.pointer = 0
        self.scale = 7
        self.rotation = 0

        self.default_session_date = "Load first play"
        self.default_dt = "Auto / YYYY-MM-DD"
        self.session_date = ttk.StringVar(value=self.default_session_date)
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()
        self.ttk_state = ttk.StringVar()

        self.columnconfigure(0, uniform="a", weight=1) # session log
        self.columnconfigure(1, uniform="a", weight=2) # data entry
        self.columnconfigure(2, uniform="a", weight=2) #image and buttons

        self.session_table = SessionTable(self)
        self.session_table.grid(row=0, column=0, sticky="nsew")

        self.info_frame = ttk.Frame(self)
        self.session_frame = SessionFrame(self.info_frame, self)
        self.session_frame.pack(anchor="center")
        self.entry_wigits = EntryWigits(self.info_frame, self)
        self.entry_wigits.pack(anchor="center")
        self.info_frame.grid(row=0, column=1, sticky="nsew")

        image_frame = ttk.Frame(self)
        self.image_buttons = ImageButtons(image_frame, self)
        self.image_buttons.pack(side="top", padx=5, pady=5, anchor="n")
        self.image_display = ImageDisplay(image_frame)
        self.image_display.pack(side="top", padx=5, pady=5)
        # image_frame.pack(side='right', fill='both', anchor='ne')
        image_frame.grid(row=0, column=2, sticky="nsew")

        self.make_menu()

        self.setup_keybinds()

        self.image_buttons.save_button.configure(state=DISABLED)
        self.image_buttons.save_session_button.configure(state=DISABLED)
        self.image_buttons.set_image_adders("disabled")
        self.image_buttons.remove_button.configure(state=DISABLED)
        self.image_buttons.delete_button.configure(state=DISABLED)
        self.image_buttons.set_image_navigation("disabled")
        self.image_buttons.state_button.configure(state=DISABLED)

    def get_current_play(self):
        """Gets the current play"""
        return self._current_play

    def get_dropdown_data(self):
        """load dropdown data from external sources"""
        self.play_types = App.get_entry_values(externals["play_type"])
        self.casino_values = App.get_entry_values(externals["casino"])
        self.machine_file = externals["machine"].filename
        self.machine_values = App.get_entry_values(externals["machine"])
        self.denom_values = App.get_entry_values(externals["denom"])

    def update_machine_dd(self, _=None):
        """update the machines based on casino"""
        casino = self.session_frame.casino.selection_get()
        fn = externals["machine"].filename
        if casino is not None:
            (base, ext) = splitext(fn)
            casino = casino.replace(" ", "_")
            casino_fn = f"{base}-{casino}{ext}"
            if exists(casino_fn):
                fn = casino_fn

        self.machine_file = fn
        dd = DropdownData(fn, externals["machine"].defaults)
        self.machine_values.clear()
        self.machine_values.extend(App.get_entry_values(dd))
        self.entry_wigits.machine_cb.combobox['values']=self.machine_values

    @staticmethod
    def get_entry_values(dd_data: DropdownData):
        """Read an external file to get values to use"""
        fn =  dd_data.filename
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

    def make_menu(self):
        """Make the menus"""
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)

        file_menu = ttk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Set Image Scale Divisor", command=self.set_scale)
        file_menu.add_command(label="Rotate Image", command=self.rotate_image)
        file_menu.add_separator()
        file_menu.add_command(label="Preload Test Play", command=self.load_test_play)
        file_menu.add_command(label="Open Test Folder", command=self.open_test_folder)

        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = ttk.Menu(menu, tearoff=False)
        edit_menu.add_command(label="Add Casino", command=self.add_casino)
        edit_menu.add_command(label="Add Machine", command=self.add_machine)
        edit_menu.add_command(label="Add Denom", command=self.add_denom)
        edit_menu.add_command(label="Add PlayType", command=self.add_playtype)
        edit_menu.add_separator()
        edit_menu.add_command(label="Open newest play", command=self.load_final_play)
        edit_menu.add_command(label="Force Clear Images", command=self.force_clear)
        menu.add_cascade(label="Edit", menu=edit_menu)

        nav_menu = ttk.Menu(menu, tearoff=False)
        nav_menu.add_command(label="Goto first img [Home]", command=self.display_first_image)
        nav_menu.add_command(label="Prev img [PgUp]", command=self.display_prev_image)
        nav_menu.add_command(label="Next img [PgDn]", command=self.display_next_image)
        nav_menu.add_command(label="Goto last img", command=self.display_last_image)
        menu.add_cascade(label="Navigate", menu=nav_menu)

    def load_final_play(self):
        """Load the last play in the session"""
        id= list(self.plays.keys())[-1]
        self.load_play(id)

    def force_clear(self):
        self.play_imgs.clear()
        self.start_img.set("")
        self.end_img.set("")
        self.entry_wigits.update_table(self)

    def open_test_folder(self):
        """For testing"""
        folder = join(dirname(dirname(__file__)), "Data", "test_pics")
        self.open_folder(folder)

    def open_folder(self, directory=""):
        """open a folder to get images"""
        if directory == "":
            directory = askdirectory(mustexist=True)

        if directory == "":
            return

        print("Loading ", datetime.datetime.now())
        # multi threads geting the image data ( image path, image type, image date )
        self.imgs = [d for d in multi_get_img_data(directory) if d is not None]
        print("Loaded ", datetime.datetime.now())

        if len(self.imgs) == 0:
            return

        self.pointer = 0
        self.imgs = sorted(self.imgs, key=lambda item: item[2])
        self.display_image()
        self.image_buttons.set_image_adders("normal")
        self.image_buttons.delete_button.configure(state="warning")
        self.image_buttons.set_image_navigation("normal")

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

    def add_denom(self):
        """Add a new denomination"""
        new = Querybox.get_string(prompt="Enter a denomination", title="Denom Entry")
        if (new is not None) and (new not in self.denom_values):
            self.denom_values.append(new)

    def set_scale(self):
        """Set scale factor for the image. Larger scale is smaller image."""
        scale = Querybox.get_integer(
            "Enter a integer scale. Larger makes the image smaller",
            "Set scale",
            self.scale,
            1,
        )
        if scale is None:
            pass
        else:
            self.scale = scale
        self.display_image()

    def rotate_image(self):
        """rotate the image 90 degrees"""
        self.rotation = self.rotation + 90 if self.rotation + 90 <= 360 else 0
        self.display_image()


    def image_in_another_play(self, img_name):
        """Determine if the image is in any play"""
        for p in self.plays.values():
            if self.editing_play() and p.identifier == self._current_play.identifier:
                continue
            if img_name in p.addl_images or img_name==p.start_image or img_name ==p.end_image:
                return True
        return False

    # priority should be: used, avoid, normal
    def get_image_name_color(self, img_name):
        """Determine the color to display the image name as"""
        image_name_color = {"normal": "black", "used": "orange", "avoid": "red"}
        if self.image_in_another_play(img_name):
            return image_name_color["used"]
        if "IMG_E" in basename(img_name):
            return image_name_color["avoid"]
        return image_name_color["normal"]

    def display_image(self):
        """Display the image"""
        if len(self.imgs) == 0:
            return

        self.image_display.canvas.delete("all")
        # opens the image at the current pointer
        with Image.open(self.imgs[self.pointer][0]) as image:
            image = image.reduce(self.scale)
            image = image.rotate(self.rotation, expand=1)

            global imagetk
            # turns the image into an image that tkinter can display
            imagetk = ImageTk.PhotoImage(image)

            # gets the image dimensions and divides them by 2
            x, y = image.size
            x, y = x / 2, y / 2

            # adds the image to the canvas
            self.image_display.canvas.create_image(x, y, image=imagetk)

        current_image_w_path = self.imgs[self.pointer][0]
        file_name = basename(current_image_w_path)
        index = self.pointer+1
        color= self.get_image_name_color(current_image_w_path)
        file_date= datetime.datetime.strptime(self.imgs[self.pointer][2], '%Y%m%d%H%M%S')
        self.image_buttons.update_pagination_info(file_name=file_name, file_date=file_date, image_index=index,
                                                  image_count=len(self.imgs), color=color)

        self.image_display.canvas.bind("<Double-Button-1>", lambda _: startfile(current_image_w_path) )
        if self.image_is_in_current_play(current_image_w_path):
            self.image_buttons.set_image_adders("disabled")
        else:
            self.image_buttons.set_image_adders("normal")

    def display_first_image(self, event=None):
        """display the first image"""
        self.pointer = 0
        self.display_image()

    def display_next_image(self, event=None):
        """next image"""
        self.pointer = min((self.pointer + 1), (len(self.imgs) - 1))
        self.display_image()

    def display_prev_image(self, event=None):
        """Previous image"""
        # does nothing if there are no images
        self.pointer = max((self.pointer - 1), 0)
        self.display_image()

    def display_last_image(self, event=None):
        """display the last image"""
        self.pointer = len(self.imgs) - 1
        self.display_image()

    def play_end_date_is_valid(self):
        """Returns true if end date is a valid end date"""
        return self.entry_wigits.play_end_datetime_is_valid()

    def session_date_is_valid(self):
        """Returns true if the session date is a valid date"""
        return self.session_date.get() != "" and \
            self.session_date.get() != self.default_session_date

    def get_session_date(self) -> datetime.datetime:
        """Get the session data from the entry field"""
        fmt = "%Y-%m-%d"
        if not self.session_date_is_valid():
            return datetime.datetime.strptime(datetime.MINYEAR, fmt).date()
        return datetime.datetime.strptime(self.session_date.get(), fmt).date()

    def set_session_date(self, session_date):
        """Sets the settion date with the correct format"""
        if session_date == self.default_session_date:
            self.session_date.set(session_date)
            return
        self.session_date.set(session_date.strftime("%Y-%m-%d"))

    def update_session_date(self):
        """Update the session date"""
        if self._current_play is None:
            return
        if self.session_date_is_valid():
            self._current_play.session_date = self.get_session_date()

    def update_casino(self, _=None):
        """Update casino for the play. Second param is casino"""
        if self._current_play is None:
            return
        if self.session_frame.casino.var.get():
            self._current_play.casino = self.session_frame.casino.var.get()

    def update_start_datetime(self):
        """"Update the start datetime for the play"""
        self._current_play.start_time = self.entry_wigits.get_play_start_datetime()

    def update_end_datetime(self):
        """"Update the end datetime for the play"""
        self._current_play.end_time = self.entry_wigits.get_play_end_datetime()

    def update_bet(self, _=None):
        """Update the bet for the play, second param is bet"""
        if self._current_play is None:
            return
        if self.entry_wigits.bet.var.get():
            self._current_play.bet = Decimal(self.entry_wigits.bet.var.get())

    def update_play_type(self, _=None):
        """Update the play type. Second param is play_type"""
        if self._current_play is None:
            return
        if self.entry_wigits.play_type.var.get():
            self._current_play.play_type = self.entry_wigits.play_type.var.get()

    def update_denom(self, _=None):
        """Update denom. param2 is denom"""
        if self._current_play is None:
            return
        if self.entry_wigits.denom_cb.var.get():
            self._current_play.denom = self.entry_wigits.denom_cb.var.get()

    def update_pnl(self):
        """update the profit and loss for the play"""
        if self._current_play is None:
            return
        self.entry_wigits.profit_loss.var.set(self._current_play.pnl)

    def update_cashin(self, _=None):
        """update the cash in for the play. param2 is cash in"""
        if self._current_play is None:
            return
        if self.entry_wigits.cashin.var.get():
            self._current_play.cash_in = Decimal(self.entry_wigits.cashin.var.get())
            self.update_pnl()

    def update_cashout(self, _=None):
        """update the cash out for the play. param2 is cash out"""
        if self._current_play is None:
            return
        if self.entry_wigits.cashout.var.get():
            self._current_play.cash_out = Decimal(self.entry_wigits.cashout.var.get())
            self.update_pnl()

    def update_init_state(self):
        """update initial state"""
        if self._current_play is None:
            return
        lines = self.entry_wigits.initial_state.get_text().split(r"\n")
        line = " ".join(lines)
        line = line.strip()
        self._current_play.state = line

    def update_play_note(self):
        """update play note"""
        if self._current_play is None:
            return
        lines = self.entry_wigits.note.get_text().split(r"\n")
        line = " ".join(lines)
        line = line.strip()
        self._current_play.note = line

    def update_start_image(self):
        """update start image"""
        if self._current_play is None:
            return
        self._current_play.start_image = self.entry_wigits.start_entry.var.get()

    def update_end_image(self):
        """update end image"""
        if self._current_play is None:
            return
        self._current_play.end_image = self.entry_wigits.end_entry.var.get()

    def update_addl_images(self):
        """update additional images"""
        if self._current_play is None:
            return
        # filter duplicates
        to_add = list(dict.fromkeys(self.play_imgs))
        self._current_play.add_images(to_add)

    def update_handpays(self):
        """update hand pays"""
        self._current_play.hand_pays.clear()
        for hp in self.hand_pay:
            self._current_play.add_hand_pay(hp)
        #self._current_play.hand_pays = self.hand_pay.copy()
        self.update_pnl()

    def load_play(self, playid):
        """load a pre-existing play"""
        self._loaded_play_id = playid
        self._current_index = list(self.plays.keys()).index(playid)
        self._current_play = self.plays[playid]
        self.entry_wigits.machine_cb.var.set(self._current_play.machine.get_name())
        self.set_session_date(self._current_play.session_date)
        self.session_frame.casino.var.set(self._current_play.casino)
        self.entry_wigits.set_play_start_datetime(self._current_play.start_time)
        self.entry_wigits.set_play_end_datetime(self._current_play.end_time)
        self.entry_wigits.bet.var.set(self._current_play.bet)
        self.entry_wigits.denom_cb.var.set(self._current_play.denom)
        self.entry_wigits.play_type.var.set(self._current_play.play_type)
        self.entry_wigits.cashin.var.set(self._current_play.cash_in)
        self.entry_wigits.cashout.var.set(self._current_play.cash_out)
        self.update_pnl()
        self.entry_wigits.initial_state.set_text(self._current_play.state)
        self.entry_wigits.note.set_text(self._current_play.note)

        self.entry_wigits.start_entry.var.set(self._current_play.start_image)
        self.entry_wigits.end_entry.var.set(self._current_play.end_image)
        self.play_imgs = self._current_play.addl_images
        self.entry_wigits.update_table(self)

        self.hand_pay.clear()
        for hp in self._current_play.hand_pays:
            self.hand_pay.append(hp)
        #self.hand_pay = self._current_play.hand_pays.copy()
        self.entry_wigits.update_hand_pay_table(self)

        self.image_buttons.save_button.configure(state="normal", bootstyle="normal")
        self.jump_to_start_image()

    def create_play(self, machine_name=None):
        """create a new play"""
        if machine_name is None:
            machine_name = self.entry_wigits.machine_cb.var.get()
        self._current_play = PlayFactory.get_play(machine_name)
        self.update_all_play_values()
        if self._current_play.get_entry_fields() is None:
            self.image_buttons.state_button.configure(state=DISABLED)
            self.entry_wigits.initial_state.label.configure(foreground="black")
        else:
            self.image_buttons.state_button.configure(state=NORMAL)
            self.entry_wigits.initial_state.label.configure(foreground="blue")

    def update_all_play_values(self):
        """update a play to consume values from entry fields"""
        self.update_session_date()
        self.update_casino()
        self.update_start_datetime()
        self.update_end_datetime()
        self.update_bet()
        self.update_denom()
        self.update_play_type()
        self.update_cashin()
        self.update_cashout()
        self.update_init_state()
        self.update_play_note()
        self.update_start_image()
        self.update_end_image()
        self.update_addl_images()
        self.update_handpays()

    def editing_play(self):
        """determine a current play is being editted or is a new play"""
        return self._current_index is not None

    def save(self):
        """Save the play"""
        readiness_state = self.get_save_readiness()
        if self.SaveError.FORBIDDEN in readiness_state:
            return

        if self.SaveError.DATAWARNING in readiness_state:
            confirmed = Messagebox.okcancel(
                "There is potentially some missing data, are you sure?",
                "Incomplete save warning",
            )
            if confirmed != "OK":
                return

        if self.SaveError.IMGWARNING in readiness_state:
            confirmed = Messagebox.okcancel(
                "At least one image in this play is in another play. Are you sure?",
                "Duplicate image warning",
            )
            if confirmed != "OK":
                return

        if self._current_play is None:
            self.create_play()

        if self.editing_play():
            li = list(self.plays.items())
            li[self._current_index] = (
                self._current_play.identifier,
                self._current_play,
            )
            self.plays = dict(li)
            self.update_all_play_values()
            # this shouldn't be needed, but somehow I am clearing the hand pays
            self.plays[self._current_play.identifier] = copy.deepcopy(self._current_play)
        else:
            self.update_all_play_values()
            if self._current_play.identifier in self.plays:
                button = Messagebox.okcancel(
                    "You are not editing an exiting play and this will overwrite a play. Proceed?",
                    "Overwrite Warning",
                )
                if button != "OK":
                    return
            # this shouldn't be needed, but somehow I am clearing the hand pays
            self.plays[self._current_play.identifier] = copy.deepcopy(self._current_play)

        self.session_table.update_table()

        while self.image_is_in_current_play(self.imgs[self.pointer][0]) and self.pointer < len(self.imgs)-1:
            self.display_next_image()

        # clears all entry values
        self._current_index = None
        self.entry_wigits.clear_play_start_datetime()
        self.entry_wigits.clear_play_end_datetime()
        self.entry_wigits.bet.var.set(0)
        self.entry_wigits.cashin.var.set(self._current_play.cash_out)
        self.entry_wigits.cashout.var.set(0)
        self.entry_wigits.initial_state.clear()
        self.ttk_state.set("")
        self.entry_wigits.note.clear()
        self.entry_wigits.start_entry.var.set("")
        self.entry_wigits.end_entry.var.set("")

        self.play_imgs.clear()
        self.entry_wigits.update_table(self)

        self.hand_pay.clear()
        self.entry_wigits.update_hand_pay_table(self)

        # resets the save button to disabled
        self.image_buttons.save_button.configure(state="disabled")
        self.image_buttons.save_session_button.configure(state="enabled")
        self.entry_wigits.machine_cb.combobox.focus_set()

        self.create_play()

    def save_session(self):
        """Save the session"""

        # If there are images in the image table, this will miss those, but seems fine
        if self._current_play.start_image or self._current_play.end_image or \
            len(self._current_play.addl_images) or self.entry_wigits.start_entry.var.get() or \
            self.entry_wigits.end_entry.var.get():
            confirmation = Messagebox.show_question(
                'Are you sure? There is an incomplete play',
                'Save Session Confirmation', 
                buttons=['No:secondary', 'Yes:warning'])
            if confirmation != 'Yes':
                return

        # gets the path to the data save
        save_path = join(dirname(dirname(__file__)), "Data")
        file_path = join(save_path, "slots_data.csv")

        makedirs(save_path, exist_ok=True)

        while True:
            try:
                f = open(file_path, "a+")
            except Exception:
                Messagebox.show_error(
                    f'Cannot open "{file_path}".\nPlease close and try again',
                    "File Open Error",
                )
            else:
                f.close()
                break

        new_path = ""
        if list(self.plays.values())[0].start_image:
            new_path = join(
                dirname(dirname(list(self.plays.values())[0].start_image)),
                f"Sorted/{self.get_session_date()}",
            )

            try:
                makedirs(new_path, exist_ok=False)
            except Exception:
                pass

        pics_to_remove = []
        # move all images and update play values with new location
        play_id = ""
        try:
            with open(file_path, "a+", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for p in list(self.plays.values()):
                    play_id = p.identifier
                    if p.start_image and new_path:
                        pics_to_remove.append(p.start_image)
                        p.start_image = move(p.start_image, new_path)

                    pics_to_remove.extend(p.addl_images)
                    for i, a in enumerate(p.addl_images):
                        p.addl_images[i] = move(a, new_path)

                    if p.end_image and new_path:
                        pics_to_remove.append(p.end_image)
                        p.end_image = move(p.end_image, new_path)

                    for row in p.get_csv_rows():
                        writer.writerow(row)
        except Exception as e:
            Messagebox.show_error(
                f'Error saving session at {play_id}. Aborting. You will need to manually fix things to continue.\n{e}',
                'Error Saving')
            raise e

        self.imgs = [d for d in self.imgs if d[0] not in pics_to_remove]
        self.imgs = sorted(self.imgs, key=lambda item: item[2])
        self.display_first_image()

        self.plays.clear()
        self.session_table.update_table()

        self.image_buttons.set_image_adders("normal")

        self.image_buttons.save_button.configure(state="disabled")
        self.image_buttons.save_session_button.configure(state="disabled")
        self.set_session_date(self.default_session_date)

    def image_is_in_current_play(self, img):
        """determine if the image is in the current play"""
        return (img in self.play_imgs) or \
            (img == self.entry_wigits.start_entry.var.get()) or \
            (img == self.entry_wigits.end_entry.var.get())

    def get_image_dt(self):
        """Get the date/time of the current image"""
        image_dt = self.imgs[self.pointer][2]
        image_y = int(image_dt[:4])
        image_m = int(image_dt[4:6])
        image_d = int(image_dt[6:8])
        image_h = int(image_dt[8:10])
        image_M = int(image_dt[10:12])
        image_s = int(image_dt[12:14])
        image_dt = datetime.datetime(image_y, image_m, image_d, image_h, image_M, image_s)
        return image_dt

    def should_add(self, img):
        """Check if this image is already used, if so confirm that is should be reused"""
        if self.image_is_in_current_play(img):
            confirmation = Messagebox.show_question(
                'Are you sure? This image is in the current play already',
                'Image Addition Confirmation', 
                buttons=['No:secondary', 'Yes:warning'])

            if confirmation != 'Yes':
                return False

        if self.image_in_another_play(img):
            confirmation = Messagebox.show_question(
                'Are you sure? This image is in a different play already',
                'Image Addition Confirmation', 
                buttons=['No:secondary', 'Yes:warning'])

            return confirmation == 'Yes'
        return True

    def set_current_image_as_start(self, _=None):
        """Set image as start image and update time. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        if self.entry_wigits.start_entry.var.get() is not None and self.entry_wigits.start_entry.var.get() != "":
            confirmed = Messagebox.okcancel(
                "There is a start image already. Overwrite?",
                "Overwrite data warning",
            )
            if confirmed != "OK":
                return

        img = self.imgs[self.pointer][0]
        if not self.should_add(img):
            return

        # sets the start entry wigit to the path of the current image
        self.entry_wigits.start_entry.var.set(self.imgs[self.pointer][0])

        image_dt = self.get_image_dt()
        self.entry_wigits.set_play_start_datetime(image_dt)

        if not self.session_date_is_valid():
            dt = datetime.date(image_dt.year, image_dt.month, image_dt.day) 
            self.set_session_date(dt)

        self.image_buttons.set_image_adders('disabled')
        self.entry_wigits.bet.entry.focus_set()

    def add_current_image_to_play(self, _=None):
        """add image to the play. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        img = self.imgs[self.pointer][0]
        if not self.should_add(img):
            return

        # adds the path to the play images list
        self.play_imgs.append(img)
        self.entry_wigits.update_table(self)
        self.image_buttons.set_image_adders('disabled')

    def set_current_image_as_end(self, _=None):
        """add image to the end of the play and update duration. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        if self.entry_wigits.end_entry.var.get() is not None and self.entry_wigits.end_entry.var.get() != "":
            confirmed = Messagebox.okcancel(
                "There is an end image already. Overwrite?",
                "Overwrite data warning",
            )
            if confirmed != "OK":
                return

        img = self.imgs[self.pointer][0]
        if not self.should_add(img):
            return

        self.entry_wigits.end_entry.var.set(img)

        image_dt = self.get_image_dt()

        self.entry_wigits.set_play_end_datetime(image_dt)

        self.image_buttons.set_image_adders('disabled')
        self.entry_wigits.cashout.entry.focus_set()

    def remove_current_image_from_play(self, _=None):
        """Remove the image from the play. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        path = self.imgs[self.pointer][0]
        if not self.image_is_in_current_play(path):
            return

        if self.entry_wigits.start_entry.var.get() == path:
            self.entry_wigits.start_entry.var.set('')
        elif self.entry_wigits.end_entry.var.get() == path:
            self.entry_wigits.end_entry.var.set('')
        elif path in self.play_imgs:
            self.play_imgs.remove(path)
            self.entry_wigits.update_table(self)

        self.image_buttons.set_image_adders('normal')

    def delete_current_image(self, _=None):
        """Delete the current image. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        path = self.imgs[self.pointer][0]

        confirmation = Messagebox.show_question(
            f'Are you sure you want to delete this image:\n{path}',
            'Image Deletion Confirmation', 
            buttons=['No:secondary', 'Yes:warning'])

        if confirmation != 'Yes':
            return

        self.remove_current_image_from_play()
        remove(path)

        self.imgs.pop(self.pointer)
        if len(self.imgs) <= self.pointer:
            self.pointer = max((self.pointer - 1), 0)

        self.display_image()

    def jump_to_image(self, filename):
        """Jump to the named image"""
        for index, img in enumerate(self.imgs):
            if img[0] == filename:
                self.pointer = index
#        self.pointer = self.imgs.index(self.entry_wigits.start_entry.var.get())
        self.display_image()

    def jump_to_start_image(self, _=None):
        """Jump to the image set as start for the current play"""
        filename = self.entry_wigits.start_entry.var.get()
        self.jump_to_image(filename)

    def jump_to_end_image(self, _=None):
        """Jump to the image set as end for the current play"""
        filename = self.entry_wigits.end_entry.var.get()
        self.jump_to_image(filename)

    def open_handpay_entry_win(self, callback):
        """Open handpay window"""
        HandPayWindow(callback=callback)

    def add_handpay(self, hp):
        self.hand_pay.append(hp)
        self.entry_wigits.update_hand_pay_table(self)

    def open_state_helper_win(self, _=None):
        """Open the state helper. Second param is even to allow binding"""
        if self.get_current_play() is not None:
            StateEntryHelperWindow(play=self.get_current_play())
        else:
            print("No helper available")

    def remove_play(self, key):
        """delete a play"""
        del self.plays[key]
        if len(self.plays) == 0:
            self.image_buttons.save_session_button.configure(state="disabled")

    class SaveError(Flag):
        """States allowed for Saving"""
        FORBIDDEN = auto()
        DATAWARNING = auto()
        IMGWARNING = auto()

    def get_save_readiness(self):
        """Are we ready to save?"""
        casino = self.session_frame.casino.var.get()
        dt_valid = self.entry_wigits.play_start_datetime_is_valid()
        machine = self.entry_wigits.machine_cb.var.get()
        play_type = self.entry_wigits.play_type.var.get()

        bet = self.entry_wigits.bet.var.get()
        cashin = self.entry_wigits.cashin.var.get()
        cashout = self.entry_wigits.cashout.var.get()

        rv = App.SaveError(0)
        if (casino == "" or not dt_valid or machine == "Select Machine" or play_type == ""):
            return App.SaveError.FORBIDDEN
        if bet == "0" or cashin == "0" or cashout == "0" or not self.play_end_date_is_valid():
            rv |= App.SaveError.DATAWARNING
        if self._current_play is not None:
            if self.image_in_another_play(self._current_play.start_image) or \
               self.image_in_another_play(self._current_play.end_image):
                rv |= App.SaveError.IMGWARNING
            for i in self._current_play.addl_images:
                if self.image_in_another_play(i):
                    rv |= App.SaveError.IMGWARNING
                    break
        return rv

    def set_save_button_state(self):
        """Determine if we have everything needed to save the play"""
        val = self.get_save_readiness()
        if val == self.SaveError.FORBIDDEN:
            self.image_buttons.save_button.configure(state="disabled")
        elif val:
            self.image_buttons.save_button.configure( state="normal", bootstyle="warning")
        else:
            self.image_buttons.save_button.configure(state="normal", bootstyle="normal")

    def save_externals(self):
        """Save the csv files for entry drop-downs"""
        external_csvs = {
            "casino_entry_values.csv": self.casino_values,
            self.machine_file: self.machine_values,
            "denom_entry_values.csv": self.denom_values,
            "playtype_entry_values.csv": self.play_types,
        }
        for f, var in external_csvs.items():
            file_path = join(dirname(dirname(__file__)), f)
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for item in var:
                    writer.writerow([item])

    def reset_play(self):
        """reset the current play"""
        self._current_index = None
        self.session_table.clear_selection()
        if self._current_play is None:
            return
        self.create_play()

    def setup_keybinds(self):
        """set up keyboard shortcuts"""
        self.bind("<FocusIn>", lambda _: self.set_save_button_state())
        self.bind("<FocusOut>", lambda _: self.set_save_button_state())

        self.bind("<Control-s>", lambda _: self.save())
        self.bind("<Prior>", self.display_prev_image)
        self.bind("<Next>", self.display_next_image)
        self.bind("<Home>", self.display_first_image)
        #self.bind("<End>", self.display_last_image)
        self.bind("<Control-Key-1>", self.set_current_image_as_start)
        self.bind("<Control-Key-2>", self.add_current_image_to_play)
        self.bind("<Control-Key-3>", self.set_current_image_as_end)
        self.bind("<Control-Key-h>", lambda _: self.open_handpay_entry_win(self.add_handpay))
        self.bind("<Control-Key-o>", self.open_state_helper_win)
        self.bind("<Escape>", lambda _: self.reset_play())

    def load_test_play(self):
        """for testing"""
        self.session_frame.casino.var.set("ilani")
        self.set_session_date(datetime.datetime(2024, 5, 1))
        self.entry_wigits.set_play_start_datetime(
            datetime.datetime(2024, 5, 1, 12, 3, 5)
        )
        self.entry_wigits.machine_cb.var.set("Lucky Wealth Cat")
        self.entry_wigits.cashin.var.set("100.00")
        self.entry_wigits.bet.var.set("1.20")
        self.entry_wigits.play_type.var.set("AP")
        self.entry_wigits.initial_state.text.insert("1.0", "This, is; a (state): 1223")
        self.entry_wigits.cashout.var.set("120.00")


if __name__ == "__main__":
    # calls the app
    root = App()
    # runs the main loop
    root.mainloop()
    # saves the external values to their csv files
    root.save_externals()

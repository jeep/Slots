import copy
import csv
import datetime
from decimal import Decimal
from enum import Flag, auto
from os import makedirs, remove, startfile
from os.path import basename, dirname, join
from shutil import move
from tkinter.constants import DISABLED, NORMAL
from tkinter.filedialog import askdirectory

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from pillow_heif import register_heif_opener

from DropdownData import DropdownData
from Scripts.EntryWigits import EntryWigits
from Scripts.get_imgs_data import multi_get_img_data
from Scripts.HandPayWindow import HandPayWindow
from Scripts.ImageButtons import ImageButtons, PaginationData
from Scripts.ImageDisplay import ImageDisplay
from Scripts.SessionFrame import SessionFrame
from Scripts.SessionTable import SessionTable
from Scripts.StateEntryHelperWindow import StateEntryHelperWindow
from Slots.PlayFactory import PlayFactory
from ttkbootstrap.dialogs import Messagebox, Querybox

register_heif_opener(decode_threads=8, thumbnails=False)


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
        self.cash_in = []
        self.plays = {}
        self._current_play = None
        self.start_datetime = datetime.MINYEAR
        self.dropdown_data = DropdownData()
        self.default_output_base_dir = None

        self.pointer = 0
        self.scale = 7
        self.rotation = 0

        self.default_session_date = "Load first play"
        self.default_dt = "Auto / YYYY-MM-DD"
        self.session_date = ttk.StringVar(value=self.default_session_date)
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()
        self.ttk_state = ttk.StringVar()

        self.columnconfigure(0, uniform="a", weight=1)  # session log
        self.columnconfigure(1, uniform="a", weight=2)  # data entry
        self.columnconfigure(2, uniform="a", weight=2)  # image and buttons

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

        self._make_menu()

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

    def _make_menu(self):
        """Make the menus"""
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)

        file_menu = ttk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Open Folder", command=self.get_and_open_folder)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_separator()
        file_menu.add_command(label="Preload Test Play", command=self.load_test_play)
        file_menu.add_command(label="Open Test Folder", command=self.open_test_folder)

        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = ttk.Menu(menu, tearoff=False)
        edit_menu.add_command(label="Add Casino", command=self.dropdown_data.add_casino)
        edit_menu.add_command(label="Add Machine", command=self.dropdown_data.add_machine)
        edit_menu.add_command(label="Add Denom", command=self.dropdown_data.add_denom)
        edit_menu.add_command(label="Add PlayType", command=self.dropdown_data.add_playtype)
        edit_menu.add_separator()
        edit_menu.add_command(label="Open newest play", command=self.load_final_play)
        edit_menu.add_command(label="Force Clear Images", command=self.force_clear)
        edit_menu.add_separator()
        edit_menu.add_command(label="Set Image Scale Divisor", command=self.set_scale)
        edit_menu.add_command(label="Rotate Image", command=self.rotate_image)
        menu.add_cascade(label="Edit", menu=edit_menu)

        nav_menu = ttk.Menu(menu, tearoff=False)
        nav_menu.add_command(label="Goto first img [Home]", command=self.move_to_first_image)
        nav_menu.add_command(label="Prev img [PgUp]", command=self.move_to_prev_image)
        nav_menu.add_command(label="Next img [PgDn]", command=self.move_to_next_image)
        nav_menu.add_command(label="Goto last img", command=self.move_to_last_image)
        menu.add_cascade(label="Navigate", menu=nav_menu)

    def get_and_open_folder(self):
        """open a folder to get images"""
        directory = askdirectory(mustexist=True)
        if directory == "":
            return

        self.open_folder(directory)

    def open_folder(self, directory):
        """open a folder to get images"""
        print("Loading ", datetime.datetime.now())
        # multi threads getting the image data ( image path, image type, image date )
        self.imgs = [d for d in multi_get_img_data(directory) if d is not None]
        print("Loaded ", datetime.datetime.now())

        if len(self.imgs) == 0:
            return

        self.imgs = sorted(self.imgs, key=lambda item: item.time)
        self.move_to_first_image()
        self.image_buttons.set_image_adders("normal")
        self.image_buttons.delete_button.configure(state="warning")
        self.image_buttons.set_image_navigation("normal")
        self.default_output_base_dir = directory

    def display_image(self):
        """Display the image"""
        if len(self.imgs) == 0:
            return

        self.image_display.canvas.delete("all")
        with Image.open(self.imgs[self.pointer].path) as image:
            image = image.reduce(self.scale).rotate(self.rotation, expand=1)

            global imagetk
            imagetk = ImageTk.PhotoImage(image)
            x, y = image.size
            x, y = x / 2, y / 2
            self.image_display.canvas.create_image(x, y, image=imagetk)

        pagination_data = self.get_pagination_data()
        self.image_buttons.update_pagination_info(pagination_data) 

        current_image_path = self.imgs[self.pointer].path
        # does this need to bind each time or could we bind once and have it use a member var?
        self.image_display.canvas.bind("<Double-Button-1>", lambda _: startfile(current_image_path))

        image_button_state = DISABLED if self.image_is_in_current_play(current_image_path) else NORMAL
        self.image_buttons.set_image_adders(image_button_state)

    def get_pagination_data(self):
        """Get pagination data"""
        current_image_w_path = self.imgs[self.pointer].path
        file_name = basename(current_image_w_path)
        file_date = self.imgs[self.pointer].time
        index = self.pointer + 1 # adjust for 0 based vs 1 based
        color = self.get_image_name_color(current_image_w_path)
        return PaginationData(file_name=file_name, file_date=file_date, image_index=index, image_count=len(self.imgs), color=color)

    def save_session(self):
        """Save the session"""
        if not self.session_exists():
            print("Nothing to do")
            return

        # If there are images in the image table, this will miss those, but seems fine
        if self.play_is_being_editted():
            confirmation = Messagebox.show_question(
                'Are you sure? There is an incomplete play',
                'Save Session Confirmation',
                buttons=['No:secondary', 'Yes:warning'])
            if confirmation != 'Yes':
                return

        # gets the path to the data save
        outdir = self.get_output_dir()
        save_path = join(outdir, "Data")
        csv_file_path = join(save_path, "slots_data.csv")
        makedirs(save_path, exist_ok=True)

        self.confirm_file_is_writable(csv_file_path)

        new_image_path = join(outdir, f"Sorted/{self.get_session_date()}")
        try:
            makedirs(new_image_path, exist_ok=False)
        except Exception:
            pass

        self.move_pics_and_write_csv_file(csv_file_path, new_image_path)

        self.session_table.update_table()

        self.image_buttons.set_image_adders("normal")

        self.image_buttons.save_button.configure(state="disabled")
        self.image_buttons.save_session_button.configure(state="disabled")
        self.set_session_date(self.default_session_date)

    def session_exists(self):
        """Determine if we are already in a session"""
        return len(self.plays) > 0 and self.session_date != self.default_session_date

    def play_is_being_editted(self):
        """Determine if we are editting a play (vs. creating a new one)"""
        return (self._current_play.start_image or
                self._current_play.end_image or
                len(self._current_play.addl_images) or
                self.entry_wigits.start_entry.var.get() or
                self.entry_wigits.end_entry.var.get() or
                self.editing_play())

    def confirm_file_is_writable(self, file_path):
        """Loop until the csv file is writable"""
        while True:
            try:
                f = open(file_path, "a+")
            except OSError:
                Messagebox.show_error(
                    f'Cannot open "{file_path}".\nPlease close and try again',
                    "File Open Error",
                )
            else:
                f.close()
                break

    def get_output_dir(self):
        """open a folder to get images"""
        directory = askdirectory(initialdir=self.default_output_base_dir, mustexist=False)
        return directory

    def move_pics_and_write_csv_file(self, csv_file_path, new_image_path):
        """Move all images to the processed directory and write the csv file"""
        pics_to_remove = []
        # move all images and update play values with new location
        play_id = ""
        try:
            with open(csv_file_path, "a+", newline="") as csvfile:
                writer = csv.writer(csvfile)
                for play_id, p in self.plays.items():
                    moved_pix = self.move_play_images(p, new_image_path)
                    pics_to_remove.extend(moved_pix)

                    for row in p.get_csv_rows():
                        writer.writerow(row)

                    del(self.plays[play_id])
                    self.session_table.update_table()
        except Exception as e:
            Messagebox.show_error(
                f'Error saving session at {play_id}. Aborting. You will need to manually fix things to continue.\n{e}',
                'Error Saving')

        self.imgs = [img for img in self.imgs if img.path not in pics_to_remove]
        self.imgs = sorted(self.imgs, key=lambda item: item.time)
        self.move_to_first_image()

    def move_play_images(self, play, new_path):
        """Move images associated with this play to the new path, updating the play with the new location. returns list of original picture paths"""
        pics_to_remove = []
        if not new_path:
            return pics_to_remove

        if play.start_image:
            pics_to_remove.append(play.start_image)
            play.start_image = move(play.start_image, new_path)

        pics_to_remove.extend(play.addl_images)
        for idx, img in enumerate(play.addl_images):
            play.addl_images[idx] = move(img, new_path)

        if play.end_image:
            pics_to_remove.append(play.end_image)
            play.end_image = move(play.end_image, new_path)
        return pics_to_remove

    def load_final_play(self):
        """Load the last play in the session"""
        self.load_play(list(self.plays.keys())[-1])

    def force_clear(self):
        """Clear all image data from the current play"""
        self.play_imgs.clear()
        self.start_img.set("")
        self.end_img.set("")
        self.entry_wigits.update_table(self)

    def open_test_folder(self):
        """For testing"""
        folder = join(dirname(dirname(__file__)), "Data", "test_pics")
        self.open_folder(folder)

    def set_scale(self):
        """Set scale factor for the image. Larger scale is smaller image."""
        scale = Querybox.get_integer(
            "Enter a integer scale. Larger makes the image smaller",
            "Set scale",
            self.scale,
            1,
        )

        if scale is not None:
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
            if img_name in p.addl_images or img_name == p.start_image or img_name == p.end_image:
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

    def move_to_first_image(self, _=None):
        """display the first image"""
        self.pointer = 0
        self.display_image()

    def move_to_next_image(self, _=None):
        """next image"""
        self.pointer = min((self.pointer + 1), (len(self.imgs) - 1))
        self.display_image()

    def move_to_prev_image(self, _=None):
        """Previous image"""
        # does nothing if there are no images
        self.pointer = max((self.pointer - 1), 0)
        self.display_image()

    def move_to_last_image(self, _=None):
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
        """Sets the session date with the correct format"""
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
        """Update casino for the play. Second param is event for binding"""
        if self.session_frame.casino.var.get():
            casino = self.session_frame.casino.var.get()
            self.dropdown_data.update_machine_dd(casino)
            if self._current_play is not None:
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
        """Update the play type. Param2 is event for binding"""
        if self._current_play is None:
            return
        if self.entry_wigits.play_type.var.get():
            self._current_play.play_type = self.entry_wigits.play_type.var.get()

    def update_denom(self, _=None):
        """Update denom. Param2 is event for binding"""
        if self._current_play is None:
            return
        if self.entry_wigits.denom_cb.var.get():
            self._current_play.denom = self.entry_wigits.denom_cb.var.get()

    def update_pnl(self):
        """update the profit and loss for the play"""
        if self._current_play is None:
            return
        self.entry_wigits.profit_loss.var.set(self._current_play.pnl)


    def add_cash_to_play(self, value):
        """Add this amount to the current play"""
        if self._current_play:
            self._current_play.add_cash(value)
            return True
        return False

    def get_cash_in(self):
        """Get list of cash entries from play"""
        return self._current_play.get_cash_entries()

    def update_cash_in(self, _=None):
        """update the cash in for the play by taking what's in the display table and adding it to the play. param2 is for binding"""
        if self._current_play is None:
            return

        self._current_play.clear_cash_in()
        for ci in self.entry_wigits.get_cash_in():
            self._current_play.add_cash(ci)
        self.update_pnl()
        self.update_total_cash_in()

    def update_total_cash_in(self):
        self.entry_wigits.total_cash_in.set(self._current_play.cash_in)

    def update_total_cash_out(self):
        self.entry_wigits.total_cash_out.set(self._current_play.get_total_cash_out())

    def update_cashout(self, _=None):
        """update the cash out for the play. param2 is for binding"""
        if self._current_play is None:
            return
        if self.entry_wigits.cashout.var.get():
            self._current_play.cash_out = Decimal(self.entry_wigits.cashout.var.get())
            self.update_pnl()
        self.update_total_cash_out()

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
        # self._current_play.hand_pays = self.hand_pay.copy()
        self.update_pnl()
        self.update_cashout()

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
        self.entry_wigits.cashin.var.set("")
        self.entry_wigits.update_cash_in_table(self)
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
        # self.hand_pay = self._current_play.hand_pays.copy()
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
        self.update_cash_in()
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

    def move_to_next_unused_image(self):
        """increment pointer and display tne nexe unused image"""
        # this actually moves to the next image not in current play... need to decided if I want to
        # update the name or the behavior
        while self.image_is_in_current_play(self.imgs[self.pointer].path) and self.pointer < len(self.imgs)-1:
            self.pointer = min((self.pointer + 1), (len(self.imgs) - 1))
        self.display_image()

    def save(self):
        """Save the play"""
        if not self.confirm_save_readiness():
            return

        if self._current_play is None:
            self.create_play()

        if self.editing_play():
            # Get the play id and play object for the item being edited
            li = list(self.plays.items())
            li[self._current_index] = (
                self._current_play.identifier,
                self._current_play,
            )
            # Update the current play
            self.update_all_play_values()
            # If the identifier changes, the new id needs to be used, this copies everythign back correctly.
            self.plays = dict(li)
        else:
            self.update_all_play_values()
            if self._current_play.identifier in self.plays:
                button = Messagebox.okcancel(
                    "You are not editing an exiting play and this will overwrite a play. Proceed?",
                    "Overwrite Warning",
                )
                if button != "OK":
                    return
        # this deepcopy shouldn't be needed, but somehow I am clearing the hand pays
        self.plays[self._current_play.identifier] = copy.deepcopy(self._current_play)

        self.session_table.update_table()

        self.move_to_next_unused_image()
        self.clear_entry_values()

        # resets the save button to disabled
        self.image_buttons.save_button.configure(state="disabled")
        self.image_buttons.save_session_button.configure(state="enabled")
        self.entry_wigits.machine_cb.combobox.focus_set()

        self.create_play()

    def confirm_save_readiness(self):
        """Ask for confirmation if there are warnings, if there is an error, return False, if neither return True"""
        readiness_state = self.get_save_readiness()
        if self.SaveError.FORBIDDEN in readiness_state:
            return False

        if self.SaveError.DATAWARNING in readiness_state:
            confirmed = Messagebox.okcancel(
                "There is potentially some missing data, are you sure?",
                "Incomplete save warning",
            )
            if confirmed != "OK":
                return False

        if self.SaveError.IMGWARNING in readiness_state:
            confirmed = Messagebox.okcancel(
                "At least one image in this play is in another play. Are you sure?",
                "Duplicate image warning",
            )
            if confirmed != "OK":
                return False
        return True

    def clear_entry_values(self):
        """clears all entry values"""

        self._current_index = None
        cash_out = self._current_play.cash_out
        self.play_imgs.clear()
        self.hand_pay.clear()
        self.ttk_state.set("")
        self.entry_wigits.clear_all_widgets()
        self.entry_wigits.cashin.var.set(cash_out)

    def image_is_in_current_play(self, img):
        """determine if the image is in the current play"""
        return (img in self.play_imgs) or \
            (img == self.entry_wigits.start_entry.var.get()) or \
            (img == self.entry_wigits.end_entry.var.get())

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

        img = self.imgs[self.pointer].path
        if not self.should_add(img):
            return

        # sets the start entry wigit to the path of the current image
        self.entry_wigits.start_entry.var.set(self.imgs[self.pointer].path)

        image_dt = self.imgs[self.pointer].time
        self.entry_wigits.set_play_start_datetime(image_dt)

        if not self.session_date_is_valid():
            dt = self.imgs[self.pointer].time
            self.set_session_date(dt)

        self.image_buttons.set_image_adders('disabled')
        self.entry_wigits.bet.entry.focus_set()

    def add_current_image_to_play(self, _=None):
        """add image to the play. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        img = self.imgs[self.pointer].path
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

        img = self.imgs[self.pointer].path
        if not self.should_add(img):
            return

        self.entry_wigits.end_entry.var.set(img)

        image_dt = self.imgs[self.pointer].time.date()

        self.entry_wigits.set_play_end_datetime(image_dt)

        self.image_buttons.set_image_adders('disabled')
        self.entry_wigits.cashout.entry.focus_set()

    def remove_current_image_from_play(self, _=None):
        """Remove the image from the play. Event needed for binding this to a shortcut."""
        if len(self.imgs) == 0:
            return

        path = self.imgs[self.pointer].path
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

        path = self.imgs[self.pointer].path

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
            if img.path == filename:
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

    @staticmethod
    def open_handpay_entry_win(callback):
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
        if casino == "" or not dt_valid or machine == "Select Machine" or play_type == "":
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
            self.image_buttons.save_button.configure(state="normal", bootstyle="warning")
        else:
            self.image_buttons.save_button.configure(state="normal", bootstyle="normal")

    def save_externals(self):
        """Save the csv files for entry drop-downs"""
        self.dropdown_data.save_externals()

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
        self.bind("<Prior>", self.move_to_prev_image)
        self.bind("<Next>", self.move_to_next_image)
        self.bind("<Home>", self.move_to_first_image)
        # self.bind("<End>", self.display_last_image)
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

import os

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox, Messagebox

from tkinter.filedialog import askdirectory

from Scripts.get_imgs_data import multi_get_img_data

from Scripts.ImageDisplay import ImageDisplay
from Scripts.ImageButtons import ImageButtons
from Scripts.EntryWigits import EntryWigits
from Scripts.SessionTable import SessionTable
from Scripts.SessionFrame import SessionFrame

from os import makedirs
from os.path import join, dirname, join

from shutil import move
from PIL import Image, ImageTk

from pillow_heif import register_heif_opener
from decimal import Decimal

import csv
import datetime

from Slots.PlayFactory import PlayFactory
from Slots.Play import Play, HandPay
from Slots.Machine import Machine

register_heif_opener(decode_threads=8, thumbnails=False)

class App(ttk.Window):
    def __init__(self):
        self.imgs = []
        self.play_imgs = []
        self.hand_pay = []
        self.plays = {}
        self._current_play = None
        self.start_datetime = datetime.MINYEAR

        self.play_types = App.get_play_types() 
        self.casino_values = App.get_casinos()
        self.machine_values = App.get_machines()
        self.denom_values = App.get_denoms()
            
        self.pointer = 0
        self.scale = 10
        
        super().__init__()
        self.title('Slots')
        self.minsize(450, 705)
        self.geometry('1300x800')
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        self.default_session_date = "Load first play"
        self.session_date = ttk.StringVar(value=self.default_session_date)
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()
        self.ttk_state = ttk.StringVar()

        self.columnconfigure(0, uniform='a', weight=1)
        self.columnconfigure(1, uniform='a', weight=3)
        self.columnconfigure(2, uniform='a', weight=2)

        self.session_table = SessionTable(self) 
        self.session_table.grid(row=0, column=0, sticky='nsew')

        self.info_frame = ttk.Frame(self)
        self.session_frame = SessionFrame(self.info_frame, self)
        self.session_frame.pack(anchor='center')
        self.entry_wigits = EntryWigits(self.info_frame, self)
        self.entry_wigits.pack(anchor='center')
        self.info_frame.grid(row=0, column=1, sticky='nsew')
        
        image_frame = ttk.Frame(self)
        self.image_display = ImageDisplay(image_frame)
        
        self.image_buttons = ImageButtons(image_frame, self)
        self.image_buttons.pack(side='top', padx=5, pady=5, anchor='n')
        self.image_display.pack(side='top', padx=5, pady=5)
        #image_frame.pack(side='right', fill='both', anchor='ne')
        image_frame.grid(row=0, column=2, sticky='nsew')
        
        self.make_menu()
        
        self.setup_keybinds()

    @staticmethod
    def get_entry_values(file_name, defaults=None):
        if os.path.exists(file_name):
            with open(file_name, 'r') as csvfile:
                values = list(csv.reader(csvfile))
                values = [val.strip() for sublist in values for val in sublist if (val.strip() != '')]
                return values

        msg = f"{file_name} not found."
        if defaults:
            print(msg, " Using defaults.")
            return defaults

        print(msg)
        return []

    @staticmethod
    def get_play_types():
        play_type_defaults = ('AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip')
        play_types_file = 'play_types.csv'
        return App.get_entry_values(play_types_file, play_type_defaults) 

    @staticmethod
    def get_casinos():
        casinos_file = f'casino_entry_values.csv'
        return App.get_entry_values(casinos_file)

    @staticmethod
    def get_machines():
        machines_file = f'machine_entry_values.csv'
        return App.get_entry_values(machines_file)

    @staticmethod
    def get_denoms():
        denom_file = f'denom_entry_values.csv'
        return App.get_entry_values(denom_file)

    def make_menu(self):
        # creates the menu wigit
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)
        
        # creates sub menu
        file_menu = ttk.Menu(menu, tearoff=False)
        # adds a button in the sub menu that opens a folder
        file_menu.add_command(label='Open Folder', command=self.open_folder)
        file_menu.add_separator()
        # adds a button that will open a sub window to enter a casino in
        file_menu.add_command(label='Add Casino', command=self.add_casino)
        # adds a button that will open a sub window to enter a machine in
        file_menu.add_command(label='Add Machine', command=self.add_machine)
        file_menu.add_separator()
        file_menu.add_command(label='Preload Test Play', command=self.load_test_play)
        
        file_menu.add_command(label='Set Scale', command=self.set_scale)
        
        menu.add_cascade(label='File', menu=file_menu)
    

    def open_folder(self):
        # opens a file menu to open a directory
        directory = askdirectory(mustexist=True)
        if directory == '':
            return
        
        print ('Loading ', datetime.datetime.now())
        # multi threads geting the image data ( image path, image type, image date )
        self.imgs = [d for d in multi_get_img_data(directory) if d is not None]
        print('Loaded ', datetime.datetime.now())
        
        # does nothing else if there are not images in the directory
        if len(self.imgs) == 0:
            return
        
        # sorts images in the image list by date
        self.imgs = sorted(self.imgs, key=lambda item: item[2])
        # displays the oldest image
        self.display_image()
        
        self.image_buttons.save_button.configure(state='disabled')
        self.image_buttons.add_button.configure(state='normal')
        self.image_buttons.start_button.configure(state='normal')
        self.image_buttons.end_button.configure(state='normal')
        self.image_buttons.remove_button.configure(state='disabled')

    def load_test_play(self):
        self.session_frame.casino.var.set("ilani")
        self.session_date.set(datetime.datetime(2024,5,1).strftime('%Y-%m-%d'))
        self.entry_wigits.dt.var.set(datetime.datetime(2024,5,1, 12, 3, 5).strftime('%Y-%m-%dT%H:%M:%S'))
        self.entry_wigits.machine_cb.var.set("Lucky Wealth Cat")
        self.entry_wigits.cashin.var.set("100.00")
        self.entry_wigits.bet.var.set("1.20")
        self.entry_wigits.play_type.var.set("AP")
        self.entry_wigits.initial_state.text.insert('1.0', "This, is; a (state): 1223")
        self.entry_wigits.cashout.var.set("120.00")

    def add_casino(self):
        # opens a window to ask for a casino
        new_casino = Querybox.get_string(prompt='Enter a casino', title='Casino Entry')
        
        # adds the new value to the casino values list if it is not None and not in it already
        if (new_casino is not None) and (new_casino not in self.casino_values):
            self.casino_values.append(new_casino)
    
    def add_machine(self):
        # opens a window to ask for a machine
        new_machine = Querybox.get_string(prompt='Enter a machine', title='Machine Entry')
        
        # adds the new value to the machine values list if it is not None and not in it already
        if (new_machine is not None) and (new_machine not in self.machine_values):
            self.machine_values.append(new_machine)
    
    def set_scale(self):
        scale = Querybox.get_integer('Enter a integer scale', 'Set scale', self.scale, 1)
        if scale is None:
            pass
        else:
            self.scale = scale
        self.display_image()

    def display_image(self):
        if len(self.imgs) == 0:
            return
        
        self.image_display.canvas.delete('all')
        # opens the image at the current pointer
        with Image.open(self.imgs[self.pointer][0]) as image:
            
            image = image.reduce(self.scale)
            
            global imagetk
            # turns the image into a image that tkinter can display
            imagetk = ImageTk.PhotoImage(image)
            
            # gets the image dimensions and divides them by 2
            x, y = image.size
            x, y = x/2, y/2
            
            # adds the image to the canvas
            self.image_display.canvas.create_image(x, y, image=imagetk)
    
    def create_play(self, machine_name):
        print(f"Creating play for {machine_name}")
        self._current_play = PlayFactory.get_play(machine_name)

    def save(self):
        # does nothing if the save button is disabled
        if self.image_buttons.save_button.state() == 'disabled':
            return
        #if len(self.imgs) == 0:
        #    return

        # gets all entry values
        self._current_play.casino = self.session_frame.casino.var.get()
        self._current_play.cash_in = Decimal(self.entry_wigits.cashin.var.get())
        self._current_play.bet = Decimal(self.entry_wigits.bet.var.get())
        self._current_play.play_type = self.entry_wigits.play_type.var.get()
        self._current_play.state = ' '.join(self.entry_wigits.initial_state.get_text().split(r'\n')).rstrip()
        self._current_play.cash_out = Decimal(self.entry_wigits.cashout.var.get())
        self._current_play.note = ' '.join(self.entry_wigits.note.get_text().split(r'\n')).rstrip()
        
        self._current_play.start_image = self.entry_wigits.start_entry.var.get()
        self._current_play.end_image = self.entry_wigits.end_entry.var.get()
        self._current_play.addl_images = self.play_imgs
        self._current_play.start_time = datetime.datetime.strptime(self.entry_wigits.dt.var.get(), '%Y-%m-%d %H:%M:%S')
        print(self._current_play.start_time)

        for hp in self.hand_pay:
            self._current_play.add_hand_pay(hp)

        self.plays[self._current_play.identifier] = self._current_play 
        self.session_table.update_table(self)

        self.imgs = [d for d in self.imgs if ((d[0] not in self._current_play.addl_images) and (d[0] != self._current_play.start_image) and (d[0] != self._current_play.end_image))]
        self.imgs = sorted(self.imgs, key=lambda item: item[2])

        # clears all entry values
        self.entry_wigits.dt.var.set('')
        self.entry_wigits.cashin.var.set(self._current_play.cash_out)
        self.entry_wigits.bet.var.set(0)
        self.entry_wigits.initial_state.clear()
        self.entry_wigits.cashout.var.set(0)
        self.entry_wigits.note.clear()
        self.entry_wigits.start_entry.var.set('')
        self.entry_wigits.end_entry.var.set('') 

        self.play_imgs.clear()
        self.entry_wigits.update_table(self)

        self.hand_pay.clear()
        self.entry_wigits.update_hand_pay_table(self)
        
        # resets the save button to disabled
        self.image_buttons.save_button.configure(state='disabled')

    def save_session(self):
        # gets the path to the data save
        save_path = join(dirname(dirname(__file__)), 'Data')
        file_path = join(save_path, 'slots_data.csv')
        print(save_path)

        makedirs(save_path, exist_ok=True)

        while True:
            try:
                f = open(file_path, 'a+')
            except Exception:
                Messagebox.show_error(f'Cannot open "{file_path}".\nPlease close and try again', 'File Open Error')
            else:
                f.close()
                break
        

        new_path = ""
        if list(self.plays.values())[0].start_image:
            new_path = join(dirname(dirname(list(self.plays.values())[0].start_image)), f'Sorted/{self.session_date.get()}')
        
            try:
                makedirs(new_path, exist_ok=False)
            except Exception:
                pass

            # move all images and update play values with new location
        for p in list(self.plays.values()):
            if p.start_image and new_path:
                print("start", self.session_date.get(), p.start_image) 
                p.start_image = move(p.start_image, new_path)
            for i,a in enumerate(p.addl_images):
                print("addl", self.session_date.get(), a) 
                p.addl_images[i] = move(a, new_path)
            if p.end_image and new_path:
                print("end", self.session_date.get(), p.end_image) 
                p.end_image = move(p.end_image, new_path)

            # Save csv
            print(f"Writing to {file_path}\n")
            with open(file_path, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row in p.get_csv_rows():
                    writer.writerow(row)
                    #csvfile.writelines(str(p))
            
        self.plays.clear()
        self.session_table.update_table(self)

        self.image_buttons.add_button.configure(state='normal')
        self.image_buttons.start_button.configure(state='normal')
        self.image_buttons.end_button.configure(state='normal')
        self.image_buttons.remove_button.configure(state='disabled')
        
        # resets the save button to disabled
        self.image_buttons.save_button.configure(state='disabled')
    
    def check_save_valid(self):
        casino = self.session_frame.casino.var.get()

        dt = self.entry_wigits.dt.var.get()
        machine = self.entry_wigits.machine_cb.var.get()

        play_type = self.entry_wigits.play_type.var.get()
        
        # checks if they are empty
        if casino=='' or dt=='' or machine=='' or play_type=='':
            # disables the save button
            self.image_buttons.save_button.configure(state='disabled')
        else:
            # enables the save button
            self.image_buttons.save_button.configure(state='normal')
        
    def save_externals(self):
        externals = {'casino_entry_values.csv': self.casino_values, 'machine_entry_values.csv': self.machine_values, 'denom_entry_values.csv': self.denom_values, 'playtype_entry_values.csv': self.play_types}
        for f, var in externals.items():
            file_path = join(dirname(dirname(__file__)), f)
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for item in var:
                    writer.writerow([item])
        
    def setup_keybinds(self):
        self.bind('<FocusIn>', lambda _: self.check_save_valid())
        self.bind('<FocusOut>', lambda _: self.check_save_valid())

        self.bind('<Control-s>', lambda _: self.save())
        self.bind('<Prior>', lambda _: self.image_buttons.prev_button_command(self))
        self.bind('<Next>', lambda _: self.image_buttons.next_button_command(self))
        self.bind('<Home>', lambda _: self.image_buttons.return_button_command(self))
        self.bind('<Control-Key-1>', lambda _: self.image_buttons.start_button_command(self))
        self.bind('<Control-Key-2>', lambda _: self.image_buttons.add_button_command(self))
        self.bind('<Control-Key-3>', lambda _: self.image_buttons.end_button_command(self))


if __name__ == '__main__':
    # calls the app
    root = App()
    # runs the main loop
    root.mainloop()
    # saves the external values to their csv files
    root.save_externals()
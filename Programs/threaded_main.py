import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox, Messagebox

from tkinter.filedialog import askdirectory

from Scripts.get_imgs_data import multi_get_img_data

from Scripts.ImageDisplay import ImageDisplay
from Scripts.ImageButtons import ImageButtons
from Scripts.EntryWigits import EntryWigits
from Scripts.SessionTable import SessionTable

from os import makedirs
from os.path import join, dirname, join

from shutil import move
from PIL import Image, ImageTk

from pillow_heif import register_heif_opener
from decimal import Decimal

import csv
import datetime

from Slots.Play import Play, HandPay
from Slots.Machine import Machine

register_heif_opener(decode_threads=8, thumbnails=False)


class App(ttk.Window):
    def __init__(self):
        self.imgs = []
        self.play_imgs = []
        self.hand_pay = []
        self.plays = []

        self.play_type = ('AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip')
        
        with open(f'casino_entry_values.csv', 'r') as csvfile:
            casino_values = list(csv.reader(csvfile))
            self.casino_values = [val.strip() for sublist in casino_values for val in sublist if (val.strip() != '')]
        
        with open(f'machine_entry_values.csv', 'r') as csvfile:
            machine_values = list(csv.reader(csvfile))
            self.machine_values = [val for sublist in machine_values for val in sublist]
            
        self.pointer = 0
        self.scale = 10
        
        super().__init__()
        self.title('Slots')
        self.minsize(450, 705)
        self.geometry('1300x800')
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        self.session_date = ttk.StringVar()
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()

        self.session_table = SessionTable(self) 
        self.session_table.pack(side='left', padx=5, pady=5, fill='both')

        self.entry_wigits = EntryWigits(self, self)
        self.entry_wigits.pack(side='left', padx=5, pady=5, fill='both')
        
        image_frame = ttk.Frame(self)
        
        self.image_display = ImageDisplay(image_frame)
        
        self.image_buttons = ImageButtons(image_frame, self)
        self.image_buttons.pack(side='top', padx=5, pady=5, anchor='nw')
        self.image_display.pack(side='top', padx=5, pady=5)
        image_frame.pack(side='left', fill='both')
        
        self.make_menu()
        
        self.setup_keybinds()

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
    
    def save(self):
        # does nothing if the save button is disabled
        if self.image_buttons.save_button.state() == 'disabled':
            return
        if len(self.imgs) == 0:
            return

        # gets all entry values
        casino = self.entry_wigits.casino.var.get()
        date = self.entry_wigits.date.var.get()
        machine = self.entry_wigits.machine.var.get()
        cash_in = Decimal(self.entry_wigits.cashin.var.get())
        bet = Decimal(self.entry_wigits.bet.var.get())
        play_type = self.entry_wigits.play_type.var.get()
        initial_state = ' '.join(self.entry_wigits.initial_state.get_text().split(r'\n')).rstrip()
        cash_out = Decimal(self.entry_wigits.cashout.var.get())
        note = ' '.join(self.entry_wigits.note.get_text().split(r'\n')).rstrip()
        
        start_img = self.entry_wigits.start_entry.var.get()
        end_img = self.entry_wigits.end_entry.var.get()
        other = self.play_imgs
        xdate = datetime.datetime( int(date[:4]), int(date[4:6]), int(date[6:]))
        # adding handpays is later
        current_play = Play(machine=Machine(machine), casino=casino, start_time=xdate, cash_in=cash_in, bet=bet,play_type=play_type, state=initial_state, note=note, start_image=start_img, addl_images=other, end_image=end_img, cash_out=cash_out)
        for hp in self.hand_pay:
            current_play.add_hand_pay(hp)

        self.plays.append(current_play) 
        self.session_table.update_table(self)

        self.imgs = [d for d in self.imgs if ((d[0] not in other) and (d[0] != start_img) and (d[0] != end_img))]
        self.imgs = sorted(self.imgs, key=lambda item: item[2])

        # clears all entry values
        self.entry_wigits.date.var.set('')
        self.entry_wigits.cashin.var.set(cash_out)
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
        
        new_path = join(dirname(dirname(self.plays[0].start_image)), f'Sorted/{self.session_date.get()}')
        
        try:
            makedirs(new_path, exist_ok=False)
        except Exception:
            pass

        print("plays:", len(self.plays))
        for p in self.plays:
            if p.start_image is not None:
                print("start", self.session_date.get(), p.start_image) 
                p.start_image = move(p.start_image, new_path)
            for i,a in enumerate(p.addl_images):
                print("addl", self.session_date.get(), a) 
                p.addl_images[i] = move(a, new_path)
            if p.end_image:
                print("end", self.session_date.get(), p.end_image) 
                p.end_image = move(p.end_image, new_path)

            with open(file_path, 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(str(p).split('\n'))
            
        self.plays.clear()
        self.session_table.update_table(self)

        self.image_buttons.add_button.configure(state='normal')
        self.image_buttons.start_button.configure(state='normal')
        self.image_buttons.end_button.configure(state='normal')
        self.image_buttons.remove_button.configure(state='disabled')
        
        # resets the save button to disabled
        self.image_buttons.save_button.configure(state='disabled')
    
    def check_save_valid(self):
        # gets the entry values that need to be filled to save
        casino = self.entry_wigits.casino.var.get()

        date = self.entry_wigits.date.var.get()
        machine = self.entry_wigits.machine.var.get()
        play_type = self.entry_wigits.play_type.var.get()
        
        # checks if they are empty
        if casino=='' or date=='' or machine=='' or play_type=='':
            # disables the save button
            self.image_buttons.save_button.configure(state='disabled')
        else:
            # enables the save button
            self.image_buttons.save_button.configure(state='normal')
        
    def save_externals(self):
        # gets the path to casino entry values csv file
        file_path = join(dirname(dirname(__file__)), 'casino_entry_values.csv')
        # saves the casino entry values to the csv file
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in self.casino_values:
                writer.writerow([item])
        
        # gets teh path to the machine entry values csv file
        file_path = join(dirname(dirname(__file__)), 'machine_entry_values.csv')
        # saves the machine entry values to the csv file
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in self.machine_values:
                writer.writerow([item])


if __name__ == '__main__':
    # calls the app
    root = App()
    # runs the main loop
    root.mainloop()
    # saves the external values to their csv files
    root.save_externals()
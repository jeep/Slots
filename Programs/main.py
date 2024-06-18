'''length of play      end end - start time'''


import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox

from tkinter.filedialog import askdirectory

from Premade.ComboboxLabel import ComboboxLabel
from Premade.EntryLabel import EntryLabel
from Premade.MoneyEntryLabel import MoneyEntryLabel
from Premade.LabelLabel import LabelLabel
from Premade.LargeEntryLabel import LargeEntryLabel

from os import listdir, makedirs
from os.path import isfile, join, dirname, basename

from shutil import move

from PIL import Image, ExifTags, ImageTk

from datetime import datetime

import csv




class App(ttk.Window):
    def __init__(self):
        self.imgs = []
        self.play_type = ['AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip', 'Tax Consequence']
        with open(fr'external_entry_values.csv', 'r') as csvfile:
            csv_values = list(csv.reader(csvfile))
            self.casino_values = csv_values[0]
            self.machine_values = csv_values[1]
        self.pointer = 0
        
        
        
        # main setup
        super().__init__()
        self.title('Slots')
        self.minsize(1000, 800)
        self.geometry('1000x800')
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()
        
        # wigits
        self.entry_wigits = EntryWigits(self)
        self.entry_wigits.place(x=5, y=5)
        
        self.image_display = ImageDisplay(self)
        self.image_display.place(x=440, y=5)
        
        self.image_buttons = ImageButtons(self)
        self.image_buttons.place(x=220, y=5)
        
        self.make_menu()
        
        
        # run
        self.mainloop()
    
    def make_menu(self):
        
        # menu setup
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)
        
        # file menu
        file_menu = ttk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Open Folder', command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label='Add Casino', command=self.add_casino)
        file_menu.add_command(label='Add Machine', command=self.add_machine)
        menu.add_cascade(label='File', menu=file_menu)
    
    def open_folder(self):
        directory = askdirectory(mustexist=True)
        if directory == '':
            return
        
        self.imgs = [{'path': join(directory, f)} for f in listdir(directory) if isfile(join(directory, f))]
        #self.imgs = {join(directory, f): {} for f in listdir(directory) if isfile(join(directory, f))}
        for index, img in enumerate(self.imgs):
            img_path = img['path']
            
            image = Image.open(img_path)
            time = App.get_time(image)
            
            
            
            resized_img = image.reduce(5)
            imagetk = ImageTk.PhotoImage(resized_img)
            
            self.imgs[index]['image'] = image
            self.imgs[index]['imagetk'] = imagetk
            self.imgs[index]['image_time'] = time
        
        self.imgs = list(sorted(self.imgs, key=lambda item: item['image_time']))
        
        self.display_image()
        
    
    def add_casino(self):
        new_casino = Querybox.get_string(prompt='Enter a casino', title='Casino Entry')
        if new_casino is not None:
            self.casino_values.append(new_casino)
    
    def add_machine(self):
        new_machine = Querybox.get_string(prompt='Enter a machine', title='Machine Entry')
        if new_machine is not None:
            self.machine_values.append(new_machine)
    
    @staticmethod
    def get_time(image):
        image_exif = image._getexif()
        exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
        date_obj = datetime.strptime(exif['DateTimeOriginal'], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
        return date_obj

    def display_image(self):
        self.image_display.canvas.create_image(0, 0, image=self.imgs[self.pointer]['imagetk'])



class EntryWigits(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        
        self.casino = ComboboxLabel(self, 'Casino', parent.casino_values, state='readonly')
        self.casino.pack(fill='x')
        
        self.date = EntryLabel(self, 'Date', state='readonly')
        self.date.pack(fill='x')
        
        self.machine = ComboboxLabel(self, 'Machine', parent.machine_values, state='readonly')
        self.machine.pack(fill='x')
        
        self.cashin = MoneyEntryLabel(self, 'Cash In')
        self.cashin.pack(fill='x')
        self.cashin.bind('<FocusIn>', lambda _: self.cashin.entry.selection_range(0, ttk.END))
        
        self.bet = MoneyEntryLabel(self, 'Bet')
        self.bet.pack(fill='x')
        self.bet.bind('<FocusIn>', lambda _: self.bet.entry.selection_range(0, ttk.END))
        
        self.play_type = ComboboxLabel(self, 'Play Type', parent.play_type, state='readonly')
        self.play_type.pack(fill='x')
        
        self.initial_state = LargeEntryLabel(self, 'Initial State')
        self.initial_state.pack(fill='x')
        
        self.cashout = MoneyEntryLabel(self, 'Cash Out')
        self.cashout.pack(fill='x')
        self.cashout.bind('<FocusIn>', lambda _: self.cashout.entry.selection_range(0, ttk.END))
        
        self.profit_loss = LabelLabel(self, 'Prophet/Loss', self.cashout.var.get() - self.cashin.var.get())
        parent.bind('<Key>', lambda _: self.profit_loss.var.set(self.cashout.var.get() - self.cashin.var.get()))
        self.profit_loss.pack(fill='x')
        
        self.note = LargeEntryLabel(self, 'Note', height=8)
        self.note.pack(fill='x')
        
        self.start_entry = EntryLabel(self, 'Start Image', parent.start_img, state='readonly')
        self.start_entry.pack(fill='x')

        self.end_entry = EntryLabel(self, 'End Image', parent.end_img, state='readonly')
        self.end_entry.pack(fill='x')
        
        

class ImageButtons(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.columnconfigure((0, 1), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')
        
        
        prev_button = ttk.Button(self, text='Prev', command=lambda: self.prev_button_command(parent))
        prev_button.grid(column=0, row=0, sticky='nsew', padx=(0, 3), pady=(0, 3))
        
        next_button = ttk.Button(self, text='Next', command=lambda: self.next_button_command(parent))
        next_button.grid(column=1, row=0, sticky='nsew', padx=(3, 0), pady=(0, 3))
        
        start_button = ttk.Button(self, text='Set Start', command=lambda: self.start_button_command(parent))
        start_button.grid(column=0, row=1, sticky='nsew', padx=(0, 3), pady=(3, 3))
        
        end_button = ttk.Button(self, text='Set End', command=lambda: self.end_button_command(parent))
        end_button.grid(column=1, row=1, sticky='nsew', padx=(3, 0), pady=(3, 3))
        
        add_button = ttk.Button(self, text='Add Image') # command=lambda: self.add_button_command(parent)
        add_button.grid(column=0, row=2, sticky='nsew', padx=(0, 3), pady=(3, 0))
        
        add_button = ttk.Button(self, text='Delete Image') # command=lambda: self.add_button_command(parent)
        add_button.grid(column=1, row=2, sticky='nsew', padx=(3, 0), pady=(3, 0))
    
    
    
    def next_button_command(self, parent):
        parent.pointer += 1
        
        if parent.pointer > len(parent.imgs)-1:
            parent.pointer = len(parent.imgs)-1
            return
        parent.display_image()
    
    def prev_button_command(self, parent):
        parent.pointer -= 1
        
        if parent.pointer < 0:
            parent.pointer = 0
            return
        parent.display_image()
    
    def start_button_command(self, parent):
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer]['path']
        file_name = basename(old_path)
        
        parent.entry_wigits.date.var.set(parent.imgs[parent.pointer]['image_time'][:8])
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[parent.pointer]['path'] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item['image_time']))
        
        parent.entry_wigits.start_entry.var.set(parent.imgs[parent.pointer]['path'])
    
    def end_button_command(self, parent):
        if parent.entry_wigits.start_entry.var.get() == '':
            return
        
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer]['path']
        file_name = basename(old_path)
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[parent.pointer]['path'] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item['image_time']))
        
        parent.entry_wigits.end_entry.var.set(parent.imgs[parent.pointer]['path'])


class ImageDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.canvas = ttk.Canvas(master=self, width=500, height=500)
        self.canvas.pack(fill='both')



App()
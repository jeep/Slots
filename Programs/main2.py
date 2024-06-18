'''length of play      end end - start time'''


import ttkbootstrap as ttk
#from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.dialogs import Querybox
#from tkinter.filedialog import askopenfilenames




#from os import walk
#from os.path import basename, exists, splitext
from shutil import move
from os import listdir, makedirs
from os.path import isfile, join, dirname
from tkinter.filedialog import askdirectory
from PIL import Image, ExifTags, ImageTk
from datetime import datetime
from Premade.ComboboxLabel import ComboboxLabel
from Premade.DateEntryLabel import DateEntryLabel
from Premade.EntryLabel import EntryLabel
from Premade.MoneyEntryLabel import MoneyEntryLabel
from Premade.LabelLabel import LabelLabel
import csv
from Premade.LargeEntryLabel import LargeEntryLabel




class App(ttk.Window):
    def __init__(self):
        self.imgs = {}
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
        self.image_display.place(x=400, y=5)
        
        self.image_buttons = ImageButtons(self)
        self.image_buttons.place(x=250, y=5)
        
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
        
        self.imgs = {join(directory, f): {} for f in listdir(directory) if isfile(join(directory, f))}
        for img in self.imgs:
            image = Image.open(img)
            time = App.get_time(image)
            
            self.imgs[img]['image'] = image
            
            image = image.reduce(5)
            imagetk = ImageTk.PhotoImage(image)
            
            self.imgs[img]['imagetk'] = imagetk
            self.imgs[img]['image_time'] = time
        
        self.imgs = dict(sorted(self.imgs.items(), key=lambda item: item[1]['image_time']))
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
        self.image_display.canvas.create_image(0, 0, image=self.imgs[list(self.imgs.keys())[self.pointer]]['imagetk'])



class EntryWigits(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        
        self.casino = ComboboxLabel(self, 'Casino', parent.casino_values, state='readonly')
        self.casino.pack(fill='x')
        
        self.date = DateEntryLabel(self, 'Date', r'%Y%m%d')
        self.date.pack(fill='x')
        
        self.machine = ComboboxLabel(self, 'Machine', parent.machine_values, state='readonly')
        self.machine.pack(fill='x')
        
        self.cashin = MoneyEntryLabel(self, 'Cash In')
        self.cashin.pack(fill='x')
        
        self.bet = MoneyEntryLabel(self, 'Bet')
        self.bet.pack(fill='x')
        
        self.play_type = ComboboxLabel(self, 'Play Type', parent.play_type, state='readonly')
        self.play_type.pack(fill='x')
        
        self.initial_state = LargeEntryLabel(self, 'Initial State')
        self.initial_state.pack(fill='x')
        
        self.cashout = MoneyEntryLabel(self, 'Cash Out')
        self.cashout.pack(fill='x')
        
        self.profit_loss = LabelLabel(self, 'Prophet/Loss', self.cashout.var.get() - self.cashin.var.get())
        parent.bind('<Key>', lambda _: self.profit_loss.var.set(self.cashout.var.get() - self.cashin.var.get()))
        self.profit_loss.pack(fill='x')
        
        self.note = LargeEntryLabel(self, 'Note', height=8)
        self.note.pack(fill='x')
        
        self.start_entry = EntryLabel(self, 'Start Image', parent.start_img)
        self.start_entry.pack(fill='x')

        self.end_entry = EntryLabel(self, 'End Image', parent.end_img)
        self.end_entry.pack(fill='x')
        
        

class ImageButtons(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        
        move_button_frame = ttk.Frame(self)
        prev_button = ttk.Button(move_button_frame, text='Prev', command=lambda: self.prev_button_command(parent))
        prev_button.pack(side='left', padx=(0, 2))
        
        next_button = ttk.Button(move_button_frame, text='Next', command=lambda: self.next_button_command(parent))
        next_button.pack(side='right', padx=(2, 0))
        move_button_frame.pack(pady=5)
        
        pos_button_frame = ttk.Frame(self)
        start_button = ttk.Button(pos_button_frame, text='Set Start', command=lambda: self.start_button_command(parent))
        start_button.pack(side='left', padx=(0, 2))
        
        end_button = ttk.Button(pos_button_frame, text='Set End', command=lambda: self.end_button_command(parent))
        end_button.pack(side='right', padx=(2, 0))
        pos_button_frame.pack()
    
    
    
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
        old_path = list(parent.imgs.keys())[parent.pointer]
        
        parent.entry_wigits.date.var.set(parent.imgs[old_path]['image_time'][:8])
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[new_path] = parent.imgs.pop(old_path)
        
        parent.entry_wigits.start_entry.var.set(list(parent.imgs.keys())[parent.pointer])
    
    def end_button_command(self, parent):
        old_path = list(parent.imgs.keys())[parent.pointer]
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[new_path] = parent.imgs.pop(old_path)
        
        parent.entry_wigits.end_entry.var.set(list(parent.imgs.keys())[parent.pointer])


class ImageDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.canvas = ttk.Canvas(master=self, width=500, height=500)
        self.canvas.pack(fill='both')










App()
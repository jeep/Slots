import ttkbootstrap as ttk
#from ttkbootstrap.widgets import DateEntry
#from ttkbootstrap.dialogs import Querybox
#from tkinter.filedialog import askopenfilenames

#from PIL import Image, ImageTk

#import csv
#from os import walk, makedirs
#from os.path import basename, exists, splitext
#from shutil import move
from os import listdir
from os.path import isfile, join
from tkinter.filedialog import askdirectory
from PIL import Image, ExifTags
from datetime import datetime
from Premade.ComboboxLabel import ComboboxLabel
from Premade.DateEntryLabel import DateEntryLabel
from Premade.EntryLabel import EntryLabel
from Premade.MoneyEntryLabel import MoneyEntryLabel
import csv




class App(ttk.Window):
    def __init__(self):
        self.imgs = {}
        self.play_type = ['AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip', 'Tax Consequence']
        with open(fr'external_entry_values.csv', 'r') as csvfile:
            csv_values = list(csv.reader(csvfile))
            self.casino_values = csv_values[0]
            self.machine_values = csv_values[1]
        
        # main setup
        super().__init__()
        self.title('Slots')
        self.minsize(600, 450)
        self.geometry('600x450')
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        # wigits
        self.entry_wigits = EntryWigits(self)
        self.entry_wigits.pack()
        
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
        #file_menu.add_command(label='Add Casino', command=self.add_casino)
        menu.add_cascade(label='File', menu=file_menu)
    
    def open_folder(self):
        directory = askdirectory(mustexist=True)
        self.imgs = {join(directory, f): {} for f in listdir(directory) if isfile(join(directory, f))}
        for img in self.imgs:
            image = Image.open(img)
            time = App.get_time(image)
            
            self.imgs[img]['image'] = image
            self.imgs[img]['time'] = time
        
        self.imgs = dict(sorted(self.imgs.items(), key=lambda item: item[1]['time']))
    
    @staticmethod
    def get_time(image):
        image_exif = image._getexif()
        exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
        date_obj = datetime.strptime(exif['DateTimeOriginal'], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
        return date_obj



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
        
        self.bet = EntryLabel(self, 'Bet')
        self.bet.pack(fill='x')
        
        self.play_type = ComboboxLabel(self, 'Play Type', parent.play_type, state='readonly')
        self.play_type.pack(fill='x')
        
        #initial state
        #
        
        self.cashout = MoneyEntryLabel(self, 'Cash Out')
        self.cashout.pack(fill='x')
        
        #pl
        #
        
        #note
        #
        
        
        
        
        





App()
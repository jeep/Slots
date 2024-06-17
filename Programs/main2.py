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
import csv




class App(ttk.Window):
    def __init__(self):
        self.imgs = {}
        with open(fr'casino_entry_values.csv', 'r') as csvfile:
            self.casino_values = list(csv.reader(csvfile))
        
        # main setup
        super().__init__()
        self.title('Slots')
        self.minsize(600, 450)
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        # wigits
        EntryWigits(self)
        
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
        
        self.casino = ComboboxLabel(self, 'Casino', combobox_values=parent.casino_values)
        self.casino.pack()
        
        
        





App()
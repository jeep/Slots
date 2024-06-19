'''length of play      end end - start time'''
''' add image remove from play'''


import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox, Messagebox

from tkinter.filedialog import askdirectory

from Premade.ComboboxLabel import ComboboxLabel
from Premade.EntryLabel import EntryLabel
from Premade.MoneyEntryLabel import MoneyEntryLabel
from Premade.LabelLabel import LabelLabel
from Premade.LargeEntryLabel import LargeEntryLabel

from os import listdir, makedirs, remove
from os.path import isfile, join, dirname, basename

from shutil import move

from PIL import Image, ExifTags, ImageTk

from datetime import datetime

import csv

from pillow_heif import register_heif_opener


register_heif_opener()



class App(ttk.Window):
    def __init__(self):
        self.imgs = []
        self.play_imgs = []
        self.play_type = ['AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip', 'Tax Consequence']
        with open(fr'external_entry_values.csv', 'r') as csvfile:
            csv_values = list(csv.reader(csvfile))
            self.casino_values = csv_values[0]
            self.machine_values = csv_values[1]
        self.pointer = 0
        
        super().__init__()
        self.title('Slots')
        self.minsize(1000, 800)
        self.geometry('1000x800')
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        self.start_img = ttk.StringVar()
        self.end_img = ttk.StringVar()
        
        self.entry_wigits = EntryWigits(self)
        self.entry_wigits.place(x=5, y=5)
        
        self.image_display = ImageDisplay(self)
        self.image_display.place(x=440, y=5)
        
        self.image_buttons = ImageButtons(self)
        self.image_buttons.place(x=220, y=5)
        
        self.make_menu()
        
        self.bind('<FocusIn>', lambda _: self.check_save_valid())
        self.bind('<FocusOut>', lambda _: self.check_save_valid())
        self.bind('Control-s', lambda _: self.save())
        
        self.mainloop()
        
        self.save_externals()
    
    
    def make_menu(self):
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)
        
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
        
        if len(self.imgs) != 0:
            for index, img in enumerate(self.imgs):
                img_path = img['path']
                image_type = img_path[img_path.find('.'):]
                print(image_type)
                
                image = Image.open(img_path)
                time = App.get_time(image)
                
                
                
                resized_img = image.reduce(10)
                imagetk = ImageTk.PhotoImage(resized_img)
                
                self.imgs[index]['image'] = image
                self.imgs[index]['imagetk'] = imagetk
                self.imgs[index]['image_time'] = time
                self.imgs[index]['image_type'] = image_type
            
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
        try:
            image_exif = image._getexif()
            exif = { ExifTags.TAGS[k]: v for k, v in image_exif.items() if k in ExifTags.TAGS and type(v) is not bytes }
            date_obj = datetime.strptime(exif['DateTimeOriginal'], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
            return date_obj
        except AttributeError:
            image_exif = image.getexif()
            date_obj = datetime.strptime(image_exif[306], r'%Y:%m:%d %H:%M:%S').strftime(r'%Y%m%d%H%M%S')
            return date_obj
        

    def display_image(self):
        if self.imgs[self.pointer]['image_type'] == '.HEIC':
            place = 250
        else: place = 0
        
        self.image_display.canvas.create_image(place, place, image=self.imgs[self.pointer]['imagetk'])
    
    def save(self):
        if self.image_buttons.save_button.state() == 'disabled':
            return
        
        casino = self.entry_wigits.casino.var.get()
        date = self.entry_wigits.date.var.get()
        machine = self.entry_wigits.machine.var.get()
        cash_in = self.entry_wigits.cashin.var.get()
        bet = self.entry_wigits.bet.var.get()
        play_type = self.entry_wigits.play_type.var.get()
        initial_state = self.entry_wigits.initial_state.get_text()
        cash_out = self.entry_wigits.cashout.var.get()
        note = self.entry_wigits.note.get_text()
        start_img = self.entry_wigits.start_entry.var.get()
        end_img = self.entry_wigits.end_entry.var.get() 
        other = self.play_imgs
        values = [casino, date, machine, cash_in, bet, play_type, initial_state, cash_out, note, start_img, end_img, other]
        
        file_path = join(dirname(dirname(__file__)), 'Data\\slots_data.csv')
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(values)
        
        self.entry_wigits.casino.var.set('')
        self.entry_wigits.date.var.set('')
        self.entry_wigits.machine.var.set('')
        self.entry_wigits.cashin.var.set('0')
        self.entry_wigits.bet.var.set('0')
        self.entry_wigits.play_type.var.set('')
        self.entry_wigits.initial_state.clear()
        self.entry_wigits.cashout.var.set('0')
        self.entry_wigits.note.clear()
        self.entry_wigits.start_entry.var.set('')
        self.entry_wigits.end_entry.var.set('') 
        self.play_imgs.clear()
    
    def check_save_valid(self):
        casino = self.entry_wigits.casino.var.get()
        date = self.entry_wigits.date.var.get()
        machine = self.entry_wigits.machine.var.get()
        play_type = self.entry_wigits.play_type.var.get()
        
        if casino=='' or date=='' or machine=='' or play_type=='':
            self.image_buttons.save_button.configure(state='disabled')
        else:
            self.image_buttons.save_button.configure(state='normal')
        
    def save_externals(self):
        file_path = join(dirname(dirname(__file__)), 'external_entry_values.csv')
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows([self.casino_values, self.machine_values])
            
        
        



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
        
        self.table = ttk.Treeview(self, columns='imgs', show='headings')
        self.table.heading('imgs', text='Images')
        self.table.pack()
    
    def update_table(self, parent):
        self.table.delete(*self.table.get_children())
        for item in parent.play_imgs:
            self.table.insert(parent='', index=ttk.END, values=item)
        

class ImageButtons(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.columnconfigure((0, 1), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform='a')
        
        
        self.prev_button = ttk.Button(self, text='Prev', command=lambda: self.prev_button_command(parent))
        self.prev_button.grid(column=0, row=0, sticky='nsew', padx=(0, 3), pady=(0, 3))
        
        self.next_button = ttk.Button(self, text='Next', command=lambda: self.next_button_command(parent))
        self.next_button.grid(column=1, row=0, sticky='nsew', padx=(3, 0), pady=(0, 3))
        
        self.start_button = ttk.Button(self, text='Set Start', command=lambda: self.start_button_command(parent))
        self.start_button.grid(column=0, row=1, sticky='nsew', padx=(0, 3), pady=(3, 3))
        
        self.end_button = ttk.Button(self, text='Set End', command=lambda: self.end_button_command(parent))
        self.end_button.grid(column=1, row=1, sticky='nsew', padx=(3, 0), pady=(3, 3))
        
        self.add_button = ttk.Button(self, text='Add Image', command=lambda: self.add_button_command(parent))
        self.add_button.grid(column=0, row=2, sticky='nsew', padx=(0, 3), pady=(3, 3))
        
        self.remove_button = ttk.Button(self, text='Remove Image', command=lambda: self.remove_button_command(parent))
        self.remove_button.grid(column=1, row=2, sticky='nsew', padx=(3, 0), pady=(3, 3))
        
        self.save_button = ttk.Button(self, text='Save Play', command=lambda: parent.save(), bootstyle='success')
        self.save_button.grid(column=0, row=3, sticky='nsew', padx=(0, 3), pady=(3, 0))
        
        self.delete_button = ttk.Button(self, text='Delete Image', command=lambda: self.delete_button_command(parent), bootstyle='danger')
        self.delete_button.grid(column=1, row=3, sticky='nsew', padx=(3, 0), pady=(3, 0))
    
    
    
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
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        parent.entry_wigits.date.var.set(parent.imgs[parent.pointer]['image_time'][:8])
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.imgs[parent.pointer]['image_time'][:8]}')
        
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
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[parent.pointer]['path'] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item['image_time']))
        
        parent.entry_wigits.end_entry.var.set(parent.imgs[parent.pointer]['path'])
    
    def add_button_command(self, parent):
        if parent.entry_wigits.start_entry.var.get() == '':
            return
        
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer]['path']
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        
        parent.imgs[parent.pointer]['path'] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item['image_time']))
        
        parent.play_imgs.append(parent.imgs[parent.pointer]['path'])
        
        parent.entry_wigits.update_table(parent)
    
    def delete_button_command(self, parent):
        if len(parent.imgs) == 0:
            return
        
        path = parent.imgs[parent.pointer]['path']
        confirmation = Messagebox.show_question(f'Are you sure you want to delete this image:\n{path}',
                                                'Delete Confirmation',
                                                buttons=['No:secondary', 'Yes:warning'])
        
        if confirmation != 'Yes':
            return
        
        remove(path)
        parent.imgs.pop(parent.pointer)
        
        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)
    
    def remove_button_command(self, parent):
        if len(parent.imgs) == 0:
            return
        
        path = parent.imgs[parent.pointer]['path']
        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)
        
        
        
        


class ImageDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.canvas = ttk.Canvas(master=self, width=500, height=500)
        self.canvas.pack(fill='both')



App()
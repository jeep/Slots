import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox, Messagebox

from tkinter.filedialog import askdirectory

from Scripts.ComboboxLabel import ComboboxLabel
from Scripts.EntryLabel import EntryLabel
from Scripts.MoneyEntryLabel import MoneyEntryLabel
from Scripts.LabelLabel import LabelLabel
from Scripts.LargeEntryLabel import LargeEntryLabel
from Scripts.get_imgs_data import multi_get_img_stuff

from os import makedirs, remove
from os.path import join, dirname, basename, join

from shutil import move

from PIL import Image, ImageTk

import csv

from pillow_heif import register_heif_opener

register_heif_opener()




class App(ttk.Window):
    def __init__(self):
        self.imgs = []
        self.play_imgs = []
        self.play_type = ['AP', 'Gamble', 'Misplay', 'Non-play', 'Science', 'Tip', 'Tax Consequence']
        with open(f'casino_entry_values.csv', 'r') as csvfile:
            casino_values = list(csv.reader(csvfile))
            casino_values = [val for sublist in casino_values for val in sublist]

            self.casino_values = casino_values
        with open(f'machine_entry_values.csv', 'r') as csvfile:
            machine_values = list(csv.reader(csvfile))
            machine_values = [val for sublist in machine_values for val in sublist]
            
            self.machine_values = machine_values
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
        
        self.imgs = multi_get_img_stuff(directory)
        
        if len(self.imgs) == 0:
            return
        
        self.imgs = sorted(self.imgs, key=lambda item: item[2])
        self.display_image()
        print('Loaded')
        
    
    def add_casino(self):
        new_casino = Querybox.get_string(prompt='Enter a casino', title='Casino Entry')
        if new_casino is not None:
            self.casino_values.append(new_casino)
    
    def add_machine(self):
        new_machine = Querybox.get_string(prompt='Enter a machine', title='Machine Entry')
        if new_machine is not None:
            self.machine_values.append(new_machine)

    def display_image(self):
        with Image.open(self.imgs[self.pointer][0]) as image:
            if image.size[0] >= 450 or image.size[1] >= 450:
                if self.imgs[self.pointer][1] =='.HEIC' or self.imgs[self.pointer][1] == '.PNG':
                    image = image.reduce(10)
                else:
                    image = image.reduce(5)
            
            global imagetk
            imagetk = ImageTk.PhotoImage(image)
            
            x, y = image.size
            x, y = x/2, y/2
            
            self.image_display.canvas.delete('all')
            self.image_display.canvas.create_image(x, y, image=imagetk)
    
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
        with open(file_path, 'a+', newline='') as csvfile:
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
        
        self.image_buttons.save_button.configure(state='disabled')
    
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
        file_path = join(dirname(dirname(__file__)), 'casino_entry_values.csv')
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in self.casino_values:
                writer.writerow([item])
        file_path = join(dirname(dirname(__file__)), 'machine_entry_values.csv')
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for item in self.machine_values:
                writer.writerow(item)

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
        parent.pointer = min((parent.pointer+1), (len(parent.imgs)-1))
        parent.display_image()
    
    def prev_button_command(self, parent):
        parent.pointer = max((parent.pointer-1), 0)
        parent.display_image()
    
    def start_button_command(self, parent):
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer][0]
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        parent.entry_wigits.date.var.set(parent.imgs[parent.pointer][2][:8])
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.imgs[parent.pointer][2][:8]}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[parent.pointer][0] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item[2]))
        
        parent.entry_wigits.start_entry.var.set(parent.imgs[parent.pointer][0])
    
    def end_button_command(self, parent):
        if parent.entry_wigits.start_entry.var.get() == '':
            return
        
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer][0]
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        parent.imgs[parent.pointer][0] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item[2]))
        
        parent.entry_wigits.end_entry.var.set(parent.imgs[parent.pointer][0])
    
    def add_button_command(self, parent):
        if parent.entry_wigits.start_entry.var.get() == '':
            return
        
        if len(parent.imgs) == 0:
            return
        
        old_path = parent.imgs[parent.pointer][0]
        
        if 'Sorted' in old_path:
            return
        
        file_name = basename(old_path)
        
        new_path = join(dirname(dirname(old_path)), fr'Sorted\{parent.entry_wigits.date.var.get()}')
        
        try: makedirs(new_path)
        except FileExistsError: pass
        
        move(old_path, new_path)
        
        parent.imgs[parent.pointer][0] = join(new_path, file_name)
        parent.imgs = list(sorted(parent.imgs, key=lambda item: item[2]))
        
        parent.play_imgs.append(parent.imgs[parent.pointer][0])
        
        parent.entry_wigits.update_table(parent)
    
    def delete_button_command(self, parent):
        if len(parent.imgs) == 0:
            return
        
        path = parent.imgs[parent.pointer]['path']
        confirmation = Messagebox.show_question(f'Are you sure you want to delete this image:\n{path}',
                                                'Image Deletion Confirmation',
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
        
        path = parent.imgs[parent.pointer][0]
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
        self.canvas = ttk.Canvas(master=self, width=750, height=750)
        self.canvas.pack(fill='both')



if __name__ == '__main__':
    root = App()
    root.mainloop()
    root.save_externals()
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.dialogs import Querybox
from tkinter.filedialog import askopenfilenames

from PIL import Image, ImageTk

import csv
from os import walk, makedirs
from os.path import basename, exists, splitext
from shutil import move

global imgs, misc_entry_vars
imgs = []
misc_entry_vars = []

global start_var, end_var

global image_scale
image_scale = 20


class App(ttk.Window):
    def __init__(self):
        
        
        # main setup
        super().__init__()
        self.title('Slots')
        self.minsize(600, 450)
        self.iconphoto(False, ttk.PhotoImage(file=r'Programs\Icon\slot_machine_icon.png'))
        
        self.left_wigits = LeftScreenWigits(self)
        self.image_display = ImageDisplay(self)
        self.make_menu()
        
        # run
        self.mainloop()
    
    def make_menu(self):
        
        # menu setup
        menu = ttk.Menu(master=self)
        self.configure(menu=menu)
        
        # file menu
        file_menu = ttk.Menu(menu, tearoff=False)
        file_menu.add_command(label='Save', command=App.save)
        file_menu.add_command(label='Load', command=App.load)
        menu.add_cascade(label='File', menu=file_menu)

        # image menu
        image_menu = ttk.Menu(menu, tearoff=False)
        image_menu.add_command(label='Add Image', command=App.add_image)
        image_menu.add_separator()
        image_menu.add_command(label='Scale', command=App.set_image_scale)
        menu.add_cascade(label='Image', menu=image_menu)
    
    @staticmethod
    def save():
        global start_var, end_var, date_var, misc_entry_vars, imgs
        
        date = date_var.get()
        
        info = [date, *tuple(entry.get() for entry in misc_entry_vars), start_var.get(), end_var.get()]
        
        with open(fr'Data\{date}.csv', 'w+') as csvfile:
            data_writer = csv.writer(csvfile)
            data_writer.writerow(info)
        
        new_image_path = fr'Pics\Sorted\{date}'
        if not exists(new_image_path):
            makedirs(new_image_path)
        
        for img in imgs:
            move(fr'Pics\Unsorted\{img}', fr'Pics\Sorted\{date}')
    
    @staticmethod
    def load():
        global imgs, misc_entry_vars, start_var, end_var, date_var
        
        date = date_var.get()
        
        imgs = []
        imgs = next(walk(fr'Pics\Sorted\{date}'), (None, None, []))[2]

        with open(fr'Data\{date}.csv', 'r') as csvfile:
            data = list(csv.reader(csvfile))
            for index, item in enumerate(data[0][1:4]):
                misc_entry_vars[index].set(item)
            
            start_var.set(data[0][4])
            end_var.set(data[0][5])
        
        LeftScreenWigits.update_image_table()
    
    @staticmethod
    def add_image():
        global imgs
        
        paths = askopenfilenames()
        for path in paths:
            file_name = basename(path)
            if file_name not in imgs:
                imgs.append(file_name)
        
        LeftScreenWigits.update_image_table()
    
    @staticmethod
    def set_image_scale():
        global image_scale
        image_scale = Querybox.get_integer(prompt='', title='Set Scale', initialvalue=image_scale, minvalue=1)
        LeftScreenWigits.table_selection_event()


class LeftScreenWigits(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        
        self.date_entry = self.make_date_entry()
        self.misc_entries = self.make_misc_entries()
        ttk.Separator(self).pack(fill='x')
        self.start_entry = self.make_start_entry()
        self.end_entry = self.make_end_entry()
        ttk.Separator(self).pack(fill='x')
        self.image_table = self.make_image_table()
        
        self.place(x=0, y=0)
        
    def make_date_entry(self):
        date_frame = ttk.Frame(self)
        
        date_label = ttk.Label(date_frame, text='Date')
        date_label.pack(side='left', padx=5)
        
        global date_var
        date_var = ttk.StringVar()
        date_entry = DateEntry(date_frame, dateformat=r'%m%d%Y')
        date_entry.entry.configure(textvariable=date_var)
        date_entry.pack(side='left')
        
        date_frame.pack(pady=5)
    
    def make_misc_entries(self):
        global misc_entry_vars
        misc_entry_vars = []
        for x in range(1, 4):
            entry_field_frame = ttk.Frame(self)
            
            entry_field_label = ttk.Label(entry_field_frame, text=f'Entry {x}')
            entry_field_label.pack(side='left', padx=5)
            
            entry_field_var = ttk.StringVar()
            misc_entry_vars.append(entry_field_var)
            entry_field = ttk.Entry(entry_field_frame, textvariable=misc_entry_vars[x-1])
            entry_field.pack(side='left')
            
            entry_field_frame.pack(pady=5)
    
    def make_start_entry(self):
        global imgs
        
        start_frame = ttk.Frame(self)
        
        start_label = ttk.Label(start_frame, text='Start Image')
        start_label.pack(side='left', padx=5)
        
        global start_var, start_combobox
        start_var = ttk.StringVar()
        start_combobox = ttk.Combobox(start_frame, textvariable=start_var, postcommand=LeftScreenWigits.update_start_combobox)
        start_combobox['values'] = [splitext(img)[0] for img in imgs]
        start_combobox.pack(side='left')
        
        start_frame.pack(pady=5)
    
    @staticmethod
    def update_start_combobox():
        global imgs, start_combobox
        start_combobox['values'] = [splitext(img)[0] for img in imgs]
    
    def make_end_entry(self):
        global imgs
        end_frame = ttk.Frame(self)
        
        end_label = ttk.Label(end_frame, text='Start Image')
        end_label.pack(side='left', padx=5)
        
        global end_var, end_combobox
        end_var = ttk.StringVar()
        end_combobox = ttk.Combobox(end_frame, textvariable=end_var, postcommand=LeftScreenWigits.update_end_combobox, )
        end_combobox['values'] = [splitext(img)[0] for img in imgs]
        end_combobox.pack(side='left')
        
        end_frame.pack(pady=5)
    
    @staticmethod
    def update_end_combobox():
        global imgs, end_combobox
        end_combobox['values'] = [splitext(img)[0] for img in imgs]

    def make_image_table(self):
        global image_table
        image_table = ttk.Treeview(self, columns='imgs', show='headings')
        image_table.heading('imgs', text='Images')
        
        image_table.bind('<<TreeviewSelect>>', func=lambda event: LeftScreenWigits.table_selection_event())
        image_table.bind('<Delete>', func=LeftScreenWigits.table_delete_event)
        
        image_table.pack(pady=5)
    
    @staticmethod
    def update_image_table():
        global imgs
        for item in image_table.get_children():
            image_table.delete(item)
        
        for img in imgs:
            image_table.insert(parent='', index=ttk.END, values=[splitext(img)[0]])
    
    @staticmethod
    def table_delete_event():
        global imgs
        for img in image_table.selection():
            imgs.remove(fr'{image_table.item(img)['values'][0]}.jpeg')
        
        LeftScreenWigits.update_image_table()
    
    @staticmethod
    def table_selection_event():
        img_path = fr'{image_table.item(image_table.selection()[0])['values'][0]}.jpeg'
        try:
            img = Image.open(fr'Pics\Unsorted\{img_path}')
        except FileNotFoundError:
            try:
                img = Image.open(fr'Pics\Sorted\{date_var.get()}\{img_path}')
            except FileNotFoundError:
                return
        
        resized_img = img.reduce(image_scale)
        global tk_image
        tk_image = ImageTk.PhotoImage(resized_img)
        ImageDisplay.image_display_create_image(tk_image)


class ImageDisplay(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        global canvas
        canvas = ttk.Canvas(master=self, width=3000, height=3000)
        canvas.pack()
        self.place(y=0, x=250)
    
    @staticmethod
    def image_display_create_image(new_image):
        canvas.create_image(0, 0, image=new_image, anchor='nw')
        
    
        



App()
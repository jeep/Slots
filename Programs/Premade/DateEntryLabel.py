import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

class DateEntryLabel(ttk.Frame):
    def __init__(self,parent, label_text='', dateformat=r'%d-%m-%Y'):
        
        super().__init__(master=parent)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side='left')
        
        self.var = ttk.StringVar()
        self.date_entry = DateEntry(self, dateformat=dateformat)
        self.date_entry.entry.configure(textvariable=self.var)
        self.date_entry.pack(side='left')
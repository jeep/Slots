import ttkbootstrap as ttk

class EntryLabel(ttk.Frame):
    def __init__(self, parent, label_text=''):
        
        super().__init__(master=parent)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side='left', )
        
        self.var = ttk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.pack(side='right')
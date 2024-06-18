import ttkbootstrap as ttk

class EntryLabel(ttk.Frame):
    def __init__(self, parent, label_text='', entry_var=None, state='normal'):
        
        super().__init__(master=parent)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side='left', )
        
        if entry_var is None:
            self.var = ttk.StringVar()
        else:
            self.var = entry_var
            
        self.entry = ttk.Entry(self, textvariable=self.var, state=state)
            
        self.entry.pack(side='right')
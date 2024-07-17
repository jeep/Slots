import ttkbootstrap as ttk

class LabelLabel(ttk.Frame):
    def __init__(self, parent, label_text='', label_text_var='', label_var=None):
        if label_var is None:
            self.var= ttk.StringVar(value=label_text_var)
        else:
            self.var = label_var

        super().__init__(master=parent)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side='left', )
        
        self.entry = ttk.Label(self, textvariable=self.var)
        self.entry.pack(side='right')
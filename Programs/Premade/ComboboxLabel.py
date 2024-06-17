import ttkbootstrap as ttk

class ComboboxLabel(ttk.Frame):
    def __init__(self, parent, label_text='', combobox_values=(),  state='normal'):
        
        super().__init__(master=parent)
        self.label = ttk.Label(self,text=label_text)
        self.label.pack(side='left')
        
        self.var = ttk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.var, state=state)
        self.combobox.configure(postcommand=lambda: self.update_combobox(combobox_values))
        
        self.combobox['values'] = combobox_values
        self.combobox.pack(side='right')
    
    def update_combobox(self, new_values):
        self.combobox['values'] = new_values
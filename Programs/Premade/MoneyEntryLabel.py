import ttkbootstrap as ttk

class MoneyEntryLabel(ttk.Frame):
    def __init__(self, parent, label_text=''):
        
        super().__init__(master=parent)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side='left')
        
        self.var = ttk.DoubleVar(value=0)
        self.entry = ttk.Entry(self, textvariable=self.var, validate='key', validatecommand=(self.register(self.validate), '%P'))
        self.entry.pack(side='right')
    
    def validate(self, inp):
        try:
            if inp == '':
                return True

            float(inp)
            split_inp = inp.split('.')
            
            if len(split_inp) > 2:
                return False
            if len(split_inp) == 2 and len(split_inp[1]) > 2:
                return False
        except:
            return False
        return True
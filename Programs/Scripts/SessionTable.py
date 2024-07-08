import ttkbootstrap as ttk

class SessionTable(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(master=parent, columns='id', show='headings')
        self.heading('id', text="Play ID")
        
    def update_table(self, parent):
        self.delete(*self.get_children())
        for play in parent.plays:
            self.insert(parent='', index=ttk.END, values=play.identifier)


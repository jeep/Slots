import ttkbootstrap as ttk

class SessionTable(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(master=parent, columns='id', show='headings')
        self._parent = parent
        self.heading('id', text="Play ID")
        self.bind('<Delete>', self.delete_play)
        
    def update_table(self, parent):
        self.delete(*self.get_children())
        for play_id in parent.plays.keys():
            self.insert(parent='', index=ttk.END, values=play_id)

    def delete_play(self, _):
        for item in self.selection():
            value = self.item(item)['values'][0]
            del self._parent.plays[value]
            self.delete(item)


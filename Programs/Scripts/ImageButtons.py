import datetime

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from os import remove

from Scripts.HandPayWindow import HandPayWindow
from Scripts.StateEntryHelperWindow import StateEntryHelperWindow


class ImageButtons(ttk.Frame):
    """Frame for the buttons above the image"""
    def __init__(self, parent, window):
        super().__init__(master=parent)

        self.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')
        self._window = window

        self.file_name = ttk.StringVar(value="Name:")
        self.file_date = ttk.StringVar(value="Date:")
        self.picture_count = ttk.StringVar(value="End")

        self._create_buttons()
        self._place_buttons()


    def _create_buttons(self):
        self.prev_button = ttk.Button(self, text='Prev', command=self._window.display_prev_image)
        self.next_button = ttk.Button(self, text='Next', command=self._window.display_next_image)
        self.return_button = ttk.Button(self, text='Return to Start',
                                        command=self._window.display_first_image)

        self.goto_start = ttk.Label(self, text='1')
        self.goto_start.bind("<Button-1>", self._window.display_first_image)
        self.goto_prev = ttk.Label(self, text='prev')
        self.goto_prev.bind("<Button-1>", self._window.display_prev_image)
        self.goto_next = ttk.Label(self, text='next')
        self.goto_next.bind("<Button-1>", self._window.display_next_image)
        self.goto_end = ttk.Label(self, textvariable=self.picture_count)
        self.goto_end.bind("<Button-1>", self._window.display_last_image)

        self.state_button = ttk.Button(self, text="Open State Helper",
                                       command=lambda: self._open_state_helperwin(self._window))

        self.start_button = ttk.Button(self, text='Set Start',
                                       command=self._window.set_current_image_as_start)
        self.add_button = ttk.Button(self, text='Add Image',
                                     command=self._window.add_current_image_to_play)
        self.end_button = ttk.Button(self, text='Set End',
                                     command=self._window.set_current_image_as_end)
        self.hp_button = ttk.Button(self, text="Add HandPay",
                                    command=lambda: self._open_hpwin(
                                        lambda hpd: self._get_hpwin_data(self._window, hpd)))

        self.save_button = ttk.Button(self, text='Save Play', command=self._window.save, bootstyle='success')
        self.remove_button = ttk.Button(self, text='Remove Image',
                                        command=lambda: self.remove_button_command(self._window))
        self.delete_button = ttk.Button(self, text='Delete Image',
                                        command=lambda: self.delete_button_command(self._window), bootstyle='danger')

        self.save_session_button = ttk.Button(self, text='Save Session', command=self._window.save_session,
                                              bootstyle='success')

        self.file_name_label = ttk.Label(self, textvariable=self.file_name)
        self.file_date_label = ttk.Label(self, textvariable=self.file_date)

    def _place_buttons(self):
        pad_double = (4, 4)
        pad_front = (4, 0)
        pad_back = (0, 4)

        # row = 0
        # self.prev_button.grid(column=0, row=row, sticky='nsew', padx=pad_back, pady=pad_back)
        # self.next_button.grid(column=1, row=row, sticky='nsew', padx=pad_double, pady=pad_back)
        # self.return_button.grid(column=2, row=row, sticky='nsew', padx=pad_double, pady=pad_back)
        # self.state_button.grid(column=3, row=row, sticky='nsew', padx=pad_front, pady=pad_back)

        row = 0
        self.start_button.grid(column=0, row=row, sticky='nsew', padx=pad_back, pady=pad_double)
        self.add_button.grid(column=1, row=row, sticky='nsew', padx=pad_double, pady=pad_double)
        self.end_button.grid(column=2, row=row, sticky='nsew', padx=pad_front, pady=pad_double)

        row = 1
        self.state_button.grid(column=0, row=row, sticky='nsew', padx=pad_back, pady=pad_back)
        self.hp_button.grid(column=1, row=row, sticky='nsew', padx=pad_double, pady=pad_double)
        self.remove_button.grid(column=2, row=row, sticky='nsew', padx=pad_front, pady=pad_front)

        row = 2
        self.save_button.grid(column=0, row=row, sticky='nsew', padx=pad_back, pady=pad_front)
        self.save_session_button.grid(column=1, row=row, sticky='nsew', padx=pad_double, pady=pad_front)
        self.delete_button.grid(column=2, row=row, sticky='nsew', padx=pad_front, pady=pad_front)

        row = row+1
        self.file_name_label.grid(column=0, columnspan=2, row=row, sticky="nsew", padx=pad_back, pady=pad_front)
        self.file_date_label.grid(column=2, columnspan=2, row=row, sticky="nsew", padx=pad_front, pady=pad_front)

        row =  row+1
        self.goto_start.grid(column=0, row=row, sticky='nsew', padx=pad_double, pady=pad_back)
        self.goto_prev.grid(column=1, row=row, sticky='nsew', padx=pad_back, pady=pad_back)
        self.goto_next.grid(column=2, row=row, sticky='nsew', padx=pad_double, pady=pad_back)
        self.goto_end.grid(column=3, row=row, sticky='nsew', padx=pad_double, pady=pad_back)

    def _open_hpwin(self, callback):
        HandPayWindow(callback=callback)

    def _open_state_helperwin(self, _):
        """second param is 'parent'"""
        if self._window.get_current_play() is not None:
            StateEntryHelperWindow(play=self._window.get_current_play())
        else:
            print("No helper available")

    def _get_hpwin_data(self, parent, hp):
        parent.hand_pay.append(hp)
        parent.entry_wigits.update_hand_pay_table(parent)

    def set_image_navigation(self, state):
        """set the image navigation buttons appropriately"""
        self.prev_button.configure(state=state)
        self.next_button.configure(state=state)
        self.return_button.configure(state=state)

    def opposite_state(self, state):
        """return the opposite state from what is passed in."""
        if state == 'disabled':
            return 'normal'
        if state == 'normal':
            return 'disabled'
        return None

    def set_image_adders(self, state):
        """Set the state of the image add/remove buttons"""
        self.add_button.configure(state=state)
        self.start_button.configure(state=state)
        self.end_button.configure(state=state)
        self.remove_button.configure(state=self.opposite_state(state))

    def remove_button_command(self, parent):
        """Remove the image from the play"""
        if len(parent.imgs) == 0:
            return

        path = parent.imgs[parent.pointer][0]

        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
            #parent.entry_wigits.clear_play_start_datetime()
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
            #parent.entry_wigits.clear_play_end_datetime()
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)

        self.set_image_adders('normal')

    def delete_button_command(self, parent):
        """Delete the current image"""
        if len(parent.imgs) == 0:
            return

        path = parent.imgs[parent.pointer][0]

        confirmation = Messagebox.show_question(
            f'Are you sure you want to delete this image:\n{path}',
            'Image Deletion Confirmation', 
            buttons=['No:secondary', 'Yes:warning'])

        if confirmation != 'Yes':
            return

        remove(path)

        parent.imgs.pop(parent.pointer)
        parent.pointer = max((parent.pointer - 1), 0)
        parent.display_image()

        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
            parent.entry_wigits.date.var.set('')
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)

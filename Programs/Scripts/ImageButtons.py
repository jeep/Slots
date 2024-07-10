import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

from os import remove

from Scripts.HandPayWindow import HandPayWindow


class ImageButtons(ttk.Frame):
    def __init__(self, parent, window):
        # initializes the frame
        super().__init__(master=parent)
        # creates 3 columns that are the same width ( x )
        self.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        # creates 3 rows that are the same width ( y )
        self.rowconfigure((0, 1, 2), weight=1, uniform='a')
        # creates a 'private' window variable
        self._window = window
        
        # creates the buttons
        self._create_buttons()
        # places the buttons onto the frame
        self._place_buttons()
    
    def _create_buttons(self):
        # creates the first row of buttons
        self.prev_button    = ttk.Button(self, text='Prev', command=lambda: self.prev_button_command(self._window))
        self.next_button    = ttk.Button(self, text='Next', command=lambda: self.next_button_command(self._window))
        self.return_button  = ttk.Button(self, text='Return to Start', command=lambda: self.return_button_command(self._window))
        
        # creates the second row of buttons
        self.start_button   = ttk.Button(self, text='Set Start', command=lambda: self.start_button_command(self._window))
        self.add_button     = ttk.Button(self, text='Add Image', command=lambda: self.add_button_command(self._window))
        self.end_button     = ttk.Button(self, text='Set End', command=lambda: self.end_button_command(self._window))
        self.hp_button = ttk.Button(self, text="Add HandPay", command=lambda: self._open_hpwin(lambda hpd: self._get_hpwin_data(self._window, hpd)))
        
        # creates the third row of buttons
        self.save_button    = ttk.Button(self, text='Save Play', command=lambda: self._window.save(), bootstyle='success')
        self.remove_button  = ttk.Button(self, text='Remove Image', command=lambda: self.remove_button_command(self._window))
        self.delete_button  = ttk.Button(self, text='Delete Image', command=lambda: self.delete_button_command(self._window), bootstyle='danger')

        self.save_session_button    = ttk.Button(self, text='Save Session', command=lambda: self._window.save_session(), bootstyle='success')
    
    def _place_buttons(self):
        pad_double = (4, 4)
        pad_front = (4, 0)
        pad_back = (0, 4)
        
        # places the first row of buttons
        self.prev_button.grid(column=0, row=0, sticky='nsew', padx=pad_back, pady=pad_back)
        self.next_button.grid(column=1, row=0, sticky='nsew', padx=pad_double, pady=pad_back)
        self.return_button.grid(column=2, row=0, sticky='nsew', padx=pad_front, pady=pad_back)
        
        # places the second row of buttons
        self.start_button.grid(column=0, row=1, sticky='nsew', padx=pad_back, pady=pad_double)
        self.add_button.grid(column=1, row=1, sticky='nsew', padx=pad_double, pady=pad_double)
        self.end_button.grid(column=2, row=1, sticky='nsew', padx=pad_front, pady=pad_double)
        self.hp_button.grid(column=3, row=1, sticky='nsew', padx=(8, 0), pady=pad_double)
        
        # places the third row of buttons
        self.save_button.grid(column=0, row=2, sticky='nsew', padx=pad_back, pady=pad_front)
        self.remove_button.grid(column=1, row=2, sticky='nsew', padx=pad_double, pady=pad_front)
        self.delete_button.grid(column=2, row=2, sticky='nsew', padx=pad_double, pady=pad_front)
        self.save_session_button.grid(column=3, row=2, sticky='nsew', padx=pad_front, pady=pad_front)
    
    
    def _open_hpwin(self, callback):
        HandPayWindow(callback=callback)
    
    def _get_hpwin_data(self, parent, hp):
        parent.hand_pay.append(hp)
        parent.entry_wigits.update_hand_pay_table(parent)
        
        
    def prev_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # decrements the pointer by one
        # minimum of 0
        parent.pointer = max((parent.pointer-1), 0)
        # updates the image display
        parent.display_image()
        
        # gets the path of the current image
        current_image_path = parent.imgs[parent.pointer][0]
        
        # checks if the current image is in the current play
        if ((current_image_path in parent.play_imgs) or
            (current_image_path == parent.entry_wigits.start_entry.var.get()) or 
            (current_image_path == parent.entry_wigits.end_entry.var.get())):
            
            # disables the buttons to add the image to the play
            self.add_button.configure(state='disabled')
            self.start_button.configure(state='disabled')
            self.end_button.configure(state='disabled')
            # enables the button to remove the image from the play
            self.remove_button.configure(state='normal')
        else:
            # enables the buttons to add the image to the play
            self.add_button.configure(state='normal')
            self.start_button.configure(state='normal')
            self.end_button.configure(state='normal')
            # disables the button to remove the image from the play
            self.remove_button.configure(state='disabled')
    
    def next_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # increments the pointer by one
        # maximum of the length of images minus 1
        parent.pointer = min((parent.pointer+1), (len(parent.imgs)-1))
        # updates the image display
        parent.display_image()
        
        # gets the path of the current image
        current_image_path = parent.imgs[parent.pointer][0]
        
        # checks if the current image is in the current play
        if ((current_image_path in parent.play_imgs) or
            (current_image_path == parent.entry_wigits.start_entry.var.get()) or 
            (current_image_path == parent.entry_wigits.end_entry.var.get())):
            
            # disables the buttons to add the image to the play
            self.add_button.configure(state='disabled')
            self.start_button.configure(state='disabled')
            self.end_button.configure(state='disabled')
            # enables the button to remove the image from the play
            self.remove_button.configure(state='normal')
        else:
            # enables the buttons to add the image to the play
            self.add_button.configure(state='normal')
            self.start_button.configure(state='normal')
            self.end_button.configure(state='normal')
            # disables the button to remove the image from the play
            self.remove_button.configure(state='disabled')
    
    def return_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # sets the pointer to 0
        parent.pointer = 0
        # updates the image display
        parent.display_image()
        
        # gets the path of the current image
        current_image_path = parent.imgs[parent.pointer][0]
        
        # checks if the current image is in the current play
        if ((current_image_path in parent.play_imgs) or
            (current_image_path == parent.entry_wigits.start_entry.var.get()) or 
            (current_image_path == parent.entry_wigits.end_entry.var.get())):
            
            # disables the buttons to add the image to the play
            self.add_button.configure(state='disabled')
            self.start_button.configure(state='disabled')
            self.end_button.configure(state='disabled')
            # enables the button to remove the image from the play
            self.remove_button.configure(state='normal')
        else:
            # enables the buttons to add the image to the play
            self.add_button.configure(state='normal')
            self.start_button.configure(state='normal')
            self.end_button.configure(state='normal')
            # disables the button to remove the image from the play
            self.remove_button.configure(state='disabled')
    
    def start_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # sets the start entry wigit to the path of the current image
        parent.entry_wigits.start_entry.var.set(parent.imgs[parent.pointer][0])
        
        # sets the date wigit to the date ( year month day ) of the current image
        parent.entry_wigits.date.var.set(parent.imgs[parent.pointer][2])

        if not parent.session_date.get():
            parent.session_date.set(parent.imgs[parent.pointer][2][:8])
        
        # disables the buttons to add the image to the play
        self.add_button.configure(state='disabled')
        self.end_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        # enables the button to remove the image from the play
        self.remove_button.configure(state='normal')
    
    def add_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # adds the path to the play images list
        parent.play_imgs.append(parent.imgs[parent.pointer][0])
        
        # updates the table of images in the play images
        parent.entry_wigits.update_table(parent)
        
        # disables the button to add the image to the play
        self.add_button.configure(state='disabled')
        self.end_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        # enables the button to remove the image form the play
        self.remove_button.configure(state='normal')
    
    def end_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # sets the end entry wigit to the path of the current image
        parent.entry_wigits.end_entry.var.set(parent.imgs[parent.pointer][0])
        
        # disables the buttons to add the image to the play
        self.add_button.configure(state='disabled')
        self.end_button.configure(state='disabled')
        self.start_button.configure(state='disabled')
        # enables the button to remove the image from the play
        self.remove_button.configure(state='normal')
    
    def remove_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # gets the path of the current image
        path = parent.imgs[parent.pointer][0]
        
        # removes the image from the start entry, end entry, or play images
        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
            parent.entry_wigits.date.var.set('')
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)
    
    def delete_button_command(self, parent):
        # does nothing if there are no images
        if len(parent.imgs) == 0:
            return
        
        # gets the path of the current image
        path = parent.imgs[parent.pointer][0]
        
        # opens a message box to confirm that you want to delete the image
        confirmation = Messagebox.show_question(f'Are you sure you want to delete this image:\n{path}',
                                                'Image Deletion Confirmation',
                                                buttons=['No:secondary', 'Yes:warning'])
        
        # does nothing if the result of the message box was not 'Yes'
        if confirmation != 'Yes':
            return
        
        # deletes the path
        remove(path)
        
        
        
        # removes the image from the image list
        parent.imgs.pop(parent.pointer)
        parent.pointer = max((parent.pointer-1), 0)
        parent.display_image()
        
        # removes the image from the start entry, end entry or play images
        if parent.entry_wigits.start_entry.var.get() == path:
            parent.entry_wigits.start_entry.var.set('')
            parent.entry_wigits.date.var.set('')
        elif parent.entry_wigits.end_entry.var.get() == path:
            parent.entry_wigits.end_entry.var.set('')
        elif path in parent.play_imgs:
            parent.play_imgs.remove(path)
            parent.entry_wigits.update_table(parent)
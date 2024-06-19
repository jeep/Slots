# import what is needed and don't ask about threading yet that will be explained
# (pretty useless comment anyways)
from tkinter import Tk, Button, Label, DoubleVar
from tkinter.ttk import Progressbar
from multiprocessing import Process, Queue
from threading import Thread
from queue import Empty
from time import perf_counter, sleep


# create main window also inherit from `Tk` to make the whole thing a bit easier
# because it means that `self` is the actual `Tk` instance
class MainWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        # prepare the window, some labels are initiated but not put on the screen
        self.geometry('400x200')

        self.btn = Button(
            self, text='Calculate', command=self.start_calc
        )
        self.btn.pack()

        self.info_label = Label(self, text='Calculating...')

        # progressbar stuff
        self.progress_var = DoubleVar(master=self, value=0.0)
        self.progressbar = Progressbar(
            self, orient='horizontal', length=300, variable=self.progress_var
        )

        # create a queue for communication
        self.queue = Queue()

    # the method to launch the whole process and start the progressbar
    def start_calc(self):
        self.info_label.pack()
        self.progressbar.pack()
        Process(target=calculation, args=(self.queue, ), daemon=True).start()
        self.update_progress()

    # this function simply updates the `DoubleVar` instance
    # that is assigned to the Progressbar so basically makes
    # the progressbar move
    def update_progress(self):
        try:
            data = self.queue.get(block=False)
        except Empty:
            pass
        else:
            # if the process has finished stop this whole thing (using `return`)
            if data == 'done':
                self.info_label.config(text='Done')
                self.progress_var.set(100)
                return
            self.progress_var.set(data)
        finally:
            self.after(100, self.update_progress)


# interestingly this function couldn't be a method of the class
# because the class was inheriting from `Tk` (at least I think that is the reason)
# and as mentioned `tkinter` and multiprocessing doesn't go well together
def calculation(queue):
    # here is the threading this is important because the below
    # "calculation" is super quick while the above update loop runs only every
    # 100 ms which means that the Queue will be full and this process finished
    # before the progressbar will show that it is finished
    # so this function in a thread will only put stuff in the queue
    # every 300 ms giving time for the progressbar to update
    # if the calculation takes longer per iteration this part is not necessary
    def update_queue():
        while True:
            sleep(0.3)
            queue.put(i / range_ * 100)  # put in percentage as floating point where 100 is 100%
    # here starting the above function again if the calculations per iteration
    # take more time then it is fine to not use this
    Thread(target=update_queue).start()
    # starts the "calculation"
    start = perf_counter()
    range_ = 100_000_000
    for i in range(range_):
        pass
    finish = perf_counter()
    # put in the "sentinel" value to stop the update
    # and notify that the calculation has finished
    queue.put('done')
    # could actually put the below value in the queue to and
    # handle so that this is show on the `tkinter` window
    print((finish - start))


# very crucial when using multiprocessing always use the `if __name__ == "__main__":` to avoid
# recursion or sth because the new processes rerun this whole thing so it can end pretty badly
# there is sth like a fail safe but remember to use this anyways (a good practice in general)
if __name__ == '__main__':
    # as you can see then inheriting from `Tk` means that this can be done too
    root = MainWindow()
    root.mainloop()
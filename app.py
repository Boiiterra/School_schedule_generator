from tkinter import Label, Menu, Tk, Frame, Button, Toplevel
from platform import system

# Colors
fg = "#3f3f3f" # Foreground active
bg = "#cfcfcf" # Background color 
bg1 = "#bababa" # Background color 1
bg2 = "#c5c5c5" # Background color 2
b_f = ("Arial", 35)


class MainAppBody(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("School schedule generator")  # App's title
        # Icon file based on OS
        if system().lower() == "linux":
            self.iconbitmap("@icon.xbm")
        elif system().lower() == "windows":
            self.iconbitmap("icon.ico")
        self.geometry(f"800x570+{(self.winfo_screenwidth() - 800) // 2}+{(self.winfo_screenheight() - 570) // 2}")  # Middle of the screen
        self.resizable(0, 0) # App is now fixed size

        # Menu bar with help button
        menubar = Menu(self, tearoff=0, bd=0, bg=bg)
        menubar.add_command(label="Помощь...", command=lambda: Help(self), background=bg1, activebackground=bg2, activeforeground=fg)
        self.config(menu=menubar)

        # Place page into app
        container = Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # ALL PAGES MUST BR LISTED HERE!!! (Frame classes). All listed pages are going to be constructed
        frame_collection = (MainPage, GeneratorPage, DataEntryPage, DataCheckPage)

        for frame in frame_collection:
            current_frame = frame(container, self)
            self.frames[frame] = current_frame
            current_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    # This is used to show any page (page MUST be listed in frame_collection)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Gets methods of the given page and its variables with "self." in front of them, ex.: self.variable_name)
    def get_page(self, page_class):
        return self.frames[page_class]


class MainPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        info = Label(self, font=("Arial", 35), text="Генератор расписания уроков")
        info.pack(fill="x", pady=25)

        Label(self, height="4").pack()

        container = Frame(self)
        container.pack(expand=True, fill="both", padx=160)

        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)

        data_entry_btn = Button(container, font=("Arial", 35), command=lambda: controller.show_frame(DataEntryPage), bd=0, text="Внести данные.",
                                bg=bg2, activeforeground=fg, activebackground=bg)
        data_entry_btn.grid(row=0, column=0, ipady=5, sticky="nsew")

        data_check_btn = Button(container, font=("Arial", 35), command=lambda: controller.show_frame(DataCheckPage), bd=0, text="Проверить данные.",
                                bg=bg1, activeforeground=fg, activebackground=bg, disabledforeground=bg2)#, state="disabled")
        data_check_btn.grid(row=1, column=0, ipady=5, sticky="nsew")

        generator_btn = Button(container, font=("Arial", 35), command=lambda: controller.show_frame(GeneratorPage), bd=0, text="Создать расписание.",
                               bg=bg2, activeforeground=fg, activebackground=bg, disabledforeground=bg)#, state="disabled")
        generator_btn.grid(row=2, column=0, ipady=5, sticky="nsew")

        Label(self, height="7").pack(side="bottom")


class GeneratorPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        back_btn = Button(self, font=b_f, command=lambda: controller.show_frame(MainPage), bd=0, text="Назад",
                          bg=bg1, activeforeground=fg, activebackground=bg)
        back_btn.pack(side='bottom', fill='x', ipady=5)


class DataEntryPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        back_btn = Button(self, font=b_f, command=lambda: controller.show_frame(MainPage), bd=0, text="Назад",
                          bg=bg1, activeforeground=fg, activebackground=bg)
        back_btn.pack(side='bottom', fill='x', ipady=5)


class DataCheckPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        back_btn = Button(self, font=b_f, command=lambda: controller.show_frame(MainPage), bd=0, text="Назад",
                          bg=bg1, activeforeground=fg, activebackground=bg)
        back_btn.pack(side='bottom', fill='x', ipady=5)


class Help(Toplevel):
    
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Help manager")
        self.transient(parent)
        self.grab_set()
        self.minsize(500, 40)

        help_title = Label(self, font=("Arial", 20), text="Что нужно чтобы работал генератор:")
        help_title.pack(fill="x", ipadx=5, ipady=5)

        help_txt = "1. Нажать кнопку 'Внести данные.'\n" \
                   "?. Нажать кнопку 'Создать рассписание'\n" \
                   "?. Ждать уведомления"

        help_info = Label(self, font=("Arial", 20), text=help_txt)
        help_info.pack(fill="both", expand=True, pady=15)

        ok_btn = Button(self, font=("Arial", 20), command=self.destroy, text="OK", bg=bg1,
                          activeforeground=fg, activebackground=bg)
        ok_btn.pack(side='bottom', ipady=5)


if __name__ == "__main__":
    MainAppBody().mainloop()

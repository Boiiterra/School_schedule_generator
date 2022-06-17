from tkinter import Canvas, Label, Menu, PhotoImage, Scrollbar, Tk, Frame, Button, Toplevel
from webbrowser import open_new_tab
from PIL import Image, ImageTk
from platform import system

# Colors
fg = "#3f3f3f" # Foreground active
bg = "#cfcfcf" # Background color 
bg1 = "#bababa" # Background color 1
bg2 = "#c5c5c5" # Background color 2
b_f = ("Arial", 35)
s_f = ("TkDefaultFont", 12) # Small font (for about section)
width = 800
height = 570

class MainAppBody(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("School schedule generator")  # App's title
        # Icon file based on OS
        if system().lower() == "linux":
            self.iconbitmap("@icon.xbm")
        elif system().lower() == "windows":
            self.iconbitmap("icon.ico")
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width) // 2}+{(self.winfo_screenheight() - height) // 2}")  # Middle of the screen
        self.resizable(0, 0)
        # self.minsize(800, 570)  # App's minimal size
        # self.maxsize(self.winfo_screenwidth(), self.winfo_screenheight() - 31) # App's maximum size -> screen size

        # Menu bar with help button
        menubar = Menu(self, tearoff=0, bd=0, bg=bg)
        self.menubar = menubar
        menubar.add_command(label="Помощь", command=lambda: Help(self), background=bg1, activebackground=bg2, activeforeground=fg)
        menubar.add_command(label="", activebackground=menubar.cget("background"))
        menubar.add_command(label="О приложении", command=lambda: About(self), background=bg1, activebackground=bg2, activeforeground=fg)
        self.config(menu=menubar)

        # Place page into app
        container = Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # ALL PAGES MUST BR LISTED HERE!!! (Frame classes). All listed pages are going to be constructed
        frame_collection = (MainPage, )

        for frame in frame_collection:
            current_frame = frame(container, self)
            self.frames[frame] = current_frame
            current_frame.grid(row=0, column=0, sticky="nsew")

        # Show main page whenever the app is opened, can add if/else statements to choose which page should be first 
        self.show_frame(MainPage)

    # This is used to show any page (page MUST be listed in frame_collection)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Gets methods of the given page and its variables with "self." in front of them, ex.: self.variable_name)
    def get_page(self, page_class):
        return self.frames[page_class]


class AutoScrollbar(Scrollbar):
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side="right", fill="y")
        Scrollbar.set(self, low, high)


class Links(Label):
    def __init__(self, parent, text: str, profile_url: str, **kw):
        Label.__init__(self, parent, text=text, font=s_f, fg=fg, **kw)

        self.bind("<Leave>", lambda _: self.config(font=s_f, cursor="", fg=fg))
        self.bind("<Enter>", lambda _: self.config(font=s_f + ("underline",), cursor="hand2", fg="blue"))
        self.bind("<Button-1>", lambda _: open_new_tab(profile_url))


class Year(Frame):
    def __init__(self, parent, year, letter):
        Frame.__init__(self, parent, width=60, height=50)

        def remove():
            self.destroy()
            app = parent.master.master.master.master.master
            app.geometry(f"{app.winfo_width()}x{app.winfo_height() + 1}")
            self.after( 1, lambda: app.geometry(f"{app.winfo_width()}x{app.winfo_height() - 1}"))

        Label(self, text=f"{year}{letter}", width="8", pady=18).grid(row=0, column=0)

        minus = ImageTk.PhotoImage(Image.open('remove.png').resize((25, 25)))
        remove_btn = Button(self, image=minus, width=70, height=25, bd=0, bg=bg2, activebackground=bg, command=remove)
        remove_btn.image = minus
        remove_btn.grid(row=1, column=0, sticky="nw")

    def grid(self, **kwargs):
        self.grid_configure(kwargs, padx=5, pady=5, sticky="nw")


class MainPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        top = Frame(self, bg="blue")
        top.pack(side="top", expand=True, fill="both")

        bottom = Frame(self, height=50, bg=fg)
        bottom.pack(side="bottom", fill="both")

        canvas = Canvas(top)
        # canvas.grid(row=0, column=0, sticky="nsew")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = AutoScrollbar(top, orient="vertical", command=canvas.yview, width=20)
# top, orient="vertical", command=canvas.yview, width=20, bg="#898989", bd=1, troughcolor="#a9a9a9", elementborderwidth=2, activebackground="#696969", highlightthickness=0
        self.scrollbar = scrollbar
        # scrollbar.grid(row=0, column=1, sticky="ns")
        # scrollbar.pack(side="right", fill="y")

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        for i in range(30):
            test = Year(ui, i, "A")
            test.grid(row=(i // 9), column=((i % 9)))

        # test = Year(ui, 11, "A")
        # test.grid(row=0, column=1)

        minus = ImageTk.PhotoImage(Image.open('remove.png').resize((25, 20)))
        label = Button(ui, image=minus, width=60, height=20, bd=0, command=lambda: print(ui.grid_slaves()))
        label.image = minus
        label.grid(row=5, column=0, sticky="nw")


class Help(Toplevel):
    
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Help manager")
        self.transient(parent)
        self.geometry("500x85")
        self.grab_set()
        # self.minsize(500, 40)

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


class About(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)

        self.transient(parent)
        self.grab_set()
        self.geometry(f'{313}x{250}+{int((self.winfo_screenwidth() - 313) / 2)}+{int((self.winfo_screenheight() - 250) / 2)}')
        self.resizable(0, 0)
        self.title('About')

        title = Label(self, text="О приложении:", font=("TkDefaultFont", 15), pady=5)
        title.pack()

        Button(self, text='OK', font=15, command=self.destroy, width=7).pack(side="bottom", pady=10)

        # Links:
        Label(self, text="Авторы:", font=s_f+("bold",)).pack(fill="x")
        container = Frame(self)
        container.pack()
        Links(container, "TerraBoii", "https://github.com/TerraBoii").grid(row=0, column=0, padx=15)
        Links(container, "EvgenHi", "https://github.com/EvgenHi").grid(row=0, column=1, padx=15)

        Frame(self, height=4, bg=bg1).pack(fill="x", padx=20) # Separator

        # License
        l_container = Frame(self)
        l_container.pack(anchor="w", padx=25)
        Label(l_container, text="Приложение распространяется", font=s_f).grid(row=0, column=0, columnspan=2)
        Label(l_container, text="под лицензией:", font=s_f).grid(row=1, column=0)
        Links(l_container, "MIT license", "https://ru.wikipedia.org/wiki/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F_MIT", anchor="w").grid(row=1, column=1, padx=8)
        Label(l_container, text="© 2022 TerraBoii, EvgenHi", font=s_f).grid(row=2, column=0, columnspan=2)


if __name__ == "__main__":
    MainAppBody().mainloop()
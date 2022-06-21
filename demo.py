from tkinter import Canvas, Entry, Label, Menu, Scrollbar, Tk, Frame, Button, Toplevel
from tkinter.messagebox import showinfo
from webbrowser import open_new_tab
from PIL import Image, ImageTk
from platform import system

# Colors
fg = "#3f3f3f" # Foreground active
bg = "#cfcfcf" # Background color 
bg1 = "#bababa" # Background color 1
bg2 = "#c5c5c5" # Background color 2
b_f = ("Arial", 35) # Big font
s_f = ("TkDefaultFont", 12) # Small font
width = 1050
height = 620
w_b = 0 # mount of CardDelWarn instancies
card_id = 0 # Card's index (is used for positioning them on screen)
cards = [] # Empty list for cards
# Cards example: [("db_id", "Year", "<class_instance>"), ...]


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


class CardDelWarn(Toplevel):
    """Card deletion warning"""
    def __init__(self, parent, card):
        Toplevel.__init__(self, parent)
        self.card = card
        global w_b
        w_b += 1
        # Limits amount of CardDelWarn instancies
        if w_b > 1:
            self.destroy()
        else:
            self.transient(parent)
            self.wait_visibility() # Fixes softlock, which happens when grab_set fails
            self.grab_set()
            self.title('Warning - class deletion')
            self.geometry(f"367x102+{(self.winfo_screenwidth() - 367) // 2}+{(self.winfo_screenheight() - 102) // 2}")
            self.resizable(0, 0)
            self.protocol('WM_DELETE_WINDOW', self.self_delete)

            mes_cont = Frame(self)
            mes_cont.pack(side="top", expand=True, fill="x", anchor="w")
            mes_cont.rowconfigure(0, weight=1)
            mes_cont.columnconfigure(0, weight=1)
            mes_cont.columnconfigure(1, weight=1)

            photo = ImageTk.PhotoImage(Image.open('warning.png'))
            label = Label(mes_cont, image=photo)
            label.image = photo
            label.grid(row=0, column=0, padx=6)
            text = f"Все данные о '{card.full_year}' будут удалены\nбезвозвратно! Вы уверены?"
            Label(mes_cont, text=text, font=("Times New Roman", 12, "bold")).grid(row=0, column=1, sticky="w")

            but_cont = Frame(self)
            but_cont.pack(side="bottom", pady=7)
            but_cont.rowconfigure(0, weight=1)
            but_cont.columnconfigure(0, weight=1)
            but_cont.columnconfigure(1, weight=1)

            def run(do=False):
                global w_b
                w_b = 0
                if do:
                    found = False
                    # Find and delete element from list "cards"
                    for pos, info in enumerate(cards):
                        if card in info:
                            found = True
                            cards.remove(info)
                        if found and 0 <= pos < len(cards):
                            cards[pos][0] = cards[pos][0] - 1
                            cards[pos][-1].grid_forget()
                            cards[pos][-1].grid(row=(pos // 12), column=((pos % 12)), padx=15, pady=15)

                    card.destroy()
                    parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() + 1}")
                    self.after( 1, lambda: parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() - 1}"))
                    self.destroy()
                else:
                    self.destroy()
                    card.remove_btn.config(state="normal")

            Button(but_cont, text='Да', command=lambda: run(True), width=7).grid(row=0, column=0, padx=10)
            Button(but_cont, text="Нет", command=run, width=7).grid(row=0, column=1, padx=10)

    def self_delete(self):
        global w_b
        w_b = 0
        self.destroy()
        self.card.remove_btn.config(state="normal")


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
        global cards, card_id
        Frame.__init__(self, parent, width=70, height=50, bg=bg)
        full_year = f"{year}{letter}"
        self.full_year = full_year
        data = [card_id, self.full_year, self]
        card_id += 1
        cards.append(data)
        cards[-2], cards[-1] = cards[-1], cards[-2]
        cards[-1][0] += 1

        def remove():
            remove_btn.config(state="disabled")
            CardDelWarn(parent.master.master.master.master.master, self)

        label = Label(self, text=full_year, width="8", pady=12, cursor="hand2")
        label.grid(row=0, column=0, pady=3)

        minus = ImageTk.PhotoImage(Image.open('remove.png').resize((25, 25)))
        remove_btn = Button(self, image=minus, width=70, height=25, bd=0, bg=bg2, activebackground=bg, command=remove, cursor="hand2")
        remove_btn.image = minus
        remove_btn.grid(row=1, column=0, sticky="nw")
        self.remove_btn = remove_btn

    def grid(self, **kwargs):
        if "padx" in kwargs:
            del(kwargs["padx"])
        if "pady" in kwargs:
            del(kwargs["pady"])
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

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        plus = ImageTk.PhotoImage(Image.open('add.png').resize((50, 50)))
        add_card = Button(ui, image=plus, width=50, height=50, bg=bg2, bd=0, activebackground=bg, cursor="hand2",
                          command=lambda: AddYear(parent.master, add_card, [ui, add_card.grid_info()["row"], add_card.grid_info()["column"]]))
        add_card.image = plus
        cards.append([0, None, add_card])
        add_card.grid(row=0, column=0, padx=15, pady=15)


class AddYear(Toplevel):
    def __init__(self, parent, add_card, location: list):
        Toplevel.__init__(self, parent, bg="#898989")
        view = Frame(self)
        view.pack(pady=10, padx=10, fill="both", expand=True)
        self.title("Add class")
        self.geometry(f"220x150+{(self.winfo_screenwidth() - 220) // 2}+{(self.winfo_screenheight() - 150) // 2}")
        self.resizable(0, 0)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        def cancel():
            self.destroy()

        def add():
            _number = number.get()
            _letter = letter.get().upper()
            if _number != "" and _letter != "":
                number.delete(0, "end")
                letter.delete(0, "end")
                # Find and delete element from list "cards"
                for info in cards:
                    if f"{_number}{_letter}" in info:
                        showinfo("Class exists", f"Класс {_number}{_letter} уже существует попробуйте другой")
                        break
                else:
                    add_card.grid_forget()
                    Year(location[0], _number, _letter).grid(row=location[1], column=location[2])
                    if location[2] == 11:
                        add_card.grid(row=location[1]+1, column=0)
                    else:
                        add_card.grid(row=location[1], column=location[2]+1)
                    cancel()
            else:
                if _number == "" and _letter == "":
                    message = "номер и букву класса. Пример: 3 В"
                elif _number == "":
                    message = f"номер класса. Пример: 3 {_letter}"
                else:
                    message = f"букву класса. Пример: {_number} В"
                showinfo("Data is missing", f"Вы забыли ввести {message}")

        header = Label(view, text="Добавить класс:", font=s_f)
        header.pack()

        class_cont = Frame(view)
        class_cont.pack(pady=10)

        is_valid_i = (parent.register(self.validate_int), '%d', '%i', '%P') # action, index, value
        is_valid_c = (parent.register(self.validate_char), '%d', '%P') # action, value
        Label(class_cont, text="Класс:", font=s_f).grid(row=0, column=0)
        number = Entry(class_cont, width=2, validatecommand=is_valid_i, validate="key", font=s_f)
        number.grid(row=0, column=1) # Number
        letter = Entry(class_cont, width=2, validatecommand=is_valid_c, validate="key", font=s_f)
        letter.grid(row=0, column=2) # Letter

        btn_cont = Frame(view)
        btn_cont.pack(side="bottom", pady=5)

        cancel_btn = Button(btn_cont, text="Отмена", command=cancel)
        cancel_btn.grid(row=0, column=0, padx=10, pady=5)
        add_btn = Button(btn_cont, text="Добавить", command=add)
        add_btn.grid(row=0, column=1, padx=10, pady=5)
        self.add_btn = add_btn

    def validate_int(self, action, index, value):
        """Enter only integer values"""
        if value != "":
            # Integers does not start from zero
            if index == "0" and value == "0":
                return False
        # Entry validation
        if len(value) > 2 and action == "1":  # Limiting input length
            return False
        elif all(symbol in "0123456789" for symbol in value):  # Allowed values
            return True
        else:
            return False

    def validate_char(self, action, value):
        """Enter only integer values"""
        # Entry validation
        if len(value) > 1 and action == "1":  # Limiting input length
            return False
        elif all(symbol.lower() in "абвгдежзийклмнопрстуфхцчшщъыьэюяё" for symbol in value):  # Allowed values
            return True
        else:
            return False


class Help(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Help manager")
        self.transient(parent)
        self.geometry("500x400")
        self.wait_visibility()
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
        self.wait_visibility()
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
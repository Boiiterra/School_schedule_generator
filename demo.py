from tkinter import Canvas, Entry, Label, Menu, Scrollbar, Tk, Frame, Button, Toplevel
from tkinter.messagebox import showinfo
from webbrowser import open_new_tab
from PIL import Image, ImageTk
from platform import system
from sqlite3 import connect, OperationalError

# Colors
fg = "#3f3f3f" # Foreground active
bg = "#cfcfcf" # Background color 
bg1 = "#bababa" # Background color 1
bg2 = "#c5c5c5" # Background color 2
b_f = ("Arial", 35) # Big font
m_f = ("Arial", 20) # Medium font
s_f = ("Arial", 15) # Small font
ss_f = ("TkDefaultFont", 12) # Super small font
width = 1050
height = 620
c_card_id = 0 # Card's index (is used for positioning them on screen)
c_cards = [] # Empty list for class cards
# ? Cards example: [["db_id", "Year", "<class_instance>"], ...]
s_card_id = 0 # Card's index (is used for positioning them on screen)
s_cards = [] # Empty list for subject cards
# ? Cards example: [["db_id", "Year", "<class_instance>"], ...]
lessons = [] # Empty list for lessons
# Lessons example: [[id, hours, "class", "Lesson", "teacher", object]]
classes = {}


# TODO: Figure out the data
def create_db(table: str, args: tuple[str]):

    try:

        connection = connect("data.db")

        cursor = connection.cursor()

        cursor.execute(f"CREATE TABLE {table} {args}")

        connection.commit()

        connection.close()

    except OperationalError as e:
        print(all(["table", "exists" in str(e)]))


def create_class():
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


class MainAppBody(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("School schedule generator")  # App's title
        # Icon file based on OS
        if system().lower() == "linux":
            self.iconbitmap("@images/icon.xbm")
        elif system().lower() == "images/windows":
            self.iconbitmap("icon.ico")
        self.geometry(f"{width}x{height}+{(self.winfo_screenwidth() - width) // 2}+{(self.winfo_screenheight() - height) // 2}")  # Middle of the screen
        self.resizable(0, 0)

        # Menu bar with help button
        menubar = Menu(self, tearoff=0, bd=0, bg=bg)
        self.menubar = menubar
        # File submenu
        menubar.add_command(label="File", background=bg1, activebackground=bg2, activeforeground=fg)
        menubar.add_command(label="\u22EE", activebackground=menubar.cget("background"))
        # Help submenu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Помощь", command=lambda: Help(self))
        help_menu.add_separator()
        help_menu.add_command(label="О приложении", command=lambda: About(self))
        menubar.add_cascade(label="Помощь...", menu=help_menu, background=bg1, activebackground=bg2, activeforeground=fg)
        menubar.add_command(label="\u22EE", activebackground=menubar.cget("background"))
        menubar.add_command(label="Текущее положение ->", activebackground=menubar.cget("background"))
        self.config(menu=menubar)

        main_page = MainPage(self)
        self.main_page = main_page
        self.show_frame(main_page)

        self.binding_0 = self.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
        self.binding_1 = self.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
        self.binding_2 = self.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)

    def show_frame(self, new, prev=None, extra=None, launch=True):
        """Used to show any page and user's location"""
        if prev is not None:
            prev.pack_forget()
        if extra is not None and not "MainPage".lower() in str(new).lower():
            if "MainPage".lower() in str(prev).lower():
                self.unbind("<MouseWheel>", self.binding_0)
                self.unbind("<Button-4>", self.binding_1)
                self.unbind("<Button-5>", self.binding_2)
            new(self, extra).pack(fill="both", expand=True)
        else:
            if prev is not None:
                self.binding_0 = self.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
                self.binding_1 = self.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
                self.binding_2 = self.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)
            self.main_page.pack(fill="both", expand=True)

        if "MainPage".lower() in str(new).lower() and launch:
            self.menubar.add_command(label="Главная страница", activebackground=self.menubar.cget("background"))
        elif "LessonSchedule".lower() in str(new).lower() and "MainPage".lower() in str(prev).lower():
            self.menubar.delete(self.menubar.index("Главная страница"))
            self.menubar.add_command(label=f"Станица класса {extra}", activebackground=self.menubar.cget("background"))
        elif "MainPage".lower() in str(new).lower():
            self.menubar.delete(self.menubar.index(f"Станица класса {extra}"))
            self.menubar.add_command(label="Главная страница", activebackground=self.menubar.cget("background"))
        elif "LessonHours".lower() in str(new).lower():
            self.menubar.delete(self.menubar.index(f"Станица класса {extra}"))
            self.menubar.add_command(label=f"{new.user_position} {extra}", activebackground=self.menubar.cget("background"))
        elif "LessonSchedule".lower() in str(new).lower() and "LessonHours".lower() in str(prev).lower():
            self.menubar.delete(self.menubar.index(f"{prev.user_position} {extra}"))
            self.menubar.add_command(label=f"Станица класса {extra}", activebackground=self.menubar.cget("background"))

    def get_page(self, page_class):
        """Gets methods of the given page and its variables with "self." in front of them, ex.: self.variable_name)"""
        return self.frames[page_class]

    def mouse_wheel(self, event):
        """ Mouse wheel as scroll bar"""
        direction = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        if "AutoScrollbar" in str(self.main_page.top.pack_slaves()):
            self.main_page.canvas.yview_scroll(direction, "units")


class CCardDelWarn(Toplevel):
    """Class card deletion warning"""
    def __init__(self, parent, card):
        Toplevel.__init__(self, parent)
        self.card = card
        self.transient(parent)
        self.wait_visibility() # * Fixes softlock, which happens when grab_set fails
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

        photo = ImageTk.PhotoImage(Image.open('images/warning.png'))
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
            if do:
                found = False
                # Find and delete element from list "c_cards"
                for pos, info in enumerate(c_cards):
                    if card in info:
                        found = True
                        c_cards.remove(info)
                    if found and 0 <= pos < len(c_cards):
                        c_cards[pos][0] = c_cards[pos][0] - 1
                        c_cards[pos][-1].grid_forget()
                        c_cards[pos][-1].grid(row=(pos // 12), column=((pos % 12)), padx=15, pady=15)

                card.destroy()
                parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() + 1}")
                self.after(1, lambda: parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() - 1}"))
                self.destroy()
            else:
                self.self_delete()

        Button(but_cont, text='ДА', command=lambda: run(True), width=7).grid(row=0, column=0, padx=10)
        Button(but_cont, text="НЕТ", command=run, width=7).grid(row=0, column=1, padx=10)

    def self_delete(self):
        self.destroy()
        self.card.remove_btn.config(state="normal")


class SCardDelWarn(Toplevel):
    """Subject card deletion warning"""
    def __init__(self, parent, card):
        Toplevel.__init__(self, parent)
        self.card = card
        self.transient(parent)
        self.wait_visibility() # * Fixes softlock, which happens when grab_set fails
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

        photo = ImageTk.PhotoImage(Image.open('images/warning.png'))
        label = Label(mes_cont, image=photo)
        label.image = photo
        label.grid(row=0, column=0, padx=6)
        text = f"Вы уверены, что хотите удалить\nпредмет  '{card.name}'?"
        Label(mes_cont, text=text, font=("Times New Roman", 12, "bold")).grid(row=0, column=1, sticky="w")

        but_cont = Frame(self)
        but_cont.pack(side="bottom", pady=7)
        but_cont.rowconfigure(0, weight=1)
        but_cont.columnconfigure(0, weight=1)
        but_cont.columnconfigure(1, weight=1)

        def run(do=False):
            if do:
                found = False
                # Find and delete element from list "s_cards"
                for pos, info in enumerate(s_cards):
                    if card in info:
                        found = True
                        s_cards.remove(info)
                    if found and 0 <= pos < len(s_cards):
                        s_cards[pos][0] = s_cards[pos][0] - 1
                        s_cards[pos][-1].grid_forget()
                        s_cards[pos][-1].grid(row=(pos // 3), column=((pos % 3)), padx=15, pady=15)

                card.destroy()
                parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() + 1}")
                self.after(1, lambda: parent.geometry(f"{parent.winfo_width()}x{parent.winfo_height() - 1}"))
                self.destroy()
            else:
                self.destroy()

        Button(but_cont, text='Добавить', command=lambda: run(True), width=7).grid(row=0, column=0, padx=10)
        Button(but_cont, text="Отмена", command=run, width=7).grid(row=0, column=1, padx=10)

    def self_delete(self):
        self.destroy()


class AutoScrollbar(Scrollbar):
    def set(self, low, high):
        if float(low) <= 0.0 and float(high) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side="right", fill="y")
        Scrollbar.set(self, low, high)


class Links(Label):
    def __init__(self, parent, text: str, profile_url: str, **kw):
        Button.__init__(self, parent, text=text, font=ss_f, fg=fg, bd=0, activebackground="#d9d9d9", activeforeground="blue", command=lambda: open_new_tab(profile_url), **kw)

        self.bind("<Leave>", lambda _: self.config(font=ss_f, cursor=""))
        self.bind("<Enter>", lambda _: self.config(font=ss_f + ("underline",), cursor="hand2"))


class Year(Frame):
    def __init__(self, parent, year, letter):
        global c_cards, c_card_id
        Frame.__init__(self, parent, width=70, height=50, bg=bg)
        full_year = f"{year}{letter}"
        self.full_year = full_year
        data = [c_card_id, self.full_year, self]
        c_card_id += 1
        c_cards.append(data)
        c_cards[-2], c_cards[-1] = c_cards[-1], c_cards[-2]
        c_cards[-1][0] += 1
        c_cards[-1][-1].grid(row=c_cards[-1][0] // 12, column=c_cards[-1][0] % 12, padx=15, pady=15)

        def remove():
            remove_btn.config(state="disabled")
            CCardDelWarn(parent.master.master.master.master, self)

        year_info = Button(self, text=full_year, width=5, pady=12, bd=0, cursor="hand2", activebackground="#dfdfdf",
                           command=lambda: parent.master.master.master.master.show_frame(LessonSchedule, parent.master.master.master, self.full_year))
        year_info.grid(row=0, column=0, pady=3)

        minus = ImageTk.PhotoImage(Image.open('images/remove.png').resize((25, 25)))
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


class Subject(Frame):
    def __init__(self, parent, name, teacher, year):
        global s_cards, s_card_id
        Frame.__init__(self, parent, bg=bg)
        data = [s_card_id, 1, year, name, teacher, parent.master.master.master.year, self]
        # * [[id, hours, "class", "Lesson", "teacher", object]]
        s_card_id += 1
        s_cards.append(data)
        s_cards[-2], s_cards[-1] = s_cards[-1], s_cards[-2]
        s_cards[-1][0] += 1
        s_cards[-1][-1].grid(row=s_cards[-1][0] // 3, column=s_cards[-1][0] % 3, padx=15, pady=15)
        self.name = name

        def increase():
            if (int(amount.cget("text")) + 1) <= 99:
                amount.config(text=(int(amount.cget("text")) + 1))
            else:
                showinfo("Limit -- hours", "Вы достигли максимального доступного значения.")

        def decrease():
            if int(amount.cget("text")) - 1 != 0:
                amount.config(text=(int(amount.cget("text")) - 1))
            else:
                SCardDelWarn(parent.master.master.master.master, self)

        element_1 = Frame(self, bg=bg)
        element_1.grid(row=0, column=0, padx=4, pady=4)
        if len(name) < 11:
            Label(element_1, text=name, font=s_f, bg=bg).grid(row=0, column=0)
        else:
            Label(element_1, text=name, font=("Arial", 8), bg=bg).grid(row=0, column=0)
        if len(teacher) < 11:
            Label(element_1, text=f"({teacher})", font=s_f, bg=bg).grid(row=1, column=0)
        else:
            Label(element_1, text=f"({teacher})", font=("Arial", 8), bg=bg).grid(row=1, column=0)

        element_2 = Frame(self, padx=20, bg=bg)
        element_2.grid(row=0, column=1, pady=4)

        minus = ImageTk.PhotoImage(Image.open('images/remove.png').resize((25, 25)))
        decrease_hours = Button(element_2, image=minus, bg=bg1, bd=0, activebackground=bg, cursor="hand2", font=s_f,
                               command=decrease)
        decrease_hours.image = minus
        decrease_hours.grid(row=0, column=0, sticky="nsew")

        amount = Label(element_2, text=1, font=s_f, justify="center", bg=bg, width=2)
        amount.grid(row=0, column=1, sticky="nsew", padx=3)

        plus = ImageTk.PhotoImage(Image.open('images/add.png').resize((25, 25)))
        increase_hours = Button(element_2, image=plus, bg=bg1, bd=0, activebackground=bg, cursor="hand2", font=s_f,
                            command=increase)
        increase_hours.image = plus
        increase_hours.grid(row=0, column=2, sticky="nsew")

    def grid(self, **kwargs):
        if "padx" in kwargs:
            del(kwargs["padx"])
        if "pady" in kwargs:
            del(kwargs["pady"])
        self.grid_configure(kwargs, padx=5, pady=15, sticky="nw")


class MainPage(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        top = Frame(self)
        top.pack(side="top", expand=True, fill="both")
        self.top = top

        bottom = Frame(self, height=50, bg="#d2d2d2")
        bottom.pack(side="bottom", fill="both")

        def _import(): ...

        def _export(): ...

        def _generate(): ...

        import_btn = Button(bottom, bd=0, text="Импорт", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                            command=_import)
        import_btn.pack(side="left", padx=35, pady=5)

        export_btn = Button(bottom, bd=0, text="Экспорт", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                            command=_export)
        export_btn.pack(side="left", pady=5)

        generate_schedule = Button(bottom, bd=0, text="Создать расписание", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=_generate)
        generate_schedule.pack(side="right", pady=5, padx=35)

        canvas = Canvas(top)
        canvas.pack(side="left", fill="both", expand=True)
        self.canvas = canvas

        scrollbar = AutoScrollbar(top, orient="vertical", command=canvas.yview, width=20)

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        plus = ImageTk.PhotoImage(Image.open('images/add.png').resize((50, 50)))
        add_card = Button(ui, image=plus, width=50, height=50, bg=bg2, bd=0, activebackground=bg, cursor="hand2",
                          command=lambda: AddYear(parent, [ui, add_card.grid_info()["row"], add_card.grid_info()["column"]]))
        add_card.image = plus
        c_cards.append([0, None, add_card])
        add_card.grid(row=0, column=0, padx=15, pady=15)

        for i in range(230):
            Year(ui, i, "А").grid(row=(i // 12), column=((i % 12)))

        self.parent.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
        self.parent.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
        self.parent.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)

    def mouse_wheel(self, event):
        """ Mouse wheel as scroll bar """
        direction = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        if "AutoScrollbar" in str(self.top.pack_slaves()):
            self.canvas.yview_scroll(direction, "units")


class AddYear(Toplevel):
    def __init__(self, parent, location: list):
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
                # Find and delete element from list "c_cards"
                for info in c_cards:
                    if f"{_number}{_letter}" in info:
                        showinfo("Class exists", f"Класс {_number}{_letter} уже существует попробуйте другой")
                        break
                else:
                    Year(location[0], _number, _letter).grid(row=location[1], column=location[2])
                    cancel()
            else:
                if _number == "" and _letter == "":
                    message = "номер и букву класса. Пример: 3 В"
                elif _number == "":
                    message = f"номер класса. Пример: 3 {_letter}"
                else:
                    message = f"букву класса. Пример: {_number} В"
                showinfo("Data is missing", f"Вы забыли ввести {message}")

        header = Label(view, text="Добавить класс:", font=ss_f)
        header.pack()

        class_cont = Frame(view)
        class_cont.pack(pady=10)

        is_valid_i = (parent.register(self.validate_int), '%d', '%i', '%P') # action, index, value
        is_valid_c = (parent.register(self.validate_char), '%d', '%P') # action, value
        Label(class_cont, text="Класс:", font=ss_f).grid(row=0, column=0)
        number = Entry(class_cont, width=2, validatecommand=is_valid_i, validate="key", font=ss_f)
        number.grid(row=0, column=1) # Number
        letter = Entry(class_cont, width=2, validatecommand=is_valid_c, validate="key", font=ss_f)
        letter.grid(row=0, column=2) # Letter

        btn_cont = Frame(view)
        btn_cont.pack(side="bottom", pady=5)

        cancel_btn = Button(btn_cont, text="Отмена", command=cancel)
        cancel_btn.grid(row=0, column=0, padx=10, pady=5)
        add_btn = Button(btn_cont, text="Добавить", command=add)
        add_btn.grid(row=0, column=1, padx=10, pady=5)
        self.add_btn = add_btn

    def validate_int(self, action, index, value):
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
        # Entry validation
        if len(value) > 1 and action == "1":  # Limiting input length
            return False
        elif all(symbol.lower() in "абвгдежзийклмнопрстуфхцчшщъыьэюяё" for symbol in value):  # Allowed values
            return True
        else:
            return False


class AddSubject(Toplevel):
    def __init__(self, parent, location: list):
        Toplevel.__init__(self, parent, bg="#898989")
        view = Frame(self)
        view.pack(pady=10, padx=10, fill="both", expand=True)
        self.title("Add subject")
        self.geometry(f"500x500+{(self.winfo_screenwidth() - 500) // 2}+{(self.winfo_screenheight() - 500) // 2}")
        self.resizable(0, 0)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        def cancel():
            self.destroy()

        def add():
            _subject = subject.get()
            _teacher = teacher.get()
            if _subject != "" and _teacher != "":
                subject.delete(0, "end")
                teacher.delete(0, "end")
                # Find and delete element from list "c_cards"
                for info in c_cards:
                    if f"{_subject}{_teacher}" in info:
                        showinfo("Class exists", f"Класс {_subject}{_teacher} уже существует попробуйте другой")
                        break
                else:
                    Subject(location[0], _subject, _teacher, location[0].master.master.master.year).grid(row=location[1], column=location[2])
                    cancel()
            else:
                if _subject == "" and _teacher == "":
                    message = "предмет и его учителя. Попробуйте:\nМатематика\nИ.И.Иванов"
                elif _subject == "":
                    message = f"учителя. Попробуйте:\nМатематика\n{_teacher}"
                else:
                    message = f"предмет. Попробуйте: {_subject} И.И.Иванов"
                showinfo("Data is missing", f"Вы забыли ввести {message}")

        header = Label(view, text="Добавить предмет:", font=ss_f)
        header.pack()

        subject_cont = Frame(view)
        subject_cont.pack(pady=10)

        is_valid_c = (parent.register(self.validate_char), '%d', '%P') # action, index, value
        Label(subject_cont, text="Предмет:", font=ss_f).grid(row=0, column=0)
        subject = Entry(subject_cont, width=21, validatecommand=is_valid_c, validate="key", font=ss_f)
        subject.grid(row=0, column=1) # Letter
        Label(subject_cont, text="Учитель:", font=ss_f).grid(row=1, column=0)
        teacher = Entry(subject_cont, width=21, validatecommand=is_valid_c, validate="key", font=ss_f)
        teacher.grid(row=1, column=1)

        btn_cont = Frame(view)
        btn_cont.pack(side="bottom", pady=5)

        cancel_btn = Button(btn_cont, text="Отмена", command=cancel)
        cancel_btn.grid(row=0, column=0, padx=10, pady=5)
        add_btn = Button(btn_cont, text="Добавить", command=add)
        add_btn.grid(row=0, column=1, padx=10, pady=5)
        self.add_btn = add_btn

    def validate_char(self, action, value):
        # Entry validation
        if len(value) > 20 and action == "1":  # Limiting input length
            return False
        elif all(symbol.lower() in "абвгдежзийклмнопрстуфхцчшщъыьэюяё .," for symbol in value):  # Allowed values
            return True
        else:
            return False


class AddLesson(Toplevel):
    def __init__(self, parent, location):
        Toplevel.__init__(self, parent)
        view = Frame(self)
        view.pack(pady=10, padx=10, fill="both", expand=True)
        self.title("Add lesson")
        self.geometry(f"500x500+{(self.winfo_screenwidth() - 500) // 2}+{(self.winfo_screenheight() - 500) // 2}")
        self.resizable(0, 0)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        def cancel():
            self.destroy()

        def add():
            _number = number.get()
            _lesson = lesson.get().upper()
            if _number != "" and _lesson != "":
                number.delete(0, "end")
                lesson.delete(0, "end")
            else:
                showinfo("Data is missing", f"Вы забыли ввести {location}")

        header = Label(view, text="Добавить урок:", font=ss_f)
        header.pack()

        class_cont = Frame(view)
        class_cont.pack(pady=10)

        is_valid_i = (parent.register(self.validate_int), '%d', '%i', '%P') # action, index, value
        is_valid_c = (parent.register(self.validate_char), '%d', '%P') # action, value
        Label(class_cont, text="Информация об уроке:", font=ss_f).grid(row=0, column=0)
        number = Entry(class_cont, width=2, validatecommand=is_valid_i, validate="key", font=ss_f)
        number.grid(row=0, column=1) # Number
        lesson = Entry(class_cont, width=26, validatecommand=is_valid_c, validate="key", font=ss_f)
        lesson.grid(row=0, column=2) # Lesson

        btn_cont = Frame(view)
        btn_cont.pack(side="bottom", pady=5)

        cancel_btn = Button(btn_cont, text="Отмена", command=cancel)
        cancel_btn.grid(row=0, column=0, padx=10, pady=5)
        add_btn = Button(btn_cont, text="Добавить", command=add)
        add_btn.grid(row=0, column=1, padx=10, pady=5)
        self.add_btn = add_btn

    def validate_int(self, action, index, value):
        if value != "":
            # Integers does not start from zero
            if index == "0" and value == "0":
                return False
        # Entry validation
        if len(value) > 1 and action == "1":  # Limiting input length
            return False
        elif all(symbol in "0123456789" for symbol in value):  # Allowed values
            return True
        else:
            return False

    def validate_char(self, action, value):
        # Entry validation
        if len(value) > 25 and action == "1":  # Limiting input length
            return False
        elif all(symbol.lower() in "абвгдежзийклмнопрстуфхцчшщъыьэюяё .," for symbol in value):  # Allowed values
            return True
        else:
            return False


class RemoveLesson(Toplevel):
    def __init__(self, parent, location):
        Toplevel.__init__(self, parent, bg="#898989")
        view = Frame(self)
        view.pack(pady=10, padx=10, fill="both", expand=True)
        self.title("Remove lesson")
        self.geometry(f"260x195+{(self.winfo_screenwidth() - 260) // 2}+{(self.winfo_screenheight() - 195) // 2}")
        self.resizable(0, 0)
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        def cancel():
            self.destroy()

        def confirm():
            _number = number.get()
            if _number != "" and location.grid_slaves(row=int(_number), column=1)[0].cget("text") != "":
                number.delete(0, "end")
                location.grid_slaves(row=int(_number), column=1)[0].configure(text="")
                cancel()
            elif _number != "" and location.grid_slaves(row=int(_number), column=1)[0].cget("text") == "":
                showinfo("Info -- Lesson does not exist", f"Урок номер {_number} не существует, попробуйте другой номер урока.")
            else:
                showinfo("Info -- Data is missing", f"Вы забыли ввести номер урока")

        container = Frame(view)
        container.pack(pady=10)

        is_valid_i = (parent.register(self.validate_int), '%d', '%P') # action, value
        Label(container, text="Удалить урок номер:", font=ss_f).grid(row=0, column=0)
        number = Entry(container, width=3, validatecommand=is_valid_i, validate="key", font=ss_f, justify="center")
        number.grid(row=0, column=1) # Number

        # Lesson to delete
        lesson = Label(view, text="", font=ss_f, justify="center", height=3)
        lesson.pack(fill="x")

        btn_cont = Frame(view)
        btn_cont.pack(side="bottom", pady=5)

        cancel_btn = Button(btn_cont, text="Отмена", command=cancel)
        cancel_btn.grid(row=0, column=0, padx=10, pady=5)
        confirm_btn = Button(btn_cont, text="Подтвердитть", command=confirm, state="disabled")
        confirm_btn.grid(row=0, column=1, padx=10, pady=5)

        self.confirm_btn = confirm_btn
        self.location = location
        self.lesson = lesson

    def validate_int(self, action, value):
        if len(value) >= 1 and all(symbol in "123456789" for symbol in value):
            self.confirm_btn.config(state="normal")
            self.lesson.config(text=f"Будет удалён урок номер {value[0]}:\n" \
                                    f"{self.location.grid_slaves(row=int(value[0]))[0].cget('text')},\n" \
                                    f"в день: {self.location.grid_slaves(row=0)[0].cget('text')}")
        elif len(value) < 1 and all(symbol in "123456789" for symbol in value):
            self.confirm_btn.config(state="disabled")
            self.lesson.config(text="")
        if len(value) > 1 and action == "1":  # Limiting input length
            return False
        elif all(symbol in "123456789" for symbol in value):  # Allowed values
            return True
        else:
            return False


class ScheduleTable(Frame):
    def __init__(self, parent, day):
        Frame.__init__(self, parent)

        # Day of the week
        Label(self, text=day, font=s_f, bg="#b9b9b9").grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Setup table of 9 lessons
        for number in range(9):
            if number % 2 != 0:
                _bg1 = "#b9b9b9"
                _bg2 = "#c5c5c5"
            else:
                _bg1 = "#c5c5c5"
                _bg2 = "#d9d9d9"
            Label(self, text=number+1, width=1, font=s_f, bg=_bg1).grid(column=0, row=number+1, sticky="nsew", ipadx=2, ipady=2)
            Label(self, font=s_f, width=26, bg=_bg2, text=f"test{number+1}").grid(column=1, row=number+1, sticky="nsew", padx=2, pady=2)

        def add():
            if lessons:
                AddLesson(parent, self)
            elif int(parent.master.master.master.year[:-1]) < 10:
                    showinfo("Info -- no lessons available", "Отсутствуют предметы. Создайте их в меню 'Обязательные часы'")
            elif int(parent.master.master.master.year[:-1]) >= 10:
                    showinfo("Info -- no lessons available", "Отсутствуют предметы. Создайте их в меню 'Индивидуальные часы'")

        def remove():
            counter = 0
            for pos in range(9):
                if self.grid_slaves(row=pos+1, column=1)[0].cget("text"):
                    RemoveLesson(parent, self)
                    break
                else:
                    counter += 1
                    if counter == 9:
                        showinfo("Info -- no lessons available", f"Отсутствуют уроки в день недели: '{self.grid_slaves(row=0, column=0)[0].cget('text')}'. " \
                                 "Добавте урок нажав 'Добавить урок'.")

        # Buttons:
        plus = ImageTk.PhotoImage(Image.open('images/add.png').resize((25, 25)))
        add_lesson = Button(self, image=plus, bg=bg2, bd=0, activebackground=bg, cursor="hand2", compound="left", text="Добавить урок", font=s_f,
                            command=add)
        add_lesson.image = plus
        add_lesson.grid(row=10, column=0, columnspan=2, pady=2, sticky="nsew")

        minus = ImageTk.PhotoImage(Image.open('images/remove.png').resize((25, 25)))
        remove_lesson = Button(self, image=minus, bg=bg2, bd=0, activebackground=bg, cursor="hand2", compound="left", text="Удалить урок", font=s_f,
                               command=remove)
        remove_lesson.image = minus
        remove_lesson.grid(row=11, column=0, columnspan=2, pady=2, sticky="nsew")

    def grid(self, **kwargs):
        self.grid_configure(kwargs, pady=15, padx=14)


class LessonSchedule(Frame):
    def __init__(self, parent, year):
        Frame.__init__(self, parent)
        self.parent = parent
        self.year = year

        top = Frame(self)
        top.pack(side="top", expand=True, fill="both")
        self.top = top

        bottom = Frame(self, height=50, bg="#d2d2d2")
        bottom.pack(side="bottom", fill="both")

        canvas = Canvas(top)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = AutoScrollbar(top, orient="vertical", command=canvas.yview, width=20)

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        self.canvas = canvas

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        for pos, day in enumerate(days):
            ScheduleTable(ui, day).grid(row=pos // 3, column=pos % 3)

        def cancel():
            parent.show_frame(parent.main_page, self, extra=year, launch=False)

        if int(year[:-1]) >= 10:
            hours = Button(bottom, bd=0, text="Индивидуальные часы", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                           command=lambda: parent.show_frame(LessonHoursI, self, year))
            hours.pack(side="left", padx=40)
        else:
            hours = Button(bottom, bd=0, text="Обязательные часы", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                           command=lambda: parent.show_frame(LessonHoursA, self, year))
            hours.pack(side="left", padx=40)

        save_btn = Button(bottom, bd=0, text="Сохранить", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        save_btn.pack(side="right", pady=5, padx=40)

        cancel_btn = Button(bottom, bd=0, text="Отмена", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        cancel_btn.pack(side="right", pady=5)

        self.parent.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
        self.parent.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
        self.parent.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)

    def mouse_wheel(self, event):
        """ Mouse wheel as scroll bar """
        direction = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        if "AutoScrollbar" in str(self.top.pack_slaves()):
            self.canvas.yview_scroll(direction, "units")


class LessonHoursA(Frame):
    user_position = "Обязательные часы"

    def __init__(self, parent, year):
        Frame.__init__(self, parent)
        self.parent = parent
        self.year = year

        top = Frame(self)
        top.pack(side="top", expand=True, fill="both")
        self.top = top

        bottom = Frame(self, height=50, bg=fg)
        bottom.pack(side="bottom", fill="both")

        canvas = Canvas(top)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = AutoScrollbar(top, orient="vertical", command=canvas.yview, width=20)

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        self.canvas = canvas

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        plus = ImageTk.PhotoImage(Image.open('images/add.png').resize((25, 25)))
        add_card = Button(ui, image=plus, height=50, bg=bg2, bd=0, activebackground=bg, cursor="hand2", compound="left",
                          command=lambda: AddSubject(parent, [ui, add_card.grid_info()["row"], add_card.grid_info()["column"]]),
                          text="Добавить предмет", font=s_f)
        add_card.image = plus
        s_cards.append([0, None, add_card])
        add_card.grid(row=0, column=0, padx=15, pady=15)

        def cancel():
            parent.show_frame(LessonSchedule, self, extra=year)

        save_btn = Button(bottom, bd=0, text="Сохранить", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        save_btn.pack(side="right", pady=5, padx=40)

        cancel_btn = Button(bottom, bd=0, text="Отмена", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        cancel_btn.pack(side="right", pady=5)

        self.parent.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
        self.parent.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
        self.parent.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)

    def mouse_wheel(self, event):
        """ Mouse wheel as scroll bar """
        direction = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        if "AutoScrollbar" in str(self.top.pack_slaves()):
            self.canvas.yview_scroll(direction, "units")


class LessonHoursI(Frame):
    user_position = "Индивидуальные часы"

    def __init__(self, parent, year):
        Frame.__init__(self, parent)
        self.parent = parent
        self.year = year

        top = Frame(self)
        top.pack(side="top", expand=True, fill="both")
        self.top = top

        bottom = Frame(self, height=50, bg=fg)
        bottom.pack(side="bottom", fill="both")

        canvas = Canvas(top)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = AutoScrollbar(top, orient="vertical", command=canvas.yview, width=20)

        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _: canvas.config(scrollregion=canvas.bbox("all")))
        self.canvas = canvas

        ui = Frame(canvas) # User Interface
        canvas.create_window((0, 0), window=ui, anchor="nw")

        plus = ImageTk.PhotoImage(Image.open('images/add.png').resize((25, 25)))
        add_card = Button(ui, image=plus, height=50, bg=bg2, bd=0, activebackground=bg, cursor="hand2", compound="left",
                          command=lambda: AddSubject(parent, [ui, add_card.grid_info()["row"], add_card.grid_info()["column"]]),
                          text="Добавить предмет", font=s_f)
        add_card.image = plus
        add_card.grid(row=0, column=0, padx=15, pady=15)
        if not s_cards:
            s_cards.append([0, None, add_card])
        else:
            print("exists")

        def cancel():
            parent.show_frame(LessonSchedule, self, extra=year)

        save_btn = Button(bottom, bd=0, text="Сохранить", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        save_btn.pack(side="right", pady=5, padx=40)

        cancel_btn = Button(bottom, bd=0, text="Отмена", bg=bg1, activebackground=bg, activeforeground=fg, font=m_f,
                                   command=cancel)
        cancel_btn.pack(side="right", pady=5)

        self.parent.bind("<MouseWheel>", self.mouse_wheel) # Windows mouse wheel event
        self.parent.bind("<Button-4>", self.mouse_wheel) # Linux mouse wheel event (Up)
        self.parent.bind("<Button-5>", self.mouse_wheel) # Linux mouse wheel event (Down)

    def mouse_wheel(self, event):
        """ Mouse wheel as scroll bar """
        direction = 0
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1
        if "AutoScrollbar" in str(self.top.pack_slaves()):
            self.canvas.yview_scroll(direction, "units")


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
        self.geometry(f'{313}x{254}+{int((self.winfo_screenwidth() - 313) / 2)}+{int((self.winfo_screenheight() - 254) / 2)}')
        self.resizable(0, 0)
        self.title('About')

        title = Label(self, text="О приложении:", font=("TkDefaultFont", 15), pady=5)
        title.pack()

        Button(self, text='OK', font=15, command=self.destroy, width=7).pack(side="bottom", pady=10)

        # Links:
        Label(self, text="Авторы:", font=ss_f+("bold",)).pack(fill="x")
        container = Frame(self)
        container.pack()
        Links(container, "TerraBoii", "https://github.com/TerraBoii").grid(row=0, column=0, padx=10)
        Links(container, "EvgenHi", "https://github.com/EvgenHi").grid(row=0, column=1, padx=10)

        Frame(self, height=4, bg=bg1).pack(fill="x", padx=20) # Separator

        # License
        l_container = Frame(self)
        l_container.pack(anchor="w", padx=25)
        Label(l_container, text="Приложение распространяется", font=ss_f).grid(row=0, column=0, columnspan=2)
        Label(l_container, text="под лицензией:", font=ss_f).grid(row=1, column=0)
        Links(l_container, "MIT license", "https://ru.wikipedia.org/wiki/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F_MIT", anchor="w").grid(row=1, column=1, padx=8)
        Label(l_container, text="© 2022 TerraBoii, EvgenHi", font=ss_f).grid(row=2, column=0, columnspan=2)


if __name__ == "__main__":
    MainAppBody().mainloop()
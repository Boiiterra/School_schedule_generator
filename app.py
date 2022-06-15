from tkinter import Tk, Frame, Button


class MainAppBody(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("School schedule generator")  # App's title
        # self.iconbitmap("icon.ico")  # icon file
        self.geometry(f"800x600+{(self.winfo_screenwidth() - 800) // 2}+{(self.winfo_screenheight() - 600) // 2}")  # Middle of the screen
        self.minsize(800, 600)  # App's minimal size
        self.maxsize(self.winfo_screenwidth(), self.winfo_screenheight()) # App's maximum size -> screen size

        # Place page into app
        container = Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # ALL PAGES MUST BR LISTED HERE!!! (Frame classes). All listed pages are going to be constructed
        frame_collection = (WelcomePage, MainPage)

        for frame in frame_collection:
            current_frame = frame(container, self)
            self.frames[frame] = current_frame
            current_frame.grid(row=0, column=0, sticky="nsew")

        # Show main page whenever the app is opened, can add if/else statements to choose which page should be first 
        self.show_frame(WelcomePage)

    # This is used to show any page (page MUST be listed in frame_collection)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Gets methods of the given page and its variables with "self." in front of them, ex.: self.variable_name)
    def get_page(self, page_class):
        return self.frames[page_class]


class WelcomePage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.switch_pages = Button(self, text="To MainPage", font=("Arial", 45), command=lambda: controller.show_frame(MainPage))
        self.switch_pages.pack(fill='both', pady=2, expand=True)



class MainPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)


if __name__ == "__main__":
    MainAppBody().mainloop()

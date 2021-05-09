import tkinter
import sys


# Thanks to TomSchimansky:
# https://github.com/TomSchimansky/GuitarTuner/blob/master/documentation/tkinter_custom_button.py


class TkinterCustomButton(tkinter.Frame):
    """ tkinter custom button with border, rounded corners and hover effect
        Arguments:  master= where to place button
                    bg_color= background color, None is standard,
                    fg_color= foreground color, blue is standard,
                    hover_color= foreground color, lightblue is standard,
                    border_color= foreground color, None is standard,
                    border_width= border thickness, 0 is standard,
                    command= callback function, None is standard,
                    width= width of button, 110 is standard,
                    height= width of button, 35 is standard,
                    corner_radius= corner radius, 10 is standard,
                    text_font= (<Name>, <Size>),
                    text_color= test color, white is tandard,
                    text= text of button,
                    hover= hover effect, True is standard """

    def __init__(self,
                 bg_color=None,
                 fg_color="#2874A6",
                 hover_color="#5499C7",
                 border_color=None,
                 border_width=0,
                 command=None,
                 width=120,
                 height=40,
                 corner_radius=10,
                 text_font=None,
                 text_color="white",
                 text="CustomButton",
                 hover=True,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = command
        if bg_color is None:
            self.bg_color = self.master.cget("bg")
        else:
            self.bg_color = bg_color

        self.fg_color = fg_color
        self.hover_color = hover_color
        self.border_color = border_color

        self.width = width
        self.height = height

        if corner_radius * 2 > self.height:
            self.corner_radius = self.height / 2
        elif corner_radius * 2 > self.width:
            self.corner_radius = self.width / 2
        else:
            self.corner_radius = corner_radius

        self.border_width = border_width

        if self.corner_radius >= self.border_width:
            self.inner_corner_radius = self.corner_radius - self.border_width
        else:
            self.inner_corner_radius = 0

        self.text = text
        self.text_color = text_color
        if text_font is None:
            if sys.platform == "darwin":  # macOS
                self.text_font = ("Avenir", 13)
            elif "win" in sys.platform:  # Windows
                self.text_font = ("Century Gothic", 11)
            else:
                self.text_font = ("TkDefaultFont")
        else:
            self.text_font = text_font

        self.function = command
        self.hover = hover

        self.configure(width=self.width, height=self.height)

        if sys.platform == "darwin" and self.function is not None:
            self.configure(cursor="pointinghand")

        self.canvas = tkinter.Canvas(master=self,
                                     highlightthicknes=0,
                                     background=self.bg_color,
                                     width=self.width,
                                     height=self.height)
        self.canvas.place(x=0, y=0)

        if self.hover is True:
            self.canvas.bind("<Enter>", self.on_enter)
            self.canvas.bind("<Leave>", self.on_leave)

        self.canvas.bind("<Button-1>", self.clicked)
        self.canvas.bind("<Button-1>", self.clicked)

        self.canvas_fg_parts = []
        self.canvas_border_parts = []
        self.text_part = None

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.canvas_fg_parts = []
        self.canvas_border_parts = []
        self.canvas.configure(bg=self.bg_color)

        # border button parts
        if self.border_width > 0:

            if self.corner_radius > 0:
                self.canvas_border_parts.append(self.canvas.create_oval(0,
                                                                        0,
                                                                        self.corner_radius * 2,
                                                                        self.corner_radius * 2))
                self.canvas_border_parts.append(self.canvas.create_oval(self.width - self.corner_radius * 2,
                                                                        0,
                                                                        self.width,
                                                                        self.corner_radius * 2))
                self.canvas_border_parts.append(self.canvas.create_oval(0,
                                                                        self.height - self.corner_radius * 2,
                                                                        self.corner_radius * 2,
                                                                        self.height))
                self.canvas_border_parts.append(self.canvas.create_oval(self.width - self.corner_radius * 2,
                                                                        self.height - self.corner_radius * 2,
                                                                        self.width,
                                                                        self.height))

            self.canvas_border_parts.append(self.canvas.create_rectangle(0,
                                                                         self.corner_radius,
                                                                         self.width,
                                                                         self.height - self.corner_radius))
            self.canvas_border_parts.append(self.canvas.create_rectangle(self.corner_radius,
                                                                         0,
                                                                         self.width - self.corner_radius,
                                                                         self.height))

        # inner button parts

        if self.corner_radius > 0:
            self.canvas_fg_parts.append(self.canvas.create_oval(self.border_width,
                                                                self.border_width,
                                                                self.border_width + self.inner_corner_radius * 2,
                                                                self.border_width + self.inner_corner_radius * 2))
            self.canvas_fg_parts.append(self.canvas.create_oval(self.width - self.border_width - self.inner_corner_radius * 2,
                                                                self.border_width,
                                                                self.width - self.border_width,
                                                                self.border_width + self.inner_corner_radius * 2))
            self.canvas_fg_parts.append(self.canvas.create_oval(self.border_width,
                                                                self.height - self.border_width - self.inner_corner_radius * 2,
                                                                self.border_width + self.inner_corner_radius * 2,
                                                                self.height - self.border_width))
            self.canvas_fg_parts.append(self.canvas.create_oval(self.width - self.border_width - self.inner_corner_radius * 2,
                                                                self.height - self.border_width - self.inner_corner_radius * 2,
                                                                self.width - self.border_width,
                                                                self.height - self.border_width))

        self.canvas_fg_parts.append(self.canvas.create_rectangle(self.border_width + self.inner_corner_radius,
                                                                 self.border_width,
                                                                 self.width - self.border_width - self.inner_corner_radius,
                                                                 self.height - self.border_width))
        self.canvas_fg_parts.append(self.canvas.create_rectangle(self.border_width,
                                                                 self.border_width + self.inner_corner_radius,
                                                                 self.width - self.border_width,
                                                                 self.height - self.inner_corner_radius - self.border_width))

        for part in self.canvas_fg_parts:
            self.canvas.itemconfig(part, fill=self.fg_color, outline=self.fg_color)  # width=0 causes some render issues

        for part in self.canvas_border_parts:
            self.canvas.itemconfig(part, fill=self.border_color, outline=self.border_color, width=0)

        self.text_part = self.canvas.create_text(self.width / 2,
                                                 self.height / 2,
                                                 text=self.text,
                                                 font=self.text_font,
                                                 fill=self.text_color)

        self.set_text(self.text)

    def configure_color(self, bg_color=None, fg_color=None, hover_color=None, text_color=None):
        if bg_color is not None:
            self.bg_color = bg_color
        else:
            self.bg_color = self.master.cget("bg")

        if fg_color is not None:
            self.fg_color = fg_color

        if hover_color is not None:
            self.hover_color = hover_color

        if text_color is not None:
            self.text_color = text_color
            self.canvas.itemconfig(self.text_part, fill=self.text_color)

        self.draw()

    def configure_command(self, command):
        self.command = command
        self.function = command

    def set_text(self, text):
        self.canvas.itemconfig(self.text_part, text=text)

    def get_text(self):
        return self.text

    def on_enter(self, event=0):
        for part in self.canvas_fg_parts:
            self.canvas.itemconfig(part, fill=self.hover_color, outline=self.hover_color)

    def on_leave(self, event=0):
        for part in self.canvas_fg_parts:
            self.canvas.itemconfig(part, fill=self.fg_color, outline=self.fg_color)

    def clicked(self, event=0):
        if self.function is not None:
            self.function()
            self.on_leave()

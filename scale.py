import serial, io, sys, struct
import tkinter as tk
from tkinter import ttk

def getWeight(comPort):
    with serial.Serial(comPort,9600,timeout=1) as ser:
        weightReading = ser.read_until(b'\x67')   # read until 'g' appears
        weightReading = float(weightReading.strip(b'\x02\x2b\x20\x67')) #strip SoT, '+', space and 'g'
        return weightReading

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.option_menu_list = ["", "grams", "ounces", "parts"]
        # Create control variables
        self.var_0 = tk.BooleanVar()
        self.var_1 = tk.BooleanVar(value=True)
        self.var_2 = tk.BooleanVar()
        self.var_3 = tk.IntVar(value=2)
        self.var_4 = tk.StringVar(value=self.option_menu_list[1])
        self.var_5 = tk.DoubleVar(value=75.0)
        #self.var_5 = float(getWeight('COM12'))


        # Create widgets :)
        self.setup_widgets()

    def setup_widgets(self):

        # Create a Frame for input widgets
        self.widgets_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.widgets_frame.grid(
            row=0, column=1, padx=10, pady=(30, 10), sticky="nsew", rowspan=3
        )
        self.widgets_frame.columnconfigure(index=0, weight=1)

        # Label
        self.label = ttk.Label(
            self.widgets_frame,
            text="~Weightometer~",
            justify="center",
            font=("-size", 15, "-weight", "bold"),
        )
        self.label.grid(row=0, column=0, pady=10, columnspan=2)

        # Entry - weight reading
        self.entry = ttk.Entry(self.widgets_frame)
        self.entry.insert(0, "0.0g")
        self.entry.grid(row=1, column=0, padx=5, pady=(10, 10), sticky="ew")

        # Progressbar
        self.progress = ttk.Progressbar(
            self.widgets_frame, value=0, variable=self.var_5, mode="determinate"
        )
        self.progress.grid(row=2, column=0, padx=(10, 20), pady=(20, 20), sticky="ew")

        # OptionMenu - Units of measure g / oz / part count
        self.optionmenu = ttk.OptionMenu(
            self.widgets_frame, self.var_4, *self.option_menu_list
        )
        self.optionmenu.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Button - tare to zero
        self.button = ttk.Button(self.widgets_frame, text="tare")
        self.button.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")

        # Accentbutton - get single part weight
        self.accentbutton = ttk.Button(
            self.widgets_frame, text="weigh part", style="Accent.TButton"
        )
        self.accentbutton.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

        # Switch - measure continuously or not
        self.switch = ttk.Checkbutton(
            self.widgets_frame, text="stop/run", style="Switch.TCheckbutton"
        )
        self.switch.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")



        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Weightometer")

    # Simply set the theme
    root.tk.call("source", "Sun-Valley-ttk-theme\sun-valley.tcl")
    root.tk.call("set_theme", "light")

    app = App(root)
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

    weight = getWeight('COM12')

    print(f"test: the weight on the scale is: {weight}g")

    root.mainloop()


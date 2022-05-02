import serial, io, sys, struct
import tkinter as tk
from tkinter import ttk
#import threading
from threading import Thread
import logging
import time

class AsyncScale(Thread):
    def __init__(self):
        self.comPort = 'COM12'
        super().__init__()
        logging.info("scale comm thread starting")
        self.weightReading = None
        self.goodReading = float(0)
        self.ser = serial.Serial(self.comPort,9600,timeout=1)
        logging.info("port open")

    def run(self):
        while True:
            self.try_capture = True
            while self.try_capture == True:
                logging.info("readuntil")
                self.weightReading = self.ser.read_until(b'\x67')   # read until 'g' appears
                logging.info(f"raw reading: {self.weightReading}")
                self.weightReading = self.weightReading.strip(b'\n\r\x02\x2b\x20\x67')
                #weightReading = weightReading.strip(b'\x02\x2b\x20\x67')
                logging.info(f"stripped reading: {self.weightReading}")
                try:
                    self.weightReading = float(self.weightReading) #strip SoT, '+', space and 'g'
                except:
                    logging.info("bad reading!")
                    self.ser.reset_input_buffer()
                    time.sleep(0.25)
                    self.try_capture = True
                else:
                    self.try_capture = False
                    self.goodReading = self.weightReading
        logging.info("Thread scale comm, finishing")



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

        self.formatted_weight = tk.StringVar()
        self.formatted_weight.set("0.0g")
        self.raw_weight = tk.IntVar()


        # Create widgets :)
        self.setup_widgets()

    def setup_widgets(self):

        # ---------- title frame ----------
        self.widgets_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.widgets_frame.grid(
            row=0, column=0, padx=10, pady=(30, 10), sticky="nsew", rowspan=1
        )
        self.widgets_frame.columnconfigure(index=0, weight=1)

        # title
        self.label = ttk.Label(
            self.widgets_frame,
            text="~Weightometer~",
            justify="center",
            font=("-size", 15, "-weight", "bold"),
        )
        self.label.grid(row=0, column=0, pady=10, columnspan=1)

        # ---------- labelframe for weight reading ----------
        self.weight_frame = ttk.LabelFrame(
            self, padding=(0,0,0,10), 
            text="weight on scale:"
        )
        self.weight_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew", rowspan=1
        )

        # weight reading
        self.reading = ttk.Label(
            self.weight_frame,
            textvariable=self.formatted_weight)
        self.reading.grid(row=0, column=0, padx=0, pady=0, columnspan=1)

        # scale capacity bar
        self.progress = ttk.Progressbar(
            self.weight_frame, value=0, variable=self.raw_weight, mode="determinate"
        )
        self.progress.grid(row=1, column=0, padx=0, pady=0, sticky="ew")


        # OptionMenu - Units of measure g / oz / part count
        self.optionmenu = ttk.OptionMenu(
            self.widgets_frame, self.var_4, *self.option_menu_list
        )
        self.optionmenu.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Button - tare to zero
        self.button = ttk.Button(self.widgets_frame, text="tare")
        self.button.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")

        # Accentbutton - get single part weight
        self.weigh_button = ttk.Button(
            self.widgets_frame, text="weigh part", style="Accent.TButton"
        )
        #self.weigh_button['command'] = self.handle_scale
        self.weigh_button.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

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

    format = '%(asctime)s.%(msecs)03d: %(message)s'

    logging.basicConfig(format=format, level=logging.ERROR, datefmt='%Y-%m-%d,%H:%M:%S') 

    logging.info("Main")

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

    #weight = getWeight('COM12')

    #print(f"test: the weight on the scale is: {weight}g")

    scale_thread = AsyncScale()
    scale_thread.daemon = True  # This thread dies when main thread (only non-daemon thread) exits
    scale_thread.start()

    def updateWeight():
        app.formatted_weight.set(str(scale_thread.goodReading) + " g")
        app.raw_weight.set(int(scale_thread.goodReading))
        app.after(100, updateWeight)

    updateWeight()

    with open("testLog.csv", "a") as myfile:
        myfile.write("time,scaleWeight,scaleUnit" + "\n")

    def logData():
        with open("testLog.csv", "a") as myfile:
            myfile.write(str(time.time()) + "," + str(scale_thread.goodReading) + "," + "g" + "\n")
        app.after(1000, logData)

    logData()

    root.mainloop()


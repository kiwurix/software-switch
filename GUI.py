import tkinter as tk
from tkinter import ttk

from ui.filters_tab import FiltersTab
from ui.logs_tab import LogsTab
from ui.mac_tab import MacTab
from ui.stats_tab import StatsTab
from ui.syslog_tab import SyslogTab


class GUI:
    def __init__(self, switch):
        self.root = tk.Tk()
        self.root.title("Software Switch")
        self.root.geometry("1100x600")

        self.switch = switch

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        tabs = ttk.Notebook(self.root)
        tabs.grid(row=0, column=0, sticky="nsew")

        self.mac_tab = MacTab(tabs, self.switch, self.root, self.show_info)
        self.stats_tab = StatsTab(tabs, self.switch, self.root)
        self.filters_tab = FiltersTab(tabs, self.switch)
        self.syslog_tab = SyslogTab(tabs, self.switch, self.root, self.show_info)
        self.logs_tab = LogsTab(tabs, self.root)

    def show(self):
        self.root.mainloop()

    def log(self, message: str):
        self.logs_tab.log(message)

    def show_info(self, text: str):
        win = tk.Toplevel(self.root)
        win.title("INFO")
        win.geometry("320x100")
        ttk.Label(win, text=text).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(win, text="OK", command=win.destroy).grid(row=1, column=0, padx=10, pady=5, sticky="w")



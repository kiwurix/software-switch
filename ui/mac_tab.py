import time
import tkinter as tk
from tkinter import ttk


class MacTab:
    def __init__(self, notebook, switch, root, show_info):
        self.switch = switch
        self.root = root
        self.show_info = show_info

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="MAC table")

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(self.frame, columns=("mac", "port", "lifetime"), show="headings", height=12)
        self.table.heading("mac", text="MAC address")
        self.table.heading("port", text="Port")
        self.table.heading("lifetime", text="Lifetime")
        self.table.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        bottom = ttk.Frame(self.frame)
        bottom.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        bottom.columnconfigure(1, weight=1)

        ttk.Button(bottom, text="Clear table", command=self._clear_table).grid(row=0, column=0, sticky="w")

        self.timer_var = tk.StringVar(value=str(getattr(self.switch.cam, "time_limit", 300)))
        ttk.Entry(bottom, textvariable=self.timer_var, width=10).grid(row=0, column=1, sticky="e", padx=(10, 5))

        ttk.Button(bottom, text="Set timer (s)", command=self._set_timer).grid(row=0, column=2, sticky="e")

        self.refresh()

    def refresh(self):
        for iid in self.table.get_children():
            self.table.delete(iid)

        now = time.monotonic()
        for mac, (port, learned_at) in self.switch.cam.get_table():
            lifetime = int(now - learned_at)
            self.table.insert("", "end", values=(mac, port, lifetime))

        self.root.after(1000, self.refresh)

    def _clear_table(self):
        self.switch.clear_cam()

    def _set_timer(self):
        try:
            new_limit = int(self.timer_var.get())
            if new_limit <= 0:
                raise ValueError
        except ValueError:
            self.show_info("Timer must be a positive integer")
            return

        self.switch.set_cam_timer(new_limit)




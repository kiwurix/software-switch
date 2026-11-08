import tkinter as tk
from tkinter import ttk, scrolledtext


class LogsTab:
    def __init__(self, notebook, root):
        self.root = root
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Logs")

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.log_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=80, height=18)
        self.log_area.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.log_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.frame, text="Auto scroll down", variable=self.log_scroll).grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def log(self, message: str):
        def _insert():
            self.log_area.insert(tk.END, message + "\n")
            if self.log_scroll.get():
                self.log_area.see(tk.END)

        self.root.after(0, _insert)



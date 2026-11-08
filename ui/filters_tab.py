import tkinter as tk
from tkinter import ttk, scrolledtext
from helpers import parse_acl_input, acls_to_str


class FiltersTab:
    def __init__(self, notebook, switch):
        self.switch = switch

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Filters")

        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=2)

        self.cli = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD)
        self.cli.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.cli.bind("<Return>", self._on_acl_enter)
        self.cli.bind("<Key>", self._on_acl_key)
        self._acl_prompt()

        self.acl_display = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, state="disabled")
        self.acl_display.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.refresh_acl()

    def refresh_acl(self):
        self.acl_display.config(state="normal")
        self.acl_display.delete("1.0", tk.END)
        self.acl_display.insert(tk.END, acls_to_str(self.switch))
        self.acl_display.config(state="disabled")

    def _acl_prompt(self):
        self.cli.insert(tk.END, "ACL> ")
        self.cli.mark_set("input_start", "end-1c")
        self.cli.mark_set(tk.INSERT, "end-1c")
        self.cli.mark_gravity("input_start", "left")
        self.cli.see(tk.END)

    def _on_acl_enter(self, _):
        cmd = self.cli.get("input_start", tk.END).strip()
        self.cli.insert(tk.END, "\n")

        if cmd:
            result = parse_acl_input(cmd, self.switch)
            if result == "OK":
                self.refresh_acl()
            else:
                self.cli.insert(tk.END, result + "\n")

        self._acl_prompt()
        return "break"

    def _on_acl_key(self, event):
        if event.keysym in ("BackSpace", "Delete"):
            if self.cli.compare(tk.INSERT, "<=", "input_start"):
                return "break"
        elif self.cli.compare(tk.INSERT, "<", "input_start"):
            self.cli.mark_set(tk.INSERT, tk.END)



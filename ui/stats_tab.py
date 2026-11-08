from tkinter import ttk


class StatsTab:
    def __init__(self, notebook, switch, root):
        self.switch = switch
        self.root = root

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Statistics")

        self.stats_notebook = ttk.Notebook(self.frame)
        self.stats_notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.port_trees = {}
        for port in range(len(self.switch.interfaces)):
            port_frame = ttk.Frame(self.stats_notebook)
            self.stats_notebook.add(port_frame, text=f"Port {port}")

            port_frame.rowconfigure(0, weight=1)
            port_frame.columnconfigure(0, weight=1)

            tree = ttk.Treeview(port_frame, columns=("Protocol", "IN", "OUT"), show="headings", height=15)
            tree.heading("Protocol", text="Protocol")
            tree.heading("IN", text="IN")
            tree.heading("OUT", text="OUT")
            tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            self.port_trees[port] = tree

        reset_frame = ttk.Frame(self.frame)
        reset_frame.grid(row=1, column=0, pady=10, sticky="ew")
        ttk.Button(reset_frame, text="Reset Statistics", command=self.switch.reset_statistics).pack(side="left")

        self.refresh()

    def refresh(self):
        stats_by_port = self.switch.statistics

        for port, tree in self.port_trees.items():
            for child in tree.get_children():
                tree.delete(child)

            for proto in stats_by_port[port]:
                stats = stats_by_port[port][proto]
                tree.insert("", "end", values=(proto, stats["IN"], stats["OUT"]))

        self.root.after(1000, self.refresh)



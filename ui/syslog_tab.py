import tkinter as tk
from tkinter import ttk


class SyslogTab:
    def __init__(self, notebook, switch, root, show_info):
        self.switch = switch
        self.root = root
        self.show_info = show_info

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Syslog")

        logger = self.switch.logger
        self.frame.columnconfigure(1, weight=1)

        ttk.Label(self.frame, text="Source IP:").grid(row=0, column=0, padx=(20, 5), pady=(20, 5), sticky="w")
        self.syslog_src_var = tk.StringVar(value=logger.src_ip or "")
        ttk.Entry(self.frame, textvariable=self.syslog_src_var, width=20).grid(
            row=0, column=1, padx=(0, 20), pady=(20, 5), sticky="w")

        ttk.Label(self.frame, text="Server IP:").grid(row=1, column=0, padx=(20, 5), pady=5, sticky="w")
        self.syslog_dst_var = tk.StringVar(value=logger.dst_ip or "")
        ttk.Entry(self.frame, textvariable=self.syslog_dst_var, width=20).grid(
            row=1, column=1, padx=(0, 20), pady=5, sticky="w")

        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        self.syslog_start_btn = ttk.Button(btn_frame, text="Start", command=self._syslog_start)
        self.syslog_start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.syslog_stop_btn = ttk.Button(btn_frame, text="Stop", command=self._syslog_stop)
        self.syslog_stop_btn.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(btn_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.syslog_status_label = ttk.Label(btn_frame, text="")
        self.syslog_status_label.pack(side=tk.LEFT)

        self._update_syslog_status()

    def _validate_ip(self, ip: str) -> bool:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

    def _syslog_start(self):
        src = self.syslog_src_var.get().strip()
        dst = self.syslog_dst_var.get().strip()

        if not self._validate_ip(src):
            self.show_info(f"Invalid source IP: '{src}'")
            return
        if not self._validate_ip(dst):
            self.show_info(f"Invalid server IP: '{dst}'")
            return

        logger = self.switch.logger
        logger.src_ip = src
        logger.dst_ip = dst
        if not logger.start():
            self.show_info(f"Failed to bind to {src}")

        self._update_syslog_status()

    def _syslog_stop(self):
        self.switch.logger.stop()
        self._update_syslog_status()

    def _update_syslog_status(self):
        running = self.switch.logger.is_running()
        self.syslog_start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.syslog_stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        self.syslog_status_label.config(text="Running" if running else "Stopped",
                                        foreground="green" if running else "red")

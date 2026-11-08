from socket import socket
from socket import AF_INET, SOCK_DGRAM
from datetime import datetime
from enum import Enum

FACILITY = 16
SYSLOG_PORT = 514

class Severity(Enum):
    Error = 3
    Warning = 4
    Notification = 5
    Informational = 6


class SyslogClient:
    def __init__(self):
        self.sock = None
        self.src_ip = None
        self.dst_ip = None

    def is_running(self):
        return self.sock is not None

    def start(self):
        self.stop()

        if self.src_ip:
            try:
                self.sock = socket(AF_INET, SOCK_DGRAM)
                self.sock.bind((self.src_ip, 0))
                return True
            except OSError as e:
                self.stop()
                self.log(Severity.Error, f"Syslog start failed on {self.src_ip}: {e}")
                return False
        else:
            return False

    def stop(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def log(self, severity: Severity, message):
        if self.sock is None or self.dst_ip is None:
            return

        pri = FACILITY * 8 + severity.value
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = f"<{pri}>1 {timestamp} {self.src_ip} SWITCH - - - {message}"

        self.sock.sendto(payload.encode("utf-8"), (self.dst_ip, SYSLOG_PORT))



class Logger(SyslogClient):
    def __init__(self):
        super().__init__()
        self.local_log = None

    def log(self, severity: Severity, message):
        try:
            super().log(severity, message)
        except Exception as e:
            if self.local_log:
                self.local_log(f"[{Severity.Error.name}] Syslog sending error: {e}")

        if self.local_log:
            self.local_log(f"[{severity.name}] {message}")

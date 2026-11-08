import time
from threading import Lock


class CAM:
    def __init__(self):
        self.cam = {}
        self.time_limit = 300
        self.lock = Lock()


    def update(self, src_mac : str, port : int):
        with self.lock:
            is_new = src_mac not in self.cam
            self.cam[src_mac] = (port, time.monotonic())
            return is_new


    def get_port(self, mac : str):
        with self.lock:
            entry = self.cam.get(mac)
            return entry[0] if entry else None


    def clear(self):
        with self.lock:
            self.cam = {}


    def check_timer(self):
        now = time.monotonic()

        with self.lock:
            to_delete = [(mac, entry[0]) for mac, entry in self.cam.items() if now - entry[1] > self.time_limit]

            for mac, _ in to_delete:
                del self.cam[mac]

            return to_delete


    def get_table(self):
        with self.lock:
            return list(self.cam.items())

    def reset_port(self, port: int):
        with self.lock:
            self.cam = {mac: entry for mac, entry in self.cam.items() if entry[0] != port}
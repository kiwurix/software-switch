import time
from CAM import CAM
import scapy.all as scapy
from scapy.layers.l2 import Ether
from threading import Thread
from helpers import PROTOCOLS, has_protocol
from filters import ACL
from logger import Severity, Logger

class Switch:
    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.interface_to_port = {iface.network_name: port for port, iface in enumerate(interfaces)}
        self.macs = {iface.mac for iface in interfaces}
        self.connected_ports = [None] * len(self.interfaces)
        self.cam = CAM()
        self.hash_table = {}
        self.logger: Logger = None
        self.acls = {(port, direction): ACL() for port in range(len(interfaces)) for direction in ('IN', 'OUT')}
        self.reset_statistics()

    def log(self, severity, message):
        if self.logger:
            self.logger.log(severity, message)

    def _handle_frame(self, frame):
        if not Ether in frame:
            return

        ethernet = frame[Ether]

        src_mac = ethernet.src
        dst_mac = ethernet.dst

        if src_mac in self.macs or dst_mac in self.macs:
            return

        if self._is_loop(frame):
            return

        input_port = self.interface_to_port.get(frame.sniffed_on)

        if self.cam.update(src_mac, input_port):
            self.log(Severity.Informational, f"MAC learned: {src_mac} on port {input_port}")

        self._update_statistic(frame, input_port, 'IN')

        if not self.acls[(input_port, 'IN')].is_permitted(frame):
            self.log(Severity.Warning, f"ACL IN deny: {src_mac} -> {dst_mac} on port {input_port}")
            return

        output_port = self.cam.get_port(dst_mac)

        if dst_mac == "ff:ff:ff:ff:ff:ff" or output_port is None:
            for port in range(0, len(self.interfaces)):
                self._send_frame(frame, port, input_port, src_mac, dst_mac)

        else:
            self._send_frame(frame, output_port, input_port, src_mac, dst_mac)


    def _send_frame(self, frame, output_port, input_port, src_mac, dst_mac):
        if output_port == input_port or not self.connected_ports[output_port]:
            return

        if not self.acls[(output_port, 'OUT')].is_permitted(frame):
            self.log(Severity.Warning, f"ACL OUT deny: {src_mac} -> {dst_mac} on port {output_port}")
            return

        try:
            scapy.sendp(frame, iface=self.interfaces[output_port])
        except Exception as e:
            self.log(Severity.Error, f"Frame send failed on port {output_port}: {e}")
            return
        self._update_statistic(frame, output_port, 'OUT')


    def _update_statistic(self, frame, port, direction):
        for p in PROTOCOLS:
            if has_protocol(frame, p):
                self.statistics[port][p][direction] += 1


    def clear_cam(self):
        self.cam.clear()
        self.log(Severity.Notification, "MAC table cleared")

    def reset_statistics(self):
        self.statistics = {
            port: {prot: {'IN': 0, 'OUT': 0} for prot in PROTOCOLS}
            for port in range(len(self.interfaces))
        }
        self.log(Severity.Informational, "Statistics reset")

    def _is_loop(self, frame):
        key = bytes(frame)

        now = time.monotonic()
        last = self.hash_table.get(key)

        if last is not None and now - last <= 1:
            return True

        self.hash_table[key] = now

        if len(self.hash_table) > 1000:
            self.hash_table = {k : t for k, t in self.hash_table.items() if now - t <= 1}

        return False



    def _start_cam(self):
        while True:
            for mac, port in self.cam.check_timer():
                self.log(Severity.Informational, f"MAC aged out: {mac} on port {port}")
            time.sleep(2)


    def _start_listening(self):
        try:
            scapy.sniff(iface=self.interfaces, prn=self._handle_frame, store=False)
        except Exception as e:
            self.log(Severity.Error, f"Packet sniffing failed: {e}")


    def _connection_check(self):
        while True:
            scapy.conf.ifaces.reload()

            for interface, port in self.interface_to_port.items():
                if "DISCONNECTED" in scapy.resolve_iface(interface).flags:
                    if self.connected_ports[port]:
                        self.log(Severity.Warning, f"Port {port} disconnected")
                    self.connected_ports[port] = False
                    self.cam.reset_port(port)

                else:
                    if self.connected_ports[port] is False:
                        self.log(Severity.Notification, f"Port {port} connected")
                    self.connected_ports[port] = True

            time.sleep(2)


    def set_cam_timer(self, limit):
        self.cam.time_limit = limit
        self.log(Severity.Informational, f"MAC timer set to {limit} s")


    def start(self):
        self.log(Severity.Informational, "Switch service starting")
        Thread(target= self._start_cam, daemon= True).start()
        Thread(target= self._connection_check, daemon= True).start()
        Thread(target= self._start_listening, daemon= True).start()

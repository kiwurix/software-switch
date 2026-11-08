import scapy.all as scapy
from scapy.arch.windows import get_windows_if_list
from switch import Switch
from GUI import GUI
from logger import Logger

if __name__ == "__main__":
    scapy.conf.verb = 0

    interfaces = []

    for interface in get_windows_if_list():
        if interface.get("ipv4_metric") and interface.get("type") == 6:
            idx = interface["index"]
            device = scapy.dev_from_index(idx)

            if "WIRELESS" not in device.flags:
                interfaces.append(device)


    switch = Switch(interfaces)

    logger = Logger()
    switch.logger = logger

    gui = GUI(switch)
    logger.local_log = gui.log

    switch.start()
    gui.show()

# Software Switch

A Layer 2 software switch written in Python with Scapy and a Tkinter interface. I built it to understand how Ethernet frames are learned, filtered and forwarded, and tested it with physical Cisco networking equipment.

## Features

- MAC address learning and aging with a configurable timer.
- Forwarding to known destinations and flooding unknown/broadcast frames.
- Per-port ingress and egress ACLs for MAC/IP addresses, TCP/UDP ports and ICMP types.
- Per-port protocol counters for incoming and outgoing traffic.
- Local logs and remote Syslog logging over UDP.
- GUI tabs for the MAC table, statistics, filters and logging.

## Run

The current interface discovery is Windows-specific. Use Python 3.11+, Tkinter and [Npcap](https://npcap.com/). Packet capture and transmission may require administrator privileges.

From the project folder, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install scapy
python main.py
```

Connect at least two wired Ethernet interfaces to a lab topology. The program discovers interfaces at startup. Use the GUI to inspect learned MAC addresses, change the aging timer, configure ACLs and view traffic counters.

## Main files

- `switch.py` - frame processing and forwarding.
- `CAM.py` - MAC address table.
- `filters.py` - ACL rules.
- `logger.py` - local and Syslog logging.
- `GUI.py` and `ui/` - interface.


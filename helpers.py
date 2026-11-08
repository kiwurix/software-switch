from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, TCP, UDP, ICMP
from filters import ACE, RuleMac, RuleIP, RuleTCP, RuleUDP, RuleICMP
from logger import Severity

PROTOCOLS = {
    'Ethernet II': lambda f: Ether in f,
    'ARP': lambda f: ARP in f,
    'IP': lambda f: IP in f,
    'UDP': lambda f: UDP in f,
    'TCP': lambda f: TCP in f,
    'ICMP': lambda f: ICMP in f,
    'HTTP': lambda f: TCP in f and (f[TCP].dport == 80 or f[TCP].sport == 80)
}

def has_protocol(frame, protocol):
    checker = PROTOCOLS.get(protocol)
    return checker and checker(frame)


CMDS = {'mac', 'ip', 'tcp', 'udp', 'icmp'}

USAGE = (
    "Usage:\n"
    "  <port> <direction> <action> [groups...]          append\n"
    "  <port> <direction> <index> <action> [groups...]  insert at index\n"
    "  no <port> <direction>                            clear all\n"
    "  no <port> <direction> <index>                    delete\n"
    "\n"
    "Groups:\n"
    "  mac\n"
    "      src\t<xx:xx:xx:xx:xx:xx>\n"
    "      dst\t<xx:xx:xx:xx:xx:xx>\n"
    "  ip\n"
    "      src\t<x.x.x.x>\n"
    "      dst\t<x.x.x.x>\n"
    "  tcp\n"
    "      src\t<0-65535>\n"
    "      dst\t<0-65535>\n"
    "  udp\n"
    "      src\t<0-65535>\n"
    "      dst\t<0-65535>\n"
    "  icmp\n"
    "      type\t<0-255 | request | reply>\n"
)

def parse_acl_input(command, switch):
    tokens = command.strip().split()

    is_delete = tokens and tokens[0].lower() == 'no'

    if is_delete:
        if len(tokens) < 3:
            return USAGE
        port_str, direction_str = tokens[1], tokens[2].lower()
    else:
        if len(tokens) < 4:
            return USAGE
        port_str, direction_str = tokens[0], tokens[1].lower()

    if not port_str.isdigit() or int(port_str) >= len(switch.interfaces):
        return f"Invalid port: '{port_str}'"
    if direction_str not in ('in', 'out'):
        return f"Invalid direction: '{direction_str}'"

    acl = switch.acls[(int(port_str), direction_str.upper())]

    if is_delete:
        if len(tokens) == 3:
            acl.ACEs.clear()
            switch.log(Severity.Notification, f"ACL cleared on port {port_str} {direction_str}")
            return 'OK'
        index_str = tokens[3]
        if not index_str.isdigit():
            return f"Invalid index: '{index_str}'"
        index = int(index_str)
        if index >= len(acl.ACEs):
            return f"Index out of range: {index_str}"
        acl.delete_ACE(index)
        switch.log(Severity.Notification, f"ACL entry {index} deleted on port {port_str} {direction_str}")
        return 'OK'

    if tokens[2].isdigit():
        index, action, i = int(tokens[2]), tokens[3].lower(), 4
    else:
        index, action, i = None, tokens[2].lower(), 3

    if action not in ('permit', 'deny'):
        return f"Invalid action: '{action}'"

    rules = []
    while i < len(tokens):
        cmd = tokens[i].lower()
        if cmd not in CMDS:
            return f"Unknown command: '{tokens[i]}'"
        i += 1
        src = dst = type_val = None
        while i < len(tokens) and tokens[i].lower() not in CMDS:
            token = tokens[i].lower()
            if i + 1 >= len(tokens):
                return f"Missing value after '{token}'"
            if token == 'src':
                src = tokens[i+1].lower(); i+=2
            elif token == 'dst':
                dst = tokens[i+1].lower(); i+=2
            elif token == 'type':
                type_val = tokens[i+1].lower(); i+=2
            else:
                return f"Unexpected token '{tokens[i]}'"
        try:
            rules.append(parse_group(cmd, src, dst, type_val))
        except ValueError as e:
            return str(e)

    if not rules:
        return "At least one group is required"

    ace = ACE(rules, action == 'permit')
    if index is not None:
        acl.ACEs.insert(index, ace)
    else:
        acl.add_ACE(ace)

    switch.log(Severity.Notification, f"ACL entry added on port {port_str} {direction_str}")
    return 'OK'


def parse_group(cmd, src, dst, type_val):
    if cmd == 'mac': return RuleMac(src, dst)
    if cmd == 'ip': return RuleIP(src, dst)
    if cmd == 'tcp': return RuleTCP(src, dst)
    if cmd == 'udp': return RuleUDP(src, dst)
    if cmd == 'icmp': return RuleICMP(type_val)


def acls_to_str(switch):
    lines = []
    for port in range(len(switch.interfaces)):
        for direction in ('IN', 'OUT'):
            lines.append(f"Port {port} {direction}:")
            aces = switch.acls[(port, direction)].ACEs
            if not aces:
                lines.append("  -- empty --")
            else:
                for i, ace in enumerate(aces):
                    lines.append(f"  {i}  {ace}")
            lines.append("")
    return '\n'.join(lines)

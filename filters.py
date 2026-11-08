from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP, ICMP
from abc import ABC, abstractmethod


class Rule(ABC):
    @abstractmethod
    def matches(self, frame) -> bool:
        pass


class SrcDstRule(Rule):
    cmd = ''

    def __init__(self, protocol, src=None, dst=None):
        self.protocol = protocol
        self.src = src
        self.dst = dst

    def matches(self, frame) -> bool:
        if self.protocol not in frame:
            return False

        layer = frame[self.protocol]

        if self.protocol in (TCP, UDP):
            src, dst = layer.sport, layer.dport
        elif self.protocol in (Ether, IP):
            src, dst = layer.src, layer.dst
        else:
            return True

        if self.src is not None and src != self.src:
            return False
        if self.dst is not None and dst != self.dst:
            return False

        return True

    def __str__(self):
        parts = [self.cmd]
        if self.src is not None: parts += ['src', str(self.src)]
        if self.dst is not None: parts += ['dst', str(self.dst)]
        return ' '.join(parts)


class RuleMac(SrcDstRule):
    cmd = 'mac'

    def __init__(self, src=None, dst=None):
        for val in (src, dst):
            if val is None:
                continue
            parts = val.split(':')
            if len(parts) != 6:
                raise ValueError(f"Invalid MAC: '{val}'")
            for part in parts:
                if len(part) != 2:
                    raise ValueError(f"Invalid MAC: '{val}'")
                for c in part:
                    if not (('0' <= c <= '9') or ('a' <= c <= 'f')):
                        raise ValueError(f"Invalid MAC: '{val}'")
        super().__init__(Ether, src, dst)


class RuleIP(SrcDstRule):
    cmd = 'ip'

    def __init__(self, src=None, dst=None):
        for val in (src, dst):
            if val is None:
                continue
            parts = val.split('.')
            if len(parts) != 4:
                raise ValueError(f"Invalid IP: '{val}'")
            for part in parts:
                if not (part.isdigit() and 0 <= int(part) <= 255):
                    raise ValueError(f"Invalid IP: '{val}'")
        super().__init__(IP, src, dst)


class RuleTransport(SrcDstRule):
    def __init__(self, protocol, src=None, dst=None):
        for val in (src, dst):
            if val is not None and (not val.isdigit() or not 0 <= int(val) <= 65535):
                raise ValueError(f"Invalid port: '{val}'")
        super().__init__(protocol, int(src) if src else None, int(dst) if dst else None)


class RuleTCP(RuleTransport):
    cmd = 'tcp'
    def __init__(self, src=None, dst=None):
        super().__init__(TCP, src, dst)


class RuleUDP(RuleTransport):
    cmd = 'udp'
    def __init__(self, src=None, dst=None):
        super().__init__(UDP, src, dst)


class RuleICMP(Rule):
    ALIASES = {'request': '8', 'reply': '0'}

    def __init__(self, type_field=None):
        if type_field is not None:
            type_field = self.ALIASES.get(type_field, type_field)
            if not type_field.isdigit() or not 0 <= int(type_field) <= 255:
                raise ValueError(f"Invalid ICMP type: '{type_field}'")
        self.type = int(type_field) if type_field is not None else None

    def matches(self, frame) -> bool:
        if ICMP not in frame:
            return False
        if self.type is not None and frame[ICMP].type != self.type:
            return False
        return True

    def __str__(self):
        parts = ['icmp']
        if self.type is not None:
            parts += ['type', str(self.type)]
        return ' '.join(parts)


class ACE:
    def __init__(self, rules, permit):
        self.rules = rules
        self.permit = permit

    def status(self, frame):
        if all(rule.matches(frame) for rule in self.rules):
            return self.permit

        return None

    def __str__(self):
        action = 'permit' if self.permit else 'deny'
        return f"{action:<7} {' '.join(str(r) for r in self.rules)}"


class ACL:
    def __init__(self):
        self.ACEs = []

    def add_ACE(self, ace):
        self.ACEs.append(ace)

    def delete_ACE(self, index):
        del self.ACEs[index]

    def is_permitted(self, frame):
        for ace in self.ACEs:
            result = ace.status(frame)
            if result is not None:
                return result
        return True

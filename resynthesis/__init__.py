__all__ = ['states', 'ResynthesisState', 'ResynthesisError']

states = ['tap', 'hold', 'roll', 'tail']

class ResynthesisState(object):
    
    def __init__(self, gametype, l, r):
        self.l = l
        self.r = r
        self.real_l = gametype.l
        self.real_r = gametype.r
        self.h1 = min(gametype.h1, 0)
        self.h2 = min(gametype.h2, 0)
        self.real_h1 = gametype.h1
        self.real_h2 = gametype.h2
        self.last_used = gametype.last_used
        self.jack = gametype.jack
        self.drill = gametype.drill
        self.ambiguous = gametype.ambiguous
    
    def __str__(self):
        return " ".join((str(n).ljust(4) for n in (
            self.l,
            self.r,
            self.h1,
            self.h2,
            self.last_used,
            'J' if self.jack else '-',
            'D' if self.drill else '-',
            'A' if self.ambiguous else '-',
        )))
    
    def __eq__(self, other):
        for attr in ('l', 'r', 'h1', 'h2', 'last_used', 'jack', 'drill',
                'ambiguous'):
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

class ResynthesisError(Exception):
    pass
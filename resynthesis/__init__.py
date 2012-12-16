__all__ = ['states', 'ResynthesisState', 'ResynthesisError']

states = ['tap', 'hold', 'roll', 'tail']

class ResynthesisState(object):
    l = None
    r = None
    h1 = None
    h2 = None
    
    def __init__(self, l, r, h1, h2):
        self.l = l
        self.r = r
        self.h1 = h1
        self.h2 = h2
    
    def __str__(self):
        return "%s %s %s %s" % tuple(str(n).ljust(4)
            for n in (self.l, self.r, self.h1, self.h2))


class ResynthesisError(Exception):
    pass
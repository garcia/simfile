import logging
import math

__all__ = ['states', 'SynthesisState', 'SynthesisError', 'Synthesizer']

states = ['tap', 'hold', 'roll', 'tail']

class SynthesisState(object):
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
        self.error = gametype.error
        self.msimmons = gametype.msimmons
    
    def __str__(self):
        return " ".join((str(n).ljust(4) for n in (
            self.l,
            self.r,
            self.h1,
            self.h2,
            self.last_used,
            'J' if self.jack else '' +
            'D' if self.drill else '' +
            'A' if self.ambiguous else '' +
            'E' if self.error else '' +
            'M' if self.msimmons else '',
        )))
    
    def __eq__(self, other):
        for attr in ('l', 'r', 'h1', 'h2', 'last_used', 'jack', 'drill',
                'ambiguous', 'msimmons'):
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)


class SynthesisError(Exception):
    pass


class Synthesizer(object):
    # Common attributes
    h1 = None
    h2 = None
    last_used = 'j'
    jack = False
    drill = False
    ambiguous = False
    error = False
    msimmons = False
    
    def __init__(self, gametype, silent=False):
        if gametype == 'dance-single':
            self.p = ((-1, 0), (0, -1), (0, 1), (1, 0))
            self.l = (0, 1)
            self.r = (3, 1)
        elif gametype == 'techno-single8':
            self.p = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),
                      (1, 1), (1, 0), (1, -1))
            self.l = (1, 1)
            self.r = (6, 1)
        else:
            raise ValueError('unsupported gametype')
        self.pc = len(self.p)
        if silent:
            self.log = logging.getLogger('synctools.silent')
            self.log.setLevel('CRITICAL')
        else:
            self.log = logging.getLogger('synctools')
    
    def _lineMagnitude(self, x1, y1, x2, y2):
        lineMagnitude = math.sqrt(math.pow((x2 - x1), 2)+ math.pow((y2 - y1), 2))
        return lineMagnitude

    def dpl(self, p, a, b):
        # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
        LineMag = self._lineMagnitude(a[0], a[1], b[0], b[1])
        if LineMag < 0.00000001:
            DistancePointLine = 9999
            return DistancePointLine
        u1 = (((p[0] - a[0]) * (b[0] - a[0])) + ((p[1] - a[1]) * (b[1] - a[1])))
        u = u1 / (LineMag * LineMag)
        if (u < 0.00001) or (u > 1):
            # closest point does not fall within the line segment, take the
            # shorter distance to an endpoint
            ix = self._lineMagnitude(p[0], p[1], a[0], a[1])
            iy = self._lineMagnitude(p[0], p[1], b[0], b[1])
            if ix > iy:
                DistancePointLine = iy
            else:
                DistancePointLine = ix
        else:
            # Intersecting point is on the line, use the formula
            ix = a[0] + u * (b[0] - a[0])
            iy = a[1] + u * (b[1] - a[1])
            DistancePointLine = self._lineMagnitude(p[0], p[1], ix, iy)
        return DistancePointLine
    
    def is_hold(self, arrow):
        # Includes rolls because they're basically the same for our purposes
        return arrow and arrow[1] in (2, 4)
    
    def is_roll(self, arrow):
        return arrow and arrow[1] == 4
    
    def is_tail(self, arrow):
        return arrow and arrow[1] == 3
    
    def load_state(self, state):
        self.l = state.real_l
        self.r = state.real_r
        self.h1 = state.real_h1
        self.h2 = state.real_h2
        self.last_used = state.last_used
        self.jack = state.jack
        self.drill = state.drill
        self.ambiguous = state.ambiguous
        self.error = state.error
    
    def distance(self, a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    
    def _tap_ab(self, anchor, buoyant):
        l, r, b = self.p[self.l[0]], self.p[self.r[0]], self.p[buoyant[0]]
        if self.last_used == 'l':
            if l != b and r != b and self.dpl(l, r, b) < 0.25:
                self.log.debug('\t\t\t%s %s %s' % (l, r, b))
                self.msimmons = True
            self.l = anchor
            self.r = buoyant
        elif self.last_used == 'r':
            if l != b and r != b and self.dpl(r, l, b) < 0.25:
                self.log.debug('\t\t\t%s %s %s' % (l, r, b))
                self.msimmons = True
            self.r = anchor
            self.l = buoyant
    
    def _tap_left(self, arrow):
        if self.l[0] == arrow[0]:
            self.jack = True
        self.l = arrow
        self.last_used = 'l'
    
    def _tap_right(self, arrow):
        if self.r[0] == arrow[0]:
            self.jack = True
        self.r = arrow
        self.last_used = 'r'
    
    def tap(self, arrow):
        p = self.p[arrow[0]]
        l, r = self.p[self.l[0]], self.p[self.r[0]]
        # Are both feet planted?
        if self.is_hold(self.l) and self.is_hold(self.r):
            # Is one hand planted too?
            if self.is_hold(self.h1):
                self.h2 = arrow
            # No, just the feet
            else:
                self.h1 = arrow
        # Is one foot planted?
        elif self.is_hold(self.l):
            self._tap_right(arrow)
        elif self.is_hold(self.r):
            self._tap_left(arrow)
        # Were both feet just used?
        elif self.last_used == 'j':
            # Was a foot was just used to hit that panel?
            self.log.debug(p, l, r)
            if (p == l):
                self._tap_left(arrow)
            elif (p == r):
                self._tap_right(arrow)
            # Does using one foot to hit the panel result in a crossover?
            elif p[0] < l[0]:
                self._tap_left(arrow)
            elif p[0] > r[0]:
                self._tap_right(arrow)
            # Must be at least somewhat ambiguous
            else:
                d = self.distance(p, r) - self.distance(p, l)
                # Is one foot significantly closer?
                if d >= .5:
                    self._tap_left(arrow)
                elif d <= .5:
                    self._tap_right(arrow)
                # Must be ambiguous
                else:
                    self.ambiguous = True
                    self._tap_left(arrow) # Arbitrarily chosen
        # Must have last used one foot
        else:
            if self.last_used == 'l':
                anchored = self.l
                buoyant = self.r
            elif self.last_used == 'r':
                anchored = self.r
                buoyant = self.l
            a, b = self.p[anchored[0]], self.p[buoyant[0]]
            # Is this a jack?
            if a == p:
                self._tap_ab(arrow, buoyant)
                self.jack = True
            # Is this a crossover / doublestep?
            elif (self.last_used == 'l' and p[0] < l[0] or
                    self.last_used == 'r' and p[0] > r[0]):
                self._tap_ab(arrow, buoyant)
            # Must be a regular step
            else:
                # Is the buoyant foot staying in position?
                if b == p:
                    self.drill = True
                self._tap_ab(anchored, arrow)
                self.last_used = {'l': 'r', 'r': 'l'}[self.last_used]
    
    def jump(self, arrow1, arrow2):
        p1 = self.p[arrow1[0]]
        p2 = self.p[arrow2[0]]
        l, r = self.p[self.l[0]], self.p[self.r[0]]
        # Is at least one foot planted?
        if self.is_hold(self.l) or self.is_hold(self.r):
            self.h1 = arrow1
            self.h2 = arrow2
        # Does hitting the jump one way result in a crossover?
        elif p1[0] < p2[0]:
            self.l = arrow1
            self.r = arrow2
        elif p2[0] < p1[0]:
            self.l = arrow2
            self.r = arrow1
        # Was a foot just used to hit one of these panels?
        elif l == p1 or r == p2:
            self.l = arrow1
            self.r = arrow2
        elif l == p2 or r == p1:
            self.l = arrow2
            self.r = arrow1
        # Must be ambiguous
        else:
            self.ambiguous = True
            # Arbitrarily chosen
            self.l = arrow1
            self.r = arrow2
        # Find jacks
        if self.p[self.l[0]] == l and  self.p[self.r[0]] == r:
            self.jack = True
        self.last_used = 'j'
    
    def _triple_feet(self, arrow1, arrow2):
        p1 = self.p[arrow1[0]]
        p2 = self.p[arrow2[0]]
        # TODO: repeated code (copied from jump method)
        # Does hitting the jump one way result in a crossover?
        if p1[0] < p2[0]:
            self.l = arrow1
            self.r = arrow2
        elif p2[0] < p1[0]:
            self.l = arrow2
            self.r = arrow1
        # Must be ambiguous (all three arrows in one vertical plane)
        else:
            self.ambiguous = True
            # Arbitrarily chosen
            self.l = arrow1
            self.r = arrow2
    
    def triple(self, arrow1, arrow2, arrow3):
        p1 = self.p[arrow1[0]]
        p2 = self.p[arrow2[0]]
        p3 = self.p[arrow3[0]]
        l, r = self.p[self.l[0]], self.p[self.r[0]]
        # TODO: where to put other foot shouldn't be purely arbitrary
        # Is one foot planted?
        if self.is_hold(self.l):
            self.r = arrow1
            self.h1 = arrow2
            self.h2 = arrow3
        if self.is_hold(self.r):
            self.l = arrow1
            self.h1 = arrow2
            self.h2 = arrow3
        # Is one of these panels further up than the rest?
        if p1[1] > p2[1] and p1[1] > p3[1]:
            self._triple_feet(arrow2, arrow3)
            self.h1 = arrow1
        elif p2[1] > p1[1] and p2[1] > p3[1]:
            self._triple_feet(arrow1, arrow3)
            self.h1 = arrow2
        elif p3[1] > p1[1] and p3[1] > p2[1]:
            self._triple_feet(arrow1, arrow2)
            self.h1 = arrow3
        # An ideal solution after this would be to assume the player will try
        # to stay as forward-facing as possible, and failing that, will try to
        # hit whichever arrow is in the middle with his hand, but these edge
        # cases will have to wait
        else:
            self.ambiguous = True
            # Arbitrarily chosen
            self.l = arrow1
            self.r = arrow2
            self.h1 = arrow3

    def quad(self, arrow1, arrow2, arrow3, arrow4):
        # TODO: this shouldn't always be ambiguous
        self.ambiguous = True
        self.l = arrow1
        self.r = arrow2
        self.h1 = arrow3
        self.h2 = arrow4
    
    def tail(self, panel):
        # Left tail
        if (self.is_hold(self.l) and self.l[0] == panel):
            self.l = (self.l[0], 3)
            self.last_used = 'l'
        # Right tail
        elif (self.is_hold(self.r) and self.r[0] == panel):
            self.r = (self.r[0], 3)
            self.last_used = 'r'
        # Hand 1 tail
        elif (self.is_hold(self.h1) and self.h1[0] == panel):
            self.h1 = (self.h1[0], 3)
        # Hand 2 tail
        elif (self.is_hold(self.h2) and self.h2[0] == panel):
            self.h2 = (self.h2[0], 3)
        # Unmatched tail
        else:
            self.log.warn("Unmatched tail")
            self.error = True
    
    def state(self):
        l = r = ''
        # Left tail
        if self.is_tail(self.l):
            l = 'tail'
            # Immediately following right event
            if self.last_used == 'r':
                if self.is_hold(self.r):
                    if self.is_roll(self.r):
                        r = 'roll'
                    else:
                        r = 'hold'
                elif self.is_tail(self.r):
                    r = 'tail'
                    self.last_used = 'j'
                else:
                    r = 'tap'
        # TODO: repeated code (copied from above)
        # Right tail
        elif self.is_tail(self.r):
            r = 'tail'
            # Immediately following left event
            if self.last_used == 'l':
                if self.is_hold(self.l):
                    if self.is_roll(self.l):
                        l = 'roll'
                    else:
                        l = 'hold'
                elif self.is_tail(self.l):
                    l = 'tail'
                    self.last_used = 'j'
                else:
                    l = 'tap'
        elif self.last_used == 'j':
            l = 'tap'
            r = 'tap'
        elif self.last_used == 'r':
            r = 'tap'
        elif self.last_used == 'l':
            l = 'tap'
        if self.is_hold(self.l):
            if self.is_roll(self.l):
                l = 'roll'
            else:
                l = 'hold'
        if self.is_hold(self.r):
            if self.is_roll(self.r):
                r = 'roll'
            else:
                r = 'hold'
        return SynthesisState(self, l, r)
    
    def parse_row(self, row):
        # Remove non-holding hands
        if not self.is_hold(self.h1):
            self.h1 = None
        if not self.is_hold(self.h2):
            self.h2 = None
        # Remove tails
        if self.is_tail(self.l):
            self.l = (self.l[0], 1)
        if self.is_tail(self.r):
            self.r = (self.r[0], 1)
        if self.is_tail(self.h1):
            self.h1 = (self.h1[0], 1)
        if self.is_tail(self.h2):
            self.h2 = (self.h2[0], 1)
        # Get nonzero arrows from row
        arrows = []
        state_changed = False
        for i, c in enumerate(row):
            # Try/except clause handles mines, lifts, etc. by ignoring them
            try:
                c = int(c)
            except ValueError:
                c = 0
            # Process tails first
            if c == 3:
                self.tail(i)
                state_changed = True
            elif c:
                arrows.append((i, c))
                state_changed = True
        if not state_changed:
            return
        # Reset parameters
        self.jack = False
        self.drill = False
        self.ambiguous = False
        self.error = False
        self.msimmons = False
        # Check hold integrity
        for part in (self.l, self.r, self.h1, self.h2):
            for arrow in arrows:
                if self.is_hold(part) and part[0] == arrow[0]:
                    raise SynthesisError("Arrow inside hold")
        # Call the appropriate function
        if arrows:
            [self.tap, self.jump, self.triple, self.quad][len(arrows) - 1](
                *arrows)
        return self.state()
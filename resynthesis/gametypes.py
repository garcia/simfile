import logging

from resynthesis import *

__all__ = ['DanceSingle', 'TechnoSingle8', 'gametypes']

class DanceSingle(object):
    # Constants
    L, D, U, R = xrange(4)
    P = 4
    # Attributes
    l = L
    r = R
    h1 = -1
    h2 = -1
    last_used = 'j'
    jack = False
    
    def __init__(self):
        self.log = logging.getLogger('synctools')
    
    def _is_hold(self, f):
        # Includes rolls because they're basically the same for our purposes
        return f in (4, 5, 6, 7, 12, 13, 14, 15)
    
    def _is_roll(self, f):
        return f >= 12
    
    def _is_tail(self, f):
        return 8 <= f < 12
    
    def tap(self, arrow):
        self.jack = False
        panel = arrow % self.P
        # Hands
        if self._is_hold(self.r) and self._is_hold(self.l):
            # Three holds and a tap
            if self._is_hold(self.h1):
                self.h2 = arrow
            # Two holds and a tap
            else:
                self.h1 = arrow
                self.h2 = -1
            last_used = 'h'
        # TODO: lots of repeated code here, but reducing repetition would also
        #       reduce readability... sigh
        # Last used left foot
        elif self.last_used == 'l':
            # One-footing or jack
            if self._is_hold(self.r) or self.l == panel:
                self.l = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif arrow == self.L:
                if self._is_hold(self.l):
                    self.r = arrow
                    self.last_used = 'r'
                else:
                    self.log.warn("Double step")
                    self.l = arrow
            # Alternating feet
            else:
                self.r = arrow
                self.last_used = 'r'
        # Last used right foot
        elif self.last_used == 'r':
            # One-footing or jack
            if self._is_hold(self.l) or self.r == panel:
                self.r = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif arrow == self.R:
                if self._is_hold(self.r):
                    self.l = arrow
                    self.last_used = 'l'
                else:
                    self.log.warn("Double step")
                    self.r = arrow
            # Alternating feet
            else:
                self.l = arrow
                self.last_used = 'l'
        # Last used both (jump)
        elif self.last_used == 'j':
            # One hold
            if self._is_hold(self.l):
                self.r = arrow
                self.last_used = 'r'
            elif self._is_hold(self.r):
                self.l = arrow
                self.last_used = 'l'
            # Unambiguous
            elif self.l == panel or self.L == panel:
                self.l = arrow
                self.last_used = 'l'
            elif self.r == panel or self.R == panel:
                self.r = arrow
                self.last_used = 'r'
            # Ambiguous
            elif (self.l == self.L and self.r == self.U and panel == self.D or
                  self.l == self.L and self.r == self.D and panel == self.U):
                self.log.warn("Semi-ambiguous tap")
                self.l = arrow
                self.last_used = 'l'
            elif (self.r == self.R and self.l == self.U and panel == self.D or
                  self.r == self.R and self.l == self.D and panel == self.U):
                self.log.warn("Semi-ambiguous tap")
                self.r = arrow
                self.last_used = 'r'
            # Completely ambiguous (i.e. LR jump followed by U/D tap)
            else:
                self.log.warn("Ambiguous tap")
                # Arbitrary values
                self.l = arrow
                self.last_used = 'l'
    
    def hold(self, arrow):
        self.tap(arrow + self.P)
    
    def roll(self, arrow):
        self.tap(arrow + self.P * 3)
    
    def tail(self, arrow):
        self.jack = False
        # Left tail
        if self.l / self.P in (1, 3) and self.l % self.P == arrow:
            self.l = self.l % self.P + self.P * 2
            self.last_used = 'l'
        # Right tail
        elif self.r / self.P in (1, 3) and self.r % self.P == arrow:
            self.r = self.r % self.P + self.P * 2
            self.last_used = 'r'
        # Hold wasn't found
        else:
            self.log.warn("Unmatched tail")
    
    def jump(self, arrow1, arrow2):
        self.jack = False
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        # Hands (probably actually bracketing but oh well)
        if self._is_hold(self.r) or self._is_hold(self.l):
            self.h1 = arrow1
            self.h2 = arrow2
            self.last_used = 'h'
            return
        # Both feet were just used to hit these arrows
        if (self.l == panel1 and self.r == panel2 or
                self.l == panel2 and self.r == panel1):
            self.jack = True
        # At least one foot was just used to hit one of these arrows
        if self.l == panel1 or self.r == panel2:
            self.l = arrow1
            self.r = arrow2
        elif self.l == panel2 or self.r == panel1:
            self.l = arrow2
            self.r = arrow1
        # At least one arrow is non-ambiguous
        elif self.L == panel1 or self.R == panel2:
            self.l = arrow1
            self.r = arrow2
        elif self.L == panel2 or self.R == panel1:
            self.l = arrow2
            self.r = arrow1
        # Ambiguous U/D jump
        else:
            self.log.warn("Ambiguous jump")
            # Arbitrary values
            self.l = arrow1
            self.r = arrow2
        self.last_used = 'j'
    
    def state(self, readable=False):
        l = r = ''
        # Left tail
        if self._is_tail(self.l):
            l = 'tail'
            self.l %= self.P
            # Immediately following right event
            if self.last_used == 'r':
                if self._is_hold(self.r):
                    if self._is_roll(self.r):
                        r = 'roll'
                    else:
                        r = 'hold'
                elif self._is_tail(self.r):
                    r = 'tail'
                    self.last_used = 'j'
                else:
                    r = 'tap'
        # Right tail
        elif self._is_tail(self.r):
            r = 'tail'
            self.r %= self.P
            # Immediately following left event
            if self.last_used == 'l':
                if self._is_hold(self.l):
                    if self._is_roll(self.l):
                        l = 'roll'
                    else:
                        l = 'hold'
                elif self._is_tail(self.l):
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
        if self._is_hold(self.l):
            if self._is_roll(self.l):
                l = 'roll'
            else:
                l = 'hold'
        if self._is_hold(self.r):
            if self._is_roll(self.r):
                r = 'roll'
            else:
                r = 'hold'
        if readable:
            return '%s %s' % (self.STATES[l], self.STATES[r])
        return ResynthesisState(l, r, self.h1, self.h2)
        
    def parse_row(self, row):
        # No taps
        if set(row) == set('0'):
            return
        # Single tap, hold, roll, or tail
        if row.count('0') == 3:
            if '1' in row:
                self.tap(row.find('1'))
            elif '2' in row:
                self.hold(row.find('2'))
            elif '3' in row:
                self.tail(row.find('3'))
            elif '4' in row:
                self.roll(row.find('4'))
        # Jump with no tails
        elif row.count('0') == 2 and '3' not in row:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + 4 * (int(col) - 1))
            self.jump(*arrows)
        # Tail and one or two taps / other tails
        elif '0' in row and '3' in row:
            arrows = []
            for i, col in enumerate(row):
                if col == '3':
                    self.tail(i)
                elif col != '0':
                    arrows.append(i + 4 * (int(col) - 1))
            if len(arrows) == 1:
                self.tap(arrows[0])
            elif len(arrows) == 2:
                self.jump(*arrows)
        else:
            raise ResynthesisError()
        return self.state()


class TechnoSingle8(object):
    # Constants
    LD, L, LU, D, U, RU, R, RD = xrange(8)
    LS = (LD, L, LU)
    RS = (RD, R, RU)
    UD = (U, D)
    P = 8
    # Attributes
    l = L
    r = R
    h1 = -1
    h2 = -1
    last_used = 'j'
    jack = False
    
    def __init__(self):
        self.log = logging.getLogger('synctools')
    
    def _is_hold(self, f):
        # Includes rolls because they're basically the same for our purposes
        return (8 <= f < 16) or (24 <= f < 32)
    
    def _is_roll(self, f):
        return f >= 24
    
    def _is_tail(self, f):
        return 16 <= f < 24
    
    def tap(self, arrow):
        self.jack = False
        panel = arrow % self.P
        # Hands
        if self._is_hold(self.r) and self._is_hold(self.l):
            # Three holds and a tap
            if self._is_hold(self.h1):
                self.h2 = arrow
            # Two holds and a tap
            else:
                self.h1 = arrow
                self.h2 = -1
            last_used = 'h'
        # TODO: lots of repeated code here, but reducing repetition would also
        #       reduce readability... sigh
        # Last used left foot
        elif self.last_used == 'l':
            # One-footing or jack
            if self._is_hold(self.r) or self.l == panel:
                self.l = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif (arrow in self.LS and self.l not in self.LS or
                  arrow in self.UD and self.l in self.RS):
                if self._is_hold(self.l):
                    self.r = arrow
                    self.last_used = 'r'
                else:
                    self.log.warn("Double step")
                    self.l = arrow
            # Alternating feet
            else:
                self.r = arrow
                self.last_used = 'r'
        # Last used right foot
        elif self.last_used == 'r':
            # One-footing or jack
            if self._is_hold(self.l) or self.r == panel:
                self.r = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif (arrow in self.RS and self.r not in self.RS or
                  arrow in self.UD and self.r in self.LS):
                if self._is_hold(self.r):
                    self.l = arrow
                    self.last_used = 'l'
                else:
                    self.log.warn("Double step")
                    self.r = arrow
            # Alternating feet
            else:
                self.l = arrow
                self.last_used = 'l'
        # Last used both (jump)
        elif self.last_used == 'j':
            # One hold
            if self._is_hold(self.l):
                self.r = arrow
                self.last_used = 'r'
            elif self._is_hold(self.r):
                self.l = arrow
                self.last_used = 'l'
            # Unambiguous
            # TODO: patterns like UD jump, L will be perceived as ambiguous
            elif (self.l == panel or panel in self.LS and 
                  not self.l in self.LS and not self.r in self.LS):
                self.l = arrow
                self.last_used = 'l'
            elif (self.r == panel or panel in self.RS and 
                  not self.r in self.RS and not self.l in self.RS):
                self.r = arrow
                self.last_used = 'r'
            # Ambiguous
            elif (self.l in self.LS and self.r == self.U and panel == self.D or
                  self.l in self.LS and self.r == self.D and panel == self.U):
                self.log.warn("Semi-ambiguous tap")
                self.l = arrow
                self.last_used = 'l'
            elif (self.r in self.RS and self.l == self.U and panel == self.D or
                  self.r in self.RS and self.l == self.D and panel == self.U):
                self.log.warn("Semi-ambiguous tap")
                self.r = arrow
                self.last_used = 'r'
            # Completely ambiguous (e.g. LR jump followed by U/D tap)
            else:
                self.log.warn("Ambiguous tap")
                # Arbitrary values
                self.l = arrow
                self.last_used = 'l'
    
    def hold(self, arrow):
        self.tap(arrow + self.P)
    
    def roll(self, arrow):
        self.tap(arrow + self.P * 3)
    
    def tail(self, arrow):
        self.jack = False
        # Left tail
        if self.l / self.P in (1, 3) and self.l % self.P == arrow:
            self.l = self.l % self.P + self.P * 2
            self.last_used = 'l'
        # Right tail
        elif self.r / self.P in (1, 3) and self.r % self.P == arrow:
            self.r = self.r % self.P + self.P * 2
            self.last_used = 'r'
        # Hold wasn't found
        else:
            self.log.warn("Unmatched tail")
    
    def jump(self, arrow1, arrow2):
        self.jack = False
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        # Hands (probably actually bracketing but oh well)
        if self._is_hold(self.r) or self._is_hold(self.l):
            self.h1 = arrow1
            self.h2 = arrow2
            self.last_used = 'h'
            return
        # Both feet were just used to hit these arrows
        if (self.l == panel1 and self.r == panel2 or
                self.l == panel2 and self.r == panel1):
            self.jack = True
        # At least one foot was just used to hit one of these arrows
        if self.l == panel1 or self.r == panel2:
            self.l = arrow1
            self.r = arrow2
        elif self.l == panel2 or self.r == panel1:
            self.l = arrow2
            self.r = arrow1
        # At least one arrow is non-ambiguous
        elif ((panel1 in self.LS and panel2 not in self.LS) or
              (panel2 in self.RS and panel1 not in self.RS)):
            self.l = arrow1
            self.r = arrow2
        elif ((panel2 in self.LS and panel1 not in self.LS) or
              (panel1 in self.RS and panel2 not in self.RS)):
            self.l = arrow2
            self.r = arrow1
        # Ambiguous U/D jump
        else:
            self.log.warn("Ambiguous jump")
            # Arbitrary values
            self.l = arrow1
            self.r = arrow2
        self.last_used = 'j'
    
    def state(self, readable=False):
        l = r = ''
        # Left tail
        if self._is_tail(self.l):
            l = 'tail'
            self.l %= self.P
            # Immediately following right event
            if self.last_used == 'r':
                if self._is_hold(self.r):
                    if self._is_roll(self.r):
                        r = 'roll'
                    else:
                        r = 'hold'
                elif self._is_tail(self.r):
                    r = 'tail'
                    self.last_used = 'j'
                else:
                    r = 'tap'
        # Right tail
        elif self._is_tail(self.r):
            r = 'tail'
            self.r %= self.P
            # Immediately following left event
            if self.last_used == 'l':
                if self._is_hold(self.l):
                    if self._is_roll(self.l):
                        l = 'roll'
                    else:
                        l = 'hold'
                elif self._is_tail(self.l):
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
        if self._is_hold(self.l):
            if self._is_roll(self.l):
                l = 'roll'
            else:
                l = 'hold'
        if self._is_hold(self.r):
            if self._is_roll(self.r):
                r = 'roll'
            else:
                r = 'hold'
        if readable:
            return '%s %s' % (self.STATES[l], self.STATES[r])
        return ResynthesisState(l, r, self.h1, self.h2)
        
    def parse_row(self, row):
        # No taps
        if set(row) == set('0'):
            return
        # Single tap, hold, roll, or tail
        if row.count('0') == 7:
            if '1' in row:
                self.tap(row.find('1'))
            elif '2' in row:
                self.hold(row.find('2'))
            elif '3' in row:
                self.tail(row.find('3'))
            elif '4' in row:
                self.roll(row.find('4'))
        # Jump with no tails
        elif row.count('0') == 6 and '3' not in row:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            self.jump(*arrows)
        # Tail and one or two taps / other tails
        elif row.count('0') >= 5 and '3' in row:
            arrows = []
            for i, col in enumerate(row):
                if col == '3':
                    self.tail(i)
                elif col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            if len(arrows) == 1:
                self.tap(arrows[0])
            elif len(arrows) == 2:
                self.jump(*arrows)
        else:
            raise ResynthesisError()
        return self.state()

gametypes = {
    'dance-single': DanceSingle,
    'techno-single8': TechnoSingle8,
}
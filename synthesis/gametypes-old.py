import logging

from resynthesis import *

__all__ = ['DanceSingle', 'TechnoSingle8', 'gametypes']

class GameType(object):
    # Common attributes
    h1 = -1
    h2 = -1
    last_used = 'j'
    jack = False
    drill = False
    ambiguous = False
    error = False
    
    def __init__(self, silent=False):
        if silent:
            self.log = logging.getLogger('synctools.silent')
            self.log.setLevel('CRITICAL')
        else:
            self.log = logging.getLogger('synctools')
    
    def reset_attrs(self):
        self.jack = False
        self.drill = False
        self.ambiguous = False
        self.error = False
        if not self.is_hold(self.h1):
            self.h1 = -1
        if not self.is_hold(self.h2):
            self.h2 = -1
    
    def is_hold(self, f):
        # Includes rolls because they're basically the same for our purposes
        return (self.P <= f < self.P * 2) or (self.P * 3 <= f < self.P * 4)
    
    def is_roll(self, f):
        return f >= self.P * 3
    
    def is_tail(self, f):
        return self.P * 2 <= f < self.P * 3
    
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

class DanceSingle(GameType):
    # Constants
    L, D, U, R = xrange(4)
    P = 4
    # Attributes
    l = L
    r = R
    
    def tap(self, arrow, reset=True):
        if reset:
            self.reset_attrs()
        panel = arrow % self.P
        # Hands
        if self.is_hold(self.r) and self.is_hold(self.l):
            # Three holds and a tap
            if self.is_hold(self.h1):
                self.h2 = arrow
            # Two holds and a tap
            else:
                self.h1 = arrow
            last_used = 'h'
        if (self.is_hold(self.l) and self.l % self.P == panel or
                self.is_hold(self.r) and self.r % self.P == panel):
            self.log.warn("Tap during hold")
            self.error = True
            return
        # TODO: lots of repeated code here, but reducing repetition would also
        #       reduce readability... sigh
        # Last used left foot
        elif self.last_used == 'l':
            # One-footing or jack
            if self.is_hold(self.r) or self.l == panel:
                self.l = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif panel == self.L:
                if self.is_hold(self.l):
                    self.r = arrow
                    self.last_used = 'r'
                else:
                    self.log.info("Double step")
                    self.r = self.l
                    self.l = arrow
            # Alternating feet
            else:
                # Drill
                if self.r == panel:
                    self.drill = True
                self.r = arrow
                self.last_used = 'r'
        # Last used right foot
        elif self.last_used == 'r':
            # One-footing or jack
            if self.is_hold(self.l) or self.r == panel:
                self.r = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif panel == self.R:
                if self.is_hold(self.r):
                    self.l = arrow
                    self.last_used = 'l'
                else:
                    self.log.info("Double step")
                    self.l = self.l
                    self.r = arrow
            # Alternating feet
            else:
                # Drill
                if self.l == panel:
                    self.drill = True
                self.l = arrow
                self.last_used = 'l'
        # Last used both (jump)
        elif self.last_used == 'j':
            # One hold
            if self.is_hold(self.l):
                self.r = arrow
                self.last_used = 'r'
            elif self.is_hold(self.r):
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
                self.log.info("Semi-ambiguous tap")
                self.l = arrow
                self.last_used = 'l'
                self.ambiguous = True
            elif (self.r == self.R and self.l == self.U and panel == self.D or
                  self.r == self.R and self.l == self.D and panel == self.U):
                self.log.info("Semi-ambiguous tap")
                self.r = arrow
                self.last_used = 'r'
                self.ambiguous = True
            # Completely ambiguous (i.e. LR jump followed by U/D tap)
            else:
                self.log.info("Ambiguous tap")
                # Arbitrary values
                self.l = arrow
                self.last_used = 'l'
                self.ambiguous = True
    
    def hold(self, arrow):
        if (self.is_hold(self.l) and self.l % self.P == arrow or
                self.is_hold(self.r) and self.r % self.P == arrow):
            self.log.info("Double hold")
            self.error = True
            return
        self.tap(arrow + self.P)
    
    def roll(self, arrow):
        self.tap(arrow + self.P * 3)
    
    def tail(self, arrow):
        #self.reset_attrs()
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
            self.error = True
    
    def jump(self, arrow1, arrow2):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        arrows = (arrow1, arrow2)
        panels = (panel1, panel2)
        if len(panels) != len(set(panels)):
            self.log.warn("Invalid jump")
            self.error = True
            return
        # Hands (probably actually bracketing but oh well)
        if self.is_hold(self.r) or self.is_hold(self.l):
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
            self.log.info("Ambiguous jump")
            self.ambiguous = True
            # Arbitrary values
            self.l = arrow1
            self.r = arrow2
        self.last_used = 'j'
    
    def triplet(self, arrow1, arrow2, arrow3):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        panel3 = arrow3 % self.P
        arrows = (arrow1, arrow2, arrow3)
        panels = (panel1, panel2, panel3)
        if len(panels) != len(set(panels)):
            self.log.warn("Invalid triplet")
            self.error = True
            return
        self.last_used = 'j'
        # Right foot is holding
        if self.is_hold(self.r):
            # Holding down arrow
            if self.r % self.P == self.D:
                for i, p in enumerate(panels):
                    if p == self.L:
                        self.l = arrows[i]
                        self.h1 = arrows[(i + 1) % 3]
                        self.h2 = arrows[(i + 2) % 3]
                        return
                # Impossible
                self.error = True
            # Holding any other arrow
            else:
                for i, p in enumerate(panels):
                    if p == self.D:
                        self.l = arrows[i]
                        self.h1 = arrows[(i + 1) % 3]
                        self.h2 = arrows[(i + 2) % 3]
                        return
                # Impossible
                self.error = True
        # Left foot is holding
        if self.is_hold(self.l):
            # Holding down arrow
            if self.l % self.P == self.D:
                for i, p in enumerate(panels):
                    if p == self.R:
                        self.r = arrows[i]
                        self.h1 = arrows[(i + 1) % 3]
                        self.h2 = arrows[(i + 2) % 3]
                        return
                # Impossible
                self.error = True
            # Holding any other arrow
            else:
                for i, p in enumerate(panels):
                    if p == self.D:
                        self.r = arrows[i]
                        self.h1 = arrows[(i + 1) % 3]
                        self.h2 = arrows[(i + 2) % 3]
                        return
                # Impossible
                self.error = True
        # No active holds
        else:
            # Up panel is used; put a hand on it
            for i, p in enumerate(panels):
                if p == self.U:
                    self.h1 = arrows[i]
                    if (panels[(i + 1) % 3] == self.L or
                            panels[(i + 2) % 3] == self.R):
                        self.l = arrows[(i + 1) % 3]
                        self.r = arrows[(i + 2) % 3]
                    else:
                        self.l = arrows[(i + 2) % 3]
                        self.r = arrows[(i + 1) % 3]
                    return
            # Up panel is not used; put a hand on the down panel
            for i, p in enumerate(panels):
                if p == self.D:
                    self.h1 = arrows[i]
                    if (panels[(i + 1) % 3] == self.L):
                        self.l = arrows[(i + 1) % 3]
                        self.r = arrows[(i + 2) % 3]
                    else:
                        self.l = arrows[(i + 2) % 3]
                        self.r = arrows[(i + 1) % 3]
    
    def quad(self, arrow1, arrow2, arrow3, arrow4):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        panel3 = arrow3 % self.P
        panel4 = arrow4 % self.P
        arrows = (arrow1, arrow2, arrow3, arrow4)
        panels = (panel1, panel2, panel3, panel4)
        # Ensure all arrows are on different panels
        if len(panels) != len(set(panels)):
            self.log.warn("Invalid quad")
            self.error = True
            return
        # Ensure there are no active holds
        if self.is_hold(self.l) or self.is_hold(self.r):
            self.log.warn("Quad during hold")
            self.error = True
            return
        self.last_used = 'j'
        # Always put feet on the LR panels and hands on the UD panels
        for i, p in enumerate(panels):
            if p == self.L:
                self.l = arrows[i]
            elif p == self.R:
                self.r = arrows[i]
            elif p == self.U:
                self.h1 = arrows[i]
            else:
                self.h2 = arrows[i]
    
    def state(self, readable=False):
        l = r = ''
        # Left tail
        if self.is_tail(self.l):
            l = 'tail'
            self.l %= self.P
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
        # Right tail
        elif self.is_tail(self.r):
            r = 'tail'
            self.r %= self.P
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
        if readable:
            return '%s %s' % (self.STATES[l], self.STATES[r])
        return ResynthesisState(self, l, r)
    
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
        elif row.count('0') == self.P - 2 and '3' not in row:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            self.jump(*arrows)
        # Tail and one or two taps / other tails
        elif (row.count('0') in (self.P - 2, self.P - 3) and
                '3' in row):
            arrows = []
            for i, col in enumerate(row):
                if col == '3':
                    self.tail(i)
                elif col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            if len(arrows) == 1:
                self.tap(arrows[0], False)
            elif len(arrows) == 2:
                self.jump(arrows[0], arrows[1], False)
        # Triple stomp
        elif row.count('0') == self.P - 3:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            self.triplet(*arrows)
        # Quad stomp
        elif row.count('0') == self.P - 4:
            self.quad(*[i + self.P * (int(c) - 1) for i, c in enumerate(row)])
        else:
            raise ResynthesisError()
        return self.state()


class TechnoSingle8(GameType):
    # Constants
    LD, L, LU, D, U, RU, R, RD = xrange(8)
    LS = (LD, L, LU)
    RS = (RD, R, RU)
    UD = (U, D)
    P = 8
    # Attributes
    l = L
    r = R
    
    def tap(self, arrow, reset=True):
        if reset:
            self.reset_attrs()
        panel = arrow % self.P
        # Hands
        if self.is_hold(self.r) and self.is_hold(self.l):
            # Three holds and a tap
            if self.is_hold(self.h1):
                self.h2 = arrow
            # Two holds and a tap
            else:
                self.h1 = arrow
            last_used = 'h'
        # TODO: lots of repeated code here, but reducing repetition would also
        #       reduce readability... sigh
        # Last used left foot
        elif self.last_used == 'l':
            # One-footing or jack
            if self.is_hold(self.r) or self.l == panel:
                self.l = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif (panel in self.LS and self.l not in self.LS or
                  panel in self.UD and self.l in self.RS):
                if self.is_hold(self.l):
                    self.r = arrow
                    self.last_used = 'r'
                else:
                    self.log.info("Double step")
                    self.l = arrow
            # Alternating feet
            else:
                # Drill
                if self.r == panel:
                    self.drill = True
                self.r = arrow
                self.last_used = 'r'
        # Last used right foot
        elif self.last_used == 'r':
            # One-footing or jack
            if self.is_hold(self.l) or self.r == panel:
                self.r = arrow
                self.jack = True
            # Crossover or double-step (always assume double-step)
            elif (panel in self.RS and self.r not in self.RS or
                  panel in self.UD and self.r in self.LS):
                if self.is_hold(self.r):
                    self.l = arrow
                    self.last_used = 'l'
                else:
                    self.log.info("Double step")
                    self.r = arrow
            # Alternating feet
            else:
                # Drill
                if self.l == panel:
                    self.drill = True
                self.l = arrow
                self.last_used = 'l'
        # Last used both (jump)
        elif self.last_used == 'j':
            # One hold
            if self.is_hold(self.l):
                self.r = arrow
                self.last_used = 'r'
            elif self.is_hold(self.r):
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
                self.log.info("Semi-ambiguous tap")
                self.l = arrow
                self.last_used = 'l'
                self.ambiguous = True
            elif (self.r in self.RS and self.l == self.U and panel == self.D or
                  self.r in self.RS and self.l == self.D and panel == self.U):
                self.log.info("Semi-ambiguous tap")
                self.r = arrow
                self.last_used = 'r'
                self.ambiguous = True
            # Completely ambiguous (e.g. LR jump followed by U/D tap)
            else:
                self.log.info("Ambiguous tap")
                self.ambiguous = True
                # Arbitrary values
                self.l = arrow
                self.last_used = 'l'
    
    def hold(self, arrow):
        if (self.is_hold(self.l) and self.l % self.P == arrow or
                self.is_hold(self.r) and self.r % self.P == arrow):
            self.log.warn("Double hold")
            self.error = True
            return
        self.tap(arrow + self.P)
    
    def roll(self, arrow):
        self.tap(arrow + self.P * 3)
    
    def tail(self, arrow):
        #self.reset_attrs()
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
            self.error = True
    
    def jump(self, arrow1, arrow2):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        # Hands (probably actually bracketing but oh well)
        if self.is_hold(self.r) or self.is_hold(self.l):
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
            self.log.info("Ambiguous jump")
            self.ambiguous = True
            # Arbitrary values
            self.l = arrow1
            self.r = arrow2
        self.last_used = 'j'
    
    def triplet(self, arrow1, arrow2, arrow3):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        panel3 = arrow3 % self.P
        arrows = (arrow1, arrow2, arrow3)
        panels = (panel1, panel2, panel3)
        if len(panels) != len(set(panels)):
            self.log.warn("Invalid triplet")
            self.error = True
            return
        # Right foot is holding
        if self.is_hold(self.r):
            # shit lets be lazy
            self.l = arrow1
            self.h1 = arrow2
            self.h2 = arrow3
        # Left foot is holding
        if self.is_hold(self.l):
            self.r = arrow1
            self.h1 = arrow2
            self.h2 = arrow3
        # No active holds
        else:
            self.l = arrow1
            self.r = arrow2
            self.h1 = arrow3
        self.last_used = 'j'
    
    def quad(self, arrow1, arrow2, arrow3, arrow4):
        self.reset_attrs()
        panel1 = arrow1 % self.P
        panel2 = arrow2 % self.P
        panel3 = arrow3 % self.P
        panel4 = arrow4 % self.P
        arrows = (arrow1, arrow2, arrow3, arrow4)
        panels = (panel1, panel2, panel3, panel4)
        # Ensure all arrows are on different panels
        if len(panels) != len(set(panels)):
            self.log.warn("Invalid quad")
            self.error = True
            return
        # Ensure there are no active holds
        if self.is_hold(self.l) or self.is_hold(self.r):
            self.log.warn("Quad during hold")
            self.error = True
            return
        # laaaaazy
        self.l = arrow1
        self.r = arrow2
        self.h1 = arrow3
        self.h2 = arrow4
        self.last_used = 'j'
    
    def state(self, readable=False):
        l = r = ''
        # Left tail
        if self.is_tail(self.l):
            l = 'tail'
            self.l %= self.P
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
        # Right tail
        elif self.is_tail(self.r):
            r = 'tail'
            self.r %= self.P
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
        if readable:
            return '%s %s' % (self.STATES[l], self.STATES[r])
        return ResynthesisState(self, l, r)
        
    def parse_row(self, row):
        # No taps
        if set(row) == set('0'):
            return
        # Single tap, hold, roll, or tail
        if row.count('0') == self.P - 1:
            if '1' in row:
                self.tap(row.find('1'))
            elif '2' in row:
                self.hold(row.find('2'))
            elif '3' in row:
                self.tail(row.find('3'))
            elif '4' in row:
                self.roll(row.find('4'))
        # Jump with no tails
        elif row.count('0') == self.P - 2 and '3' not in row:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            self.jump(*arrows)
        # Tail and one or two taps / other tails
        elif (row.count('0') in (self.P - 2, self.P - 3) and
                '3' in row):
            arrows = []
            for i, col in enumerate(row):
                if col == '3':
                    self.tail(i)
                elif col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            if len(arrows) == 1:
                self.tap(arrows[0], False)
            elif len(arrows) == 2:
                self.jump(arrows[0], arrows[1], False)
        # Triple stomp
        elif row.count('0') == self.P - 3:
            arrows = []
            for i, col in enumerate(row):
                if col != '0':
                    arrows.append(i + self.P * (int(col) - 1))
            self.triplet(*arrows)
        # Quad stomp
        elif row.count('0') == self.P - 4:
            self.quad(*[i + self.P * (int(c) - 1) for i, c in enumerate(row)])
        else:
            raise ResynthesisError()
        return self.state()

gametypes = {
    'dance-single': DanceSingle,
    'techno-single8': TechnoSingle8,
}
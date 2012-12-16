#!/usr/bin/env python
import itertools
import logging
import math
import os
import random
import sys

import synctools
from synctools.simfile import *
import resynthesis
from resynthesis.gametypes import *

__all__ = ['resynthesize']


def resynthesize(simfile):
    log = logging.getLogger('synctools')
    cfg = synctools.get_config()
    # Retrieve the hardest dance-single chart
    for d in ('Challenge', 'Hard', 'Medium', 'Easy', 'Beginner', 'Edit'):
        try:
            chart = simfile.get_chart(difficulty=d, stepstype='techno-single8')
            log.info('Using %s chart' % d)
            break
        except (MultiInstanceError, NoChartError):
            pass
    if not chart:
        log.error('This simfile does not have any single charts; aborting')
        return
    # Abstract the chart down to foot motions
    synth_in = TechnoSingle8()
    for m, measure in enumerate(chart['notes']):
        for r, row in enumerate(measure):
            row = row.replace('M', '0')
            try:
                state = synth_in.parse_row(row)
            except resynthesis.ResynthesisError:
                log.warn("Unsupported pattern at %s" %
                    (4 * (m + float(r) / len(measure))))
                continue
            if not state:
                continue
            log.debug('%s %s %s %s %s' % (state, synth_in.l, synth_in.r,
                synth_in.last_used, synth_in.jack))
            # Now let's make magic happen.
            
            
            
            # Except magic is hard.


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(resynthesize, sys.argv[1:])
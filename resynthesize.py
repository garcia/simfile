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


def synthesize_row(synth_in, synth_out, row, pos, blacklist=[]):
    log = logging.getLogger('synctools')
    default = '0' * synth_out.P
    old_state = synth_out.state()
    try:
        state = synth_in.parse_row(row)
    except resynthesis.ResynthesisError:
        log.warn('Unsupported pattern at %s' % pos)
        return default
    if not state:
        return default
    log.debug('IN  ' + str(state))
    # Get all possible matching patterns
    elements = row.replace('0', '')
    if len(elements) > synth_out.P:
        log.warn('Too many arrows at %s' % pos)
        # TODO: write a quad stomp or similar at this point
        return default
    elements = elements.zfill(synth_out.P)
    options = [''.join(option) for option in
        set(itertools.permutations(elements))]
    chose = False
    while options:
        choice = options.pop(random.randint(0, len(options) - 1))
        try:
            new_state = synth_out.parse_row(choice)
        except resynthesis.ResynthesisError:
            synth_out.load_state(old_state)
            continue
        if new_state == state:
            chose = True
            log.debug('OUT ' + str(new_state))
            break
        else:
            synth_out.load_state(old_state)
    if not chose:
        log.warn('Unable to find a valid pattern for %s' % pos)
    return choice


def resynthesize(simfile):
    log = logging.getLogger('synctools')
    cfg = synctools.get_config()
    intype = cfg['resynthesize']['input']
    outtype = cfg['resynthesize']['output']
    # Retrieve the hardest dance-single chart
    for d in ('Challenge', 'Hard', 'Medium', 'Easy', 'Beginner', 'Edit'):
        try:
            chart = simfile.get_chart(difficulty=d, stepstype=intype)
            log.info('Using %s chart' % d)
            break
        except (MultiInstanceError, NoChartError):
            pass
    if not chart:
        log.error('This simfile does not have any single charts; aborting')
        return
    # Abstract the chart down to foot motions
    synth_in = gametypes[intype]()
    synth_out = gametypes[outtype](silent=True)
    old_state = synth_out.state()
    new_chart = ""
    for m, measure in enumerate(chart['notes']):
        for r, row in enumerate(measure):
            row = row.replace('M', '0')
            # TODO: rewind and blacklist if nothing was found
            new_chart += synthesize_row(synth_in, synth_out, row,
                (4 * (m + float(r) / len(measure))))
            new_chart += '\n'
        new_chart += ',\n'
    new_chart = new_chart[:-2] + ';'
    print new_chart

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(resynthesize, sys.argv[1:])
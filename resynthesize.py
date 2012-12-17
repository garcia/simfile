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
    default = ['0' * synth_out.P]
    old_state = synth_out.state()
    try:
        state = synth_in.parse_row(row)
    except resynthesis.ResynthesisError:
        log.warn('Unsupported pattern at %s' % pos)
        return default
    if not state:
        return default
    log.debug('\t' + str(state))
    # Get all possible matching patterns
    elements = row.replace('0', '')
    if len(elements) > synth_out.P:
        log.warn('Too many arrows at %s' % pos)
        return '1' * synth_out.P
    elements = elements.zfill(synth_out.P)
    options = [''.join(option) for option in
        set(itertools.permutations(elements))]
    chosen = []
    while options:
        choice = options.pop()
        try:
            new_state = synth_out.parse_row(choice)
            log.debug('\t' + str(new_state))
            if new_state != state:
                raise resynthesis.ResynthesisError()
            chosen.append(choice)
        except resynthesis.ResynthesisError:
            pass
        synth_out.load_state(old_state)
    return chosen
    

def resynthesize(simfile):
    log = logging.getLogger('synctools')
    cfg = synctools.get_config()
    synctools.backup(simfile)
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
    states = [(synth_in.state(), synth_out.state())]
    rows_in = list(itertools.chain(*chart['notes']))
    rows_out = []
    options = []    
    r = 0
    pos = -1
    while r < len(rows_in):
        row = rows_in[r]
        log.debug("Row %s\t%s" % (r, row))
        # Mines currently aren't supported; remove them
        row = row.replace('M', '0')
        # Let's make magic happen
        if r < len(options):
            opt = options.pop()
            log.debug("\tUsing %s previously parsed options" % len(opt))
        else:
            log.debug("\tSynthesizing options")
            opt = synthesize_row(synth_in, synth_out, row, pos)
        if opt:
            log.debug("\tGot %s options: %s" % (len(opt), ' '.join(opt)))
            rows_out.append(opt.pop(random.randrange(0, len(opt))))
            options.append(opt)
            synth_out.parse_row(rows_out[-1])
            states.append((synth_in.state(), synth_out.state()))
            log.debug("\tGoing with " + rows_out[-1])
            r += 1
        else:
            log.debug("\tNo options found; rewinding")
            r -= 1
            if r == -1:
                log.error("I give up")
                return
            old_states = states.pop()
            synth_in.load_state(old_states[0])
            synth_out.load_state(old_states[1])
            rows_out.pop()
        synth_in.load_state(states[-2][0])
        log.debug("Old input state: %s" % synth_in.state())
        synth_in.parse_row(row)
        log.debug("New input state: %s" % synth_in.state())
    new_chart = Notes()
    for measure in chart['notes']:
        new_measure = []
        for row in measure:
            new_measure.append(rows_out.pop(0))
        new_chart.append(new_measure)
    simfile.set_chart(new_chart, difficulty='Edit', stepstype=outtype,
                      meter=chart['meter'], description='Resynthesized',
                      radar=chart['radar'])
    simfile.save()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(resynthesize, sys.argv[1:])
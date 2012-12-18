#!/usr/bin/env python
import itertools
import logging
import math
import os
import random
import sys

import synctools
from synctools.simfile import *
import synthesis

__all__ = ['resynthesize']


def synthesize_row(synth_in, synth_out, row):
    log = logging.getLogger('synctools')
    default = ['0' * synth_out.pc]
    old_state = synth_out.state()
    try:
        state = synth_in.parse_row(row)
    except synthesis.SynthesisError:
        log.warn('Unsupported pattern')
        return default
    if not state:
        return default
    log.debug('\tSEEKING\t' + str(state))
    log.debug('\tFROM\t' + str(old_state))
    # Get all possible matching patterns
    elements = row.replace('0', '')
    if len(elements) > synth_out.pc:
        log.warn('Too many arrows')
        return '1' * synth_out.pc
    elements = elements.zfill(synth_out.pc)
    options = [''.join(option) for option in
        set(itertools.permutations(elements))]
    chosen = []
    while options:
        choice = options.pop()
        try:
            new_state = synth_out.parse_row(choice)
            log.debug('\t%s\t%s' % (choice, str(new_state)))
            if new_state != state:
                raise synthesis.SynthesisError()
            chosen.append(choice)
        except synthesis.SynthesisError:
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
        log.error('This simfile does not have any input charts; aborting')
        return
    # Preprocess measure boundaries to give better error messages
    measures = [len(m) for m in chart['notes']]
    bounds = [sum(measures[:i]) for i in xrange(len(measures))]
    last_milestone = 0
    # Abstract the chart down to foot motions
    synth_in = synthesis.Synthesizer(intype)
    synth_out = synthesis.Synthesizer(outtype, silent=True)
    states = [(synth_in.state(), synth_out.state())]
    rows_in = list(itertools.chain(*chart['notes']))
    rows_out = []
    options = []
    r = 0
    while r < len(rows_in):
        if 10 * r / len(rows_in) > last_milestone:
            last_milestone = 10 * r / len(rows_in)
            log.info('%s%% done' % (last_milestone * 10))
        row = rows_in[r]
        measure = bounds.index(reduce(lambda x, y: x if y > r else y, bounds))
        beat = (measure + float(r - bounds[measure]) / measures[measure]) * 4
        log.debug('Beat %s\t%s' % (beat, row))
        # Mines currently aren't supported; remove them
        row = row.replace('M', '0')
        # Let's make magic happen
        if r < len(options):
            opt = options.pop()
            log.debug('\tUsing %s previously synthesized options' % len(opt))
        else:
            log.debug('\tSynthesizing options')
            opt = synthesize_row(synth_in, synth_out, row)
        if opt:
            log.debug('\tGot %s options: %s' % (len(opt), ' '.join(opt)))
            rows_out.append(opt.pop(random.randrange(0, len(opt))))
            options.append(opt)
            try:
                synth_out.parse_row(rows_out[-1])
            except synthesis.SynthesisError:
                continue
            states.append((synth_in.state(), synth_out.state()))
            log.debug('\tGoing with ' + rows_out[-1])
            r += 1
        else:
            log.debug('\tNo options found; rewinding')
            r -= 1
            if r == -1:
                log.error('I give up')
                return
            old_states = states.pop()
            synth_in.load_state(old_states[0])
            synth_out.load_state(old_states[1])
            rows_out.pop()
            log.debug('Input state~ %s' % synth_in.state())
            continue
        synth_in.load_state(states[-1][0])
        log.debug('Input state: %s' % synth_in.state())
    new_chart = Notes()
    for measure in chart['notes']:
        new_measure = []
        for row in measure:
            new_measure.append(rows_out.pop(0))
        new_chart.append(new_measure)
    difficulty = 'Challenge'
    if intype == outtype:
        difficulty = 'Edit'
    simfile.set_chart(new_chart, difficulty=difficulty, stepstype=outtype,
                      meter=chart['meter'], description='Resynthesized',
                      radar=chart['radar'])
    simfile.save()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(resynthesize, sys.argv[1:])
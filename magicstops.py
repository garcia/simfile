#!/usr/bin/env python
import logging
import math
import os
import random
import shutil
import sys
import traceback
import wave

from hsaudiotag import ogg, mpeg

from utils.synctools import *
from utils.simfile import *


# TODO: separate these functions and variables
unround_values = {
    # thirds
    333: 1. / 3,
    667: 2. / 3,
    # sixths
    167: 1. / 6,
    833: 5. / 6,
    # twelfths
     83: 1. / 12,
    417: 5. / 12,
    583: 7. / 12,
    917: 11. / 12,
    # sixteenths
     63: 1. / 16,
    188: 3. / 16,
    313: 5. / 16,
    438: 7. / 16,
    563: 9. / 16,
    688: 11. / 16,
    813: 13. / 16,
    938: 15. / 16
}


def unround(number):
    global unround_values
    n = [int(part) for part in number.split('.')]
    if n[1] in unround_values:
        return n[0] + unround_values[n[1]]
    else:
        return float(number)


def parse_timing_data(data):
    output = dict()
    if not data.strip(): return output
    for pair in [line.strip().split('=') for line in data.strip().split(',')]:
        output[unround(pair[0])] = float(pair[1])
    return output


def main():
    global cfg, log
    for simfile in find_simfiles(sys.argv[1:],
                                 cfg['synctools']['extensions'],
                                 unique=True):
        log.warning('Processing ' + simfile)
        # TODO: separate this
        # Create a backup of the file
        if cfg['synctools']['backup']:
            shutil.copy2(simfile, simfile + '.' + 
                         cfg['synctools']['backup_extension'])
        subdir = os.path.dirname(simfile)
        sf = Simfile(simfile)
        # Retrieve the needed data
        bpms = sf.get('BPMS')[1]
        stops = sf.get('STOPS')[1]
        # Process BPM data
        bpms = parse_timing_data(bpms)
        stops = parse_timing_data(stops)
        # Fix stop values
        # 'residue' contains the number of seconds by which the chart is early
        drift = 0
        residue = 0.0
        new_stops = []
        while stops:
            stop_start = min(stops.iterkeys())
            stop_value = stops.pop(stop_start)
            # Get current BPM
            bpm_start = 0.0
            for bpm_s, bpm_v in bpms.iteritems():
                if bpm_s > bpm_start and bpm_s <= stop_start:
                    bpm_start = bpm_s
            bpm_value = bpms[bpm_start]
            # Really big BPM values should be decreased until they're reasonable
            while bpm_value > 625:
                bpm_value /= 2
            # Determine real stop value
            stop_real = stop_192nd = 60 / bpm_value / 48
            corrected_stop = False
            while stop_real <= stop_value + cfg['magicstops']['margin']:
                # Found a good approximation yet?
                if stop_real >= stop_value - cfg['magicstops']['margin']:
                    log.debug('Real value of stop at %s is %s' % (stop_start, stop_real))
                    residue += stop_value - stop_real
                    log.debug('Current residue is %s' % residue)
                    # Chart is more than half a ms early
                    if residue > .0005:
                        log.debug('Chart is now early; decreasing stop value')
                        residue -= .001
                        stop_value -= .001
                        drift -= 1
                    # Chart is at least half a ms late
                    elif residue <= -.0005:
                        log.debug('Chart is now late; increasing stop value')
                        residue += .001
                        stop_value += .001
                        drift += 1
                    corrected_stop = True
                    break
                stop_real += stop_192nd
            if not corrected_stop:
                log.warn('Could not correct stop at %s' % stop_start)
            new_stops.append((round(stop_start, 3), stop_value))
        # Reassemble stops data
        new_stops = ',\n'.join(['%s=%s' % new_stop for new_stop in new_stops])
        with codecs.open(simfile, 'w', 'utf-8') as output:
            for param in sf.params:
                if param[0].upper() == 'STOPS':
                    param[1] = new_stops
                output.write(unicode(param) + '\n')
        log.info('Corrected about %s milliseconds of drift' % abs(drift))

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    cfg = load_config()
    log = logging.getLogger('synctools')
    log.setLevel(getattr(logging, cfg["synctools"]["verbosity"]))
    log.addHandler(logging.StreamHandler())
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
    except:
        traceback.print_exc()
    if cfg['synctools']['delayed_exit']:
        sys.stdout.write('Press any key to continue...')
        getch()
        sys.stdout.write('\n')

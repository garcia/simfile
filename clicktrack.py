#!/usr/bin/env python
import logging
import math
import os
import random
import sys
import traceback
import wave

from hsaudiotag import ogg, mpeg

from utils.synctools import *
from utils.simfile import *


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


def get_hardest_chart(sf):
    for diff in ('Challenge', 'Hard', 'Medium', 'Easy', 'Beginner', 'Edit'):
        for game in ('dance', 'pump', 'ez2'):
            for sd in ('single', 'double'):
                try:
                    chart = sf.get_notes(diff, stepstype=(game + '-' + sd))
                    log.info('Using %s-%s %s chart' % (game, sd, diff))
                    return chart
                except (MultiInstanceError, NoChartError):
                    pass


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
        subdir = os.path.dirname(simfile)
        sf = Simfile(simfile)
        # Retrieve the needed data
        musicfile = sf.get('MUSIC')[1]
        bpms = sf.get('BPMS')[1]
        stops = sf.get('STOPS')[1]
        offset = float(sf.get('OFFSET')[1]) + cfg['synctools']['global_offset']
        # Retrieve the hardest chart, if possible
        chart = get_hardest_chart(sf)
        if not chart:
            log.warning('Unable to find any dance, pump, or ez2 charts')
            try:
                chart = sf.get_notes_positional(0)
                log.info('Using %s %s chart' % (chart['stepstype'],
                                              chart['difficulty']))
            except IndexError:
                log.error('This simfile does not have any charts; aborting')
                continue
        # Generate click track
        clicks = []
        for (m, measure) in enumerate(chart['notes']):
            for (l, line) in enumerate(measure):
                line_pos = 4 * (m + float(l) / len(measure))
                if any([c in '124' for c in line]) and \
                    cfg['clicktrack']['taps']:
                    clicks.append((line_pos, 'tap'))
                if any([c == 'M' for c in line]) and \
                    cfg['clicktrack']['mines']:
                    clicks.append((line_pos, 'mine'))
                if not l % (len(measure) / 4) and \
                    cfg['clicktrack']['metronome']:
                    clicks.append((line_pos, 'metronome'))
        log.debug('%s clicks loaded' % len(clicks))
        # Get the necessary metadata from the music file
        musicpath = subdir + os.sep + musicfile
        if not os.path.isfile(musicpath):
            log.error(musicfile + ': audio file not found')
            continue
        ext = os.path.splitext(musicpath)[1]
        if not ext in ('.ogg', '.mp3', '.wav'):
            log.error(musicfile + ': unknown audio format "%s"' % ext)
            continue
        elif ext in ('.ogg', '.mp3'):
            log.info('Loading audio file')
            if ext == '.ogg':
                metadata = ogg.Vorbis(musicpath)
            elif ext == '.mp3':
                metadata = mpeg.Mpeg(musicpath)
            if not metadata.valid:
                log.error(musicfile + ': unable to read file')
                continue
            sample_rate = metadata.sample_rate
            audio_length = (metadata.duration + 1) * sample_rate
        elif ext == '.wav':
            metadata = wave.open(musicpath)
            sample_rate = metadata.getframerate()
            audio_length = metadata.getnframes()
            samples = audio_length
        log.debug("%s fps, ~%s samples long" % (sample_rate, audio_length))
        # Process BPM data
        bpms = parse_timing_data(bpms)
        bpms[len(chart['notes']) * 4] = bpms[max(bpms.keys())]
        stops = parse_timing_data(stops)
        beats = [(offset * -sample_rate, 'first_beat')] # first beat
        # residue: samples between beat and end of bpm change
        residue = 0
        # cursor: the location of the beat or BPM change prior to current_click
        cursor = 0
        current_click, click_type = clicks.pop(0) # the next beat to locate
        while len(bpms) > 1:
            bpm_start = min(bpms.keys())
            bpm_value = bpms.pop(min(bpms.keys()))
            bpm_end = min(bpms.keys())
            beat_length = 60. / bpm_value * sample_rate
            while current_click <= bpm_end:
                # add stop value(s) to residue
                while len(stops) and min(stops.keys()) < current_click:
                    residue += stops.pop(min(stops.keys())) * sample_rate
                beats.append((beats[-1][0] + beat_length * 
                             (current_click - cursor) + 
                             residue, click_type))
                cursor = current_click
                try:
                    current_click, click_type = clicks.pop(0)
                except:
                    break
                residue = 0
            # residue will remain 0 if bpm_end is on a whole beat
            residue += (bpm_end - cursor) * beat_length
            cursor = bpm_end
        # Generate some sounds
        amp = cfg['clicktrack']['amplitude']
        sound = {
            'metronome': ''.join([
                chr(int(random.randrange(256) * a + 127 * (1 - a)))
                for a in [amp * b / 1024. for b in xrange(1024, 0, -1)]
            ]),
            'tap': ''.join([
                chr(int((math.sin(b / 4.) * 127 + 127) * a + 127 * (1 - a)))
                for a, b in [(amp * b / 1024., b) for b in xrange(1024, 0, -1)]
            ]),
            'mine': ''.join([
                chr(int((int(b / 128) % 2) * 255 * a + 127 * (1 - a)))
                for a, b in [(amp * b / 1024., b) for b in xrange(1024, 0, -1)]
            ]),
        }
        # Write click track to memory buffer
        log.info('Generating click track')
        clicks = bytearray('\x80' * audio_length)
        for i, (click, click_type) in enumerate(beats):
            click = int(click)
            # Too early
            if click < 0:
                continue
            # Too late
            if click + 1024 > audio_length:
                break
            if click_type == 'first_beat':
                if not cfg['clicktrack']['first_beat']:
                    continue
                click_type = 'metronome'
            clicks[int(click):int(click) + 1024] = sound[click_type]
        # Write to WAV
        log.info('Writing WAV file')
        clicks_h = wave.open(subdir + os.sep + 'clicktrack.wav', 'w')
        clicks_h.setnchannels(1)
        clicks_h.setsampwidth(1)
        clicks_h.setframerate(sample_rate)
        clicks_h.writeframes(str(clicks))
        clicks_h.close()
        log.info('Done.')
    # Wait for user input
    if cfg['synctools']['delayed_exit']:
        while True:
            sys.stdout.write('Press R to rerun, ' +
                             'P to reload preferences and rerun, ' +
                             'or Q to quit')
            c = getch()
            sys.stdout.write('\r\n')
            if c.upper() == 'R':
                main()
            elif c.upper() == 'P':
                cfg = load_config()
                main()
            elif c in '\x03Qq':
                raise KeyboardInterrupt
            


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

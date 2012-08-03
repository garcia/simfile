#!/usr/bin/env python
import logging
import os
import shutil
import sys
import traceback
from decimal import *

from utils.synctools import *
from utils.simfile import *

def main():
    global cfg
    for simfile in find_simfiles(sys.argv[1:], cfg['synctools']['extensions']):
        log.info('processing ' + simfile)
        # Create a backup of the file
        if cfg['synctools']['backup']:
            shutil.copy2(simfile, simfile + '.' + 
                         cfg['synctools']['backup_extension'])
        sf = Simfile(simfile)
        with codecs.open(simfile, 'w', 'utf-8') as output:
            for param in sf.params:
                if param[0].upper() == 'OFFSET':
                    # Process offset
                    offset = Decimal(param[1])
                    offset2 = offset + Decimal(cfg['adjustoffset']['amount'])
                    log.info('%s -> %s' % (str(offset), str(offset2)))
                    # Rewrite parameter
                    param[1] = str(offset2)
                output.write(unicode(param) + '\n')

if __name__ == '__main__':
    # TODO: this should be shared among all the tools
    # Maybe have a class with this in its __init__?
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

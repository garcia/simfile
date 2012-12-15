#!/usr/bin/env python
import codecs
import logging
import os
import sys
from decimal import *

import synctools

__all__ = ['adjustoffset']

def adjustoffset(simfile):
    log = logging.getLogger('synctools')
    cfg = synctools.get_config()
    synctools.backup(simfile)
    with codecs.open(simfile.filename, 'w', 'utf-8') as output:
        for param in simfile.params:
            if param[0].upper() == 'OFFSET':
                # Process offset
                offset = Decimal(param[1])
                offset2 = offset + Decimal(cfg['adjustoffset']['amount'])
                log.info('%s -> %s' % (str(offset), str(offset2)))
                # Rewrite parameter
                param[1] = str(offset2)
            output.write(unicode(param) + '\n')


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(adjustoffset, sys.argv[1:])
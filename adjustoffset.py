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
    offset_param = simfile.get('OFFSET')
    # Process offset
    offset = Decimal(offset_param[1])
    offset2 = offset + Decimal(cfg['adjustoffset']['amount'])
    log.info('%s -> %s' % (str(offset), str(offset2)))
    # Rewrite parameter
    offset_param[1] = str(offset2)
    simfile.save()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(adjustoffset, sys.argv[1:])
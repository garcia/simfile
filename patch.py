#!/usr/bin/env python
import logging
import os
import shutil
import struct
import sys
import synctools
import zlib

__all__ = ['patch']

# Taken from mutagen/_util.py
bitswap = ''.join([chr(sum([((val >> i) & 1) << (7-i) for i in range(8)]))
    for val in range(256)])

def patch(simfile):
    log = logging.getLogger('synctools')
    cfg = synctools.get_config()
    patchedlength = cfg['patch']['patched_length']
    
    # Get audio path
    audiopath = os.path.join(simfile.dirname, simfile.get_string('MUSIC'))
    if not audiopath.lower().endswith('.ogg'):
        log.error('Only OGG is supported')
        return
    
    # Backup audio
    if cfg['patch']['backup']:
        shutil.copy2(audiopath, audiopath + '.' + 
                     cfg['synctools']['backup_extension'])
    
    # Get audio data
    with open(audiopath, 'rb') as audiofile:
        audiodata = audiofile.read()
    
    # Find last page by the 4-byte header + version 0 + last page indicator
    lpindex = audiodata.rfind('OggS\x00\x05')
    lp2index = audiodata.rfind('OggS\x00')
    if lpindex == -1:
        log.error('Unable to find last OGG page')
        return
    if lpindex != lp2index:
        log.error('There is something very wrong with this OGG')
        return
    lp = audiodata[lpindex:]
    
    # TODO: don't assume 44.1kHz below
    # Get original length & insert new length
    oldlength = struct.unpack('<q', lp[6:14])[0]
    oldlength /= 44100.
    lp = lp[:6] + struct.pack('<q', patchedlength * 44100) + lp[14:]
    
    # Insert new CRC sum
    # Note: Python computes CRC backwards relative to OGG
    crc = (~zlib.crc32((lp[:22] + '\x00' * 4 + lp[26:]).translate(bitswap), 
        -1)) & 0xffffffff
    lp = (lp[:22] + struct.pack('>I', crc).translate(bitswap) + lp[26:])
    
    # Write new audio file
    with open(audiopath, 'wb') as audiofile:
        audiofile.write(audiodata[:lpindex])
        audiofile.write(lp)
    log.info('Patched audio length from %s seconds to %s seconds' %
        (oldlength, patchedlength))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    synctools.main_iterator(patch, sys.argv[1:])
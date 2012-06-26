import os
from glob import *
from ConfigParser import SafeConfigParser

config_structure = {
    'synctools': {
        'verbosity': str,
        'global_offset': float,
        'delayed_exit': bool,
        'extensions': str,
    },
    'clicktrack': {
        'metronome': bool,
        'first_beat': bool,
        'taps': bool,
        'mines': bool,
        'amplitude': float,
    },
    'adjustoffset': {
        'backup': bool,
        'amount': str,
    }
}


def load_config():
    """Fetches preferences.ini as a nested dictionary.
    
    The top-level dictionary maps sections and the second-level dictionaries
    map the options for the respective section.
    
    """
    global config_structure
    config = SafeConfigParser()
    config.read('preferences.ini')
    cfg = {'synctools': {}}
    for section, options in config_structure.iteritems():
        cfg[section] = {}
        for option, option_type in options.iteritems():
            if option_type is bool:
                cfg[section][option] = config.getboolean(section, option)
            elif option_type is float:
                cfg[section][option] = config.getfloat(section, option)
            elif option_type is int:
                cfg[section][option] = config.getint(section, option)
            else:
                cfg[section][option] = config.get(section, option)
    # Special cases for certain options
    if not 0 <= cfg['clicktrack']['amplitude'] <= 1:
        raise ValueError('Error: amplitude must be between [0, 1]')
    cfg['synctools']['extensions'] = [ext.strip() for ext in
        cfg['synctools']['extensions'].split(',')]
    return cfg


def find_simfiles(paths, extensions, unique=False):
    """Recursively get all the valid simfile paths under the given paths.
    
    A simfile is only valid if the file ends in one of the given simfile
    extensions (which are defined in the preferences file) and if there
    are no other files ending in that extension in the directory. A
    directory containing two .sm files is not valid, but one containing a
    .sm and .ssc file is valid and both files will be loaded separately.
    (That is, assuming .sm and .ssc are both defined as valid extensions
    in the preferences file.)
    
    The function performs a recursive search of the specified directories,
    so any folder containing simfiles will work, whether it be a single
    song folder, a song pack, or an entire /Songs/ folder containing
    multiple packs.
    
    """
    simfiles = []
    for path in paths:
        for ext in extensions:
            simfiles_in_cwd = glob(os.path.join(path, '*.' + ext))
            # No simfiles in current directory
            if len(simfiles_in_cwd) == 0:
                for subdir in iglob(os.path.join(path, '*')):
                    simfiles.extend(find_simfiles([subdir], [ext]))
            # Multiple simfiles in current directory
            elif len(simfiles_in_cwd) > 1:
                print '%s has multiple simfiles; skipping' % path
            # Exactly one simfile in current directory
            else:
                simfiles.extend(simfiles_in_cwd)
    return simfiles


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
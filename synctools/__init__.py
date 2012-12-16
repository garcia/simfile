from ConfigParser import SafeConfigParser
from glob import *
import logging
import os
import shutil
import sys
import traceback

from simfile import Simfile
from utils import getch

__all__ = ['get_config', 'find_simfiles', 'backup', 'main_iterator']

class GetConfig(object):

	config_structure = {
		'synctools': {
			'verbosity': str,
			'global_offset': float,
			'delayed_exit': bool,
			'extensions': str,
			'backup': bool,
			'backup_extension': str,
		},
		'clicktrack': {
			'metronome': bool,
			'first_beat': bool,
			'taps': bool,
			'mines': bool,
			'amplitude': float,
		},
		'adjustoffset': {
			'amount': str,
		},
		'formatter': {
			'in_file': str,
			'out_file': str,
		},
		'magicstops': {
			'margin': float,
		},
		'rename': {
			'keep_other_files': bool,
            'directory': str,
            'simfile': str,
            'music': str,
            'background': str,
            'banner': str,
            'cdtitle': str,
            'lyricspath': str,
		},
        'resynthesize': {
            'input': str,
            'output': str,
        },
	}

	_config = None

	def get_config(self, reload=False):
		# If we've already parsed the configuration file, return it
		if (not reload and self._config):
			return self._config
		# Otherwise, get to parsing
		parser = SafeConfigParser()
		parser.read('preferences.ini')
		config = {'synctools': {}}
		for section, options in self.config_structure.iteritems():
			config[section] = {}
			for option, option_type in options.iteritems():
				if option_type is bool:
					config[section][option] = parser.getboolean(section, option)
				elif option_type is float:
					config[section][option] = parser.getfloat(section, option)
				elif option_type is int:
					config[section][option] = parser.getint(section, option)
				else:
					config[section][option] = parser.get(section, option)
		# Special cases for certain options
		if not 0 <= config['clicktrack']['amplitude'] <= 1:
			raise ValueError('Error: amplitude must be between [0, 1]')
		config['synctools']['extensions'] = [ext.strip() for ext in
			config['synctools']['extensions'].split(',')]
		self._config = config
		return config

_get_config = GetConfig()

def get_config(*args, **kwargs):
    """Fetches preferences.ini as a nested dictionary.
    
    The top-level dictionary maps sections and the second-level dictionaries
    map the options for the respective section.
    
    """
    return _get_config.get_config(*args, **kwargs)


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
        # glob tries to parse square braces and that's not what we want
        glob_safe_path = path.replace('[', '[[]')
        for ext in extensions:
            simfiles_in_cwd = glob(os.path.join(glob_safe_path, '*.' + ext))
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


def backup(simfile):
    """Backup the given simfile.
    
    This function does nothing if backups are turned off in the configuration
    file. Otherwise, it copies the .sm to a file in the same directory with the
    extension given in backup_extension.
    
    """
    cfg = get_config()
    if cfg['synctools']['backup']:
        shutil.copy2(simfile.filename, simfile.filename + '.' + 
                     cfg['synctools']['backup_extension'])


def main_iterator(callback, paths, rerunnable=False, recursed=False):
    """Call a function for each simfile found in the given paths.
    
    The callback is called multiple times with a Simfile as the sole
    argument. Its return value is ignored. If delayed_exit is turned on in
    the configuration file and rerunnable is True, the user will be given
    the option to rerun the script after completion. Otherwise the script
    will simply say "Press any key to continue..." if delayed_exit is
    enabled.
    
    """
    cfg = get_config()
    log = logging.getLogger('synctools')
    if not recursed:
        log.setLevel(getattr(logging, cfg["synctools"]["verbosity"]))
        log.addHandler(logging.StreamHandler())
    try:
        for simfile in find_simfiles(paths, cfg['synctools']['extensions']):
            log.info('processing ' + simfile)
            callback(Simfile(simfile))
    except Exception:
        traceback.print_exc()
    except:
        sys.exit()
    if cfg['synctools']['delayed_exit']:
        if rerunnable:
            while True:
                sys.stdout.write('Press R to rerun, ' +
                                 'P to reload preferences and rerun, ' +
                                 'or Q to quit')
                c = getch()
                sys.stdout.write(os.linesep)
                if c.upper() == 'R':
                    main_iterator(callback, paths, rerunnable, True)
                elif c.upper() == 'P':
                    get_config(True)
                    main_iterator(callback, paths, rerunnable, True)
                elif c in '\x03Qq':
                    sys.exit()
        else:
            sys.stdout.write('Press any key to continue...')
            getch()
            sys.stdout.write(os.linesep)
"""
This script is used to change the config file of the Virtuoso Universal Server.

Usage:
  update_config.py -h|-v
  update_config.py [-d] [-c CFG_FILE] PARAMS...

Arguments:
  PARAMS...                 Set parameter(s) using the format:
                              'sec:opt=val sec:opt=val...'

Options:
  -h, --help                Show the usage message.
  -v, --version             Show software version.
  -d, --dry-run             Show what would be done but don't exexute anything.
  -c, --config CFG_FILE     Config file path [default: ./virtuoso.ini].

"""

import os
import sys
import re
import logging
import six
from docopt import docopt

if six.PY2:
    from ConfigParser import SafeConfigParser
else:
    from configparser import SafeConfigParser

__author__ = 'Arnold Kuzniar'
__version__ = '0.1.0'
__status__ = 'alpha'
__license__ = 'Apache License, Version 2.0'


class VirtuosoConfigParser(SafeConfigParser):
    def __init__(self):
        SafeConfigParser.__init__(self)
        
    def setParams(self, params):
        for par in params:
            match = re.search("^(\w+):(\w+)=(\S+)", par)
            if not match:
                raise IOError("Incorrect input format: '{0}'".format(par))
            section, option, value = match.groups()
            if self.has_option(section, option) is False:
                raise IOError("Unsupported config section or option: '{0}:{1}'"
                              .format(section, option))
            if self.get(section, option) == value:
                return False
            else:
                self.set(section, option, value)
                return True

    def __str__(self):
        conf = ''
        for section in self.sections():
            conf += section + "\n"
            for option, value in self.items(section):
                conf += "\t{0}: {1}\n".format(option, value)
        return conf


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    sys.tracebacklimit = 0
    params = args['PARAMS']
    log_file = os.path.splitext(os.path.basename(__file__))[0] + '.log'
    cfg_file = args['--config']
    dry_run = args['--dry-run']
    
    if os.path.exists(cfg_file) is False:
        raise IOError("Config file '{0}' not found.".format(cfg_file))

    cfg = VirtuosoConfigParser()
    cfg.optionxform = str  # set case-sensitivity
    cfg.read(cfg_file)
    flag = cfg.setParams(params)
    
    # write log file of config changes
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        level=logging.INFO,
        format='[%(asctime)s]\t%(pathname)s:%(lineno)d\t%(levelname)s\t%(message)s')
    logging.info("InputParams: %s\n", ' '.join(params))

    # backup the original config & write a modified config
    if dry_run is True:
        print(cfg)
    else:
        if flag is True:
            os.rename(cfg_file, cfg_file + '.bck')
        with open(cfg_file, 'w') as fp:
            cfg.write(fp)

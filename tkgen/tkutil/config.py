# -*- coding: utf-8 -*-
"""
tkutil/config

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import ConfigParser
from misc import MyDict
from console import cprint

class Config(object):
    """
    Config accessor.
    You can access with object-like format.
    Normal dictionary access is also available to some extent.
        ex.) Yes: config.section_name.option_name
             Yes: config.section_name['option_name']
              No: config['section_name']['option_name']
    """

    def __init__(self, config_path):
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(config_path)
        self.values = self._getmap(self.config)

    def _getmap(self, config):
        mapped = MyDict()
        for section in self.config.sections():
            mapped[section] = MyDict()
            for option in self.config.options(section):
                mapped[section][option] = self.config.get(section, option)
        return mapped

    def __getattr__(self, section):
        if section not in self.values:
            raise AttributeError('No such config section: %s' % section)
        return self.values[section]

    def describe(self):
        """dump all config values"""
        print ('-' * 40)
        for section in self.config.sections():
            cprint("<green:%s:/>" % (section))
            for option in self.config.options(section):
                print (' ' * 3), ("%s:" % option), self.config.get(section, option)
        print ('-' * 40)

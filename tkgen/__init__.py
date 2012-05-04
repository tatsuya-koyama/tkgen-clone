# -*- coding: utf-8 -*-
"""
tkGen - Tatsuya Koyama's style document generator

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

version = "0.1"

import sys
import replacer
from optparse import OptionParser

def main(argv=sys.argv, config_path='tkgen.cfg'):
    opt_parser = OptionParser()
    opt_parser.add_option('-a', '--all', action='store_true', default=False,
                          dest='all',
                          help="process all source files regardless of whether it is updated")
    opts, args = opt_parser.parse_args()

    return replacer.main(opts=opts, config_path=config_path)

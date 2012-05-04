#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tkGen - Tatsuya Koyama's style document generator

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import sys

if __name__ == '__main__':
    from tkgen import main
    sys.exit(main(argv = sys.argv, config_path='tkgen.cfg'))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import re
from tkgen.tkutil.file import get_all_files
from tkgen.tkutil.console import cprint

def doit(config):
    """
    自分が置かれている階層の深さを見て、
    html 内の $HOME を、そこがルートディレクトリになるように置き換える。

    例えば build/dir1/dir2/hoge.html 内に
    '$HOME/resource/fuga.png'    と書かれていたとしたら、
    '../../../resource/fuga.png' となるように置換する
    """

    REPLACE_TAG = '$HOME'
    for path in get_all_files(config.path.build, '*.html'):
        print ' '*4, path
        result_lines = []
        tag_count = 0
        dir_level = path.count('/')
        dest_path = '..' + ('/..' * (dir_level - 1))

        # read file
        in_file = open(path, 'r')
        try:
            for i, line in enumerate(in_file):
                tag_count += line.count(REPLACE_TAG)
                replaced_line = line.replace(REPLACE_TAG, dest_path)
                result_lines.append(replaced_line)
        finally:
            in_file.close()

        # write file
        out_file = open(path, 'w')
        try:
            out_file.writelines(result_lines)
        finally:
            out_file.close()

        if tag_count > 0:
            cprint("<green:%s %d %s/>" % (' '*8, tag_count, '$HOME replaced'))
        else:
            cprint("<red:%s *** $HOME not found ***/>" % (' '*8))

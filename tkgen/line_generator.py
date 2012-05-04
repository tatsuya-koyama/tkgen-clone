# -*- coding: utf-8 -*-
"""
tkgen/line_generator

@copyright: 2012 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import sys
import re
import codecs
from tkutil.console import cprint, dump

class LineGenerator(object):
    """
    読み込んだテキストファイルの現在行や前後行を返す
    """

    def __init__(self, src_path):
        self.lines   = self._get_lines(src_path)
        self.length  = len(self.lines)
        self.pointer = 0

    def _get_lines(self, src_path):
        in_file = codecs.open(src_path, 'r', 'utf-8')
        try:
            lines = in_file.readlines()  # store all lines of file into a list
        finally:
            in_file.close()

        ignore_comment_lines = [line.rstrip() for line in lines if not self._is_comment(line)]
        lf_concat_lines = self._get_lf_concat_lines(ignore_comment_lines)
        return lf_concat_lines

    def _get_lf_concat_lines(self, all_lines, linefeed_code=r'\\'):
        """
        行末に途中改行を示す文字（デフォルトはバックスペース）がある行を次の行と連結する
        （このとき、次の行の先頭の空白は捨てられる）
        """
        result = []
        line_buf = ''
        is_continuing = False
        for line in all_lines:
            if is_continuing:
                line = re.search('^\s*(.*)$', line).group(1)  # ignore leading white space

            if re.search((linefeed_code + '$'), line):
                is_continuing = True
                line_buf += re.search(('^(.*)' + linefeed_code + '$'), line).group(1)
            else:
                is_continuing = False
                line_buf += line
                result.append(line_buf)
                line_buf = ''
        return result

    def _is_comment(self, line):
        return re.search('^\s*//.*', line)

    def is_end(self):
        return (self.pointer >= self.length)

    def proceed(self):
        if not self.is_end():
            self.pointer += 1

    def get_line_number(self):
        return self.pointer

    def get_current_line(self):
        if (self.pointer >= self.length):
            return ''
        return self.lines[self.pointer]

    def get_prev_line(self):
        if self.pointer == 0:
            return ''
        return self.lines[self.pointer - 1]

    def get_next_line(self):
        if (self.pointer + 1 >= self.length):
            return ''
        return self.lines[self.pointer + 1]

    def proceed_and_get_line(self):
        self.proceed()
        return self.get_current_line()


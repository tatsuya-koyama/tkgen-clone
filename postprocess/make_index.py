#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import re
from tkgen.tkutil.file import get_all_files
from tkgen.tkutil.console import cprint

def doit(config):
    """
    ページ内の h タグをさらってインデックスをつくり、
    タグの位置に挿入する。
    また、ディレクトリ位置を観てページのパンくずリストも挿入する。
    タグが見つからなければ何もしない
    """

    BREADCRUMBS_TAG = 'POST_PROCESS_BREADCRUMBS'
    INDEX_TAG       = 'POST_PROCESS_GLOBAL_INDEX'
    for path in get_all_files(config.path.build, '*.html'):
        print ' '*4, path
        result_lines = []
        head_items   = []
        insert_line_num      = None
        breadcrumbs_line_num = None

        # read file
        in_file = open(path, 'r')
        try:
            for i, line in enumerate(in_file):
                result_lines.append(line)
                if insert_line_num == None and re.search(INDEX_TAG, line):
                    insert_line_num = i
                if breadcrumbs_line_num == None and re.search(BREADCRUMBS_TAG, line):
                    breadcrumbs_line_num = i

                header_pattern = '<h(\d)(.*)>(.*)</h\d>'
                if re.search(header_pattern, line):
                    groups = re.search(header_pattern, line).groups()
                    header_level = groups[0]
                    header_class = groups[1]
                    header_title = groups[2]
                    head_items.append((i, header_level, header_class, header_title))
        finally:
            in_file.close()
        if insert_line_num == None:
            cprint("<red:%s *** not found ***/>" % (' '*8))
            continue

        # make breadcrubms list and insert it
        breadcrumbs_lines = get_breadcumbs(path)
        result_lines[breadcrumbs_line_num] = breadcrumbs_lines

        # make index and insert it
        index_lines = '<ul class="global_index">\n'
        for i, head in enumerate(head_items):
            (line_num, lv, class_name, title) = head
            numbering = i + 1
            # insert anchor
            result_lines[line_num] = re.sub(
                '<h\d.*/h\d>',
                '<h%s%s id="head%d">%s</h%s>' % (lv, class_name, numbering, title, lv),
                result_lines[line_num]
            )

            # generate link
            index_lines += '    <li class="level%s" id="li_index%s"><a href="#head%d">%s</a></li>\n' \
                % (lv, numbering, numbering, title)
        index_lines += '</ul>'
        result_lines[insert_line_num] = index_lines

        # write file
        out_file = open(path, 'w')
        try:
            out_file.writelines(result_lines)
        finally:
            out_file.close()

        cprint("<green:%s %d %s/>" % (' '*8, len(head_items), 'headers found'))


def get_breadcumbs(path):
    traces   = path.split('/')
    last_dir = traces[-2]
    href     = '$HOME/'
    level    = 1
    t = '<ul class="global_index">\n'
    for filename in traces:
        link_name = filename if filename != 'html' else 'home'
        if filename == last_dir:
            t += '    <li class="level%d current_file">%s</li>' % (level, link_name)
            break
        href += filename + '/'
        t += '    <li class="level%d"><a href="%sindex.html">%s/</a></li>' % (level, href, link_name)
        level += 1
    t += '</ul>'
    return t


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

import re
from tkgen.tkutil.file import get_all_files
from tkgen.tkutil.console import cprint

def doit(config):
    """
    ページ内に PREVIEW_[リンク先] の形式の id があれば、
    そのエレメントのマウスオーバ時に「次のページのプレビュー内容」のテキストを
    id = "PREVIEW_AREA" のエレメントに表示する。
    そのための JS のコードは FOOTER_JS_AREA の位置に埋め込まれる
    """

    PREVIEW_ID_SEARCH_PATTERN = 'id="_PREVIEW_'
    PREVIEW_ID_TAG_PATTERN    = '_PREVIEW_(.*)"'
    PREVIEW_ID_TAG_PREFIX     = '_PREVIEW_'
    PREVIEW_AREA_TAG = 'PREVIEW_AREA'
    INSERT_JS_TAG    = 'FOOTER_JS_AREA'

    for path in get_all_files(config.path.build, '*.html'):
        print ' '*4, path
        result_lines = []
        preview_ids  = []
        footer_js_line_num = 0

        # read file
        in_file = open(path, 'r')
        try:
            for i, line in enumerate(in_file):
                result_lines.append(line)
                if re.search(PREVIEW_ID_SEARCH_PATTERN, line):
                    groups = re.search(PREVIEW_ID_TAG_PATTERN, line).groups()
                    href   = groups[0]
                    preview_id = PREVIEW_ID_TAG_PREFIX + href
                    preview_ids.append({
                        'id'  : preview_id,
                        'href': href.replace('--', '/') + '.html'
                    })

                if re.search(INSERT_JS_TAG, line):
                    footer_js_line_num = i
        finally:
            in_file.close()
        if not preview_ids:
            cprint("<red:%s *** not found ***/>" % (' '*8))
            continue

        # make preview index and embed it in html as JavaScript
        js_code = '\n'
        js_code += '    if (!tk) { tk = {}; }\n'
        js_code += '    tk.PREVIEW_DATA = {};\n'
        for preview_data in preview_ids:
            preview_text = get_preview_text(path, preview_data['href'])
            js_code += '    tk.PREVIEW_DATA["%s"] = "%s";\n' % (preview_data['id'], preview_text)

        # insert event attachment code as JavaScript
        for i, preview_data in enumerate(preview_ids):
            js_code += '    $("#%s").mouseover(function() {\n' % (preview_data['id'])
            js_code += '        $("#%s").html(tk.PREVIEW_DATA["%s"]);\n' % (PREVIEW_AREA_TAG, preview_data['id'])
            #js_code += '        $("#%s").fadeIn(500);\n' % (PREVIEW_AREA_TAG);
            js_code += '        $(".auto_preview").css("margin-top", "%dem");\n' % (i * 4)
            js_code += '        $(".auto_preview").css("color", "#eee");\n'
            js_code += '        $(".auto_preview").animate(\n'
            js_code += '            {"color": "#333"}, 300\n'
            js_code += '        );\n'
            js_code += '    });\n'

        result_lines[footer_js_line_num] += js_code

        # write file
        out_file = open(path, 'w')
        try:
            out_file.writelines(result_lines)
        finally:
            out_file.close()

        cprint("<green:%s %d %s/>" % (' '*8, len(preview_ids), 'preview links found'))


def get_preview_text(path_from, href):
    result = []
    result.append('<ul class=\\"auto_preview\\">')
    groups = re.search('(.*)/', path_from).groups()
    base_path = groups[0]
    link_file_path = base_path + '/' + href

    in_file = open(link_file_path, 'r')
    try:
        # extract link text from linked file
        for line in in_file:
            link_pattern = '<a.*>(.*)</a>'
            if re.search(link_pattern, line):
                groups = re.search(link_pattern, line).groups()
                link_name = groups[0]
                result.append('<li>' + link_name + '</li>')
    finally:
        in_file.close()

    result.append('</ul>')
    return ''.join(result)

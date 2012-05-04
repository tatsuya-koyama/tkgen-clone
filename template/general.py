#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
* こう書くと
$module_name.func_name(
   【yaml 形式のデータ】
)
<<
複数行の
文字列
>>

* これが渡される
{
    CONVERTER: 【define で変換するためのオブジェクト】
    DATA     : [ yaml 形式のデータ ],
    data     : DATA への便利アクセサ
    SOURCE   : "複数行の\n文字列\n"
    SRC_PATH : (対象ソースファイルのパス)
    OUT_PATH : (出力ファイルのパス)
}

* 関数中で CONVERTER.convert(src) を呼ぶと src を
  define で定義したルールで変換できる

* DATA に渡ってきたオブジェクトは、専用アクセサインスタンス data を用いて
  プロパティ形式でキーの存在の有無を気にせずアクセスできる。

  例えば、引数名が args で
  DATA = {
      alist: [1, 2, 3]
  }
  が想定されている（が、alist が無くてもよい）とき、alist には
      args.data.alist
  でアクセスできる。キーが無かった場合には '' （空文字列）が返ってくる。
  そのため、気軽に
      for a in args.data.alist:
  などと書ける。

  root というキーは特別で、DATA の値をそのまま返す。
  DATA = [1, 2, 3]
  となっているとき、args.data.root は [1, 2, 3] を返す。
  * DATA = {'root': 123} の場合、args.data.root は {'root': 123} を返すことに注意。
"""
#-------------------------------------------------------------------------------

import os, stat, time
import re
import widget

# なんかテンプレートエンジン使えばいいんだろうけどひとまずすげー地道に書いて動かす
# string.Template 使ってもいいんだけどあんまり楽にもならないんだよなぁ

def header(args):
    t = ''
    t += '<!DOCTYPE html>\n'
    t += '<html><head>\n'
    t += u'<title>俺式4.0 :: %s</title>\n' % (args.data.title)
    t += '<meta http-equiv="content-type" content="text/html; charset=utf-8" />\n'
    t += '<meta name="copyright" content="tatsuya-koyama.com 2002-2012 All Rights Reserved" />\n'

    if not args.data.css:
        args.data.css = []
    if not args.data.js:
        args.data.js = []

    # css
    css_list = args.data.css
    css_list.append('my_style_common')
    for css_path in css_list:
        t += '<link rel="stylesheet" type="text/css" href="$HOME/css/%s.css" />\n' % css_path

    # pc / ipad
    t += """
<script type="text/javascript">
    if (navigator.userAgent.indexOf('iPad') != -1) {
        document.write('<link rel="stylesheet" type="text/css" href="$HOME/css/my_style_ipad.css">');
    } else {
        document.write('<link rel="stylesheet" type="text/css" href="$HOME/css/my_style_pc.css">');
    }
</script>

"""

    # syntax highlighter
    if args.data.syntax:
        t += '<link rel="stylesheet" type="text/css" href="$HOME/js/sh/styles/shCore.css" />\n'
        t += '<link rel="stylesheet" type="text/css" href="$HOME/js/sh/styles/shThemeKoyama.css" />\n'
    t += _add_syntax_highlighter_js(args.data.syntax)

    # jQuery
    t += '<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>\n'
    t += '<script type="text/javascript" src="$HOME/js/jquery.easing.1.3.js"></script>\n'
    t += '<script type="text/javascript" src="$HOME/js/jquery.color.js"></script>\n'

    # js
    js_list = args.data.js
    js_list.append('tk_global_index')
    js_list.append('tk_general')
    for js_path in js_list:
        t += '<script type="text/javascript" src="$HOME/js/%s.js"></script>\n' % js_path

    t += '</head><body id="contents">\n'

    # for facebook comment box
    t += widget.facebook_comment_js()

    t += '<div id="contents_outer"><div id="contents_inner">\n'

    t += _get_global_tollbar(args.SRC_PATH)
    t += '\n\n<div id="main_contents">\n';

    # Top Header
    head_title = args.data.head or args.data.title
    t += '<a class="title_head" href="$HOME/html/index.html">\n'
    t += '    <h1><img class="title_head" src="$HOME/resource/image/icon/tkstyle_trademark_s.png" />%s</h1>\n' \
        % head_title
    t += '</a>\n'

    # update time
    if not args.data.hide_update_time:
        t += update_time(args)

    return t


def footer(args):
    t = u"""
<br/><br/>
</div></div></div>
<div class="footer">
    Copyright © 2012 Tatsuya Koyama. All rights reserved.<br/>
    <p id="pageview" class="pageview"></p>
"""

    # social widgets
    t += """
    <!-- Social Like Buttons -->
    <div class="grid_container clearfix" style="display: block;">
        <div class="grid_start"></div>
        <div class="grid12"><div class="grid_inner">
            <h2 class="footer_caption">Social Buttons</h2>
        </div></div>
        <div class="grid1"><div class="grid_inner"></div></div>
        <div class="grid11"><div class="grid_inner">
"""
    t += widget.tweet_button()
    t += widget.hatebu_button(args)
    t += widget.google_plus_button()
    t += '<br/>'
    t += widget.facebook_like_button(args)
    t += widget.mixi_like_button()
    t += """
        </div></div>
    </div>
"""
    t += widget.facebook_comment_body(args)

    page_id = re.search('html/(.*).html', args.OUT_PATH).groups()[0]
    t += u"""
</div>
<script type="text/javascript">
    if (navigator.userAgent.indexOf('iPad') == -1) {
        tk.initLazyGlobalIndex();
    }
"""
    t += '    tk.countPageView("%s");' % page_id
    t += u"""
    tk.highlightLookingGlobalIndex();
    // FOOTER_JS_AREA
</script>
</body></html>
"""
    return t


def _add_syntax_highlighter_js(syntax_list):
    t = ''
    syntax_highlighter_filname_map = {
        'text'  : 'Plain',
        'cpp'   : 'Cpp',
        'js'    : 'JScript',
        'perl'  : 'Perl',
        'python': 'Python',
        'ruby'  : 'Ruby',
        'xml'   : 'Xml',
        'css'   : 'Css',
        'sql'   : 'Sql',
        'as3'   : 'AS3',
        'java'  : 'Java',
        'scala' : 'Scala',
    }
    added = False
    for syntax in syntax_list:
        if syntax in syntax_highlighter_filname_map.keys():
            sh_file_name = 'shBrush' + syntax_highlighter_filname_map[syntax] + '.js'
            t += '<script type="text/javascript" src="$HOME/js/sh/scripts/' + sh_file_name + '"></script>\n'
            added = True
    if added:
        t = '<script type="text/javascript" src="$HOME/js/sh/scripts/shCore.js"></script>\n' + t
    return t


# positionally-fixed global toolbar and
# positionally-fixed index column (extend when mouse is over)
#---------------------------------------------------------------------
def _get_global_tollbar(path):
    t = '\n'
    t += u"""
<div class="global_navi" id="global_navi">
    <img src="$HOME/resource/image/general/title_logo.png" /><br/>
    <a href="$HOME/html/index.html"><img class ="navi_button" src="$HOME/resource/image/icon/home.png" /></a>
"""
    # back button
    if path.count('/') > 1:
        t += '<a href="../index.html"><img class ="navi_button" src="$HOME/resource/image/icon/back.png" /></a>'
    else:
        t += '<img class ="navi_button" src="$HOME/resource/image/icon/back_disabled.png" />'

    t += u"""
</div>
<div class="global_index" id="global_index">
    <p class="global_index">Tree</p>
    POST_PROCESS_BREADCRUMBS
    <p class="global_index">Index</p>
    POST_PROCESS_GLOBAL_INDEX
</div>
"""
    return t
#---------------------------------------------------------------------


def plain(args):
    t = args.SOURCE
    return t


def code(args):
    t = ''
    t += '<div class="code">\n'
    t += '<script type="syntaxhighlighter" class="brush: %s" title="%s"><![CDATA[' \
        % (args.data.type, args.data.title)
    #t += '<pre class="brush: %s" title="%s">' % (args.data.type, args.data.title)
    t += args['SOURCE']
    t += ']]></script></div>'
    #t += '</pre></div>'
    return t


def js(args):
    t = ''
    t += '<script type="text/javascript">'
    t += args['SOURCE']
    t += '</script>'
    return t


def table(args):
    return _generic_table(args)


def plain_table(args):
    return _generic_table(args, "plain")


def clear_table(args):
    return _generic_table(args, "clear", head=False)


def _generic_table(args, classname="mystyle", head=True):
    t = ''
    t += '<table class="%s">\n' % classname
    count = 0
    for row_data in args.data.root:
        if count == 0:
            if head:
                t += '    <tr class="head">\n'
            else:
                t += '    <tr class="color2">\n'
        elif (count % 2) == 1:
            t += '    <tr class="color1">\n'
        else:
            t += '    <tr class="color2">\n'
        count += 1

        td_count = 0
        for cell_data in row_data:
            # 先頭が plain:: だったら変換かけない
            if re.search('^plain::(.*)', cell_data):
                cell_data = re.search('^plain::(.*)', cell_data).groups()[0]
                converted_cell_data = '<em class="plain">' + cell_data + '</em>'
            else:
                converted_cell_data = args['CONVERTER'](cell_data)

            if td_count == 0 and (not head or count > 1):
                t += '        <td class="left">' + converted_cell_data + '</td>\n'
            else:
                t += '        <td>' + converted_cell_data + '</td>\n'
            td_count += 1
        t += '    </tr>\n'
    t += '</table>'
    return t


def back_button(args):
    t = ''
    indent = ' ' * (args.data.indent or 0)
    href = args.data.link or '../index'
    t += indent + '<div class="grid_container clearfix">\n'
    t += indent + '    <div class="grid_start"></div>\n'
    t += indent + '    <div class="grid3"><div class="grid_inner">\n'
    t += indent + '        <a class="box_subcategory" href="%s.html">\n' % (href)
    t += indent + '            <div class="box_back box-shadow border-radius">\n'

    img_name = args.data.alt_img or 'icon/arrow_left'
    t += indent + '                <img src="$HOME/resource/image/%s.png" />\n' % (img_name)
    t += indent + '                <p>Back</p>\n'
    t += indent + '            </div>\n'
    t += indent + '            <div class="clearfix"></div>\n'
    t += indent + '        </a>'
    t += indent + '    </div></div>'
    t += indent + '</div>'
    return t


def category_button(args):
    t = ''
    indent = ' ' * (args.data.indent or 0)
    if (args.data.anchor):
        t += indent + '<a class="box_category" href="#%s">\n' % (args.data.anchor)
        t += indent + '  <div class="box_category">\n'
    else:
        t += indent + '<a class="box_category" href="%s.html">\n' % (args.data.link)
        t += indent + '  <div class="box_category">\n'
        # insert PREVIEW tag
        # id_name = args.data.link.replace('/', '--')  # id attribute cannot use slash
        # t += indent + '  <div class="box_category" id="_PREVIEW_%s">\n' % (id_name)

    img_name = args.data.alt_img or 'icon/arrow_right2'
    t += indent + '    <img src="$HOME/resource/image/%s.png" />\n' % (img_name)
    t += indent + '    <p class="category_name">%s</p>\n' % (args.data.title)
    t += indent + '    <p>%s</p>\n' % (args.data.guide)
    t += indent + '  </div>\n'
    t += indent + '  <div class="clearfix"></div>\n'
    t += indent + '</a>'
    return t


def subcategory_buttons(args):
    t = ''
    indent  = ' ' * (args.data.indent or 0)
    for link in args.data.links:
        if len(link) >= 3:
            if link[1]:
                # id of another page
                t += indent + '<a class="box_subcategory" href="%s.html#%s">\n' % (link[1], link[2])
            else:
                # id of current page
                t += indent + '<a class="box_subcategory" href="#%s">\n' % link[2]
        else:
            # no id
            t += indent + '<a class="box_subcategory" href="%s.html">\n' % link[1]
        t += indent + '  <div class="box_subcategory border-radius">\n'
        t += indent + '    %s\n' % link[0]
        t += indent + '</div></a>\n'
    return t


def links(args):
    t = ''
    indent = ' ' * (args.data.indent or 0)
    links = args.data.links

    if len(links) < 6:
        num_harf = len(links)
    else:
        num_harf = len(links) / 2 + 1
    first_harf = links[0:num_harf]
    last_harf  = links[num_harf:]

    # back to navi button
    t += indent + '<div class="grid_container clearfix">\n'
    t += indent + '    <div class="grid_start"></div>\n'
    t += indent + '    <div class="grid1"><div class="grid_inner">\n'
    t += indent + '        <a class="box_back" href="#navi">\n'
    t += indent + '            <div class="box_back_navi box-shadow border-radius">\n'
    t += indent + '                <img src="$HOME/resource/image/icon/arrow_up.png" />\n'
    t += indent + '            </div>\n'
    t += indent + '            <div class="clearfix"></div>\n'
    t += indent + '        </a>\n'
    t += indent + '    </div></div>\n'

    # left column
    t += indent + '    <div class="grid5"><div class="grid_inner">\n\n'
    t += indent + '        <ul class="level1">\n'
    for link in first_harf:
        t += indent + '            <li><a href="%s.html">%s</a></li>\n' % (link[1], link[0])
    t += indent + '        </ul>\n\n'
    t += indent + '    </div></div>\n'

    # right column
    t += indent + '    <div class="grid5"><div class="grid_inner">\n\n'
    t += indent + '        <ul class="level1">\n'
    for link in last_harf:
        t += indent + '            <li><a href="%s.html">%s</a></li>\n' % (link[1], link[0])
    t += indent + '        </ul>\n\n'
    t += indent + '    </div></div>\n'

    t += indent + '</div>'
    return t


def update_time(args):
    timestamp   = os.stat(args.SRC_PATH)[stat.ST_CTIME]
    output_fmt  = '%Y-%m-%d %H:%M:%S'
    update_time = time.strftime(output_fmt, time.localtime(timestamp))
    t = '<p class="update_time">'
    if args.data.create_date:
        t += 'Created: %s<br/>' % args.data.create_date
    #t += 'Modified: %s<br/>Written by Tatsuya Koyama</p>' % update_time
    if args.data.modify_date:
        t += 'Modified: %s<br/>' % args.data.modify_date
    t += 'Written by Tatsuya Koyama</p>'
    return t

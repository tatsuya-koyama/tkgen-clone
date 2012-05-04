# -*- coding: utf-8 -*-
"""
tkutil/console

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import re
import json

def cprint(src):
    """
    print colored text. you can apply a color to text by embedding color tag
    like <colorname:text what you want/>

    ex.) cprint('<red:apple/> and <yellow:lemon/> tart')

    the colorname beginning with 'l' such as 'lred' provides bright color.
    """
    colors = {
        'white' :  0,
        'red'   : 31,  'lred'   : 31,
        'green' : 32,  'lgreen' : 32,
        'yellow': 33,  'lyellow': 33,
        'blue'  : 34,  'lblue'  : 34,
        'purple': 35,  'lpurple': 35,
        'cyan'  : 36,  'lcyan'  : 36,
    }

    def esc_color(matched):
        # for example: src = '<red:apple/> and <yellow:lemon/> tart'
        # then 'matched' of first call is ('red', 'apple')
        color, text = matched.groups()
        bright = 1 if (color[0] == 'l') else 0
        color_format = '\033[%d;%dm%s\033[0m'
        return color_format % (bright, colors[color], text)

    color_names = '|'.join(colors.keys())
    replaced = re.sub('<(%s):(.*?)/>' % color_names, esc_color, src)
    print replaced


def dump(json_obj, color='green', title=None):
    """dump json object pretty. I don't like print or pprint format..."""
    if title:
        cprint('<%s:===== %s =====/>' % (color, title))
    dumped = json.dumps(json_obj, sort_keys=True, indent=4)
    if color:
        for line in dumped.split('\n'):
            cprint('<%s:%s/>' % (color, line))
    else:
        print dumped


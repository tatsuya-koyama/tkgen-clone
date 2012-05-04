# -*- coding: utf-8 -*-
"""
tkgen/replacer

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import sys, os
import time
import tkutil.file
from tkutil.console import cprint
from tkgen.template_engine import TemplateEngine
from tkutil.config import Config

def main(opts={}, config_path='tkgen.cfg'):
    # initial time
    start_time = time.time()

    # load config file
    cprint('<lred:load config file:/> %s' % config_path)
    config = Config(config_path)
    config.describe()

    # list rule file paths
    rule_file_pattern = config.file_pattern.rule
    cprint('\n\n<lred:target rule files:/> %s%s' % (config.path.rule, rule_file_pattern))
    put_line()
    rule_files = []
    for path in tkutil.file.get_all_files(config.path.rule, rule_file_pattern):
        print path
        rule_files.append(path)

    # list source file paths
    src_file_pattern = config.file_pattern.src
    cprint('\n\n<lred:target source files:/> %s%s' % (config.path.src, src_file_pattern))
    put_line()
    src_files = []
    for path in tkutil.file.get_all_files(config.path.src, src_file_pattern):
        print path
        src_files.append(path)

    # compare timestamp of files and erase not-updated file path
    cprint('\n\n<lred:compare timestamp of files with last update time/>')
    put_line()
    last_update_timestamps = tkutil.file.load_obj_from_file(config.path.last_update) or {}
    updated_src_files = get_updated_src_files(
        src_files, last_update_timestamps, opts.all
    )

    # list python module file path for template processing
    cprint('\n\n<lred:target template module files:/> %s*.py' % config.path.module)
    put_line()
    module_files = []
    for path in tkutil.file.get_all_files(config.path.module, '*.py'):
        if not path == (config.path.module + '__init__.py'):
            print path
            module_files.append(path)

    # load rules, sources, and modules
    template_engine = TemplateEngine(
        rule_files, updated_src_files, module_files, config.path.build, config.extension_map
    )

    # convert sources
    cprint('\n\n<lred:start converting.../>')
    put_line()
    template_engine.go()

    # save timestamps
    tkutil.file.save_obj_to_file(last_update_timestamps, config.path.last_update)

    # post process
    cprint('\n\n<lred:start post process:/> %s' % config.module.postprocess)
    put_line()
    run_postprocess(config.module.postprocess, opts, config)

    # print processing time
    end_time = time.time()
    print '\n\nprocessing time: %.3f [sec]' % (end_time - start_time)

    cprint('<lred:tkgen completed./>')
    return 0


def put_line(width=80):
    print '-' * width


def get_updated_src_files(src_files, last_update_timestamps, option_all=False):
    updated_src_files = []
    # return copy of all source file paths
    if option_all:
        cprint('<purple:option "all" is True: update all source files./>')
        return [path for path in src_files]

    # return only updated source file paths
    for path in src_files:
        t = tkutil.file.get_timestamp(path)
        color = 'white'
        tag   = ' ' * 10
        if path in last_update_timestamps:
            last_update = last_update_timestamps[path]
            if t > last_update:
                updated_src_files.append(path)
                last_update_timestamps[path] = t
                color = 'yellow'
                tag   = '[ updated]'
        else:
            updated_src_files.append(path)
            last_update_timestamps[path] = t
            color = 'green'
            tag   = '[new file]'

        cprint ('<%s:%s %s %s-%s %s:%s:%s ::: %s/>'
            % (color, tag, t[:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:], path)
        )
    cprint('<cyan:number of updated files: %d/>' % len(updated_src_files))
    return updated_src_files


def run_postprocess(module_path, opts, config):
    try:
        module = __import__(
            module_path, globals(), locals(), [''], -1
        )
    except ImportError:
        cprint("<red:Import Error: module file for postprocess not found: %s/>" % (module_path))
        sys.exit()

    entry_func_name = 'postprocess'
    try:
        func = getattr(module, entry_func_name)
        func(opts, config)
    except AttributeError:
        cprint("<red:Attribute Error: postprocess function <%s.%s> not found/>" \
               % (module_path, entry_func_name))
        sys.exit()

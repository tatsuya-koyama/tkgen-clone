# -*- coding: utf-8 -*-
"""
tkgen/template_engine
    * required PyYAML

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import sys
import os
import re
import codecs
import yaml
from tkgen.reg_converter import RegConverter
from tkgen.line_generator import LineGenerator
from tkutil.console import cprint, dump
from tkutil.misc import MyDict, SafetyGetter


class ParseState(object):

    def __init__(self):
        self.is_parsing = False
        self.last_key   = ''


class TemplateEngine(object):
    """ ToDo """

    def __init__(self, rule_files=[], src_files=[], module_files=[],
                 build_path='', ext_map={}):
        """
        @param rule_files  : path list of define-rule files
        @param src_files   : path list of source files
        @param module_files: path list of python module files (for template)
        @param build_path  : path to output converted files
        @param ext_map     : dictionary; source file extension => output file extension
        """
        self.rule_files    = rule_files
        self.src_files     = src_files
        self.module_files  = module_files
        self.build_path    = build_path
        self.ext_map       = ext_map
        self.defines       = {}
        self.templates     = {}
        self.def_state     = ParseState()
        self.replace_table = {}

        self._load_rules(self.rule_files, self._parse_define)
        self.template_modules = self._import_modules(self.module_files)
        #dump(self.defines, title='defines') ##### debug

    def _load_rules(self, rule_files, rule_handler):
        for rule in rule_files:
            #in_file = open(rule, 'r')
            in_file = codecs.open(rule, 'r', 'utf-8')
            try:
                for line in in_file:
                    line = line.rstrip()
                    rule_handler(line)
            finally:
                in_file.close()

    def _parse_define(self, line):
        """
        Load definition file and set dictionary to 'self.defines'.
        Following keys are set if it is defined:
            dest         # pattern after converted
            if_prev      # if previous line matches this pattern,
            prev_insert  #     insert value of 'prev_insert' to previous line
            if_next      # if next line matches this pattern,
            next_insert  #     insert value of 'next insert' to next line
            option_not_indent  # if this is true, stop nesting
                               # (results are nested until 'next_insert' appear by default)
            option_indent    # indent without if_prev
            option_unindent  # unindent on convert
        """
        if self._is_comment(line): return
        #cprint('<blue:%s/>' % line) ##### debug

        if not self.def_state.is_parsing:
            if re.search('^define\s', line):
                self.def_state.is_parsing = True
                self.def_state.last_key = re.search('^\s*define\s(.*)$', line).group(1)
                self.defines[self.def_state.last_key] = {'dest': ''}
        else:
            defines = self.defines[self.def_state.last_key]
            # if_prev
            if re.search('^\s+if_prev\s+(.*)\s+then\s+(.*)$', line):
                groups = re.search('^\s+if_prev\s+(.*)\s+then\s+(.*)$', line).groups()
                defines['if_prev']     = groups[0]
                defines['prev_insert'] = groups[1]

            # if_next
            elif re.search('^\s+if_next\s+(.*)\s+then\s+(.*)$', line):
                groups = re.search('^\s+if_next\s+(.*)\s+then\s+(.*)$', line).groups()
                defines['if_next']     = groups[0]
                defines['next_insert'] = groups[1]

            # option: not_indent
            elif re.search('^\s+option\s+not_indent', line):
                defines['option_not_indent'] = True

            # option: indent
            elif re.search('^\s+option\s+indent', line):
                defines['option_indent'] = True

            # option: unindent
            elif re.search('^\s+option\s+unindent', line):
                defines['option_unindent'] = True

            # replace pattern
            elif re.search('^\t+', line):
                dest = re.search('^\t+(.*)$', line).group(1)
                if defines['dest']:
                    defines['dest'] += '\n'
                defines['dest'] += dest

            else:
                self.def_state.is_parsing = False

    def _import_modules(self, module_files):
        """モジュール名のキーにモジュールオブジェクトを入れた辞書を返す"""
        result = {}
        for file_path in module_files:
            # 'package/module.py' -> 'package.module'
            groups      = re.search('^(.*)/(.*)\.py$', file_path).groups()
            package     = groups[0]
            module_name = groups[1]
            module_path = (package + '.' + module_name)
            try:
                result[module_name] = __import__(
                    module_path, globals(), locals(), [''], -1  # これまだ引数完全に理解してない
                )
            except ImportError:
                cprint("<red:Import Error: module file not found: %s/>" % (module_path))
                sys.exit()
        # print result
        return result

    def _is_comment(self, line):
        return re.search('^\s*//.*', line)

    def _is_blank(self, line):
        return re.search('^\s*$', line)

    def go(self):
        """convert all source files according to defines and templates"""
        for i, src_path in enumerate(self.src_files):
            length = len(self.src_files)
            rate   = (i + 1.0) / length * 100
            cprint('%d / %d <yellow:(%5.1f %%)/> ::: %s' % (i+1, length, rate, src_path))
            convert_result = self._convert(src_path)
            self._write_file(convert_result, src_path, self.build_path, self.ext_map)

    def _convert(self, src_path):
        """return converted all lines of one source file"""
        results           = []
        line_generator    = LineGenerator(src_path)
        self.next_rules   = []
        self.indent_level = 0

        try:
            while not line_generator.is_end():
                prev_line   = line_generator.get_prev_line()
                line        = line_generator.get_current_line()
                next_line   = line_generator.get_next_line()
                result_line = ''

                if re.search('^\s*\$', line):
                    result_line = self._get_result_by_template(line_generator, src_path)
                else:
                    result_line = self._get_result_by_define(prev_line, line, next_line)

                #print result_line ##### debug
                results.append(result_line + '\n')
                line_generator.proceed()
        except:
            prev_line   = line_generator.get_prev_line()
            line        = line_generator.get_current_line()
            next_line   = line_generator.get_next_line()
            cprint('<red:Convert Error: />line %d' % line_generator.get_line_number())
            cprint('  <lred:%s/>\n> <lred:%s/>\n  <lred:%s/>' % (prev_line, line, next_line))
            raise
        return results

    def _get_result_by_template(self, line_generator, src_path):
        result_lines = ''

        #----- テンプレート呼び出し全体を１つの文字列に
        # 閉じ括弧が現れるまでをまとめる
        template_unit = line_generator.get_current_line()
        while not re.search('\)', template_unit):
            template_unit += ('\n' + line_generator.proceed_and_get_line())

        # <<< があれば >>> があるまでもまとめる
        if re.search('<<', template_unit) or re.search('<<', line_generator.get_next_line()):
            while not re.search('\n>>', template_unit):
                template_unit += ('\n' + line_generator.proceed_and_get_line())
                if line_generator.is_end():
                    cprint("<red:Error: >> is not found/>")
                    print "processing data:\n" + template_unit
                    sys.exit()

        module_name    = ''
        func_name      = ''
        arguments_yaml = ''
        source_strings = ''
        p1 = re.compile('\$(.*?)\.(.*?)\((.*?)\)', re.DOTALL)  # ドットを改行文字にもマッチさせる
        if re.search(p1, template_unit):
            groups = re.search(p1, template_unit).groups()
            module_name    = groups[0]
            func_name      = groups[1]
            arguments_yaml = groups[2]

        p2 = re.compile('<<(.*)>>', re.DOTALL)
        if re.search(p2, template_unit):
            source_strings = re.search(p2, template_unit).group(1)

        # 関数に渡す引数を YAML で解釈して辞書オブジェクトに
        args = yaml.load(arguments_yaml)

        # define での変換用
        def convert(src):
            converter = RegConverter(src, self.defines)
            converter.convert()
            return converter.get_result()

        # 安全なアクセス用 getter
        def data_getter(key):
            try:
                return args[key]
            except:
                return ''
            return None

        # 指定されたモジュール内の関数を呼んでテンプレート処理の結果を得る
        module = self.template_modules[module_name]
        func   = getattr(module, func_name)
        arg_dict = MyDict({
            'CONVERTER': convert,
            'DATA'     : args,
            'data'     : SafetyGetter(args),
            'SOURCE'   : source_strings,
            'SRC_PATH' : src_path,
            'OUT_PATH' : self._get_output_path(src_path, self.build_path, self.ext_map)
        })
        result_lines = func(arg_dict)
        return result_lines

    def _get_result_by_define(self, prev_line, line, next_line):
        result_line = ''
        def indent():
            return self._get_indent(self.indent_level)

        optional_indent = self._get_optional_indent(line)
        if optional_indent == -1 and self.indent_level > 0:
            self.indent_level += optional_indent

        # strings attached to previous line
        (prev_line, indent_count) = self._get_prev_line(prev_line, line)
        if prev_line:
            result_line = (indent() + prev_line + "\n")
        self.indent_level += indent_count

        # current line
        result_line += (indent() + self._replace_by_define(line))

        # strings attached to next line
        (next_line, unindent_count) = self._get_next_line(next_line)
        self.indent_level -= unindent_count
        if next_line:
            result_line += ("\n" + indent() + next_line)

        if optional_indent == 1:
            self.indent_level += optional_indent

        # avoid whitespace-only line
        if re.search('^\s+$', result_line):
            result_line = ''
        return result_line

    def _get_indent(self, indent_level):
        return (' ' * indent_level * 4)

    def _get_optional_indent(self, line):
        """
        return  1 if 'option indent' is set
        return -1 if 'option unindent' is set
        otherwise return 0
        """
        for define_key in self.defines:
            if re.search(define_key, line):
                options = self.defines[define_key]
                if 'option_indent' in options:
                    return 1
                if 'option_unindent' in options:
                    return -1
        return 0

    def _replace_by_define(self, line):
        converter = RegConverter(line, self.defines)
        converter.convert()
        #converter.describe() ######## debug
        return converter.get_result()

    def _get_prev_line(self, prev_line, line):
        """
        置換ルールに if_prev と prev_insert が指定されていたら、
        前行が if_prev と一致するときに prev_insert を返す。
        また、if_prev がひとつマッチするたびにインデントのレベルを１つカウントする。
        （option not_indent が指定されている if_prev はインデントしない）
        この関数は複数の prev_insert を足しあわせた結果とインデントのレベルをタプルで返す。

        この関数は if_next と next_insert があった場合に、そのルールを self.next_rules という
        リストに詰む。これは _get_next_line で使う
        """
        result = ''
        indent_count = 0
        for define_key in self.defines:
            rules = self.defines[define_key]
            if 'if_prev' in rules and 'prev_insert' in rules:
                if (re.search(define_key, line) and
                    re.search(rules['if_prev'], prev_line)):
                    result += rules['prev_insert']

                    option_indent = False
                    if not 'option_not_indent' in rules:
                        option_indent = True
                        indent_count += 1

                    if 'if_next' in rules and 'next_insert' in rules:
                        self.next_rules.append(
                            (rules['if_next'], rules['next_insert'], option_indent)
                        )
        return (result, indent_count)

    def _get_next_line(self, next_line):
        """
        _get_prev_line で self.next_rules に詰んでおいたルールを見て、
        次行が if_next と一致する場合に next_insert を返す。
        この関数は複数の next_insert を足しあわせた結果とアンインデントするレベルをタプルで返す
        """
        result = ''
        unindent_count = 0
        next_rules_remain = []
        for rule in self.next_rules:
            if_next       = rule[0]
            next_insert   = rule[1]
            option_indent = rule[2]
            if re.search(if_next, next_line):
                result += next_insert
                if option_indent:
                    unindent_count += 1
            else:
                next_rules_remain.append((if_next, next_insert, option_indent))
        self.next_rules = next_rules_remain
        return (result, unindent_count)

    def _write_file(self, text_list, src_path, build_dir, ext_map):
        if not re.search('^(.*)/', src_path):
            return

        build_file_name = self._get_output_path(src_path, build_dir, ext_map)
        dir_to_build_file = re.search('^(.*)/', build_file_name).group(1)
        if not os.path.isdir(dir_to_build_file):
            os.makedirs(dir_to_build_file)

        file_obj = codecs.open(build_file_name, 'w', 'utf-8')
        file_obj.writelines(text_list)
        file_obj.close()
        cprint((' ' * 17) + '-> <blue:%s/>' % build_file_name)

    def _get_output_path(self, src_path, build_dir, ext_map):
        groups = re.search('^.*?/(.*)(\..+)', src_path).groups()
        src_file_name   = groups[0]
        src_file_ext    = groups[1]
        try:
            build_file_ext  = ext_map[src_file_ext]
        except:
            cprint('<red:key of extension table not found: /><purple:%s/>' % src_file_ext)
            cprint('<lred:    * check your tkgen.cfg file./>\n')
            raise

        build_file_name = build_dir + src_file_name + build_file_ext
        return build_file_name



    # ジェネレータとか使って俺イケてると思ったけど、
    # 前後の行も返したくなったりしたからやっぱりクラス作った
    # def gen_line(self, src_path):
    #     in_file = open(src_path, 'r')
    #     try:
    #         lines = in_file.readlines()  # store all lines of file into a list
    #         for line in lines:
    #             if not self._is_comment(line):
    #                 yield line
    #     finally:
    #         in_file.close()


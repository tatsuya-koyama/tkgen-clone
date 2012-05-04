# -*- coding: utf-8 -*-
"""
tkgen/reg_converter

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import sys
import re
import hashlib
from tkutil.console import cprint, dump


class RegConverter(object):
    """正規表現の置換ルール群を再帰的に適用してテキストの置換を行う"""

    def __init__(self, src, all_rules):
        """
        @param src      : 置換前パターン
        @param all_rules: all_rules['置換前パターン']['dest']: '置換後パターン' となっている辞書
        """
        self.replace_table = {
            src: {  # source string
                "dest": src,             # destination string (initial value is source string)
                "replacable"   : [src],  # 置換後の、さらに置換していい部分（後方参照された部分）
                "replace_table": {}      # 置換用に置き換えたハッシュ値の対応表（再帰）
            }
        }
        self.src = src

        rules = self._get_rules(src, all_rules)
        self.rules = rules  # source にヒットした置換ルールのリスト
        #dump(self.rules, title="mathced rules", color="green")  ########## debug

    def _get_rules(self, src, all_rules):
        target_rules = []
        for rule in all_rules:
            dest = all_rules[rule]['dest']
            searched_src = src

            while re.search(rule, searched_src):
                searched = re.search(rule, searched_src)
                matched  = searched.group(0)
                replaced = re.sub(rule, dest, matched)
                #cprint("<purple:%s/> ::: %s ::: <yellow:%s/>" % (rule, searched_src, matched))  ########## debug

                # store replaced text by back reference
                replacable = []
                if re.search(r"\\1", dest):
                    replacable = re.findall(rule, matched)
                    # 後方参照が２つ以上ある場合 findall はタプルを返すので、その場合は展開する
                    for maybe_tuple in replacable:
                        if isinstance(maybe_tuple, tuple):
                            replacable = [x for x in maybe_tuple]

                convertRule  = {
                    'src'         : matched,
                    'dest'        : replaced,
                    'src_len'     : len(matched),
                    'replacable'  : replacable,
                    'src_rule'    : rule,
                    'src_rule_len': len(rule)
                }
                #dump(convertRule, title="", color="yellow")  ########## debug
                searched_src = re.subn(rule, '', searched_src, 1)[0]
                if not self._is_exist_rule(matched, rule, target_rules):
                    target_rules.append(convertRule)
        # 「置き換え前の文字列」の長さが長い順にソート
        # 次に「ルール定義文の長さ」が長い順にソート
        target_rules = sorted(
            target_rules,
            key=lambda a:(a.get('src_len'), a.get('src_rule_len')),
            reverse=True)
        #print src ##### debug
        #dump(target_rules) ################## debug
        return target_rules

    def _is_exist_rule(self, matched, src_rule, rules):
        for rule in rules:
            if (matched == rule['src'] and
                src_rule == rule['src_rule']):
                return True
        return False

    def convert(self):
        self._make_replace_tree(self.replace_table)

    def _make_replace_tree(self, replace_table):
        for src_key in replace_table:
            #cprint("<yellow:%s/>" % (src_key)) ########## debug
            node = replace_table[src_key]
            dest = node['dest']
            for rule in self.rules:
                # Use only first 10 characters of hash to reduce the cpu load.
                # There is a possibility of hash conflict (but it is very small.)
                hash_src = rule['dest'].encode('utf-8')
                hash_key = '<%s>' % hashlib.md5(hash_src).hexdigest()[:10]

                for replacable in node['replacable']:
                    if rule['src'] in replacable and rule['src'] in dest:
                        # make next replace table
                        node['replace_table'][hash_key] = {
                            'dest': rule['dest'],
                            'replacable'   : rule['replacable'],
                            'replace_table': {}
                        }
                        # replace to hash key
                        dest = dest.replace(rule['src'], hash_key)
                #cprint("<purple:%s/>: %s, <blue:%s/>" % (rule["src"], rule["dest"], dest)) ############ debug
            node['dest'] = dest
            #dump(node, title="", color="red")  ########## debug
            self._make_replace_tree(node['replace_table'])

    def get_result(self):
        """出来上がった置換ツリーを再帰処理して変換後の文字列を得る"""
        return self._get_result(self.src, self.replace_table)

    def _get_result(self, src, replace_table):
        for src_key in replace_table:
            node = replace_table[src_key]
            dest = node["dest"]
            src  = src.replace(src_key, dest)
            src  = self._get_result(src, node["replace_table"])
        return src

    def describe(self):
        print "convert process description:"
        dump(self.replace_table, color="yellow")


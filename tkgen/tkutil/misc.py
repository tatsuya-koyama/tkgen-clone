# -*- coding: utf-8 -*-
"""
tkutil/misc
    [ToDo]

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""


def get_encoding(str):
    """
    return encoding name of str
    """
    lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
              'shift_jis', 'shift_jis_2004','shift_jisx0213',
              'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
              'iso2022_jp_ext','latin_1', 'ascii')
    for encoding in lookup:
        try:
            str = str.decode(encoding)
            return encoding
        except:
            pass
    return None


class MyDict(dict):
    """
    要素にドットでアクセスできる辞書。JavaScript 感覚。
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class SafetyGetter(object):
    """
    ドットで気楽にオブジェクトにアクセスするためのアクセサ。
        obj = {
            aval: 123
        }
        sgetter = SafetyGetter(obj, def_val)
    としてインスタンスを作ったとき、
        sgetter.aval
    で 123 が得られる。

        sgetter.unknown_key
    のように存在しないキーでアクセスした場合は def_val が返る。
    また、値が偽だった場合にも def_val が返る。
    def_val は特に指定しなければ空文字列になるので、気楽に
        for a in sgetter.alist:
    などと書いても例外が発生しない。

    root というキーのみ特別で、
        sgetter.root
    で obj の値そのものが得られる。
        obj = 456
    のように obj が辞書で無い場合は sgetter.root を使う。
        obj = {
            root: 789
        }
    であっても sgetter.root は 789 ではなく {'root': 789} を返すことに注意。
    """

    def __init__(self, target_obj={}, default_val=''):
        self._target_obj  = target_obj or {}
        self._default_val = default_val

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, key_name):
        if key_name == 'root':
            if self._target_obj:
                return self._target_obj
            else:
                return self._default_val

        try:
            if isinstance(self._target_obj, dict):
                target_val = self._target_obj[key_name]
                if target_val:
                    return target_val
                else:
                    return self._default_val
            else:
                return self._default_val
        except KeyError:
            return self._default_val

        if self._target_obj:
            return self._target_obj
        return self._default_val

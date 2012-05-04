#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
entry point of post process for tkgen
"""

from tkgen.tkutil.console import cprint
import make_preview
import make_index
import replace_home_path

def postprocess(opts, config):
    """
    tkgen によるコード変換が全て終えられた後に実行される後処理
    変換後のファイルおよびファイルツリー全体に対して行いたい処理をここに追記してね

    @param opts  : 起動引数 （optparse.OptionParser のパース結果）
    @param config: コンフィグファイルの内容 （tkgen.tkutil.Config のオブジェクト）
    """

    #cprint("<yellow:* run make_preview/>")
    #make_preview.doit(config)

    cprint("\n<yellow:* run make_index/>")
    make_index.doit(config)

    cprint("\n<yellow:* run replace_home_path/>")
    replace_home_path.doit(config)

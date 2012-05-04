#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
facebook のコメント欄とかそういうウィジェット系のコード
"""
#-------------------------------------------------------------------------------

def facebook_comment_js():
    t = """
<!-- for Facebook comment box widget -->
<div id="fb-root"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>

"""
    return t


def facebook_comment_body(args):
    t = """

<!-- Facebook comment box widget -->
<div class="grid_container clearfix" style="display: block;">
    <div class="grid_start"></div>
    <div class="grid12"><div class="grid_inner">
        <h2 class="footer_caption">Facebook Comment</h2>
    </div></div>
    <div class="grid_start"></div>
    <div class="grid1"><div class="grid_inner"></div></div>
    <div class="grid11"><div class="grid_inner">

"""
    t += '        <div class="fb-comments" data-href="http://www.tatsuya-koyama.com/4.0/%s"' % args.OUT_PATH
    t += """
             data-num-posts="5" data-width="500" data-colorscheme="dark">
        </div>

        <br/><br/>
    </div></div>
</div>

"""
    return t


def facebook_like_button(args):
    t = '\n'
    t += '            <!-- Facebook Like button -->\n'
    t += '            <div class="fb-like" data-href="http://www.tatsuya-koyama.com/4.0/%s"' % args.OUT_PATH
    t += """
                  data-send="true" data-width="450" data-show-faces="true"
                  data-colorscheme="dark" data-font="verdana">
            </div><br/>
"""
    return t


def mixi_like_button():
    t = """
            <!-- mixi Like Button -->
            <div data-plugins-type="mixi-favorite" data-service-key="878a516e08b08b6a38c63844cae016f2800ca95e"
                 data-size="medium" data-href="" data-show-faces="true" data-show-count="true"
                 data-show-comment="true" data-width="">
            </div>
            <script type="text/javascript">(function(d) {var s = d.createElement('script'); s.type = 'text/javascript'; s.async = true;s.src = '//static.mixi.jp/js/plugins.js#lang=ja';d.getElementsByTagName('head')[0].appendChild(s);})(document);</script>
            <br/>
"""
    return t


def tweet_button():
    t = """
            <!-- Tweet Button -->
            <a href="https://twitter.com/share" class="twitter-share-button">Tweet</a>
            <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
            <div class="ws2"></div>
"""
    return t


def google_plus_button():
    t = """
            <!-- Place this tag where you want the +1 button to render -->
            <g:plusone></g:plusone>

            <!-- Place this render call where appropriate -->
            <script type="text/javascript">
              (function() {
                var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
                po.src = 'https://apis.google.com/js/plusone.js';
                var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
              })();
            </script>
            <div class="ws4"></div>
"""
    return t


def hatebu_button(args):
    t = """
            <!-- Hatebu Button -->
"""
    t += '            <a href="http://b.hatena.ne.jp/entry/http://www.tatsuya-koyama.com/4.0/%s"' % args.OUT_PATH
    t += u"""
               class="hatena-bookmark-button" data-hatena-bookmark-title="俺式4.0 / tkStyle"
               data-hatena-bookmark-layout="standard" title="このエントリーをはてなブックマークに追加">
                <img src="http://b.st-hatena.com/images/entry-button/button-only.gif" alt="このエントリーをはてなブックマークに追加" width="20" height="20" style="border: none;" />
            </a>
            <script type="text/javascript" src="http://b.st-hatena.com/js/bookmark_button.js" charset="utf-8" async="async"></script>
            <div class="ws4"></div>
"""
    return t


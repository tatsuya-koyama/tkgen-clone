*** template の仕様 ***
	* 渡したいデータを括弧の中に yaml で記述する
	* 末尾に {{ ... }} をつけると、波括弧の中身が丸ごと文字列として渡される
	
	【ソースとなるファイルからは以下のように呼び出す】
	
	$module_name.func_name(
	  -
	    - item1
	    - hoge1
	    - fuga1
	  -
	    - item2
	    - hoge2
	    - >-
	      fuga2
	      multiline is OK
	)
	<<
	source code...
	source code...
	>>
	
		【以下の書き方も OK】
		$module_name.func_name()
		
		$module_name.func_name( arg )<<
		...
		>>
		
	// 括弧内は yaml なので、引数が定数１個だけなら文字列や値をそのまま書けばいい
	// 上記の例だと 'arg' が引数として渡される
	
	
*** template の定義の仕方 ***
	* MODULE_DIR/ の中にモジュール群を置いておく
	（Python ではモジュール名 = ファイル名）
	
	* module_name という名のモジュールの中の func_name 関数に引数が渡されて実行される
	* 関数は整形結果の文字列を返すようにする
	* 関数に渡される引数は上記の例だと
	
		{
			CONVERTER: 【define で変換するためのオブジェクト】
			DATA: [
				["item1", "hoge1", "fuga1"],
				["item2", "hoge2", "fuga2 multiline is OK"]
			],
			data: （DATA への便利アクセサ）
			SOURCE: "source code...\nsource code...\n"
			SRC_PATH: (対象ソースファイルのパス)
			OUT_PATH:（出力ファイルのパス）
		}
	
	* 閉じの >> は >> から始まる行でなければならない
	（プログラム中にある >> は無視される）
	（昔は {{ }} にしてて、Perl とかだと %{$rHash->{hash_ref}} とか普通にあったりして困ってた）
	    （PukiWiki の Syntax Highlighter ではこれでうまくいかなかったりしたなー）
	（当然、プログラム中に >> から始まる行があると残念なことになる）
	    （ヒアドキュメントが怖いけど、始めるのは >> じゃなくて << だし大丈夫だよね？）
	
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
	
	* yaml なので : や [] を書く場合に "" で囲んでエスケープしなきゃならないことに注意




# vectorworks-tools

Vectorworks（Fundamentals 2024）で使うプラグインとスクリプト。
図面に書く情報を1か所にして、図面・表・PDFが自動でそろうようにするためのもの。

- 公開のリポジトリ。**お客様・社員の名前、住所、連絡先などは入れない**（コードと使い方だけ）。
- コードを直すのは Claude（会話の中で）。担当者は Vectorworks に「読み込むだけの短いコード」を最初に1回貼るだけ。

## しくみ
Vectorworks のプラグインやスクリプトの中身は、下の「読み込むだけの短いコード」だけにする。
このコードが、GitHub の本体（`tana/〇〇.py`）を自動でダウンロードして動かす。

- 新しい版がないかを見るのは **5分に1回**（毎回見ると重くなるため）。それまではパソコンの中の控えで動く。
- ネットにつながらないときは、前の控えで動く。
- 控えの置き場所：`%APPDATA%\hako_vectorworks_tools\`
- GitHub の raw は最大5分ほど古い版を返すことがあるので、直してから新しいコードで動くまでは、最大10分ほどかかる。

## 「AI」ボタン
- Vectorworks に「AI」という名前のスクリプトを1つだけ置く（中身は下の loader で `NAME = 'ai/menu.py'`）。
- ダブルクリックすると機能の一覧が出て、番号を入れると動く。一覧は `ai/menu.py` の `MENU`。機能を足すときは、ファイルを足して `MENU` に1行足すだけ（Vectorworks の側は変えない）。
- 棚表の中の `=RUNSCRIPT('AI', 'bangou')` から呼ばれたときは、一覧を出さずに番号の自動振り直しを動かす。
- テンプレートの図面で「この図面を AI仕様にする」を1回動かして保存すれば、そこから複製する図面は最初から AI仕様になる。

## 読み込むだけの短いコード（loader）
`NAME` だけを、貼る先に合わせて変える。

| 貼る先 | NAME |
|---|---|
| スクリプト「AI」（これだけ置けばよい） | `ai/menu.py` |
| プラグイン「棚」（プラグインマネージャ → スクリプト編集、言語 Python） | `tana/plugin.py` |
| スクリプト「棚表を作る」 | `tana/hyou.py` |
| スクリプト「棚の番号_自動」（棚表から自動で呼ばれる） | `tana/bangou.py` |
| スクリプト「棚に置き換える」（古い描き方の棚を置き換えるとき） | `tana/okikae.py` |

```python
import vs, os, time, urllib.request
NAME = 'tana/plugin.py'
URL = 'https://raw.githubusercontent.com/kkkousei/vectorworks-tools/main/' + NAME
DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'hako_vectorworks_tools')
path = os.path.join(DIR, NAME.replace('/', '_'))
if not os.path.exists(path) or time.time() - os.path.getmtime(path) > 300:
    try:
        with urllib.request.urlopen(URL, timeout=5) as r:
            code = r.read()
        os.makedirs(DIR, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(code)
    except Exception:
        if os.path.exists(path):
            os.utime(path, None)
exec(compile(open(path, encoding='utf-8').read(), path, 'exec'))
```

## 棚（tana）
- プラグイン「棚」：3点型オブジェクト。置く・コピーすると白い四角と記号（SH-〇）が出る。記号が空なら次の番号が付く。品目が固定棚なら「棚柱」「金物」の欄を隠す（プラグイン定義の「イベントに対応」をオンにしたときだけ）。
- パラメータ（名前／表示名／型）：Kigou 記号 Text、Hinmoku 品目 Pop-up、Zairyo 材料 Pop-up、Iro 色 Text、Maisu 枚数 Integer、Tanabashira 棚柱 Pop-up、Kanamono 金物 Pop-up、OkuFukai 奥行が深い Boolean、Bikou 備考 Text（LineLength・BoxWidth は3点型に最初からある）。
  - 品目：未選択／固定棚／可動棚／枕棚＋HP／その他
  - 材料：未選択／仕上げてる棚板／白ポリ／ラワン合板／ラワンランバーコア／シナ合板／シナランバーコア／その他
  - 棚柱：未選択／側面／背面
  - 金物：未選択／シルバー／ブラック／ホワイト／その他
- 棚表：ワークシート「棚表」。シートレイヤに置く。表のウインドウを開いている間は図面の表が×になる（閉じれば出る）。
  - 幅は大きい方、奥行は小さい方。「奥行が深い」にチェックした棚だけ逆。
  - 固定棚は棚柱・金物を空欄。未選択は【未選択】と出る。棚柱が背面なら「背面（Lアングル要）」。
  - 1行目のいちばん右（幅を狭くした列）に `=RUNSCRIPT('棚の番号_自動')`。表が計算し直されるたびに番号が詰まる。PDF書き出し（取り出し前にワークシートを再計算）と印刷でも、表と図面の番号がそろう（2026-11-13 確認）。

## 気をつけること（分かったこと）
- 表の計算の中で別のスクリプトが動くと、動いていたスクリプトの変数が消える。表を計算し直す行（RecalculateWS、RUNSCRIPT の式を入れる行）の後には何も書かない。
- 表の中からスクリプトを動かすと、Vectorworks が確認を出す。「常にスクリプトを実行」で大丈夫。

## ほかの人に渡すとき
渡すものは2つ。渡したあとは、GitHub のコードを直すと、相手のパソコンにも自動で届く（直しは全員に同時に届くので、使う人が増えたら直す前に共有する）。

### 渡す人がやること
1. **プラグインの定義ファイル**：`%APPDATA%\Nemetschek\Vectorworks\2024\Plug-ins\` の中の「棚」のファイル（拡張子 .vsm）をコピーして渡す。
2. **ひな形の図面ファイル**（お客様の図面は渡さない）：
   1. 新しい図面ファイルを作る。
   2. お客様の図面から、棚を1つ（コピーして新しい棚を置くための見本）と、紙面に置いた棚表を、コピーして貼り付ける。
   3. リソースマネージャで、お客様の図面の「AI」フォルダ（棚表を作る・棚の番号_自動などのスクリプト）を、新しい図面にドラッグする。
   4. 「棚ひな形.vwx」などの名前で保存して渡す。

### 受け取った人がやること（最初の1回だけ）
1. 受け取った「棚」のファイルを、自分の `%APPDATA%\Nemetschek\Vectorworks\<年版>\Plug-ins\` に入れる。
2. Vectorworks を立ち上げ直す。
3. ひな形の図面を開く（またはひな形から始める）。棚表を開いて閉じたとき、または PDF を書き出したときに「外部スクリプトを実行しようとしています」と出たら「常にスクリプトを実行」。
4. 棚を足すときは、見本の棚をコピーして貼り付け、大きさと中身を変える。
- インターネットにつながっていれば、コードは GitHub から自動で読み込まれる（`%APPDATA%\hako_vectorworks_tools\` に控えができる）。

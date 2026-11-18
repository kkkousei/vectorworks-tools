# 「AI」ボタンの本体
# Vectorworks には「AI」という名前のスクリプトを1つだけ置き、中身は README の loader（NAME = 'ai/menu.py'）。
# ダブルクリック → 一覧から番号を選ぶ → その機能を GitHub から読んで動かす。
# 棚表の中の =RUNSCRIPT('AI', 'bangou') から呼ばれたときは、一覧を出さずに番号の自動振り直しを動かす。
import vs, os, time, urllib.request

BASE = 'https://raw.githubusercontent.com/kkkousei/vectorworks-tools/main/'
DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'hako_vectorworks_tools')

# 一覧（表示名, ファイル）。機能を足すときはここに1行足す
MENU = [
    ('この図面を AI仕様にする（棚表などを入れる。テンプレートで1回）', 'ai/setup.py'),
    ('棚を1つ置く（画面の真ん中に置く）', 'tana/oku.py'),
    ('棚表を作り直す', 'tana/hyou.py'),
    ('古い描き方の棚（四角形＋レコード「仕様」）を「棚」に置き換える', 'tana/okikae.py'),
    ('図枠（日付・Plan Name・Designer・Director）をファイル名と案件台帳にそろえる', 'ai/zuwaku.py'),
]

# 表の中から呼ばれたとき（引数つき）に動かすもの
AUTO = {'bangou': 'tana/bangou.py'}


def load(name):
    """GitHub から読んで（5分ごと）、控えの中身を返す"""
    path = os.path.join(DIR, name.replace('/', '_'))
    if not os.path.exists(path) or time.time() - os.path.getmtime(path) > 300:
        try:
            with urllib.request.urlopen(BASE + name, timeout=5) as r:
                code = r.read()
            os.makedirs(DIR, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(code)
        except Exception:
            if os.path.exists(path):
                os.utime(path, None)
    return compile(open(path, encoding='utf-8').read(), path, 'exec')


arg = ''
try:
    arg = vs.WSScript_GetPrmStr(0)
except Exception:
    arg = ''

if arg in AUTO:
    exec(load(AUTO[arg]))
else:
    lines = ['番号を入れて OK を押してください', '']
    for i, (label, _) in enumerate(MENU, start=1):
        lines.append(str(i) + '. ' + label)
    ans = vs.StrDialog('\n'.join(lines), '1')
    if ans and ans.strip().isdigit() and 1 <= int(ans.strip()) <= len(MENU):
        exec(load(MENU[int(ans.strip()) - 1][1]))

# 図面の日付を、ファイル名の頭の日付にそろえる
# 例：ファイル名「2026.11.18_〇〇様邸.vwx」→ 図面の「2026.11.06」を「2026.11.18」に
# 日付だけが書いてある文字（例 2026.11.06）をすべて探して書き換える。
# シンボルの中・ビューポートの注釈の中も見る。ほかの文字には触らない。
# 動かし方は3つ（HIDUKE_MODE で分ける）
#  - 「AI」ボタンから（なし）：書き換えて、結果を知らせる
#  - 表のセルの式 =RUNSCRIPT('AI', 'hiduke') から：書き換えて、そのセルにファイル名の日付を出す
#  - 棚の番号の自動振り直し（tana/bangou.py）から（'text'）：書き換えるだけ。画面には何も出さない
#    → 棚表がある図面は、PDF書き出し・印刷・棚表を閉じたときに自動でそろう
import vs, re

PAT_FILE = re.compile(r'\s*(\d{4})[.\-_/]?(\d{1,2})[.\-_/]?(\d{1,2})')
PAT_TEXT = re.compile(r'\d{4}\s*[.\-/]\s*\d{1,2}\s*[.\-/]\s*\d{1,2}')

try:
    _mode = HIDUKE_MODE
except NameError:
    try:
        _mode = 'ws' if arg == 'hiduke' else 'menu'   # arg は menu.py から
    except NameError:
        _mode = 'menu'

m = PAT_FILE.match(vs.GetFName() or '')
if not m:
    if _mode == 'ws':
        vs.WSScript_SetResStr('【ファイル名に日付なし】')
    elif _mode == 'menu':
        vs.AlrtDialog('ファイル名の頭に日付（例 2026.11.18_）がないので、何もしませんでした。')
else:
    new = '%04d.%02d.%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    found = []

    def _cb(h):
        s = (vs.GetText(h) or '').strip()
        if PAT_TEXT.fullmatch(s):
            found.append((h, s))

    vs.ForEachObject(_cb, "(INSYMBOL & INVIEWPORT & (T=TEXT))")

    n = 0
    for h, s in found:
        if s != new:
            vs.SetText(h, new)
            vs.ResetObject(h)
            n += 1

    if _mode == 'ws':
        # 表の計算の中なので画面には何も出さない。これより後に何も書かない
        vs.WSScript_SetResStr(new)
    elif _mode == 'menu':
        if not found:
            vs.AlrtDialog('日付だけの文字が見つかりませんでした（日付が表の中にあるのかもしれません）。')
        else:
            vs.AlrtDialog('日付を ' + new + ' にしました（' + str(n) + 'か所を直しました。もともと同じだったもの ' + str(len(found) - n) + 'か所）。')

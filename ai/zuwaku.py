# 図枠（タイトル欄）を、ファイル名と案件台帳にそろえる
#  - Date.      ：ファイル名の頭の日付（「2026.11.18_〇〇様邸.vwx」→ 2026.11.18）
#  - Plan Name  ：ファイル名の日付のあと（「〇〇様邸」。「試し」「_ver2」などは外す）
#  - Designer・Director：図面があるフォルダ名の頭の引合コード（「〇〇〇〇〇_〇〇様」）で、
#    Googleドライブの「00_AI・仕組み/図面の担当一覧.csv」を引く（案件台帳から書き出したもの）。
#    名前は GitHub に入れない（このファイルは公開）。
# 日付：日付だけが書いてある文字（例 2026.11.06）をすべて書き換える。
# Plan Name など：見出しの文字（Plan Name / Designer / Director）の右、同じ高さにある文字を書き換える。
# シンボルの中・ビューポートの注釈の中も見る。見つからない所・分からない所は触らない。
# 動かし方（ZUWAKU_MODE）：なし＝「AI」ボタンから（結果を知らせる）／'auto'＝棚の番号の自動振り直しから（何も出さない）
import vs, os, re, csv

PAT_FILE = re.compile(r'\s*(\d{4})[.\-_/]?(\d{1,2})[.\-_/]?(\d{1,2})[\s._\-]*(.*)$')
PAT_TEXT = re.compile(r'\d{4}\s*[.\-/]\s*\d{1,2}\s*[.\-/]\s*\d{1,2}')
PAT_CODE = re.compile(r'^(\d{5})_')
CSV_NAME = os.path.join('00_AI・仕組み', '図面の担当一覧.csv')
LABELS = {'plan name': 'plan', 'designer': 'designer', 'director': 'director'}

try:
    _mode = ZUWAKU_MODE
except NameError:
    _mode = 'menu'

_fname = vs.GetFName() or ''
_fpath = vs.GetFPathName() or ''
_msgs = []


def _plan_name(rest):
    s = os.path.splitext(rest)[0]
    s = s.split('_')[0]
    s = re.sub(r'試し\d*$', '', s).strip()
    return s


def _tanto():
    """フォルダ名の引合コードで、担当一覧を引く。(デザイナー, ディレクター) か None"""
    d = os.path.dirname(_fpath)
    code = None
    root = None
    while d and os.path.dirname(d) != d:
        base = os.path.basename(d)
        if code is None:
            mm = PAT_CODE.match(base)
            if mm:
                code = mm.group(1)
        if os.path.exists(os.path.join(d, CSV_NAME)):
            root = d
            break
        d = os.path.dirname(d)
    if code is None:
        _msgs.append('フォルダ名に引合コードがないので、Designer・Director はそのままにしました。')
        return None
    if root is None:
        _msgs.append('「00_AI・仕組み/図面の担当一覧.csv」が見つからないので、Designer・Director はそのままにしました。')
        return None
    with open(os.path.join(root, CSV_NAME), encoding='utf-8-sig', newline='') as f:
        for row in csv.reader(f):
            if row and row[0].strip() == code and len(row) >= 3:
                return row[1].strip(), row[2].strip()
    _msgs.append('担当一覧に引合コード ' + code + ' がないので、Designer・Director はそのままにしました。')
    return None


m = PAT_FILE.match(_fname)
if not m:
    if _mode == 'menu':
        vs.AlrtDialog('ファイル名の頭に日付（例 2026.11.18_）がないので、何もしませんでした。')
else:
    want = {'date': '%04d.%02d.%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3)))}
    plan = _plan_name(m.group(4))
    if plan:
        want['plan'] = plan
    t = _tanto()
    if t:
        if t[0]:
            want['designer'] = t[0]
        if t[1]:
            want['director'] = t[1]

    texts = []   # (h, 文字, 親, x1, y1, x2, y2)

    def _cb(h):
        s = (vs.GetText(h) or '').strip()
        (x1, y1), (x2, y2) = vs.GetBBox(h)
        texts.append((h, s, vs.GetParent(h), min(x1, x2), max(y1, y2), max(x1, x2), min(y1, y2)))

    vs.ForEachObject(_cb, "(INSYMBOL & INVIEWPORT & (T=TEXT))")

    targets = []   # (h, 今の文字, 入れる文字)
    for h, s, p, x1, y1, x2, y2 in texts:
        if PAT_TEXT.fullmatch(s):
            targets.append((h, s, want['date']))
        key = LABELS.get(s.lower().rstrip('.:： '))
        if key and key in want:
            cy, hh = (y1 + y2) / 2, (y1 - y2)
            best = None
            for h2, s2, p2, a1, b1, a2, b2 in texts:
                if p2 != p or h2 == h or a1 <= x2:
                    continue
                if abs((b1 + b2) / 2 - cy) > max(hh, b1 - b2) * 0.6:
                    continue
                if LABELS.get(s2.lower().rstrip('.:： ')):
                    continue
                if best is None or a1 < best[1]:
                    best = (h2, a1, s2)
            if best:
                targets.append((best[0], best[2], want[key]))

    n = 0
    for h, s, new in targets:
        if s != new:
            vs.SetText(h, new)
            vs.ResetObject(h)
            n += 1

    if _mode == 'menu':
        lines = ['図枠をそろえました（' + str(n) + 'か所を直しました）。']
        for k, label in (('date', 'Date.'), ('plan', 'Plan Name'), ('designer', 'Designer'), ('director', 'Director')):
            if k in want:
                lines.append(label + '：' + want[k])
        vs.AlrtDialog('\n'.join(lines + _msgs))

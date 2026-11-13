# PDFと図面の情報を書き出す（Claude が確認に使う）
#  1. 棚の番号をそろえ、表と図面の表示（ビューポート）を新しくする
#  2. シートレイヤ（紙面）を全部、1つのPDFに書き出す
#  3. 部品（プラグイン）の情報の一覧と点検の結果を、テキストに書き出す
#  4. どちらも Google ドライブ（パソコン版で同期しているフォルダ）の「マイドライブ/Vectorworks確認」に置く
#     ドライブが見つからないときはデスクトップに置く
# 同じ図面を書き出し直すと上書きする（いつも最新の1つだけ残る）。
#
# 注意：表の計算の中で別のスクリプト（RUNSCRIPT）が動くと、このスクリプトの変数が消える。
# そのため、棚表の RUNSCRIPT の式をいったん外してから計算し直し、最後の行で元に戻す。
import vs, os, glob, datetime

PIO_TANA = '棚'
WS_TANA = '棚表'
OUT_NAME = 'Vectorworks確認'

if 'load' not in globals():
    # 「AI」ボタンを通さずに動かしたとき（試しのスクリプトなど）
    import time, urllib.request
    _BASE = 'https://raw.githubusercontent.com/kkkousei/vectorworks-tools/main/'
    _DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'hako_vectorworks_tools')

    def load(name):
        path = os.path.join(_DIR, name.replace('/', '_'))
        if not os.path.exists(path) or time.time() - os.path.getmtime(path) > 300:
            try:
                with urllib.request.urlopen(_BASE + name, timeout=5) as r:
                    code = r.read()
                os.makedirs(_DIR, exist_ok=True)
                with open(path, 'wb') as f:
                    f.write(code)
            except Exception:
                if os.path.exists(path):
                    os.utime(path, None)
        return compile(open(path, encoding='utf-8').read(), path, 'exec')


def drive_folder():
    """同期している Google ドライブの「マイドライブ」を探す（パスはパソコンごとに違うので書かない）"""
    cands = []
    if os.name == 'nt':
        for c in 'DEFGHIJKLMNOPQRSTUVWXYZ':
            for my in ('マイドライブ', 'My Drive'):
                cands.append(c + ':\\' + my)
    else:
        for my in ('マイドライブ', 'My Drive'):
            cands += glob.glob(os.path.expanduser('~/Library/CloudStorage/GoogleDrive-*/' + my))
            cands.append('/Volumes/GoogleDrive/' + my)
    for p in cands:
        if os.path.isdir(p):
            return p
    return None


def sheet_layers():
    out = []
    h = vs.FLayer()
    while h:
        if vs.GetObjectVariableInt(h, 154) == 2:  # 2 = シートレイヤ
            out.append(vs.GetLName(h))
        h = vs.NextLayer(h)
    return out


def worksheets():
    out = []
    lst, n = vs.BuildResourceList(18, 0, '')  # 18 = ワークシート
    for i in range(1, n + 1):
        name = vs.GetNameFromResourceList(lst, i)
        ws = vs.GetObject(name)
        if ws:
            out.append((name, ws))
    return out


def has_runscript(ws):
    rows, cols = vs.GetWSRowColumnCount(ws)
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            if 'RUNSCRIPT' in (vs.GetWSCellFormula(ws, r, c) or '').upper():
                return (r, c)
    return None


def plugin_objects():
    """全部のレイヤの部品（プラグイン）と、その入力欄の値（グループの中は見ない）"""
    out = []
    lay = vs.FLayer()
    while lay:
        h = vs.FInLayer(lay)
        while h:
            rec = vs.GetParametricRecord(h)
            if rec:
                rname = vs.GetName(rec)
                vals = []
                for i in range(1, vs.NumFields(rec) + 1):
                    f = vs.GetFldName(rec, i)
                    vals.append((f, vs.GetRField(h, rname, f)))
                (x1, y1), (x2, y2) = vs.GetBBox(h)
                out.append({'name': rname, 'layer': vs.GetLName(lay), 'vals': vals,
                            'pos': (round(min(x1, x2)), round(max(y1, y2)))})
            h = vs.NextObj(h)
        lay = vs.NextLayer(lay)
    return out


def tana_checks(objs):
    msgs = []
    tana = [o for o in objs if o['name'] == PIO_TANA]
    seen = {}
    for o in tana:
        v = dict(o['vals'])
        k = v.get('Kigou', '') or '（記号なし）'
        seen[k] = seen.get(k, 0) + 1
        miss = [lab for lab, f in (('品目', 'Hinmoku'), ('材料', 'Zairyo')) if v.get(f, '') in ('', '未選択')]
        if v.get('Hinmoku') != '固定棚':
            miss += [lab for lab, f in (('棚柱', 'Tanabashira'), ('金物', 'Kanamono')) if v.get(f, '') in ('', '未選択')]
        if not v.get('Iro', ''):
            miss.append('色')
        if miss:
            msgs.append(k + '：未入力 ' + '・'.join(miss))
    for k, n in seen.items():
        if n > 1:
            msgs.append(k + '：同じ記号が ' + str(n) + ' つ')
    return len(tana), msgs


# ---- 1. 棚の番号をそろえる・表を外す ----
tana_ws = vs.GetObject(WS_TANA)
auto_cell = has_runscript(tana_ws) if tana_ws else None
auto_formula = ''
if auto_cell:
    auto_formula = vs.GetWSCellFormula(tana_ws, auto_cell[0], auto_cell[1])
    vs.SetWSCellFormulaN(tana_ws, auto_cell[0], auto_cell[1], auto_cell[0], auto_cell[1], '')
    try:
        exec(load('tana/bangou.py'))  # 番号の振り直し（表の式を外したので、計算し直しても変数は消えない）
    except Exception:
        pass

skipped_ws = []
for name, ws in worksheets():
    if has_runscript(ws):
        skipped_ws.append(name)  # ほかの RUNSCRIPT がある表は計算し直さない（変数が消えるため）
    else:
        vs.RecalculateWS(ws)

vs.ForEachObject(vs.UpdateVP, '(T=VIEWPORT)')

# ---- 2. 書き出し先 ----
base = drive_folder()
if base:
    out_dir = os.path.join(base, OUT_NAME)
else:
    out_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
os.makedirs(out_dir, exist_ok=True)
fname = os.path.splitext(vs.GetFName())[0] or '名前なし'
pdf_path = os.path.join(out_dir, fname + '.pdf')
txt_path = os.path.join(out_dir, fname + '_情報.txt')

# ---- 3. PDF（シートレイヤを全部、上から順に） ----
first_layer = vs.GetLName(vs.ActLayer())
sheets = sheet_layers()
pdf_ok = False
pdf_err = ''
if sheets:
    try:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        vs.OpenPDFDocument(pdf_path)
        for s in sheets:
            vs.Layer(s)
            vs.ExportPDFPages('')
        vs.ClosePDFDocument()
        pdf_ok = os.path.exists(pdf_path)
    except Exception as e:
        pdf_err = str(e)
vs.Layer(first_layer)

# ---- 4. 情報の一覧 ----
objs = plugin_objects()
n_tana, checks = tana_checks(objs)
lines = ['図面：' + fname,
         '書き出した日時：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
         'PDF：' + ('書き出した（シートレイヤ ' + str(len(sheets)) + ' 枚：' + '、'.join(sheets) + '）' if pdf_ok
                   else '書き出せなかった' + ('（シートレイヤがない）' if not sheets else '') + ('（' + pdf_err + '）' if pdf_err else '')),
         '']
if skipped_ws:
    lines += ['計算し直さなかった表（RUNSCRIPT がある）：' + '、'.join(skipped_ws), '']
lines += ['■ 点検（棚 ' + str(n_tana) + ' 個）']
lines += ['・' + m for m in checks] if checks else ['・問題なし']
lines += ['', '■ 部品の情報（' + str(len(objs)) + ' 個。レイヤ・左上の位置・入力欄）']
for o in sorted(objs, key=lambda o: (o['name'], o['layer'], -o['pos'][1], o['pos'][0])):
    lines.append('[' + o['name'] + '] レイヤ ' + o['layer'] + '　位置 ' + str(o['pos'][0]) + ', ' + str(o['pos'][1]))
    lines.append('　' + '／'.join(f + '=' + v for f, v in o['vals']))
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

vs.AlrtDialog(('PDFと' if pdf_ok else 'PDFは書き出せませんでした。') + '情報の一覧を置きました：\n' + out_dir
              + ('' if base else '\n（Google ドライブが見つからなかったので、デスクトップに置きました）'))

# ---- 最後：棚表の自動の式を元に戻す（入れた瞬間に表の計算が走るので、これより後に何も書かない） ----
if auto_cell:
    vs.SetWSCellFormulaN(tana_ws, auto_cell[0], auto_cell[1], auto_cell[0], auto_cell[1], auto_formula)

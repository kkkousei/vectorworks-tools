# 棚の番号を自動で振り直す（棚表の RUNSCRIPT から呼ばれる）
# 棚表の1行目のいちばん右のセル：=RUNSCRIPT('棚の番号_自動')
# 表の計算の中で動くので、画面には何も出さない。
import vs

PIO = '棚'
items = []


def cb(h):
    k = vs.GetRField(h, PIO, 'Kigou')
    n = int(k[3:]) if k.startswith('SH-') and k[3:].isdigit() else 9999
    (x1, y1), (x2, y2) = vs.GetBBox(h)
    items.append((n, -max(y1, y2), min(x1, x2), h, k))


vs.ForEachObject(cb, "(PON='" + PIO + "')")

# 今の番号の順。同じ番号（コピーした棚）や番号なしは、上→下・左→右の順
items.sort(key=lambda t: (t[0], t[1], t[2]))

changed = False
for i, (n, _, _, h, old) in enumerate(items, start=1):
    new = 'SH-' + str(i)
    if old != new:
        vs.SetRField(h, PIO, 'Kigou', new)
        vs.ResetObject(h)
        changed = True

vs.WSScript_SetResStr('')

# 番号が変わったときだけ、棚表をもう一度計算し直す（2回目は変わらないので止まる）
# 注意：表の計算の中で別のスクリプトが動くと、この行のあとの変数は消える。この行より後に何も書かない。
if changed:
    vs.RecalculateWS(vs.GetObject('棚表'))

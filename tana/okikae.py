# 古い描き方の棚（四角形＋レコード「仕様」）を、プラグイン「棚」に置き換える
# 置き換えた四角形は消す（元に戻すときは Ctrl+Z）。
import vs

REC = '仕様'
PIO = '棚'
FIELDS = [('記号', 'Kigou'), ('品目', 'Hinmoku'), ('材料', 'Zairyo'), ('色', 'Iro'),
          ('枚数', 'Maisu'), ('棚柱', 'Tanabashira'), ('金物の色', 'Kanamono'),
          ('奥行が深い', 'OkuFukai'), ('備考', 'Bikou')]

olds = []
vs.ForEachObject(lambda h: olds.append(h), "((R IN ['" + REC + "']) & (T=RECT))")

done = []
for h in olds:
    (x1, y1), (x2, y2) = vs.GetBBox(h)
    w, d = abs(x2 - x1), abs(y1 - y2)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    n = vs.CreateCustomObjectN(PIO, (cx, cy), 0, False)
    vs.SetRField(n, PIO, 'LineLength', str(w))
    vs.SetRField(n, PIO, 'BoxWidth', str(d))
    for f_old, f_new in FIELDS:
        v = vs.GetRField(h, REC, f_old)
        if v:
            vs.SetRField(n, PIO, f_new, v)
    vs.ResetObject(n)
    done.append(vs.GetRField(n, PIO, 'Kigou'))
    vs.DelObject(h)

vs.AlrtDialog('置き換えた棚：' + str(len(done)) + '\n' + '\n'.join(sorted(done)))

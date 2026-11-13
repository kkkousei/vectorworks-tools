# 棚を1つ置く（画面の真ん中。幅600・奥行300。記号は自動で次の番号）
import vs

PIO = '棚'
h = vs.CreateCustomObjectN(PIO, vs.GetVCenter(), 0, False)
if h:
    vs.SetRField(h, PIO, 'LineLength', '600')
    vs.SetRField(h, PIO, 'BoxWidth', '300')
    vs.ResetObject(h)
else:
    vs.AlrtDialog('プラグイン「棚」が入っていません。')

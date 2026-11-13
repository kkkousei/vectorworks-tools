# 棚表を作り直す（見出しと式を入れ直す）
import vs

PIO = '棚'
WS_NAME = '棚表'
DB_ROW = 2
R = "'" + PIO + "'."
KOTEI = "(" + R + "'Hinmoku'='固定棚')"
LL = R + "'LineLength'"
BW = R + "'BoxWidth'"

cols = [
    ('記号',     "=" + R + "'Kigou'"),
    ('品目',     "=" + R + "'Hinmoku'"),
    ('材料',     "=IF(" + R + "'Zairyo'='未選択', '【未選択】', " + R + "'Zairyo')"),
    ('色',       "=" + R + "'Iro'"),
    ('幅',       "=IF(" + R + "'OkuFukai', MIN(" + LL + ", " + BW + "), MAX(" + LL + ", " + BW + "))"),
    ('奥行',     "=IF(" + R + "'OkuFukai', MAX(" + LL + ", " + BW + "), MIN(" + LL + ", " + BW + "))"),
    ('枚数',     "=" + R + "'Maisu'"),
    ('棚柱',     "=IF(" + KOTEI + ", '', IF(" + R + "'Tanabashira'='未選択', '【未選択】', IF(" + R + "'Tanabashira'='背面', '背面（Lアングル要）', " + R + "'Tanabashira')))"),
    ('金物の色', "=IF(" + KOTEI + ", '', IF(" + R + "'Kanamono'='未選択', '【未選択】', " + R + "'Kanamono'))"),
    ('備考',     "=" + R + "'Bikou'"),
]
AUTO = "=RUNSCRIPT('棚の番号_自動')"

ws = vs.GetObject(WS_NAME)
if ws is None:
    vs.AlrtDialog('棚表が見つかりません')
else:
    vs.SetWSCellFormulaN(ws, DB_ROW, 0, DB_ROW, 0, "=DATABASE((PON='" + PIO + "'))")
    rows, ncol = vs.GetWSRowColumnCount(ws)
    need = len(cols) + 1
    if ncol < need:
        vs.InsertWSColumns(ws, ncol + 1, need - ncol)
    for i, (title, formula) in enumerate(cols, start=1):
        vs.SetWSCellFormulaN(ws, 1, i, 1, i, title)
        vs.SetWSCellFormulaN(ws, DB_ROW, i, DB_ROW, i, formula)
    vs.SetWSColumnWidth(ws, need, need, 1)
    vs.AlrtDialog('棚表を作り直しました')
    # 最後に自動の式を入れる（入れた瞬間に表の計算が走るので、これより後に何も書かない）
    vs.SetWSCellFormulaN(ws, 1, need, 1, need, AUTO)

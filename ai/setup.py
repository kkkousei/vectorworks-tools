# この図面を AI仕様にする（テンプレートで1回。何度動かしても大丈夫）
#  - プラグイン「棚」が入っているか確かめる
#  - 棚表（ワークシート）がなければ作り、今開いているレイヤ（紙面）に置く
#  - 棚表の見出し・式・番号の自動振り直しを入れる（tana/hyou.py）
# 「AI」ボタン（ai/menu.py）から動かす。load() は menu.py のもの。
import vs

PIO = '棚'
WS_NAME = '棚表'

msgs = []

# 1. プラグイン「棚」が入っているか（試しに1つ作って、すぐ消す）
h = vs.CreateCustomObjectN(PIO, (0, 0), 0, False)
if not h:
    vs.AlrtDialog('プラグイン「棚」が入っていません。README の「受け取った人がやること」を先にしてください。')
else:
    vs.DelObject(h)

    # 2. 棚表がなければ作って、今のレイヤに置く
    ws = vs.GetObject(WS_NAME)
    if ws is None:
        ws = vs.CreateWS(WS_NAME, 2, 11)
        vs.SetWSCellFormulaN(ws, 2, 0, 2, 0, "=DATABASE((PON='" + PIO + "'))")
        vs.CreateWSImage(ws, vs.GetVCenter())
        vs.AlrtDialog('棚表を作って、今開いている所の真ん中に置きました。紙面の置きたい場所に動かしてください。')
    else:
        vs.AlrtDialog('棚表はもうあります。見出しと式だけ入れ直します。')

    # 3. 見出し・式・番号の自動振り直し（これより後に何も書かない）
    exec(load('tana/hyou.py'))

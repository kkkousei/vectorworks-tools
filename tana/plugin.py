# プラグイン「棚」（3点型オブジェクト）の本体
# Vectorworks の中には「読み込むだけの短いコード」（README の loader）だけを置き、
# 本体はこのファイルを GitHub から自動で読み込む。
#
# 第2版：品目が固定棚のとき、オブジェクト情報パレットの「棚柱」「金物」を隠す。
#   プラグイン定義の「イベントに対応」がオンのときだけ効く。オフのままでも、棚の描き方は第1版と同じ。
import vs

VERSION = '棚 v2（2026-11-13）'
MOJI = 5.7          # 記号の文字の大きさ
KAKUSU = ['Tanabashira', 'Kanamono']   # 固定棚のとき隠す欄
KAKUSU_HINMOKU = ['固定棚']            # 隠す品目

kObjOnInitXProperties = 5
kObjOnWidgetPrep = 41
kObjXPropHasUIOverride = 8
kObjXHasCustomWidgetVisibilities = 12
kObjectEventHandled = -8


def draw():
    ok, name, oh, rh, wh = vs.GetCustomObjectInfo()
    if not ok:
        return
    L = vs.PLineLength
    W = vs.PBoxWidth

    # 棚の形（白で塗りつぶした四角形）
    vs.Rect(-L / 2, W / 2, L / 2, -W / 2)
    r = vs.LNewObj()
    vs.SetFPat(r, 1)
    vs.SetFillBack(r, (65535, 65535, 65535))

    # 記号が空なら、図面の中の棚の最大番号＋1を付ける
    code = vs.PKigou
    if not code:
        nums = []

        def cb(h):
            k = vs.GetRField(h, name, 'Kigou')
            if k.startswith('SH-') and k[3:].isdigit():
                nums.append(int(k[3:]))

        vs.ForEachObject(cb, "(PON='" + name + "')")
        code = 'SH-' + str(max(nums) + 1 if nums else 1)
        vs.SetRField(oh, name, 'Kigou', code)

    # 記号の文字を棚の真ん中に出す（縦長の棚なら縦書きにする）
    vs.TextSize(MOJI)
    vs.TextJust(2)
    vs.TextVerticalAlign(3)
    vs.MoveTo(0, 0)
    vs.CreateText(code)
    if W > L:
        vs.HRotate(vs.LNewObj(), (0, 0), 90)


def widget_prep():
    ok, name, oh, rh, wh = vs.GetCustomObjectInfo()
    if ok:
        kakusu = vs.GetRField(oh, name, 'Hinmoku') in KAKUSU_HINMOKU
        for p in KAKUSU:
            vs.SetParameterVisibility(oh, p, not kakusu)
    vs.vsoSetEventResult(kObjectEventHandled)


theEvent, theButton = vs.vsoGetEventInfo()
if theEvent == kObjOnInitXProperties:
    vs.SetObjPropVS(kObjXPropHasUIOverride, True)
    vs.SetObjPropVS(kObjXHasCustomWidgetVisibilities, True)
    vs.vsoInsertAllParams()
elif theEvent == kObjOnWidgetPrep:
    widget_prep()
else:
    draw()

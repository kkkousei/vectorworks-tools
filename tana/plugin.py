# プラグイン「棚」（3点型オブジェクト）の本体
# Vectorworks の中には「読み込むだけの短いコード」（README の loader）だけを置き、
# 本体はこのファイルを GitHub から自動で読み込む。
#
# 第2版：品目が固定棚のとき、オブジェクト情報パレットの「棚柱」「金物」を隠す。
#   プラグイン定義の「イベントに対応」がオンのときだけ効く。オフのままでも、棚の描き方は第1版と同じ。
import vs, os, json

VERSION = '棚 v2.3（2026-11-13 調査用）'
DEBUG = True        # True のあいだ、棚の記号の下に調査用の小さな文字を出す
MOJI = 5.7          # 記号の文字の大きさ
# オブジェクト情報パレットに出す欄（並び順・表示名）。番号は欄の出し入れに使う
PARAMS = [('LineLength', '幅'), ('BoxWidth', '奥行'), ('Kigou', '記号'), ('Hinmoku', '品目'),
          ('Zairyo', '材料'), ('Iro', '色'), ('Maisu', '枚数'), ('Tanabashira', '棚柱'),
          ('Kanamono', '金物'), ('OkuFukai', '奥行が深い'), ('Bikou', '備考')]
KAKUSU = ['Tanabashira', 'Kanamono']   # 固定棚のとき隠す欄
KAKUSU_HINMOKU = ['固定棚']            # 隠す品目

kObjOnInitXProperties = 5
kObjOnWidgetPrep = 41
kObjXPropHasUIOverride = 8
kObjXHasCustomWidgetVisibilities = 12
kObjectEventHandled = -8

LOG = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'hako_vectorworks_tools', 'tana_debug.json')


def log_read():
    try:
        with open(LOG, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def log_add(key, extra=None):
    if not DEBUG:
        return
    d = log_read()
    d[key] = d.get(key, 0) + 1
    if extra is not None:
        d[key + '_last'] = extra
    try:
        with open(LOG, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
    except Exception:
        pass


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
    t = vs.LNewObj()
    if W > L:
        vs.HRotate(t, (0, 0), 90)

    if DEBUG:
        d = log_read()
        evs = ' '.join(k + ':' + str(v) for k, v in sorted(d.items()) if k.startswith('ev') and not k.endswith('_last'))
        info = VERSION + ' / ' + evs + ' / init=' + str(d.get('init', 0)) + ' ' + str(d.get('init_last', '')) + ' / prep=' + str(d.get('prep', 0))
        vs.TextSize(3)
        vs.MoveTo(0, -W / 2 - 50)
        vs.CreateText(info)


def widget_prep():
    ok, name, oh, rh, wh = vs.GetCustomObjectInfo()
    msg = 'ok=' + str(ok)
    if ok:
        hin = vs.GetRField(oh, name, 'Hinmoku')
        kakusu = hin in KAKUSU_HINMOKU
        msg += ' hin=' + hin + ' kakusu=' + str(kakusu)
        for i, (p, label) in enumerate(PARAMS, start=1):
            if p in KAKUSU:
                try:
                    vs.vsoWidgetSetVisible(i, not kakusu)
                except Exception as e:
                    msg += ' err=' + str(e)[:40]
    log_add('prep', msg)
    vs.vsoSetEventResult(kObjectEventHandled)


theEvent, theButton = vs.vsoGetEventInfo()
EVENT = theEvent
log_add('ev' + str(theEvent))
if theEvent == kObjOnInitXProperties:
    a = vs.SetObjPropVS(kObjXPropHasUIOverride, True)
    b = vs.SetObjPropVS(kObjXHasCustomWidgetVisibilities, True)
    res = []
    for i, (p, label) in enumerate(PARAMS, start=1):
        try:
            res.append(str(vs.vsoAddParamWidget(i, p, label))[0])
        except Exception as e:
            res.append('E')
    log_add('init', 'ui=' + str(a) + ' vis=' + str(b) + ' w=' + ''.join(res))
elif theEvent == kObjOnWidgetPrep:
    widget_prep()
else:
    draw()

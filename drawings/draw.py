#!/usr/bin/env python3
"""Nissan Caravan camper layout drawings. All dimensions in cm.

Coordinates: x = from left wall (passenger side) to right wall,
y = from tailgate forward, z = up from the plywood floor.
Writes SVG files next to this script; render.js turns them into PNG.
"""
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- measured (QQ) ----
W = 154        # floor width
L = 250        # plywood floor length, tailgate to front edge
SEAT = 274     # seat-back base (24 cm ahead of plywood edge)
H_SIDE = 127   # floor to roof at the side
H_MID = 130    # floor to roof in the middle
ARCH = dict(w=21, y0=49, y1=119, h=17)
STEP = 17      # right step well width, floored over
DOOR = 108     # sliding door opening (position along y is assumed)

# ---- design ----
BED_H = 40     # top of bed platform
MAT = 12       # mattress thickness
FIX = 123      # fixed bed length
FOOT = 62      # folding foot section (overhangs the seat box at night)
BED_END = FIX + FOOT          # 185
BOX_D = 55     # seat box / wardrobe depth
BOX_END = FIX + BOX_D         # 175
WARD_D = 35    # wardrobe depth along the van
WARD_Y0 = BOX_END - WARD_D    # 143
SEAT_H = 31    # seat box height (plus 3 cm fixed pad = 34)
PAD = 3
UP = MAT + 2 + PAD            # depth taken by the upright foot section
ADULT_W = 114  # adult bed / seat width (left)
WARD_W = W - ADULT_W          # 40
KIT_D = 45     # kitchen depth
KIT_Y = SEAT - KIT_D          # 229
BENCH_H = 70
SINK_X0 = W + STEP - KIT_D    # 126
DRAW_W = 44    # drawer stack width
CUP_X1 = 109   # cupboard (future fridge bay) right edge
GAR_Z1 = 107   # bottom of the top cupboard
UNIT_H = 70    # low unit beside the sink (battery bay), same height as the bench
STEP_H = 20    # raised step behind the seats: height above the ply floor (ESTIMATE, to be measured)
STEP_D = 24    # raised step depth
OH = dict(x0=124, x1=154, y0=2, y1=143, z0=97, z1=126)   # overhead clothes cabinet, right wall
TOP_D = 22
WIN = (52, 104, BENCH_H + 6, BENCH_H + 26)

# suitcases lying flat: (name, x0, y0, size along x, size along y, thickness)
CASES = [
    ("28寸软箱", 27.8, 42, 48, 81, 29),
    ("28寸黑色", 79.6, 42, 48, 81, 29),
    ("24寸", 5, 0, 66, 39, 31.5),
    ("20寸", 71, 0, 47, 42, 27),
]
POCKET_X = 120   # laundry pocket: x 120..154, y 0..49

FONT = "WenQuanYi Zen Hei, sans-serif"
C = dict(
    floor="#efe9df", ply="#d9b98a", ply2="#c9a572", mat="#8fa6b8",
    mat2="#a9bccb", case="#7c6f9b", kit="#e6d3b3", top="#b98b56",
    ward="#c7a06c", steel="#b8c0c6", toilet="#f4f4f1", fridge="#dfe6ea",
    door="#f1e3c8", arch="#9a9a9a", line="#3a3a3a", dim="#b02a2a",
    text="#1d1d1d", wall="#6b6b6b", seat="#5f6770",
)


# ------------------------------------------------------------------ helpers
def svg_open(w, h, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="{FONT}">',
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
        f'<text x="{w/2}" y="34" font-size="24" text-anchor="middle" '
        f'fill="{C["text"]}" font-weight="bold">{title}</text>',
    ]


def rect(x, y, w, h, fill, stroke=None, sw=1.2, extra=""):
    stroke = stroke or C["line"]
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x0, y0, x1, y1, stroke, sw=1.5, extra=""):
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def text(x, y, s, size=14, anchor="middle", fill=None, rot=None, bold=False):
    fill = fill or C["text"]
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    fw = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}"{tr}{fw}>{s}</text>')


def mtext(x, y, lines, size=14, fill=None, lh=1.25):
    out = []
    y0 = y - (len(lines) - 1) * size * lh / 2
    for i, s in enumerate(lines):
        out.append(text(x, y0 + i * size * lh + size * 0.35, s, size, fill=fill))
    return "".join(out)


def dim_h(x0, x1, y, label):
    c = C["dim"]
    return (line(x0, y, x1, y, c, 1) + line(x0, y - 5, x0, y + 5, c, 1)
            + line(x1, y - 5, x1, y + 5, c, 1)
            + text((x0 + x1) / 2, y - 5, label, 13, fill=c))


def dim_v(x, y0, y1, label, side=-1):
    c = C["dim"]
    return (line(x, y0, x, y1, c, 1) + line(x - 5, y0, x + 5, y0, c, 1)
            + line(x - 5, y1, x + 5, y1, c, 1)
            + text(x + side * 7, (y0 + y1) / 2, label, 13, fill=c, rot=-90))


def shade(hexcol, f):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (max(0, min(255, int(v * f))) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


# ------------------------------------------------------------------ plan
def plan(mode):
    """mode: 'day', 'night' or 'under'. Front of the van at the top."""
    S = 3.4
    ox, oy = 290, 130
    Wpx = 1000
    Hpx = int(oy + SEAT * S + 150)
    titles = {"day": "白天（床脚收起）", "night": "晚上（床放平）", "under": "床面以下：箱子和支撑"}
    o = svg_open(Wpx, Hpx, "俯视图 · " + titles[mode])

    def X(x):
        return ox + x * S

    def Y(y):
        return oy + (SEAT - y) * S

    def box(x0, y0, x1, y1, fill, label=None, size=13, **kw):
        s = rect(X(x0), Y(y1), (x1 - x0) * S, (y1 - y0) * S, fill, **kw)
        if label:
            s += mtext(X((x0 + x1) / 2), Y((y0 + y1) / 2), label, size)
        return s

    under = mode == "under"
    o.append(box(0, 0, W, L, C["floor"], sw=2.5, stroke=C["wall"]))
    o.append(box(0, L, W, SEAT, "#e3ddd2", sw=2.5, stroke=C["wall"]))
    o.append(box(W, BOX_END, W + STEP, SEAT, "#e3ddd2", stroke=C["wall"]))
    o.append(box(0, 0, W, FIX, C["ply"]))
    # suitcases
    ex = "" if under else 'stroke-dasharray="6 4" fill-opacity="0.5"'
    for (nm, x0, y0, dx, dy, th) in CASES:
        lab = [nm, f"{max(dx,dy)}×{min(dx,dy)}×{th:g}"] if under else None
        o.append(box(x0, y0, x0 + dx, y0 + dy, C["case"], lab, 12, extra=ex))
    for x0 in (0, W - ARCH["w"]):
        o.append(box(x0, ARCH["y0"], x0 + ARCH["w"], ARCH["y1"], C["arch"], ["轮拱"] if under else None, 11,
                     extra='fill-opacity="0.7"'))
    if under:
        # supports
        for xx in (25.9, 77.7, 129.5):
            o.append(line(X(xx), Y(42), X(xx), Y(FIX), "#3b2a12", 5))
        o.append(line(X(POCKET_X), Y(0), X(POCKET_X), Y(42), "#3b2a12", 5))
        o.append(line(X(0), Y(FIX), X(W), Y(FIX), "#3b2a12", 5))
        for yy in (1, 41):
            o.append(line(X(0), Y(yy), X(POCKET_X), Y(yy), "#b02a2a", 4, 'stroke-dasharray="10 5"'))
        o.append(mtext(X(137), Y(22), ["脏衣格", "34×49"], 12))
        o.append(text(X(52), Y(114), "粗线 = 竖板（床的腿）", 12, fill="#ffffff", bold=True))
        o.append(text(X(60), Y(46), "红色虚线 = 40×40 钢方管", 12, fill=C["dim"]))
        o.append(box(0, FIX, 40, BOX_END, C["toilet"], ["马桶", "高≤32"], 13))
        o.append(box(40, FIX, ADULT_W, BOX_END, C["ply2"], ["座位箱内部", "74 × 55 × 高29"], 14))
        o.append(box(ADULT_W, FIX, W, WARD_Y0, C["ply2"], ["小格", "40×20"], 11))
        for i, (cx, cy) in enumerate(((52, 70), (104, 70), (38, 12), (94, 12))):
            o.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="13" fill="#ffffff" stroke="#b02a2a" stroke-width="2"/>')
            o.append(text(X(cx), Y(cy) + 5, "①①②②"[i], 15, fill=C["dim"], bold=True))
    elif mode == "night":
        o.append(box(2, 2, ADULT_W - 1, FIX - 1, C["mat"], [f"大人床垫 114 × {FIX}"], 15, extra='fill-opacity="0.82"'))
        o.append(box(40, FIX, ADULT_W - 1, BED_END - 1, C["mat"], [f"床脚段 {FOOT}", f"（前{BED_END-BOX_END}厘米悬空）"], 13,
                     extra='fill-opacity="0.82"'))
        o.append(box(2, FIX, 40, BED_END - 1, C["mat2"], ["小掀盖", "下:马桶"], 12, extra='fill-opacity="0.9"'))
    else:
        o.append(box(2, 2, ADULT_W - 1, FIX - 1, C["mat"], ["大人床垫（不用收）", f"114 × {FIX}"], 15,
                     extra='fill-opacity="0.82"'))
        o.append(box(0, FIX, ADULT_W, FIX + UP, C["seat"], None))
        o.append(text(X(ADULT_W / 2), Y(FIX + UP / 2) + 4, "床脚段竖起 = 靠背（占17）", 12, fill="#ffffff"))
        o.append(box(0, FIX + UP, 40, BOX_END, C["toilet"], ["马桶", "（掀盖）"], 13))
        o.append(box(40, FIX + UP, ADULT_W, BOX_END, C["ply2"], ["座位 高34", "宽74 × 深38"], 14))
    if not under:
        o.append(box(ADULT_W, FIX, W, WARD_Y0, C["ply"], None))
        o.append(box(ADULT_W + 1, 2, W - 2, WARD_Y0 - 1, C["mat2"], ["小珵", f"40×{WARD_Y0}"], 13, extra='fill-opacity="0.85"'))
        o.append(rect(X(W - 32), Y(32), 30 * S, 30 * S, "#ffffff", stroke="#b02a2a",
                      extra='stroke-dasharray="5 4" fill-opacity="0.6"'))
        o.append(text(X(W - 17), Y(15), "投衣口", 11, fill=C["dim"]))
        o.append(line(X(128), Y(WARD_Y0 - 3), X(128), Y(WARD_Y0 - 33), "#333", 3))
        o.append(text(X(124), Y(WARD_Y0 - 18), "挂杆", 11, anchor="end"))
    # wardrobe
    o.append(box(ADULT_W, WARD_Y0, W, BOX_END, C["ward"], ["矮柜 高70", "顶面当台面", "下:电池"], 11, sw=2))
    if not under:
        o.append(rect(X(OH["x0"]), Y(OH["y1"]), (OH["x1"] - OH["x0"]) * S, (OH["y1"] - OH["y0"]) * S, "none",
                      stroke="#8a5a1c", sw=2.5, extra='stroke-dasharray="8 4"'))
        o.append(text(X(139), Y(75), "上方：吊柜（衣服）", 12, fill="#8a5a1c", rot=-90, bold=True))
    # aisle
    aisle = KIT_Y - (BOX_END if mode != "night" else BED_END)
    o.append(mtext(X(62), Y((KIT_Y + (BOX_END if mode != "night" else BED_END)) / 2), [f"过道 {aisle}"], 15))
    # sink leg
    o.append(box(SINK_X0, BOX_END, W + STEP, KIT_Y, C["kit"], None, sw=2))
    o.append(f'<rect x="{X(SINK_X0+6):.1f}" y="{Y(KIT_Y-6):.1f}" width="{33*S:.1f}" height="{38*S:.1f}" '
             f'rx="8" fill="{C["steel"]}" stroke="{C["line"]}"/>')
    o.append(mtext(X(SINK_X0 + 22.5), Y(KIT_Y - 25), ["水槽", "下:垃圾桶"], 13))
    # front row
    o.append(box(0, KIT_Y, DRAW_W, SEAT, C["kit"], ["下:抽屉", "宽44"], 13, sw=2))
    o.append(box(DRAW_W, KIT_Y, CUP_X1, SEAT, C["kit"], ["下:储物柜 宽65", "（以后可放冰箱）"], 13, sw=2))
    o.append(box(CUP_X1, KIT_Y, W + STEP, SEAT, C["kit"], ["转角", "下:水桶"], 13, sw=2))
    o.append(rect(X(0), Y(SEAT), (W + STEP) * S, TOP_D * S, "none", stroke="#8a5a1c", sw=2,
                  extra='stroke-dasharray="7 4"'))
    o.append(text(X(30), Y(SEAT - 8), "上方：顶柜", 11, fill="#8a5a1c"))
    o.append(text(X(78), Y(SEAT - 6), "小窗", 11, fill="#2a6f9e"))
    # fold-out table at left door
    o.append(f'<rect x="{X(-40):.1f}" y="{Y(SEAT-2):.1f}" width="{40*S:.1f}" height="{41*S:.1f}" '
             f'fill="{C["top"]}" fill-opacity="0.35" stroke="{C["line"]}" stroke-dasharray="5 4"/>')
    o.append(mtext(X(-20), Y(SEAT - 22), ["翻板桌", "（车外）"], 12))
    # seats
    o.append(rect(X(8), Y(SEAT + 14), 56 * S, 12 * S, C["seat"], extra='rx="6"'))
    o.append(rect(X(90), Y(SEAT + 14), 56 * S, 12 * S, C["seat"], extra='rx="6"'))
    o.append(text(X(36), Y(SEAT + 8) + 5, "副驾座椅", 12, fill="#fff"))
    o.append(text(X(118), Y(SEAT + 8) + 5, "驾驶座椅", 12, fill="#fff"))
    # doors
    o.append(text(X(-6), Y(SEAT - 62), "左门（进出）", 13, anchor="end", fill="#2e7d32", bold=True))
    o.append(text(X(W + STEP + 6), Y(SEAT - 62), "右门", 13, anchor="start", fill="#2e7d32", bold=True))
    o.append(text(X(W + STEP + 6), Y(SEAT - 62) + 17, "（拿水桶）", 12, anchor="start", fill="#2e7d32"))
    o.append(line(X(0), Y(SEAT), X(0), Y(SEAT - DOOR), "#2e7d32", 5))
    o.append(line(X(W + STEP), Y(SEAT), X(W + STEP), Y(BOX_END), "#2e7d32", 5))
    o.append(text(X(W / 2), Y(-9), "尾门（头朝这边）", 15, bold=True))
    # dimensions
    yb = Y(0) + 62
    o.append(dim_h(X(0), X(W), yb, f"车内宽 {W}"))
    o.append(dim_h(X(0), X(ADULT_W), yb + 30, f"{ADULT_W}"))
    o.append(dim_h(X(ADULT_W), X(W), yb + 30, f"{WARD_W}"))
    xl = X(-40) - 40
    o.append(dim_v(xl, Y(FIX), Y(0), f"固定床 {FIX}"))
    o.append(dim_v(xl, Y(BOX_END), Y(FIX), f"座位箱 {BOX_D}"))
    o.append(dim_v(xl, Y(KIT_Y), Y(BOX_END), f"过道 {KIT_Y-BOX_END}"))
    o.append(dim_v(xl, Y(SEAT), Y(KIT_Y), f"厨房 {KIT_D}"))
    o.append(dim_v(xl - 34, Y(L), Y(0), f"木地板 {L}"))
    o.append(dim_v(xl - 34, Y(SEAT), Y(L), "24"))
    o.append(dim_h(X(W), X(W + STEP), Y(SEAT) - 10, "17"))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ side view
def side():
    S = 3.4
    ox, oy = 90, 90
    Wpx = int(ox + (SEAT + 40) * S + 60)
    Hpx = int(oy + H_MID * S + 130)
    o = svg_open(Wpx, Hpx, "侧面图 · 从左侧看（白天）")

    def X(y):
        return ox + y * S

    def Z(z):
        return oy + (H_MID - z) * S

    def box(y0, z0, y1, z1, fill, label=None, size=13, **kw):
        s = rect(X(y0), Z(z1), (y1 - y0) * S, (z1 - z0) * S, fill, **kw)
        if label:
            s += mtext(X((y0 + y1) / 2), Z((z0 + z1) / 2), label, size)
        return s

    o.append(f'<path d="M{X(0):.1f},{Z(0):.1f} L{X(0):.1f},{Z(H_MID-4):.1f} Q{X(0):.1f},{Z(H_MID):.1f} {X(6):.1f},{Z(H_MID):.1f} '
             f'L{X(SEAT+30):.1f},{Z(H_MID):.1f}" fill="none" stroke="{C["wall"]}" stroke-width="3"/>')
    o.append(line(X(0), Z(0), X(L), Z(0), C["wall"], 3))
    o.append(line(X(L), Z(0), X(L), Z(-6), C["wall"], 3))
    o.append(line(X(L), Z(-6), X(SEAT + 30), Z(-6), C["wall"], 3))
    # suitcases
    o.append(box(0, 0, 42, 31.5, C["case"], ["24寸", "20寸"], 12, extra='fill-opacity="0.6"'))
    o.append(box(42, 0, FIX, 29, C["case"], ["两个28寸（并排）"], 12, extra='fill-opacity="0.6"'))
    o.append(box(ARCH["y0"], 0, ARCH["y1"], ARCH["h"], C["arch"], None, extra='fill-opacity="0.3" stroke-dasharray="4 3"'))
    # platform + mattress
    o.append(box(0, BED_H - 1.8, FIX, BED_H, C["ply"]))
    o.append(box(FIX - 1.8, 0, FIX, BED_H, C["ply"]))
    o.append(box(1, BED_H, FIX - 0.5, BED_H + MAT, C["mat"], [f"主床垫 {FIX} × 厚12"], 13))
    # foot section upright
    zt = BED_H + MAT
    o.append(box(FIX, zt, FIX + MAT, zt + FOOT, C["mat"], None))
    o.append(text(X(FIX + MAT / 2), Z(zt + FOOT / 2), f"床脚床垫 {FOOT} × 厚12", 12, rot=-90))
    o.append(box(FIX + MAT, zt, FIX + MAT + 2, zt + FOOT, C["ply"]))
    o.append(box(FIX + MAT + 2, zt + 4, FIX + UP, zt + FOOT - 4, C["seat"]))
    o.append(f'<circle cx="{X(FIX):.1f}" cy="{Z(zt):.1f}" r="6" fill="#b02a2a"/>')
    o.append(text(X(FIX) - 10, Z(zt) - 10, "转轴", 12, anchor="end", fill=C["dim"]))
    o.append(text(X(FIX + UP + 4), Z(zt + FOOT - 12), "靠背垫", 12, anchor="start"))
    # night position
    o.append(box(FIX, BED_H - 2, BED_END, BED_H, "none", None, extra='stroke-dasharray="5 4"', stroke="#b02a2a"))
    o.append(box(FIX, BED_H, BED_END, zt, "none", None, extra='stroke-dasharray="5 4"', stroke="#b02a2a"))
    o.append(text(X(FIX + 40), Z(BED_H + 5), "晚上放平的位置", 11, fill=C["dim"]))
    o.append(text(X(BED_END + 3), Z(BED_H + 5), f"悬空{BED_END-BOX_END}", 11, anchor="start", fill=C["dim"]))
    # seat box
    o.append(box(FIX, 0, BOX_END, SEAT_H, C["ply2"], ["座位箱", "高31"], 13))
    o.append(box(FIX + UP, SEAT_H, BOX_END, SEAT_H + PAD, C["seat"]))
    # wardrobe outline
    o.append(box(WARD_Y0, 0, BOX_END, UNIT_H, "none", None, extra='stroke-dasharray="7 5"', stroke="#8a6a3c"))
    o.append(text(X(WARD_Y0 + WARD_D / 2), Z(UNIT_H + 3), "矮柜（右侧）", 11, fill="#8a6a3c"))
    o.append(box(OH["y0"], OH["z0"], OH["y1"], OH["z1"], "none", None, extra='stroke-dasharray="7 5"', stroke="#8a6a3c"))
    o.append(text(X(60), Z((OH["z0"] + OH["z1"]) / 2) + 4, "右侧墙吊柜（衣服）141 × 30 × 29", 12, fill="#8a6a3c"))
    # kitchen
    T = BENCH_H - 3
    o.append(box(KIT_Y, 0, SEAT, T, C["kit"], ["厨房柜"], 13))
    o.append(box(KIT_Y - 1, T, SEAT, BENCH_H, C["top"]))
    o.append(box(SEAT - 2, BENCH_H, SEAT, H_SIDE - 2, C["ply"], None))
    o.append(box(L, 0, SEAT, STEP_H, "#8d8d8d", ["台阶", "估20高"], 10, extra='fill-opacity="0.85"'))
    o.append(box(SEAT - TOP_D, GAR_Z1, SEAT - 2, H_SIDE - 1, C["door"], ["顶柜"], 11))
    # front seat
    o.append(f'<path d="M{X(SEAT+2):.1f},{Z(20):.1f} L{X(SEAT+12):.1f},{Z(95):.1f} L{X(SEAT+22):.1f},{Z(95):.1f} '
             f'L{X(SEAT+14):.1f},{Z(20):.1f} Z" fill="{C["seat"]}" stroke="{C["line"]}"/>')
    o.append(text(X(SEAT + 26), Z(60), "前排座椅", 12, rot=-90))
    # dims
    zb = Z(0) + 40
    o.append(dim_h(X(0), X(FIX), zb, f"固定床 {FIX}"))
    o.append(dim_h(X(FIX), X(BOX_END), zb, f"座位箱 {BOX_D}"))
    o.append(dim_h(X(BOX_END), X(KIT_Y), zb, f"过道 {KIT_Y-BOX_END}"))
    o.append(dim_h(X(KIT_Y), X(SEAT), zb, f"{KIT_D}"))
    o.append(dim_h(X(0), X(L), zb + 34, f"木地板 {L}"))
    o.append(dim_h(X(L), X(SEAT), zb + 34, "24"))
    xl = X(0) - 30
    o.append(dim_v(xl, Z(BED_H), Z(0), f"床面 {BED_H}"))
    o.append(dim_v(xl - 30, Z(H_MID), Z(0), f"中间车高 {H_MID}"))
    o.append(dim_v(X(FIX + 42), Z(H_MID), Z(SEAT_H + PAD), f"坐高空间 {H_MID-SEAT_H-PAD}", side=1))
    o.append(dim_v(X(KIT_Y) - 12, Z(BENCH_H), Z(0), f"台面 {BENCH_H}"))
    o.append(dim_v(X(30), Z(H_MID), Z(BED_H + MAT), f"床上净高 {H_MID-BED_H-MAT}", side=1))
    o.append(text(X(-6), Z(H_MID / 2), "尾门", 13, rot=-90, fill=C["wall"]))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ kitchen elevation
def kitchen():
    S = 4.6
    ox, oy = 130, 90
    EW = W + STEP
    Wpx = int(ox + (EW + 38 + 45 + 50 + WARD_D) * S + 200)
    Hpx = int(oy + H_MID * S + 360)
    o = svg_open(Wpx, Hpx, "厨房细节：正面、剖面、每个柜子的尺寸；矮柜剖面")

    def X(x):
        return ox + x * S

    def Z(z):
        return oy + (H_MID - z) * S

    def box(x0, z0, x1, z1, fill, label=None, size=13, **kw):
        s = rect(X(x0), Z(z1), (x1 - x0) * S, (z1 - z0) * S, fill, **kw)
        if label:
            s += mtext(X((x0 + x1) / 2), Z((z0 + z1) / 2), label, size)
        return s

    def knob(x, z):
        return f'<circle cx="{X(x):.1f}" cy="{Z(z):.1f}" r="5" fill="#777" stroke="#333"/>'

    def num(x, z, n):
        return (f'<circle cx="{X(x):.1f}" cy="{Z(z):.1f}" r="14" fill="#ffffff" stroke="#b02a2a" stroke-width="2"/>'
                + text(X(x), Z(z) + 6, n, 17, fill=C["dim"], bold=True))

    T = BENCH_H - 3
    TOPZ = H_SIDE - 1
    o.append(text(X(EW / 2), Z(H_SIDE) - 20, "正面（坐在座位上往车头看）", 14, bold=True))
    o.append(box(0, 0, EW, H_SIDE, "#f6f4ef", stroke=C["wall"], sw=2.5))
    # two drawers: shallow below (short, in front of the step), deep above (over the step)
    o.append(box(2, 3, 42, 22, C["door"], ["下：浅抽屉", "前后深约19"], 11))
    o.append(knob(22, 19))
    o.append(box(2, 24, 42, T - 2, C["door"], ["上：深抽屉", "前后深40 · 内高约36"], 11))
    o.append(knob(22, T - 6))
    o.append(num(8, 56, "1"))
    o.append(box(46, 3, 76.5, T - 2, C["door"], None))
    o.append(box(76.5, 3, 107, T - 2, C["door"], None))
    o.append(knob(73, 52))
    o.append(knob(80, 52))
    o.append(line(X(47), Z(STEP_H + 4), X(106), Z(STEP_H + 4), "#a08a5c", 1.5, 'stroke-dasharray="6 4"'))
    o.append(line(X(47), Z(45), X(106), Z(45), "#a08a5c", 1.5, 'stroke-dasharray="6 4"'))
    o.append(mtext(X(76.5), Z(34), ["对开门 · 放电器和锅"], 11))
    o.append(num(52, 60, "2"))
    o.append(box(111, 3, SINK_X0 - 1, T - 2, C["door"], None))
    o.append(num(118, 60, "3"))
    o.append(box(SINK_X0, 0, EW, T, C["kit"], ["水槽柜", "（门朝过道）"], 12, extra='fill-opacity="0.9"'))
    o.append(num(SINK_X0 + 8, 40, "4"))
    o.append(box(0, T, EW, BENCH_H, C["top"]))
    o.append(box(SINK_X0 + 6, BENCH_H - 15, EW - 6, BENCH_H, C["steel"], ["水槽 深15"], 11))
    # open wall with the cab window and a curtain
    o.append(box(WIN[0], WIN[2], WIN[1], WIN[3], "#cfe6f5", ["小窗（位置待量）"], 12))
    o.append(line(X(WIN[0] - 6), Z(WIN[3] + 3), X(WIN[1] + 6), Z(WIN[3] + 3), "#555", 3))
    o.append(text(X(WIN[1] + 10), Z(WIN[3] + 2), "窗帘杆", 11, anchor="start"))
    o.append(num(WIN[0] + 6, WIN[3] - 5, "6"))
    o.append(text(X(24), Z(88), "墙面留空", 13, fill="#999"))
    o.append(text(X(140), Z(88), "墙面留空", 13, fill="#999"))
    # top cupboard with sliding doors
    o.append(box(0, GAR_Z1, EW, TOPZ, "#e4d3b4", None))
    for i, (x0, x1) in enumerate(((0, 60), (55, 116), (111, EW))):
        o.append(box(x0 + 0.6, GAR_Z1 + 1 + (i % 2) * 0.8, x1 - 0.6, TOPZ - 1, C["door"], None))
    o.append(text(X(EW / 2), Z(GAR_Z1 + 8), "← 推拉门 →", 13))
    o.append(num(8, GAR_Z1 + 10, "5"))
    o.append(box(-22, 40, 0, 42, C["top"], None, extra='stroke-dasharray="5 4"'))
    o.append(text(X(-11), Z(46), "翻板", 11))
    o.append(text(X(-11), Z(52), "高度待定", 10, fill=C["dim"]))
    zb = Z(0) + 36
    o.append(dim_h(X(0), X(44), zb, "44"))
    o.append(dim_h(X(44), X(109), zb, "65"))
    o.append(dim_h(X(109), X(EW), zb, "62（含外伸17）"))
    xl = X(0) - 34
    o.append(dim_v(xl, Z(BENCH_H), Z(0), f"台面 {BENCH_H}"))
    o.append(dim_v(xl, Z(GAR_Z1), Z(BENCH_H), "37"))
    o.append(dim_v(xl, Z(TOPZ), Z(GAR_Z1), "19"))
    o.append(dim_v(xl - 34, Z(H_SIDE), Z(0), f"侧边车高 {H_SIDE}"))

    # ---- side section through the drawer unit
    sx = EW + 38

    def SX(v):
        return ox + (sx + v) * S

    def sbox(a0, z0, a1, z1, fill, label=None, size=11, **kw):
        s = rect(SX(a0), Z(z1), (a1 - a0) * S, (z1 - z0) * S, fill, **kw)
        if label:
            s += mtext(SX((a0 + a1) / 2), Z((z0 + z1) / 2), label, size)
        return s
    o.append(text(SX(22), Z(H_SIDE) - 20, "侧面剖开（抽屉柜）", 14, bold=True))
    o.append(line(SX(45), Z(0), SX(45), Z(H_SIDE), C["wall"], 3))
    o.append(line(SX(-6), Z(0), SX(45), Z(0), C["wall"], 3))
    o.append(sbox(0, 0, 45, T, C["kit"], None))
    o.append(sbox(45 - STEP_D, 0, 45, STEP_H, "#8d8d8d", ["台阶", "24深", "估20高"], 10))
    o.append(sbox(1, 3, 20, 21, C["door"], ["浅抽屉"], 10))
    o.append(sbox(1, 24, 41, T - 3, C["door"], ["深抽屉", "40深"], 11))
    o.append(sbox(-1, T, 45, BENCH_H, C["top"]))
    o.append(sbox(45 - TOP_D, GAR_Z1, 45, TOPZ, C["door"], ["顶柜", "深22"]))
    o.append(text(SX(48), Z(60), "座椅背", 11, anchor="start", fill=C["wall"]))
    o.append(text(SX(-4), Z(12), "过道", 11, anchor="end", fill=C["wall"]))
    o.append(dim_h(SX(0), SX(45), Z(0) + 36, "45"))

    # ---- low unit section
    wx = sx + 45 + 50

    def WX(v):
        return ox + (wx + v) * S

    def wbox(a0, z0, a1, z1, fill, label=None, size=11, **kw):
        s = rect(WX(a0), Z(z1), (a1 - a0) * S, (z1 - z0) * S, fill, **kw)
        if label:
            s += mtext(WX((a0 + a1) / 2), Z((z0 + z1) / 2), label, size)
        return s
    o.append(text(WX(WARD_D / 2), Z(UNIT_H) - 20, "水槽旁矮柜（从座位这边看）", 14, bold=True))
    o.append(wbox(0, 0, WARD_D, UNIT_H - 3, C["ward"], None, sw=2))
    o.append(wbox(-1, UNIT_H - 3, WARD_D, UNIT_H, C["top"]))
    o.append(wbox(2, 2, WARD_D - 2, 48, "#3d4a55", None))
    o.append(wbox(4, 4, 21, 25, "#6f8fa6", ["电池1"], 10))
    o.append(wbox(4, 26, 21, 47, "#8aa3b5", ["电池2"], 10))
    o.append(wbox(23, 4, 32, 36, "#55636e", ["控", "制", "器"], 10))
    o.append(wbox(0, 49, WARD_D, 51, C["ply"]))
    o.append(wbox(3, 53, 20, 65, "#111", None))
    o.append(wbox(22, 53, WARD_D - 2, 65, C["door"], ["小格"], 10))
    o.append(text(WX(WARD_D + 2), Z(59), "电源面板", 11, anchor="start"))
    o.append(text(WX(WARD_D + 2), Z(49), "活动底板", 11, anchor="start"))
    o.append(text(WX(WARD_D + 2), Z(25), "电器仓 高50", 11, anchor="start"))
    o.append(text(WX(WARD_D + 2), Z(UNIT_H - 1), "顶面 = 沥水/备菜台", 11, anchor="start"))
    o.append(dim_h(WX(0), WX(WARD_D), Z(0) + 36, f"深 {WARD_D}"))
    o.append(dim_v(WX(0) - 12, Z(UNIT_H), Z(0), f"高 {UNIT_H}"))

    rows = [
        ("1", "抽屉柜", "44 × 45 × 67", "下：浅抽屉，前后约19（让开座椅后的台阶）；上：深抽屉，前后40、内高约36", "滑轨 + 按钮锁；台阶高度是估的，量了再定"),
        ("2", "储物柜", "65 × 45 × 67", "内宽 62.5；下半截被台阶占掉后面24，上半截深43", "对开门 + 按钮锁；放空气炸锅、电煮锅、水壶、锅"),
        ("3", "转角水桶柜", "62 × 45 × 67", "清水桶、废水桶各一个，绑带固定", "站在车外从右门取；水泵和水管也在这里"),
        ("4", "水槽柜", "45 × 51 × 67", "水槽 38 × 38 × 深15；下面净高约 48", "门朝过道；放带盖垃圾桶、清洁用品"),
        ("5", "顶柜", "171 × 22 × 19", "内高约 16.5，三片推拉板走上下槽", "不用合页和撑杆；只放轻的东西；车顶弧度要现场比着做"),
        ("6", "小窗", "约 52 × 20", "开在隔墙上，对着后视镜的视线", "位置待量；挂一道小窗帘"),
    ]
    ty = Z(0) + 86
    cols = [X(-20), X(-8), X(26), X(64), X(210)]
    heads = ["编号", "名称", "外尺寸（宽×深×高）", "里面", "门和备注"]
    for cx, h in zip(cols, heads):
        o.append(text(cx, ty, h, 14, anchor="start", bold=True))
    o.append(line(cols[0], ty + 8, Wpx - 40, ty + 8, "#888", 1))
    for i, r in enumerate(rows):
        yy = ty + 34 + i * 30
        for cx, v in zip(cols, r):
            o.append(text(cx, yy, v, 13.5, anchor="start", fill=C["dim"] if cx == cols[0] else None))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ overhead cabinet sheet
def overhead():
    S = 5.0
    ox, oy = 120, 120
    Wpx = int(ox + 190 * S + 330)
    Hpx = int(oy + H_MID * S + 110)
    o = svg_open(Wpx, Hpx, "右侧墙吊柜（放衣服）：怎么固定")

    def X(y):
        return ox + y * S

    def Z(z):
        return oy + (H_MID - z) * S

    def box(y0, z0, y1, z1, fill, label=None, size=13, **kw):
        s = rect(X(y0), Z(z1), (y1 - y0) * S, (z1 - z0) * S, fill, **kw)
        if label:
            s += mtext(X((y0 + y1) / 2), Z((z0 + z1) / 2), label, size)
        return s

    o.append(text(X(0), Z(H_MID) - 16, "从车里往右侧墙看 · 左边是尾门", 14, anchor="start", bold=True))
    o.append(line(X(0), Z(0), X(190), Z(0), C["wall"], 3))
    o.append(line(X(0), Z(0), X(0), Z(H_SIDE), C["wall"], 3))
    o.append(line(X(0), Z(H_SIDE), X(190), Z(H_SIDE), C["wall"], 3))
    o.append(box(12, 70, 112, 113, "#dcecf6", ["右后侧窗（上半被柜子挡住）"], 11, extra='fill-opacity="0.6"'))
    o.append(box(0, 0, FIX, BED_H - 2, "#eee6d8", ["床下：箱子和脏衣格"], 12))
    o.append(box(0, BED_H - 2, WARD_Y0, BED_H, C["ply"]))
    o.append(box(FIX, 0, WARD_Y0, BED_H - 2, C["ply2"], ["小格"], 10))
    o.append(box(1, BED_H, WARD_Y0 - 1, BED_H + 6, C["mat2"], ["小珵的床垫 40 × 143"], 12))
    o.append(box(WARD_Y0, 0, BOX_END, UNIT_H, C["ward"], ["矮柜", "高70"], 12))
    # legs + cabinet
    o.append(box(0, BED_H, OH["y0"], OH["z1"], "#7a5a2c"))
    o.append(box(OH["y1"] - 2, BED_H, OH["y1"], OH["z0"], "#7a5a2c"))
    o.append(box(OH["y0"], OH["z0"], OH["y1"], OH["z1"], C["door"], None, sw=2))
    o.append(box(OH["y0"] + 1, OH["z0"] + 1.5, 76, OH["z1"] - 1.5, "#f6ecd6", ["推拉门"], 12))
    o.append(box(70, OH["z0"] + 2.3, OH["y1"] - 1, OH["z1"] - 1.5, "#f6ecd6", ["推拉门"], 12))
    for yy in (22, 55, 90, 125):
        o.append(f'<circle cx="{X(yy):.1f}" cy="{Z(OH["z1"] - 6):.1f}" r="6" fill="#b02a2a"/>')
    for yy in (40, 105):
        o.append(f'<rect x="{X(yy)-6:.1f}" y="{Z(OH["z1"])-6:.1f}" width="12" height="12" fill="#b02a2a"/>')
    o.append(line(X(OH["y1"] - 36), Z(OH["z0"] - 3), X(OH["y1"] - 6), Z(OH["z0"] - 3), "#333", 4))
    o.append(text(X(OH["y1"] - 21), Z(OH["z0"] - 8), "挂杆", 12))
    o.append(dim_h(X(OH["y0"]), X(OH["y1"]), Z(H_SIDE) - 26, "吊柜长 141 · 深30"))
    o.append(dim_v(X(OH["y1"]) + 16, Z(OH["z1"]), Z(OH["z0"]), "高29", side=1))
    o.append(dim_v(X(60), Z(OH["z0"]), Z(BED_H + 6), f"离床垫 {OH['z0']-BED_H-6}"))
    tx = X(190) + 20
    notes = ["三重固定", "① 两头的竖板（棕色）落在床板上，", "    重量压在腿上，不靠螺丝吊。",
             "② 红色圆点：背面 4 颗 M6 螺栓，", "    用拉铆螺母打在车身竖梁上。",
             "③ 红色方块：顶面 2 颗 M6 螺栓，", "    固定在车顶横梁上。", "",
             "做法", "柜体用 9 毫米板，越轻越好。", "只放衣服，装满约 10–15 公斤。", "推拉门走上下槽，不会自己开。", "",
             "装好后的检验", "两手抓住柜底，把体重挂上去，", "纹丝不动才算合格。", "",
             "梁的位置要到车上实际找，", "图上的螺栓位置只是示意。"]
    for i, t in enumerate(notes):
        bold = t in ("三重固定", "做法", "装好后的检验")
        o.append(text(tx, oy + 20 + i * 26, t, 15 if bold else 14, anchor="start", bold=bold,
                      fill=C["dim"] if bold else None))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ under-bed sections
def underbed():
    S = 5.0
    ox, oy = 150, 110
    Wpx = int(ox + W * S + 330)
    Hpx = 1010
    o = svg_open(Wpx, Hpx, "床下箱子怎么放（从尾门往里看）")
    ZT = 62

    def X(x):
        return ox + x * S

    def panel(y_off, title, tail):
        def Z(z):
            return oy + y_off + (ZT - z) * S

        def box(x0, z0, x1, z1, fill, label=None, size=13, **kw):
            s = rect(X(x0), Z(z1), (x1 - x0) * S, (z1 - z0) * S, fill, **kw)
            if label:
                s += mtext(X((x0 + x1) / 2), Z((z0 + z1) / 2), label, size)
            return s
        o.append(text(X(0), Z(ZT) - 12, title, 16, anchor="start", bold=True))
        o.append(line(X(0), Z(0), X(W), Z(0), C["wall"], 3))
        o.append(line(X(0), Z(0), X(0), Z(ZT - 4), C["wall"], 3))
        o.append(line(X(W), Z(0), X(W), Z(ZT - 4), C["wall"], 3))
        o.append(box(1, BED_H, ADULT_W - 1, BED_H + MAT, C["mat"], ["大人床垫"], 12, extra='fill-opacity="0.6"'))
        o.append(box(ADULT_W + 1, BED_H, W - 1, BED_H + 6, C["mat2"], ["小珵"], 12, extra='fill-opacity="0.7"'))
        o.append(box(0, BED_H - 1.8, W, BED_H, C["ply"]))
        if tail:
            o.append(box(0, BED_H - 5.8, POCKET_X, BED_H - 1.8, "#c9ced3", None))
            o.append(text(X(60), Z(BED_H - 3.8) + 4, "40×40 钢方管横梁", 11))
            n, x0, y0, dx, dy, th = CASES[2]
            o.append(box(x0, 0, x0 + dx, th, C["case"], ["24寸", "宽66 × 厚31.5"], 13))
            n, x0, y0, dx, dy, th = CASES[3]
            o.append(box(x0, 0, x0 + dx, th, C["case"], ["20寸", "宽47 × 厚27"], 13))
            o.append(box(POCKET_X, 0, POCKET_X + 1.8, BED_H - 1.8, C["ply"]))
            o.append(box(POCKET_X + 3, 2, W - 2, 34, "#e8e8e8", ["脏衣袋", "32宽"], 12, extra='stroke-dasharray="5 4"'))
            o.append(dim_v(X(0) - 20, Z(BED_H - 5.8), Z(0), "净高 34"))
        else:
            for x0 in (0, W - ARCH["w"]):
                o.append(box(x0, 0, x0 + ARCH["w"], ARCH["h"], C["arch"], ["轮拱"], 12))
            for xx in (25, 76.8, 128.6):
                o.append(box(xx, 0, xx + 1.8, BED_H - 1.8, "#7a5a2c"))
            for i in (0, 1):
                n, x0, y0, dx, dy, th = CASES[i]
                o.append(box(x0, 0, x0 + dx, th, C["case"], [n, "宽48 × 厚29"], 13))
            o.append(box(1, ARCH["h"] + 1, 24, BED_H - 2.5, "#e8e8e8", ["侧槽", "23×20"], 11, extra='stroke-dasharray="5 4"'))
            o.append(box(131, ARCH["h"] + 1, W - 1, BED_H - 2.5, "#e8e8e8", ["侧槽", "22×20"], 11, extra='stroke-dasharray="5 4"'))
            o.append(text(X(77.7), Z(BED_H + 16), "三道竖板 = 床的腿", 13, fill="#7a5a2c", bold=True))
            o.append(dim_h(X(26.8), X(76.8), Z(0) + 30, "巷道 50"))
            o.append(dim_h(X(78.6), X(128.6), Z(0) + 30, "巷道 50"))
        o.append(dim_v(X(W) + 24, Z(BED_H), Z(0), f"床面 {BED_H}", side=1))
        return Z

    panel(40, "A  尾门口这一排（离尾门 0 到 42 厘米）", True)
    panel(430, "B  往里这一排（离尾门 42 到 123 厘米）", False)
    tx = X(W) + 80
    steps = ["放的顺序", "① 两个 28 寸竖着推到最里面，", "    各走一条巷道。", "② 24 寸、20 寸横放在尾门口。",
             "③ 脏衣袋放右后角。", "", "拿的顺序", "要拿 28 寸，先把外面的", "24 寸或 20 寸拉出来。", "",
             "注意", "24 寸和 28 寸放床下时不能", "扩容，扩容后塞不进。", "",
             "每个箱子拴一根拉带，", "不用钻进去掏。"]
    for i, t in enumerate(steps):
        bold = t in ("放的顺序", "拿的顺序", "注意")
        o.append(text(tx, oy + 60 + i * 26, t, 15 if bold else 14, anchor="start", bold=bold,
                      fill=C["dim"] if bold else None))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ isometric
def iso(mode):
    S = 2.6
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    Wpx, Hpx = 1260, 1090
    ox, oy = 800, 1010
    o = svg_open(Wpx, Hpx, "效果图 · " + ("白天（床脚收起，可坐两人）" if mode == "day" else "晚上（床放平，三人）"))

    def P(x, y, z):
        return (ox + (x - y) * c30 * S, oy - (x + y) * s30 * S - z * S)

    def poly(pts, fill, op=1.0, stroke=None):
        d = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        return (f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" '
                f'stroke="{stroke or C["line"]}" stroke-width="1"/>')

    def lab(x, y, z, s, size=12, fill=None, bold=False, dy=4):
        a, b = P(x, y, z)
        o.append(text(a, b + dy, s, size, fill=fill, bold=bold))

    def box(x0, y0, z0, x1, y1, z1, col, label=None, op=1.0, ls=13):
        o.append(poly([P(x0, y0, z0), P(x0, y1, z0), P(x0, y1, z1), P(x0, y0, z1)], shade(col, 0.78), op))
        o.append(poly([P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)], shade(col, 0.90), op))
        o.append(poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], col, op))
        if label:
            lab((x0 + x1) / 2, (y0 + y1) / 2, z1, label, ls, bold=True, dy=5)

    def face_y(x0, x1, y, z0, z1, fill, label=None):
        o.append(poly([P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)], fill))
        if label:
            lab((x0 + x1) / 2, y, (z0 + z1) / 2, label)

    def face_x(x, y0, y1, z0, z1, fill, label=None, lfill=None):
        o.append(poly([P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)], fill))
        if label:
            lab(x, (y0 + y1) / 2, (z0 + z1) / 2, label, fill=lfill)

    T = BENCH_H - 3
    # shell
    o.append(poly([P(0, 0, 0), P(W, 0, 0), P(W, BOX_END, 0), P(W + STEP, BOX_END, 0),
                   P(W + STEP, SEAT, 0), P(0, SEAT, 0)], C["floor"]))
    o.append(poly([P(W, 0, 0), P(W, BOX_END, 0), P(W, BOX_END, H_SIDE), P(W, 0, H_SIDE)], "#f3f1ec", 0.9, "#aaa"))
    o.append(poly([P(0, SEAT, 0), P(W + STEP, SEAT, 0), P(W + STEP, SEAT, H_SIDE), P(0, SEAT, H_SIDE)],
                  "#f3f1ec", 0.9, "#aaa"))
    o.append(poly([P(WIN[0], SEAT, WIN[2]), P(WIN[1], SEAT, WIN[2]), P(WIN[1], SEAT, WIN[3]),
                   P(WIN[0], SEAT, WIN[3])], "#cfe6f5", 1, "#555"))
    lab(78, SEAT, BENCH_H + 16, "小窗", 13, bold=True)
    o.append(poly([P(W, 12, 70), P(W, 112, 70), P(W, 112, 113), P(W, 12, 113)], "#dcecf6", 1, "#999"))

    # kitchen front row
    box(CUP_X1, KIT_Y, 0, W + STEP, SEAT, T, C["kit"])
    face_y(CUP_X1 + 3, SINK_X0 - 2, KIT_Y, 4, T - 3, C["door"], "水桶")
    box(0, KIT_Y, 0, CUP_X1, SEAT, T, C["kit"])
    face_y(3, DRAW_W - 3, KIT_Y, 4, 22, C["door"], "浅抽屉")
    face_y(3, DRAW_W - 3, KIT_Y, 24, T - 3, C["door"], "深抽屉")
    face_y(DRAW_W + 2, 76, KIT_Y, 4, T - 3, C["door"])
    face_y(76, CUP_X1 - 3, KIT_Y, 4, T - 3, C["door"])
    lab(76, KIT_Y, 34, "储物柜")
    lab(76, KIT_Y, 26, "（以后冰箱位）", 11)
    box(0, KIT_Y - 1, T, W + STEP, SEAT, BENCH_H, C["top"], None)
    lab(78, KIT_Y + 14, BENCH_H, "台面 70", 13, bold=True, dy=5)
    # appliance cupboards + top cupboard
    box(0, SEAT - TOP_D, GAR_Z1, W + STEP, SEAT, H_SIDE - 1, C["door"])
    lab(85, SEAT - TOP_D, GAR_Z1 + 10, "顶柜（推拉门）")
    box(-40, SEAT - 43, T, 0, SEAT - 2, T + 2, C["top"], "翻板桌", 0.8, 12)
    # sink leg
    box(SINK_X0, BOX_END, 0, W + STEP, KIT_Y, T, C["kit"])
    face_x(SINK_X0, BOX_END + 3, KIT_Y - 3, 4, T - 3, C["door"], "垃圾桶")
    box(SINK_X0 - 1, BOX_END - 1, T, W + STEP, KIT_Y - 1, BENCH_H, C["top"])
    o.append(poly([P(SINK_X0 + 6, BOX_END + 8, BENCH_H), P(W + STEP - 6, BOX_END + 8, BENCH_H),
                   P(W + STEP - 6, KIT_Y - 6, BENCH_H), P(SINK_X0 + 6, KIT_Y - 6, BENCH_H)], C["steel"]))
    lab(SINK_X0 + 22, (BOX_END + KIT_Y) / 2, BENCH_H, "水槽", 13, bold=True, dy=5)
    # wardrobe
    box(ADULT_W, WARD_Y0, 0, W, BOX_END, UNIT_H - 3, C["ward"])
    face_x(ADULT_W, WARD_Y0 + 4, BOX_END - 4, 54, 65, "#3d4a55", "电源", "#ffffff")
    box(ADULT_W - 1, WARD_Y0 - 1, UNIT_H - 3, W, BOX_END, UNIT_H, C["top"], "矮柜")
    box(ADULT_W, FIX, 0, W, WARD_Y0, BED_H, C["ply2"])
    # seat boxes
    box(40, FIX, 0, ADULT_W, BOX_END, SEAT_H, C["ply2"])
    box(40, FIX + (UP if mode == "day" else 0), SEAT_H, ADULT_W, BOX_END, SEAT_H + PAD, C["seat"])
    box(0, FIX, 0, 40, BOX_END, SEAT_H + PAD, C["toilet"])
    if mode == "day":
        lab(77, FIX + UP + 19, SEAT_H + PAD, "座位（坐两人）", 13, "#ffffff", True, 5)
        lab(20, FIX + UP + 19, SEAT_H + PAD, "马桶", 13, None, True, 5)
    else:
        box(40, FIX, BED_H - 2, ADULT_W, BED_END, BED_H, C["ply"])
        box(41, FIX, BED_H, ADULT_W - 1, BED_END - 1, BED_H + MAT, C["mat"], f"床脚段 {FOOT}")
        box(0, FIX, BED_H - 2, 40, BED_END, BED_H, C["ply"])
        box(1, FIX, BED_H, 40, BED_END - 1, BED_H + MAT, C["mat2"], "小掀盖")
    # under the fixed platform
    box(0, FIX - 2, 0, W, FIX, BED_H - 2, C["ply"])
    box(W - ARCH["w"], ARCH["y0"], 0, W, ARCH["y1"], ARCH["h"], C["arch"])
    order = [CASES[1], CASES[0]]
    for (nm, x0, y0, dx, dy, th) in order:
        box(x0, y0, 0, x0 + dx, y0 + dy, th, C["case"])
    box(0, ARCH["y0"], 0, ARCH["w"], ARCH["y1"], ARCH["h"], C["arch"])
    box(POCKET_X, 0, 0, POCKET_X + 1.8, 42, BED_H - 2, C["ply"])
    for (nm, x0, y0, dx, dy, th) in (CASES[3], CASES[2]):
        box(x0, y0, 0, x0 + dx, y0 + dy, th, C["case"])
        lab(x0 + dx / 2, y0, th / 2, nm, 12, "#ffffff", True, 5)
    lab(137, 0, 18, "脏衣格", 12)
    # platform + mattresses
    box(0, 0, BED_H - 2, W, FIX, BED_H, C["ply"])
    box(ADULT_W + 1, 1, BED_H, W - 1, WARD_Y0 - 1, BED_H + 6, C["mat2"], f"小珵 40×{WARD_Y0}")
    o.append(poly([P(W - 32, 2, BED_H + 6), P(W - 2, 2, BED_H + 6), P(W - 2, 32, BED_H + 6), P(W - 32, 32, BED_H + 6)],
                  "#ffffff", 0.55, "#b02a2a"))
    lab(W - 17, 17, BED_H + 6, "投衣口", 11, C["dim"])
    # overhead clothes cabinet on the right wall, standing on two legs
    box(OH["x0"], OH["y1"] - 2, BED_H, OH["x1"], OH["y1"], OH["z0"], C["ply"])
    box(OH["x0"], OH["y0"], OH["z0"], OH["x1"], OH["y1"], OH["z1"], C["door"])
    lab(OH["x0"], 72, 111, "吊柜（衣服，推拉门）", 13, None, True)
    box(OH["x0"], 0, BED_H, OH["x1"], OH["y0"], OH["z1"], C["ply"])
    r0, r1 = P(OH["x0"] + 4, OH["y1"] - 6, OH["z0"] - 3), P(OH["x0"] + 4, OH["y1"] - 36, OH["z0"] - 3)
    o.append(line(r0[0], r0[1], r1[0], r1[1], "#333", 4))
    o.append(text(r0[0] - 6, r0[1] + 4, "挂杆", 12, anchor="end"))
    zt = BED_H + MAT
    if mode == "day":
        box(0, FIX + MAT + 2, zt + 4, ADULT_W, FIX + UP, zt + FOOT - 4, C["seat"], op=0.45)
        box(0, FIX + MAT, zt, ADULT_W, FIX + MAT + 2, zt + FOOT, C["ply"], op=0.45)
        box(0, FIX, zt, ADULT_W, FIX + MAT, zt + FOOT, C["mat"], op=0.45)
        lab(ADULT_W / 2, FIX, zt + FOOT / 2 + 8, "床脚段竖起（背面是靠背）", 13, None, True, 0)
        box(1, 1, BED_H, ADULT_W - 1, FIX - 0.5, zt, C["mat"], f"大人床 114×{FIX}（不用收）")
    else:
        box(1, 1, BED_H, ADULT_W - 1, FIX - 0.5, zt, C["mat"], "大人床 114×185")
    a, b = P(W / 2 + 30, -22, 0)
    o.append(text(a, b + 10, "尾门（头朝这边）", 15, bold=True, fill=C["wall"]))
    a, b = P(-12, SEAT - 110, 0)
    o.append(text(a - 10, b + 24, "左门（进出）", 14, anchor="end", bold=True, fill="#2e7d32"))
    o.append(text(Wpx / 2, Hpx - 18,
                  "左侧墙和车顶未画出；竖起的床脚段画成半透明，能看到后面的座位 · 单位厘米",
                  13, fill="#666"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    files = {
        "plan-day.svg": plan("day"),
        "plan-night.svg": plan("night"),
        "plan-under.svg": plan("under"),
        "side.svg": side(),
        "kitchen.svg": kitchen(),
        "underbed.svg": underbed(),
        "overhead.svg": overhead(),
        "view-day.svg": iso("day"),
        "view-night.svg": iso("night"),
    }
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", name)

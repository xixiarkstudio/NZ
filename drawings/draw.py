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
FIX = 130      # fixed bed length
FOOT = 55      # folding foot section
BED_END = FIX + FOOT          # 185
SEAT_H = 31    # seat box height (plus 3 cm fixed pad = 34)
PAD = 3
UP = MAT + 2 + PAD   # depth taken by the upright foot section: mattress + board + back pad
ADULT_W = 114  # adult bed / seat width (left)
WARD_W = W - ADULT_W          # 40
KIT_D = 45     # kitchen depth
KIT_Y = SEAT - KIT_D          # 229
BENCH_H = 70
SINK_X0 = W + STEP - KIT_D    # 126
CASE = (78, 52, 32)           # 28" suitcase, estimated

FONT = "WenQuanYi Zen Hei, sans-serif"
C = dict(
    floor="#efe9df", ply="#d9b98a", ply2="#c9a572", mat="#8fa6b8",
    mat2="#a9bccb", case="#7c6f9b", kit="#e6d3b3", top="#b98b56",
    ward="#c7a06c", steel="#b8c0c6", toilet="#f4f4f1", fridge="#dfe6ea",
    water="#9cc7e6", arch="#9a9a9a", line="#3a3a3a", dim="#b02a2a",
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


def dim_h(x0, x1, y, label, off=0):
    """horizontal dimension line"""
    c = C["dim"]
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="1"/>'
            f'<line x1="{x0:.1f}" y1="{y-5:.1f}" x2="{x0:.1f}" y2="{y+5:.1f}" stroke="{c}"/>'
            f'<line x1="{x1:.1f}" y1="{y-5:.1f}" x2="{x1:.1f}" y2="{y+5:.1f}" stroke="{c}"/>'
            + text((x0 + x1) / 2, y - 5 + off, label, 13, fill=c))


def dim_v(x, y0, y1, label, side=-1):
    c = C["dim"]
    tx = x + side * 7
    return (f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{c}" stroke-width="1"/>'
            f'<line x1="{x-5:.1f}" y1="{y0:.1f}" x2="{x+5:.1f}" y2="{y0:.1f}" stroke="{c}"/>'
            f'<line x1="{x-5:.1f}" y1="{y1:.1f}" x2="{x+5:.1f}" y2="{y1:.1f}" stroke="{c}"/>'
            + text(tx, (y0 + y1) / 2, label, 13, fill=c, rot=-90))


# ------------------------------------------------------------------ plan
def plan(mode):
    """mode: 'day' or 'night'. Front of the van at the top."""
    S = 3.4
    ox, oy = 290, 130
    Wpx = 1000
    Hpx = int(oy + SEAT * S + 150)
    titles = {"day": "白天（床脚收起）", "night": "晚上（床放平）", "under": "床面以下的储物"}
    o = svg_open(Wpx, Hpx, "俯视图 · " + titles[mode])

    def X(x):
        return ox + x * S

    def Y(y):          # y measured from tailgate; front is up
        return oy + (SEAT - y) * S

    def box(x0, y0, x1, y1, fill, label=None, size=13, **kw):
        s = rect(X(x0), Y(y1), (x1 - x0) * S, (y1 - y0) * S, fill, **kw)
        if label:
            s += mtext(X((x0 + x1) / 2), Y((y0 + y1) / 2), label, size)
        return s

    # floor
    o.append(box(0, 0, W, L, C["floor"], sw=2.5, stroke=C["wall"]))
    o.append(box(0, L, W, SEAT, "#e3ddd2", sw=2.5, stroke=C["wall"]))
    o.append(box(W, KIT_Y - 44, W + STEP, SEAT, "#e3ddd2", stroke=C["wall"]))
    # fixed bed platform
    o.append(box(0, 0, W, FIX, C["ply"]))
    # suitcases (under the platform) dashed
    dash = 'stroke-dasharray="6 4" fill-opacity="0.55"'
    cw, cd, _ = CASE
    cx0 = (W - cw) / 2
    o.append(box(cx0, 0, cx0 + cw, cd, C["case"], ["箱子1", "（床下）"], 12, extra=dash if mode != "under" else ""))
    px0 = (W - 2 * cd) / 2
    o.append(box(px0, cd, px0 + cd, cd + cw, C["case"], ["箱子2", "78×52×32"], 12, extra=dash if mode != "under" else ""))
    o.append(box(px0 + cd, cd, px0 + 2 * cd, cd + cw, C["case"], ["箱子3"], 12, extra=dash if mode != "under" else ""))
    # wheel arches
    for x0 in (0, W - ARCH["w"]):
        o.append(box(x0, ARCH["y0"], x0 + ARCH["w"], ARCH["y1"], C["arch"], ["轮拱"], 11,
                     extra='fill-opacity="0.7"'))
    # tail pockets
    o.append(mtext(X(19), Y(22), ["尾格", "38×49"], 11))
    o.append(mtext(X(W - 19), Y(22), ["尾格", "38×49"], 11))
    # mattresses
    if mode == "under":
        o.append(box(0, FIX, 40, BED_END, C["toilet"], ["马桶", "高≤32"], 13))
        o.append(box(40, FIX, ADULT_W, BED_END, C["ply2"], ["座位箱内部", "74 × 55 × 高29"], 14))
        o.append(mtext(X(12), Y(125), ["侧槽"], 11))
        o.append(mtext(X(W - 12), Y(125), ["侧槽"], 11))
    elif mode == "night":
        o.append(box(2, 2, ADULT_W - 1, FIX - 1, C["mat"], ["大人床垫", "114 × 130"], 15,
                     extra='fill-opacity="0.80"'))
        o.append(box(ADULT_W + 1, 2, W - 2, FIX - 1, C["mat2"], ["小珵", "40×130"], 13,
                     extra='fill-opacity="0.85"'))
        o.append(box(2, FIX + 1, ADULT_W / 2 - 0.5, BED_END - 1, C["mat"], ["床脚左半", "下面：马桶"], 12,
                     extra='fill-opacity="0.80"'))
        o.append(box(ADULT_W / 2 + 0.5, FIX + 1, ADULT_W - 1, BED_END - 1, C["mat"], ["床脚右半"], 12,
                     extra='fill-opacity="0.80"'))
    else:
        o.append(box(2, 2, ADULT_W - 1, FIX - 1, C["mat"], ["大人床垫（不用收）", "114 × 130"], 15,
                     extra='fill-opacity="0.80"'))
        o.append(box(ADULT_W + 1, 2, W - 2, FIX - 1, C["mat2"], ["小珵", "40×130"], 13,
                     extra='fill-opacity="0.85"'))
        o.append(box(0, FIX, ADULT_W, FIX + UP, C["seat"], None))
        o.append(text(X(ADULT_W / 2), Y(FIX + UP / 2) + 4, "床脚段竖起 = 靠背（占17）", 12, fill="#ffffff"))
        o.append(box(0, FIX + UP, 40, BED_END, C["toilet"], ["马桶", "（掀盖）"], 13))
        o.append(box(40, FIX + UP, ADULT_W, BED_END, C["ply2"], ["座位 高34", "宽74 × 深38"], 14))
    # wardrobe
    o.append(box(ADULT_W, FIX, W, BED_END, C["ward"], ["衣柜", "40×55", "到顶"], 13, sw=2))
    # aisle
    o.append(mtext(X(60), Y((BED_END + KIT_Y) / 2), ["过道 44"], 15))
    # sink leg + fridge
    o.append(box(SINK_X0, BED_END, W + STEP, KIT_Y, C["kit"], None, sw=2))
    o.append(f'<rect x="{X(SINK_X0+6):.1f}" y="{Y(KIT_Y-5):.1f}" width="{33*S:.1f}" height="{34*S:.1f}" '
             f'rx="8" fill="{C["steel"]}" stroke="{C["line"]}"/>')
    o.append(mtext(X(SINK_X0 + 22.5), Y((BED_END + KIT_Y) / 2), ["水槽", "下：冰箱"], 13))
    # front row
    o.append(box(0, KIT_Y, 109, SEAT, C["kit"], ["炉子台面 109 × 45", "下面：抽屉"], 14, sw=2))
    o.append(box(109, KIT_Y, W + STEP, SEAT, C["kit"], ["转角", "下：水桶"], 13, sw=2))
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
    for xx, lab, anchor in ((-6, "左门（进出）", "end"), (W + STEP + 6, "右门（拿水桶）", "start")):
        o.append(text(X(xx), Y(SEAT - DOOR / 2), lab, 13, anchor=anchor, fill=C["wall"], bold=True))
    o.append(f'<line x1="{X(0):.1f}" y1="{Y(SEAT):.1f}" x2="{X(0):.1f}" y2="{Y(SEAT-DOOR):.1f}" '
             f'stroke="#2e7d32" stroke-width="5"/>')
    o.append(f'<line x1="{X(W+STEP):.1f}" y1="{Y(SEAT):.1f}" x2="{X(W+STEP):.1f}" y2="{Y(KIT_Y-44):.1f}" '
             f'stroke="#2e7d32" stroke-width="5"/>')
    # labels front/back
    o.append(text(X(W / 2), Y(-9), "尾门（头朝这边）", 15, bold=True))
    # dimensions
    yb = Y(0) + 62
    o.append(dim_h(X(0), X(W), yb, f"车内宽 {W}"))
    o.append(dim_h(X(0), X(ADULT_W), yb + 30, f"{ADULT_W}"))
    o.append(dim_h(X(ADULT_W), X(W), yb + 30, f"{WARD_W}"))
    xl = X(-40) - 40
    o.append(dim_v(xl, Y(FIX), Y(0), f"固定床 {FIX}"))
    o.append(dim_v(xl, Y(BED_END), Y(FIX), f"床脚 {FOOT}"))
    o.append(dim_v(xl, Y(KIT_Y), Y(BED_END), "过道 44"))
    o.append(dim_v(xl, Y(SEAT), Y(KIT_Y), f"厨房 {KIT_D}"))
    o.append(dim_v(xl - 34, Y(L), Y(0), f"木地板 {L}"))
    o.append(dim_v(xl - 34, Y(SEAT), Y(L), "24"))
    o.append(dim_h(X(W), X(W + STEP), Y(SEAT) - 10, "17"))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ side view
def side():
    """Section along the van, seen from the left side. Tailgate on the left."""
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

    # shell
    o.append(f'<path d="M{X(0):.1f},{Z(0):.1f} L{X(0):.1f},{Z(H_MID-4):.1f} Q{X(0):.1f},{Z(H_MID):.1f} {X(6):.1f},{Z(H_MID):.1f} '
             f'L{X(SEAT+30):.1f},{Z(H_MID):.1f}" fill="none" stroke="{C["wall"]}" stroke-width="3"/>')
    o.append(f'<line x1="{X(0):.1f}" y1="{Z(0):.1f}" x2="{X(L):.1f}" y2="{Z(0):.1f}" stroke="{C["wall"]}" stroke-width="3"/>')
    o.append(f'<line x1="{X(L):.1f}" y1="{Z(0):.1f}" x2="{X(L):.1f}" y2="{Z(-6):.1f}" stroke="{C["wall"]}" stroke-width="3"/>')
    o.append(f'<line x1="{X(L):.1f}" y1="{Z(-6):.1f}" x2="{X(SEAT+30):.1f}" y2="{Z(-6):.1f}" stroke="{C["wall"]}" stroke-width="3"/>')
    # suitcases
    o.append(box(0, 0, CASE[1], CASE[2], C["case"], ["箱子1"], 12, extra='fill-opacity="0.6"'))
    o.append(box(CASE[1], 0, CASE[1] + CASE[0], CASE[2], C["case"], ["箱子2、3（并排）"], 12, extra='fill-opacity="0.6"'))
    # arch
    o.append(box(ARCH["y0"], 0, ARCH["y1"], ARCH["h"], C["arch"], None, extra='fill-opacity="0.35" stroke-dasharray="4 3"'))
    # platform
    o.append(box(0, BED_H - 1.8, FIX, BED_H, C["ply"]))
    o.append(box(FIX - 1.8, 0, FIX, BED_H, C["ply"]))
    # mattress
    o.append(box(1, BED_H, FIX - 0.5, BED_H + MAT, C["mat"], ["主床垫 130 × 厚12"], 13))
    # foot section upright: pivot at mattress-top level, so it clears the main mattress
    zt = BED_H + MAT
    o.append(box(FIX, zt, FIX + MAT, zt + FOOT, C["mat"], None))
    o.append(text(X(FIX + MAT / 2), Z(zt + FOOT / 2), "床脚床垫 厚12", 12, rot=-90))
    o.append(box(FIX + MAT, zt, FIX + MAT + 2, zt + FOOT, C["ply"]))
    o.append(box(FIX + MAT + 2, zt + 4, FIX + UP, zt + FOOT - 4, C["seat"]))
    o.append(f'<circle cx="{X(FIX):.1f}" cy="{Z(zt):.1f}" r="6" fill="#b02a2a"/>')
    o.append(text(X(FIX) - 10, Z(zt) - 10, "转轴", 12, anchor="end", fill=C["dim"]))
    o.append(text(X(FIX + UP + 4), Z(zt + FOOT - 12), "靠背垫", 12, anchor="start"))
    # night position, dashed
    o.append(box(FIX, BED_H - 2, BED_END, BED_H, "none", None, extra='stroke-dasharray="5 4"', stroke="#b02a2a"))
    o.append(box(FIX, BED_H, BED_END, zt, "none", None, extra='stroke-dasharray="5 4"', stroke="#b02a2a"))
    o.append(text(X(FIX + 36), Z(BED_H + 5), "晚上放平的位置", 11, fill=C["dim"]))
    # seat box
    o.append(box(FIX, 0, BED_END, SEAT_H, C["ply2"], ["座位箱", "高31"], 13))
    o.append(box(FIX + UP, SEAT_H, BED_END, SEAT_H + PAD, C["seat"]))
    o.append(text(X(BED_END) + 6, Z(SEAT_H + 1), "坐垫3", 11, anchor="start"))
    # wardrobe (behind, right side) dashed
    o.append(box(FIX, 0, BED_END, H_SIDE, "none", None, extra='stroke-dasharray="7 5"', stroke="#8a6a3c"))
    o.append(text(X(FIX + FOOT / 2 + 8), Z(H_SIDE - 6), "衣柜（右侧，到顶）", 12, fill="#8a6a3c"))
    # kitchen
    o.append(box(KIT_Y, -6 if False else 0, SEAT, BENCH_H - 3, C["kit"], ["厨房柜", "抽屉"], 13))
    o.append(box(KIT_Y - 1, BENCH_H - 3, SEAT, BENCH_H, C["top"]))
    o.append(box(SEAT - 2, BENCH_H, SEAT, H_SIDE - 2, C["ply"], None))
    o.append(box(SEAT - 2, BENCH_H + 6, SEAT, BENCH_H + 26, "#cfe6f5", None))
    o.append(text(X(SEAT - 4), Z(BENCH_H + 16), "小窗", 12, anchor="end"))
    for zz in (BENCH_H + 12, BENCH_H + 24):
        o.append(box(SEAT - 14, zz, SEAT - 2, zz + 1.2, C["top"], None, extra='stroke-dasharray="4 3"'))
    o.append(text(X(SEAT - 16), Z(BENCH_H + 30), "两侧置物架", 11, anchor="end"))
    o.append(box(SEAT - 22, H_SIDE - 20, SEAT - 2, H_SIDE - 18.2, C["top"]))
    o.append(text(X(SEAT - 12), Z(H_SIDE - 10), "顶部搁板", 12))
    # front seat
    o.append(f'<path d="M{X(SEAT+2):.1f},{Z(20):.1f} L{X(SEAT+12):.1f},{Z(95):.1f} L{X(SEAT+22):.1f},{Z(95):.1f} '
             f'L{X(SEAT+14):.1f},{Z(20):.1f} Z" fill="{C["seat"]}" stroke="{C["line"]}"/>')
    o.append(text(X(SEAT + 26), Z(60), "前排座椅", 12, rot=-90))
    # dims
    zb = Z(0) + 40
    o.append(dim_h(X(0), X(FIX), zb, f"固定床 {FIX}"))
    o.append(dim_h(X(FIX), X(BED_END), zb, f"{FOOT}"))
    o.append(dim_h(X(BED_END), X(KIT_Y), zb, "过道 44"))
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


# ------------------------------------------------------------------ isometric
def shade(hexcol, f):
    r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (max(0, min(255, int(v * f))) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


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

    labels = []

    def box(x0, y0, z0, x1, y1, z1, col, label=None, op=1.0, ls=13):
        o.append(poly([P(x0, y0, z0), P(x0, y1, z0), P(x0, y1, z1), P(x0, y0, z1)], shade(col, 0.78), op))
        o.append(poly([P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)], shade(col, 0.90), op))
        o.append(poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], col, op))
        if label:
            a, b = P((x0 + x1) / 2, (y0 + y1) / 2, z1)
            o.append(text(a, b + 5, label, ls, bold=True))

    def face_y(x0, x1, y, z0, z1, fill, lab=None):
        o.append(poly([P(x0, y, z0), P(x1, y, z0), P(x1, y, z1), P(x0, y, z1)], fill))
        if lab:
            a, b = P((x0 + x1) / 2, y, (z0 + z1) / 2)
            o.append(text(a, b + 4, lab, 12))

    def face_x(x, y0, y1, z0, z1, fill, lab=None):
        o.append(poly([P(x, y0, z0), P(x, y1, z0), P(x, y1, z1), P(x, y0, z1)], fill))
        if lab:
            a, b = P(x, (y0 + y1) / 2, (z0 + z1) / 2)
            o.append(text(a, b + 4, lab, 12))

    # --- shell: floor, far walls
    o.append(poly([P(0, 0, 0), P(W, 0, 0), P(W, BED_END, 0), P(W + STEP, BED_END, 0),
                   P(W + STEP, SEAT, 0), P(0, SEAT, 0)], C["floor"]))
    o.append(poly([P(W, 0, 0), P(W, BED_END, 0), P(W, BED_END, H_SIDE), P(W, 0, H_SIDE)], "#f3f1ec", 0.9, "#aaa"))
    o.append(poly([P(0, SEAT, 0), P(W + STEP, SEAT, 0), P(W + STEP, SEAT, H_SIDE), P(0, SEAT, H_SIDE)],
                  "#f3f1ec", 0.9, "#aaa"))
    o.append(poly([P(52, SEAT, BENCH_H + 6), P(104, SEAT, BENCH_H + 6), P(104, SEAT, BENCH_H + 26),
                   P(52, SEAT, BENCH_H + 26)], "#cfe6f5", 1, "#555"))
    a, b = P(78, SEAT, BENCH_H + 16)
    o.append(text(a, b + 4, "小窗", 13, bold=True))
    o.append(poly([P(W, 15, 70), P(W, 120, 70), P(W, 120, 113), P(W, 15, 113)], "#dcecf6", 1, "#999"))

    # --- kitchen (farthest)
    box(109, KIT_Y, 0, W + STEP, SEAT, BENCH_H - 3, C["kit"])
    face_y(113, SINK_X0 - 2, KIT_Y, 4, BENCH_H - 7, "#f1e3c8", "水桶")
    box(0, KIT_Y, 0, 109, SEAT, BENCH_H - 3, C["kit"])
    for i in range(3):
        face_y(4, 105, KIT_Y, 4 + i * 21, 23 + i * 21, "#f1e3c8", "抽屉" if i == 1 else None)
    box(0, KIT_Y - 1, BENCH_H - 3, W + STEP, SEAT, BENCH_H, C["top"], "炉子台面")
    for (rx0, rx1) in ((W + STEP - 62, W + STEP), (0, 48)):
        for zz in (BENCH_H + 24, BENCH_H + 12):
            box(rx0, SEAT - 12, zz, rx1, SEAT, zz + 1.5, C["top"])
    a, b = P(24, SEAT - 12, BENCH_H + 19)
    o.append(text(a, b, "置物架", 12, bold=True))
    a, b = P(W + STEP - 31, SEAT - 12, BENCH_H + 19)
    o.append(text(a, b, "置物架", 12, bold=True))
    box(0, SEAT - 20, H_SIDE - 20, W + STEP, SEAT, H_SIDE - 18, C["top"], "顶部搁板")
    box(-40, SEAT - 43, BENCH_H - 3, 0, SEAT - 2, BENCH_H - 1, C["top"], "翻板桌", 0.8, 12)
    # --- sink leg
    box(SINK_X0, BED_END, 0, W + STEP, KIT_Y, BENCH_H - 3, C["kit"])
    face_x(SINK_X0, BED_END + 3, KIT_Y - 3, 4, 50, C["fridge"], "冰箱")
    box(SINK_X0 - 1, BED_END - 1, BENCH_H - 3, W + STEP, KIT_Y - 1, BENCH_H, C["top"])
    o.append(poly([P(SINK_X0 + 6, BED_END + 5, BENCH_H), P(W + STEP - 6, BED_END + 5, BENCH_H),
                   P(W + STEP - 6, KIT_Y - 5, BENCH_H), P(SINK_X0 + 6, KIT_Y - 5, BENCH_H)], C["steel"]))
    a, b = P(SINK_X0 + 22, (BED_END + KIT_Y) / 2, BENCH_H)
    o.append(text(a, b + 5, "水槽", 13, bold=True))
    # --- wardrobe
    box(ADULT_W, FIX, 0, W, BED_END, H_SIDE, C["ward"], "衣柜")
    face_y(ADULT_W + 3, W - 3, BED_END, 4, H_SIDE - 4, shade(C["ward"], 1.08), "衣柜门")
    # --- seat boxes / foot section
    box(40, FIX, 0, ADULT_W, BED_END, SEAT_H, C["ply2"])
    box(40, FIX + (UP if mode == "day" else 0), SEAT_H, ADULT_W, BED_END, SEAT_H + PAD, C["seat"])
    box(0, FIX, 0, 40, BED_END, SEAT_H + PAD, C["toilet"])
    if mode == "day":
        a, b = P(77, FIX + UP + 19, SEAT_H + PAD)
        o.append(text(a, b + 5, "座位（坐两人）", 13, bold=True, fill="#ffffff"))
        a, b = P(20, FIX + UP + 19, SEAT_H + PAD)
        o.append(text(a, b + 5, "马桶", 13, bold=True))
    if mode == "night":
        half = ADULT_W / 2
        box(half + 0.5, FIX, BED_H - 2, ADULT_W, BED_END, BED_H, C["ply"])
        box(half + 1, FIX, BED_H, ADULT_W - 1, BED_END - 1, BED_H + MAT, C["mat"], "床脚右")
        box(0, FIX, BED_H - 2, half - 0.5, BED_END, BED_H, C["ply"])
        box(1, FIX, BED_H, half - 1, BED_END - 1, BED_H + MAT, C["mat"], "床脚左")
    # --- under the fixed platform
    cw, cd, ch = CASE
    cx0 = (W - cw) / 2
    px0 = (W - 2 * cd) / 2
    box(0, FIX - 2, 0, W, FIX, BED_H - 2, C["ply"])
    box(W - ARCH["w"], ARCH["y0"], 0, W, ARCH["y1"], ARCH["h"], C["arch"])
    box(px0 + cd, cd, 0, px0 + 2 * cd, cd + cw, ch, C["case"])
    box(px0, cd, 0, px0 + cd, cd + cw, ch, C["case"])
    box(0, ARCH["y0"], 0, ARCH["w"], ARCH["y1"], ARCH["h"], C["arch"])
    box(cx0, 0, 0, cx0 + cw, cd, ch, C["case"])
    a, b = P(cx0 + cw / 2, 0, ch / 2)
    o.append(text(a, b + 5, "28寸箱子 ×3", 13, fill="#ffffff", bold=True))
    # --- platform + mattresses
    box(0, 0, BED_H - 2, W, FIX, BED_H, C["ply"])
    box(ADULT_W + 1, 1, BED_H, W - 1, FIX - 1, BED_H + 6, C["mat2"], "小珵 40×130")
    if mode == "day":
        zt = BED_H + MAT
        box(0, FIX + MAT + 2, zt + 4, ADULT_W, FIX + UP, zt + FOOT - 4, C["seat"], op=0.45)
        box(0, FIX + MAT, zt, ADULT_W, FIX + MAT + 2, zt + FOOT, C["ply"], op=0.45)
        box(0, FIX, zt, ADULT_W, FIX + MAT, zt + FOOT, C["mat"], op=0.45)
        a, b = P(ADULT_W / 2, FIX, zt + FOOT / 2 + 6)
        o.append(text(a, b, "床脚床垫竖起（背面是靠背）", 13, bold=True))
        box(1, 1, BED_H, ADULT_W - 1, FIX - 0.5, BED_H + MAT, C["mat"], "大人床 114×130（不用收）")
    else:
        box(1, 1, BED_H, ADULT_W - 1, FIX - 1, BED_H + MAT, C["mat"], "大人床 114×185")
    # --- notes
    a, b = P(W / 2 + 30, -22, 0)
    o.append(text(a, b + 10, "尾门（头朝这边）", 15, bold=True, fill=C["wall"]))
    a, b = P(-12, SEAT - 110, 0)
    o.append(text(a - 10, b + 24, "左门（进出）", 14, anchor="end", bold=True, fill="#2e7d32"))
    o.append(text(Wpx / 2, Hpx - 18,
                  "左侧墙和车顶未画出；竖起的床脚段画成半透明，能看到后面的座位 · 单位厘米 · 箱子按 78×52×32 估算",
                  13, fill="#666"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    files = {
        "plan-day.svg": plan("day"),
        "plan-night.svg": plan("night"),
        "plan-under.svg": plan("under"),
        "side.svg": side(),
        "view-day.svg": iso("day"),
        "view-night.svg": iso("night"),
    }
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", name)

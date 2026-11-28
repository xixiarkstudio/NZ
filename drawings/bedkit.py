#!/usr/bin/env python3
"""Pre-trip bed platform: assembly drawing and cutting sheet, in Chinese and English.
Plan/elevations in cm, cutting sheet in mm."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "WenQuanYi Zen Hei, Arial, sans-serif"
RED = "#b02a2a"
COL = dict(A="#d9b98a", B="#e8cfa3", C="#7a5a2c", D="#8c6a36", E="#a5814a", F="#c08a3e", X="#e3e0d8")
LANG = "cn"


def L(cn, en):
    return cn if LANG == "cn" else en


def t(x, y, s, size=14, anchor="middle", fill="#1d1d1d", bold=False, rot=None):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    fw = ' font-weight="bold"' if bold else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{tr}{fw}>{s}</text>'


def r(x, y, w, h, fill, stroke="#3a3a3a", sw=1.2, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def ln(x0, y0, x1, y1, stroke, sw=1.5, extra=""):
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def dimh(x0, x1, y, label):
    return (ln(x0, y, x1, y, RED, 1) + ln(x0, y - 5, x0, y + 5, RED, 1) + ln(x1, y - 5, x1, y + 5, RED, 1)
            + t((x0 + x1) / 2, y - 5, label, 13, fill=RED))


def dimv(x, y0, y1, label, side=-1):
    return (ln(x, y0, x, y1, RED, 1) + ln(x - 5, y0, x + 5, y0, RED, 1) + ln(x - 5, y1, x + 5, y1, RED, 1)
            + t(x + side * 7, (y0 + y1) / 2, label, 13, fill=RED, rot=-90))


def head(w, h, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">',
            f'<rect width="{w}" height="{h}" fill="#fff"/>', t(w / 2, 40, title, 26, bold=True)]


DX = (25, 76.8, 128.6)        # D boards: distance from the left wall
EX = (2, 89.2, 150.3)         # E boards
FX = 45                       # optional extra leg from the offcut
TH = 1.7
BH = 40


# ------------------------------------------------------------------ assembly drawing
def bed():
    Wpx, Hpx = 1750, 1560
    o = head(Wpx, Hpx, L("床（出发前版本）· 组装图", "Camper bed platform – assembly drawing"))
    S = 3.5
    W, LEN = 154, 192

    # ---- plan
    ox, oy = 150, 130

    def X(x):
        return ox + x * S

    def Y(y):
        return oy + (LEN - y) * S

    def box(x0, y0, x1, y1, fill, **kw):
        return r(X(x0), Y(y1), (x1 - x0) * S, (y1 - y0) * S, fill, **kw)

    o.append(t(X(W / 2), oy - 30, L("① 俯视 · 单位厘米", "1. Top view (cm)"), 18, bold=True))
    o.append(box(0, 0, W, LEN, "#f4efe6", sw=2.5, stroke="#6b6b6b"))
    for x0 in (0, W - 21):
        o.append(box(x0, 49, x0 + 21, 119, "#bdbdbd", extra='fill-opacity="0.7"'))
        o.append(t(X(x0 + 10.5), Y(84) + 5, L("轮拱", "wheel"), 12))
        if LANG == "en":
            o.append(t(X(x0 + 10.5), Y(84) + 20, "arch", 12))
    dash = 'stroke-dasharray="6 4" fill-opacity="0.55"'
    for (nm, x0, y0, dx, dy) in ((L("28寸箱", '28" case'), 27.5, 38, 48, 81), (L("28寸箱", '28" case'), 79.3, 38, 48, 81),
                                 (L("24寸", '24"'), 5, 122, 39, 66), (L("20寸", '20"'), 96, 124, 47, 42)):
        o.append(box(x0, y0, x0 + dx, y0 + dy, "#c9c2dd", extra=dash))
        o.append(t(X(x0 + dx / 2), Y(y0 + dy / 2) + 5, nm, 13, fill="#55498a"))
    o.append(t(X(52), Y(18) + 5, L("空位：鞋、椅子", "spare space"), 12, fill="#666"))
    o.append(t(X(103), Y(18) + 5, L("空位", "spare space"), 12, fill="#666"))
    o.append(box(2, 120, 152, 120 + TH, COL["C"]))
    o.append(t(X(118), Y(121) - 7, "C", 16, fill=COL["C"], bold=True))
    for xx in DX:
        o.append(box(xx, 0, xx + TH, 120, COL["D"]))
        o.append(t(X(xx) - 7, Y(8), "D", 16, anchor="end", fill=COL["D"], bold=True))
    for xx in EX:
        o.append(box(xx, 120 + TH, xx + TH, 180 + TH, COL["E"]))
    o.append(t(X(EX[0]) + 10, Y(174), "E", 16, anchor="start", fill=COL["E"], bold=True))
    o.append(t(X(EX[1]) + 10, Y(174), "E", 16, anchor="start", fill=COL["E"], bold=True))
    o.append(t(X(EX[2]) - 6, Y(174), "E", 16, anchor="end", fill=COL["E"], bold=True))
    o.append(box(FX, 135, FX + TH, 165, COL["F"]))
    o.append(t(X(FX) + 10, Y(150) + 5, "F", 16, anchor="start", fill=COL["F"], bold=True))
    for (x0, y0, x1, y1) in ((2, 0, 152, 60), (2, 60, 152, 120), (2, 120, 92, 180), (92, 120, 152, 180)):
        o.append(box(x0, y0, x1, y1, "none", stroke=RED, sw=2, extra='stroke-dasharray="10 5"'))
    o.append(t(X(140), Y(30) + 6, "A", 22, fill=RED, bold=True))
    o.append(t(X(140), Y(90) + 6, "A", 22, fill=RED, bold=True))
    o.append(t(X(70), Y(128), "B1", 20, fill=RED, bold=True))
    o.append(t(X(140), Y(128), "B2", 20, fill=RED, bold=True))
    o.append(t(X(W / 2), Y(-6), L("尾门", "TAILGATE (rear door)"), 15, bold=True))
    o.append(t(X(W / 2), Y(LEN) - 7, L("过道 / 车头方向", "aisle / front of van"), 13, fill="#666"))
    yb = Y(0) + 46
    o.append(dimh(X(0), X(DX[0]), yb, "25"))
    o.append(dimh(X(DX[0]), X(DX[1]), yb, "52"))
    o.append(dimh(X(DX[1]), X(DX[2]), yb, "52"))
    o.append(dimh(X(DX[2]), X(W), yb, "25"))
    o.append(dimh(X(0), X(W), yb + 30, L("车内宽 154", "van floor width 154")))
    xr = X(W) + 22
    o.append(dimv(xr, Y(120), Y(0), L("固定床 120", "fixed part 120"), side=1))
    o.append(dimv(xr, Y(180), Y(120), L("床脚 60", "foot part 60"), side=1))
    o.append(t(X(0), yb + 62, L("红色虚线 = 床面板的边（A、B1、B2）；D 的数字是板的左边到左墙的距离。",
                                "Red dashed = edges of the top panels (A, B1, B2). D dimensions: left wall to left face of board."),
               13, anchor="start", fill="#555"))

    # ---- rear elevation
    ex, ey = 880, 150

    def EX_(x):
        return ex + x * S

    def EZ(z):
        return ey + (72 - z) * S

    def ebox(x0, z0, x1, z1, fill, **kw):
        return r(EX_(x0), EZ(z1), (x1 - x0) * S, (z1 - z0) * S, fill, **kw)

    o.append(t(EX_(W / 2), ey - 50, L("② 从尾门往里看", "2. View from the tailgate"), 18, bold=True))
    o.append(ln(EX_(0), EZ(0), EX_(W), EZ(0), "#6b6b6b", 3))
    o.append(ln(EX_(0), EZ(0), EX_(0), EZ(70), "#6b6b6b", 3))
    o.append(ln(EX_(W), EZ(0), EX_(W), EZ(70), "#6b6b6b", 3))
    for x0 in (0, W - 21):
        o.append(ebox(x0, 0, x0 + 21, 17, "#bdbdbd"))
    for xx in DX:
        o.append(ebox(xx, 0, xx + TH, BH, COL["D"]))
        o.append(t(EX_(xx + 0.8), EZ(BH + TH + 3) , "D", 14, fill=COL["D"], bold=True))
    for x0 in (27.5, 79.3):
        o.append(ebox(x0, 0, x0 + 48, 29, "#c9c2dd", extra=dash))
        o.append(t(EX_(x0 + 24), EZ(14), L("28寸箱 48×29", '28" case 48×29'), 12, fill="#55498a"))
    o.append(ebox(2, BH, 152, BH + TH, COL["A"]))
    o.append(ebox(2, BH + TH, 152, BH + TH + 22, "#aebccb", extra='fill-opacity="0.6"'))
    o.append(t(EX_(77), EZ(BH + 13), L("Queen 床垫 150 宽", "Queen mattress 150 wide"), 13))
    o.append(t(EX_(60), EZ(BH + TH) + 15, L("A 床面板", "A top panel"), 12, fill="#7a5a2c"))
    o.append(dimv(EX_(0) - 18, EZ(BH), EZ(0), L("竖板高 40", "boards 40 high")))
    o.append(dimh(EX_(DX[0] + TH), EX_(DX[1]), EZ(0) + 28, L("巷道 50", "lane 50")))
    o.append(dimh(EX_(DX[1] + TH), EX_(DX[2]), EZ(0) + 28, L("巷道 50", "lane 50")))

    # ---- side elevation
    sx, sy = 880, 560

    def SXf(y):
        return sx + y * S

    def SZ(z):
        return sy + (72 - z) * S

    def sbox(y0, z0, y1, z1, fill, **kw):
        return r(SXf(y0), SZ(z1), (y1 - y0) * S, (z1 - z0) * S, fill, **kw)

    o.append(t(SXf(95), sy - 50, L("③ 侧面（左边是尾门）", "3. Side view (tailgate on the left)"), 18, bold=True))
    o.append(ln(SXf(0), SZ(0), SXf(200), SZ(0), "#6b6b6b", 3))
    o.append(ln(SXf(0), SZ(0), SXf(0), SZ(70), "#6b6b6b", 3))
    o.append(sbox(0, 0, 120, BH, COL["D"]))
    o.append(t(SXf(60), SZ(20) + 5, L("D  120 × 40（共 3 块）", "D  1200 × 400 mm (x3)"), 14, fill="#fff", bold=True))
    o.append(sbox(120, 0, 120 + TH, BH - 0.6, COL["C"]))
    o.append(t(SXf(121), SZ(BH + TH + 3), "C", 14, fill=COL["C"], bold=True))
    o.append(sbox(120 + TH, 0, 180 + TH, BH, COL["E"]))
    o.append(t(SXf(151), SZ(20) + 5, L("E  60 × 40（3 块）", "E  600 × 400 (x3)"), 13, fill="#fff", bold=True))
    o.append(sbox(0, BH, 60, BH + TH, COL["A"]))
    o.append(sbox(60, BH, 120, BH + TH, COL["A"]))
    o.append(sbox(120, BH, 180, BH + TH, COL["B"]))
    o.append(sbox(0.5, BH + TH, 190, BH + TH + 22, "#aebccb", extra='fill-opacity="0.6"'))
    o.append(t(SXf(95), SZ(BH + 13), L("Queen 床垫 190 长", "Queen mattress 190 long"), 13))
    o.append(t(SXf(30), SZ(BH + TH) + 15, "A", 13, fill="#7a5a2c", bold=True))
    o.append(t(SXf(90), SZ(BH + TH) + 15, "A", 13, fill="#7a5a2c", bold=True))
    o.append(t(SXf(150), SZ(BH + TH) + 15, "B1 / B2", 13, fill="#7a5a2c", bold=True))
    o.append(dimh(SXf(0), SXf(60), SZ(0) + 28, "60"))
    o.append(dimh(SXf(60), SXf(120), SZ(0) + 28, "60"))
    o.append(dimh(SXf(120), SXf(180), SZ(0) + 28, "60"))
    o.append(dimv(SXf(0) - 18, SZ(BH + TH), SZ(0), L("床面高 约42", "top at ~42")))

    # ---- parts + steps
    ly = 990
    o.append(t(150, ly, L("④ 零件", "4. Parts (17 mm plywood)"), 18, anchor="start", bold=True))
    rows = [
        ("A", L("固定床面", "fixed top"), "1500 × 600 mm", "x2"),
        ("B1", L("床脚面板", "foot top"), "900 × 600 mm", "x1"),
        ("B2", L("床脚面板", "foot top"), "600 × 600 mm", "x1"),
        ("C", L("横挡板", "cross board"), "1500 × 394 mm", "x1"),
        ("D", L("纵向竖板", "lengthwise boards"), "1200 × 400 mm", "x3"),
        ("E", L("床脚支腿板", "foot legs"), "600 × 400 mm", "x3"),
        ("F", L("加的一条腿（边角料）", "extra leg (offcut)"), "300 × 394 mm", "x1"),
    ]
    for i, (a, b, c, d) in enumerate(rows):
        yy = ly + 34 + i * 29
        o.append(t(150, yy, a, 15, anchor="start", bold=True, fill=RED))
        o.append(t(200, yy, b, 14, anchor="start"))
        o.append(t(440, yy, c, 14, anchor="start"))
        o.append(t(610, yy, d, 14, anchor="start"))
    yy = ly + 34 + len(rows) * 29 + 14
    hw = [L("角码 约50毫米 × 32 个", "Angle brackets ~50 mm  x32"),
          L("平连接片 × 4 片（拼两块 A）", "Flat mending plates  x4 (join the two A panels)"),
          L("木螺丝 8g × 16 毫米：进地板、装角码", "Wood screws 8g x 16 mm: brackets and floor"),
          L("木螺丝 8g × 40 毫米：床面板拧进竖板", "Wood screws 8g x 40 mm: top panels into board edges")]
    for i, s in enumerate(hw):
        o.append(t(150, yy + i * 27, s, 14, anchor="start"))

    sx2 = 880
    o.append(t(sx2, ly, L("⑤ 组装顺序", "5. Assembly order"), 18, anchor="start", bold=True))
    steps_cn = [
        "1. 拆旧床，清空，扫地。",
        "2. 照图①在地板上用铅笔画出 D、C、E 的位置。",
        "3. 立 3 块 D，每块两面各 2 个角码拧到地板上。",
        "4. 立 C，贴住 3 块 D 的前端；C 和每块 D、C 和地板都用角码连上。",
        "5. 把两个 28 寸箱子从尾门推进巷道试一下，能进出再继续。",
        "6. 盖 2 块 A：先钻 3 毫米引孔，再用 40 的螺丝拧进 D 的板边。",
        "7. 两块 A 的接缝下面，在竖板之间装 4 片平连接片。",
        "8. 立 3 块 E 和 F。中间那块 E 要正对 B1、B2 的接缝。",
        "9. 盖 B1、B2，螺丝拧进 E、F 和 C。",
        "10. 磨掉毛刺，铺床垫。两个人坐上去、跪上去试。",
        "",
        "进地板的螺丝只能用 16 毫米的。",
        "C 和中间那块 E 比别的板矮约 6 毫米（锯缝造成的），下面垫平再固定。",
    ]
    steps_en = [
        "1. Remove the old bed, clear and sweep the floor.",
        "2. Mark the positions of D, C and E on the floor (see view 1).",
        "3. Stand the three D boards; 2 brackets each side into the floor.",
        "4. Stand C against the front ends of the D boards; bracket C to each D and to the floor.",
        "5. Test: slide both 28-inch suitcases into the lanes from the tailgate.",
        "6. Fit the two A panels: 3 mm pilot holes, then 40 mm screws into the D board edges.",
        "7. Under the joint between the A panels, fit 4 flat plates between the boards.",
        "8. Stand the three E boards and F. The middle E sits under the B1/B2 joint.",
        "9. Fit B1 and B2; screw into E, F and C.",
        "10. Sand sharp edges, put the mattress on, test by sitting and kneeling.",
        "",
        "Floor screws must be 16 mm only.",
        "C and one E are ~6 mm lower (saw kerf): pack them level before fixing.",
    ]
    steps = steps_cn if LANG == "cn" else steps_en
    for i, s in enumerate(steps):
        o.append(t(sx2, ly + 34 + i * 29, s, 14, anchor="start", fill=RED if i >= 11 else "#1d1d1d"))
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ cutting sheet
def cut():
    Wpx, Hpx = 1500, 1560
    o = head(Wpx, Hpx, L("裁板图（给 Bunnings）· 单位毫米", "Cutting list for Bunnings – all dimensions in mm"))
    cs = 0.44
    cx = 150

    def CX(v):
        return cx + v * cs

    def sheet(cy, title, parts, cuts, notes):
        o.append(t(cx, cy - 34, title, 19, anchor="start", bold=True))
        o.append(r(cx, cy, 2400 * cs, 1200 * cs, "#f3f1ec", sw=3, stroke="#555"))
        for (lab, x, y, w, h, colk, txt) in parts:
            dark = colk in "CDE"
            o.append(r(CX(x), cy + y * cs, w * cs, h * cs, COL[colk]))
            o.append(t(CX(x + w / 2), cy + (y + h / 2) * cs - 4, lab, 26, bold=True, fill="#fff" if dark else "#1d1d1d"))
            o.append(t(CX(x + w / 2), cy + (y + h / 2) * cs + 22, txt, 17, fill="#fff" if dark else "#1d1d1d"))
        for (n, x0, y0, x1, y1, lx, ly2) in cuts:
            o.append(ln(CX(x0), cy + y0 * cs, CX(x1), cy + y1 * cs, RED, 4))
            o.append(f'<circle cx="{CX(lx):.1f}" cy="{cy + ly2 * cs:.1f}" r="15" fill="#fff" stroke="{RED}" stroke-width="2.5"/>')
            o.append(t(CX(lx), cy + ly2 * cs + 6, str(n), 18, fill=RED, bold=True))
        o.append(dimh(CX(0), CX(2400), cy - 10, "2400"))
        o.append(dimv(CX(0) - 16, cy, cy + 1200 * cs, "1200"))
        for i, n in enumerate(notes):
            o.append(t(cx, cy + 1200 * cs + 28 + i * 24, n, 15, anchor="start", fill="#333"))

    sheet(150, L("第 1 张板：17 毫米胶合板 2400 × 1200", "SHEET 1 – 17 mm plywood 2400 x 1200"), [
        ("A", 0, 0, 1500, 600, "A", "1500 x 600"),
        ("A", 0, 600, 1500, 600, "A", "1500 x 600"),
        ("B1", 1500, 0, 900, 600, "B", "900 x 600"),
        ("B2", 1500, 600, 600, 600, "B", "600 x 600"),
        (L("余料", "offcut"), 2100, 600, 300, 600, "X", "300 x 600"),
    ], [
        (1, 1500, 0, 1500, 1200, 1500, 60),
        (2, 0, 600, 1500, 600, 80, 600),
        (3, 1500, 600, 2400, 600, 2330, 600),
        (4, 2100, 600, 2100, 1200, 2100, 1130),
    ], [
        L("4 刀，按红圈数字的顺序裁。", "4 cuts, in the order of the red numbers."),
        L("刀 1：离左边 1500。刀 2、3：离上边 600。刀 4：从刀 1 的切边量 600。",
          "Cut 1: 1500 from the left edge. Cuts 2 and 3: 600 from the top edge. Cut 4: 600 from the cut-1 edge."),
    ])
    sheet(850, L("第 2 张板：17 毫米胶合板 2400 × 1200", "SHEET 2 – 17 mm plywood 2400 x 1200"), [
        ("D", 0, 0, 1200, 400, "D", "1200 x 400"),
        ("D", 1200, 0, 1200, 400, "D", "1200 x 400"),
        ("D", 0, 400, 1200, 400, "D", "1200 x 400"),
        ("E", 1200, 400, 600, 400, "E", "600 x 400"),
        ("E", 1800, 400, 600, 400, "E", "600 x 400"),
        ("C", 0, 800, 1500, 400, "C", L("1500 x 400（余下的宽度）", "1500 x 400 (remainder)")),
        ("E", 1500, 800, 600, 400, "E", "600 x 400"),
        ("F", 2100, 800, 300, 400, "F", "300 x 400"),
    ], [
        (1, 0, 400, 2400, 400, 60, 400),
        (2, 0, 800, 2400, 800, 60, 800),
        (3, 1200, 0, 1200, 400, 1200, 200),
        (4, 1200, 400, 1200, 800, 1200, 600),
        (5, 1800, 400, 1800, 800, 1800, 600),
        (6, 1500, 800, 1500, 1200, 1500, 1000),
        (7, 2100, 800, 2100, 1200, 2100, 1000),
    ], [
        L("7 刀。先裁刀 1、2，得到 3 条 400 宽的长条；再按图把每条截短。",
          "7 cuts. First cuts 1 and 2 make three strips 400 wide; then cross-cut each strip as shown."),
        L("重要：前两条必须正好 400 宽。第 3 条会窄几毫米，没关系。",
          "IMPORTANT: the first two strips must both be exactly 400 wide. The third strip will be a few mm narrower – that is fine."),
    ])
    o.append(t(cx, Hpx - 60, L("所有尺寸都是 100 毫米的整数；除两块 300 的余料外，没有短于 600 的板。18 毫米板也可以。",
                              "Every cut is on a 100 mm increment. No piece is shorter than 600 except the two 300 offcuts. 18 mm plywood is also OK."),
               15, anchor="start", bold=True))
    o.append(t(cx, Hpx - 32, L("我要带走所有的板和余料。", "I will take all pieces and offcuts with me. Thank you!"), 15, anchor="start"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    for lang in ("cn", "en"):
        LANG = lang
        for name, fn in (("bed", bed), ("cut", cut)):
            with open(os.path.join(OUT, f"{name}-{lang}.svg"), "w", encoding="utf-8") as f:
                f.write(fn())
            print("wrote", f"{name}-{lang}.svg")

#!/usr/bin/env python3
"""One-day bed build (before the South Island trip): assembly plan + cutting diagrams. Dimensions in mm on the
cutting diagrams, cm on the plan."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "WenQuanYi Zen Hei, sans-serif"
RED = "#b02a2a"
COL = dict(A="#d9b98a", B="#e8cfa3", C="#7a5a2c", D="#8c6a36", E="#a5814a", X="#e3e0d8")


def t(x, y, s, size=14, anchor="middle", fill="#1d1d1d", bold=False, rot=None):
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ""
    fw = ' font-weight="bold"' if bold else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{tr}{fw}>{s}</text>'


def r(x, y, w, h, fill, stroke="#3a3a3a", sw=1.2, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def build():
    Wpx, Hpx = 1700, 1520
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wpx}" height="{Hpx}" viewBox="0 0 {Wpx} {Hpx}" font-family="{FONT}">',
         f'<rect width="{Wpx}" height="{Hpx}" fill="#fff"/>',
         t(Wpx / 2, 38, "一天版的床：组装图和裁板图（全部按 Bunnings 能裁的尺寸）", 26, bold=True)]

    # ---------------- plan (cm), tail at the bottom
    S = 3.6
    ox, oy = 120, 120
    W, LEN = 154, 190

    def X(x):
        return ox + x * S

    def Y(y):
        return oy + (LEN - y) * S

    def box(x0, y0, x1, y1, fill, **kw):
        return r(X(x0), Y(y1), (x1 - x0) * S, (y1 - y0) * S, fill, **kw)

    o.append(t(X(W / 2), oy - 26, "① 俯视：竖板的位置（厘米）", 17, bold=True))
    o.append(box(0, 0, W, LEN, "#f4efe6", sw=2.5, stroke="#6b6b6b"))
    for x0 in (0, W - 21):
        o.append(box(x0, 49, x0 + 21, 119, "#bdbdbd", extra='fill-opacity="0.7"'))
        o.append(t(X(x0 + 10.5), Y(84) + 5, "轮拱", 12))
    dash = 'stroke-dasharray="6 4" fill-opacity="0.55"'
    for (nm, x0, y0, dx, dy) in (("28寸", 27.5, 38, 48, 81), ("28寸", 79.3, 38, 48, 81),
                                 ("24寸", 8, 124, 66, 39), ("20寸", 96, 124, 47, 42)):
        o.append(box(x0, y0, x0 + dx, y0 + dy, "#c9c2dd", extra=dash))
        o.append(t(X(x0 + dx / 2), Y(y0 + dy / 2) + 5, nm, 13, fill="#55498a"))
    o.append(t(X(52), Y(18) + 5, "空位：鞋、椅子", 12, fill="#666"))
    o.append(t(X(103), Y(18) + 5, "空位", 12, fill="#666"))
    o.append(t(X(142), Y(25) + 5, "脏衣袋", 12, fill="#666"))
    # C
    o.append(box(2, 120, 152, 121.7, COL["C"]))
    o.append(t(X(40), Y(121) - 7, "C 横挡板", 13, fill=COL["C"], bold=True))
    # D
    for xx in (25, 76.8, 128.6):
        o.append(box(xx, 0, xx + 1.7, 120, COL["D"]))
        o.append(t(X(xx) - 7, Y(10), "D", 15, anchor="end", fill=COL["D"], bold=True))
    # E
    for xx in (2, 89.2, 150.3):
        o.append(box(xx, 121.7, xx + 1.7, 181.7, COL["E"]))
    o.append(t(X(2) + 12, Y(172), "E", 15, anchor="start", fill=COL["E"], bold=True))
    o.append(t(X(89.2) + 12, Y(172), "E", 15, anchor="start", fill=COL["E"], bold=True))
    o.append(t(X(150.3) - 6, Y(172), "E", 15, anchor="end", fill=COL["E"], bold=True))
    # tops
    for (x0, y0, x1, y1, lab) in ((2, 0, 152, 60, "A"), (2, 60, 152, 120, "A"), (2, 120, 92, 180, "B1"), (92, 120, 152, 180, "B2")):
        o.append(box(x0, y0, x1, y1, "none", stroke=RED, sw=2, extra='stroke-dasharray="10 5"'))
    o.append(t(X(14), Y(8), "A", 20, fill=RED, bold=True))
    o.append(t(X(14), Y(108), "A", 20, fill=RED, bold=True))
    o.append(t(X(46), Y(176), "B1", 18, fill=RED, bold=True))
    o.append(t(X(122), Y(176), "B2", 18, fill=RED, bold=True))
    o.append(t(X(W / 2), Y(-7), "尾门（28 寸箱子从这里推进去）", 14, bold=True))
    o.append(t(X(W / 2), Y(LEN) - 6, "过道（24 寸、20 寸和收纳箱从这里塞到床脚下面）", 13, fill="#666"))
    o.append(t(X(W) + 12, Y(60) + 5, "固定床 120", 13, anchor="start", fill=RED))
    o.append(t(X(W) + 12, Y(150) + 5, "床脚 60", 13, anchor="start", fill=RED))
    for xx, lab in ((25, "25"), (76.8, "77"), (128.6, "129")):
        o.append(t(X(xx), Y(0) + 56, lab, 12, fill=COL["D"]))
    o.append(t(X(0) - 8, Y(0) + 56, "竖板离左墙", 12, anchor="end", fill=COL["D"]))

    # ---------------- cutting diagrams (mm)
    cs = 0.30
    cx, cy = 860, 130

    def CX(v):
        return cx + v * cs

    def sheet(y_off, title, parts, notes):
        o.append(t(cx, cy + y_off - 14, title, 17, anchor="start", bold=True))
        o.append(r(cx, cy + y_off, 2400 * cs, 1200 * cs, "#f3f1ec", sw=2.5, stroke="#6b6b6b"))
        for (lab, x, y, w, h, colk, txt) in parts:
            dark = colk in "CDE"
            o.append(r(CX(x), cy + y_off + y * cs, w * cs, h * cs, COL[colk] if colk != "X" else "#e3e0d8"))
            o.append(t(CX(x + w / 2), cy + y_off + (y + h / 2) * cs - 2, lab, 18, bold=True, fill="#fff" if dark else "#1d1d1d"))
            o.append(t(CX(x + w / 2), cy + y_off + (y + h / 2) * cs + 17, txt, 13, fill="#fff" if dark else "#1d1d1d"))
        for i, n in enumerate(notes):
            o.append(t(cx, cy + y_off + 1200 * cs + 22 + i * 20, n, 13, anchor="start", fill="#555"))

    sheet(0, "② 第 1 张板（2400 × 1200 × 17 毫米）：床面", [
        ("A", 0, 0, 1500, 600, "A", "1500 × 600"),
        ("A", 0, 600, 1500, 600, "A", "1500 × 600"),
        ("B1", 1500, 0, 900, 600, "B", "900 × 600"),
        ("B2", 1500, 600, 600, 600, "B", "600 × 600"),
        ("余", 2100, 600, 300, 600, "X", "300"),
    ], ["裁 4 刀：先在 1500 处竖裁一刀；两半各在 600 处横裁一刀；", "右下那块再在 600 处裁一刀，得到 B2。"])
    sheet(480, "③ 第 2 张板（2400 × 1200 × 17 毫米）：竖板", [
        ("D", 0, 0, 1200, 400, "D", "1200 × 400"),
        ("D", 1200, 0, 1200, 400, "D", "1200 × 400"),
        ("D", 0, 400, 1200, 400, "D", "1200 × 400"),
        ("E", 1200, 400, 600, 400, "E", "600 × 400"),
        ("E", 1800, 400, 600, 400, "E", "600 × 400"),
        ("C", 0, 800, 1500, 400, "C", "1500 × 约394"),
        ("E", 1500, 800, 600, 400, "E", "600 × 约394"),
        ("余", 2100, 800, 300, 400, "X", "300"),
    ], ["裁 7 刀：先横裁两刀成 3 条 400 宽的长条（第 3 条会因为锯缝窄几毫米），", "再按图截长度。窄的那条出 C 和中间那块 E，装的时候 E 下面垫平。"])

    # ---------------- list + steps
    ly = 1050
    o.append(t(120, ly, "④ 要买的东西", 17, anchor="start", bold=True))
    rows = [
        ("A", "固定床面", "1500 × 600", "2 块"),
        ("B1 B2", "床脚面板", "900 × 600、600 × 600", "各 1 块"),
        ("C", "横挡板", "1500 × 394", "1 块"),
        ("D", "纵向竖板", "1200 × 400", "3 块"),
        ("E", "床脚支腿板", "600 × 400", "3 块"),
        ("", "17 毫米胶合板", "2400 × 1200", "2 张"),
        ("", "角码（约 50 毫米）", "", "30 个"),
        ("", "平连接片（拼接床面用）", "", "4 片"),
        ("", "木螺丝", "8g × 16 一盒；8g × 40 一盒", ""),
        ("", "工具", "充电电钻、3 毫米钻头、十字批头、铅笔、砂纸", ""),
    ]
    for i, (a, b, c, d) in enumerate(rows):
        yy = ly + 32 + i * 28
        o.append(t(120, yy, a, 15, anchor="start", bold=True, fill=RED))
        o.append(t(185, yy, b, 14, anchor="start"))
        o.append(t(390, yy, c, 14, anchor="start"))
        o.append(t(720, yy, d, 14, anchor="start"))
    sx = 860
    o.append(t(sx, ly, "⑤ 组装顺序", 17, anchor="start", bold=True))
    steps = [
        "1. 拆掉旧床架，清空，地板扫干净。",
        "2. 用卷尺和铅笔在地板上画出每块竖板的位置（照图①）。",
        "3. 立 3 块 D：每块两面各用 2 个角码固定在地板上。",
        "4. 立 C：贴着 3 块 D 的前端，用角码把 C 和每块 D、和地板连起来。",
        "5. 把两个 28 寸箱子从尾门推进去试一下，能进出再往下做。",
        "6. 盖 2 块 A：先钻 3 毫米引孔，再用 40 的螺丝拧进 D 的板边，每条边 5 颗。",
        "7. 两块 A 的接缝下面，在竖板之间装 4 片平连接片。",
        "8. 立 3 块 E（中间那块放在 B1 和 B2 的接缝正下方），用角码固定。",
        "9. 盖 B1、B2，螺丝拧进 E 和 C。",
        "10. 外露的边用砂纸磨一下，铺上床垫。",
        "",
        "进地板的螺丝只能用 16 毫米的，再长会打穿地板碰到车身铁皮。",
        "床面高约 42 厘米、宽 150、长 180；Queen 床垫铺上去，前面探出 10 厘米。",
    ]
    for i, st in enumerate(steps):
        o.append(t(sx, ly + 32 + i * 28, st, 14, anchor="start", fill=RED if i >= 11 else "#1d1d1d"))
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    with open(os.path.join(OUT, "phase1.svg"), "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote phase1.svg")

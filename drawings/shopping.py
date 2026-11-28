#!/usr/bin/env python3
"""Bunnings shopping list for the pre-trip bed build (English for staff, small Chinese gloss for QQ)."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))
FONT = "WenQuanYi Zen Hei, Arial, sans-serif"

ITEMS = [
    ("TIMBER", None, None, None),
    ("17 mm structural plywood, 2400 x 1200", "x 2 sheets", "17毫米结构胶合板（18毫米也行）", "Please cut as shown on my cutting sheet."),
    ("HARDWARE", None, None, None),
    ("Angle brackets, about 50 x 50 mm", "x 32", "角码", None),
    ("Flat mending plates, about 100 mm", "x 4", "平连接片", None),
    ("Wood screws 8g x 16 mm (to fit the brackets)", "x 200", "短螺丝：装角码、进地板", None),
    ("Wood screws 8g x 40 mm, countersunk", "x 100", "长螺丝：床面板拧进竖板", None),
    ("TOOLS", None, None, None),
    ("Ozito PXC 18V Cordless Drill Driver Kit  PXDDK-250C  (I/N 0299323)", "x 1", "充电电钻套装，带电池和充电器", None),
    ("Drill + driver bit set (must include a 3 mm drill bit and the bit for my screws)", "x 1", "钻头和批头套装", None),
    ("Combination square", "x 1", "直角尺", None),
    ("Sandpaper 80 grit and 120 grit + sanding block", "x 1 each", "砂纸和打磨块", None),
    ("Carpenter's pencil", "x 1", "木工铅笔", None),
    ("Safety glasses", "x 2", "护目镜", None),
]


def esc(s):
    return s.replace("&", "&amp;")


def build():
    W = 1300
    rows = []
    y = 150
    for (en, qty, cn, note) in ITEMS:
        if qty is None:
            rows.append(f'<rect x="60" y="{y-26}" width="{W-120}" height="36" fill="#2f4d63"/>'
                        f'<text x="76" y="{y}" font-size="20" fill="#fff" font-weight="bold">{en}</text>')
            y += 50
            continue
        rows.append(f'<rect x="64" y="{y-22}" width="24" height="24" fill="none" stroke="#333" stroke-width="2"/>')
        rows.append(f'<text x="104" y="{y}" font-size="21" fill="#111">{esc(en)}</text>')
        rows.append(f'<text x="{W-70}" y="{y}" font-size="21" fill="#b02a2a" font-weight="bold" text-anchor="end">{qty}</text>')
        rows.append(f'<text x="104" y="{y+24}" font-size="15" fill="#777">{cn}</text>')
        if note:
            rows.append(f'<text x="104" y="{y+48}" font-size="18" fill="#b02a2a" font-weight="bold">{note}</text>')
            y += 24
        rows.append(f'<line x1="60" y1="{y+38}" x2="{W-60}" y2="{y+38}" stroke="#ddd"/>')
        y += 66
    y += 10
    help_lines = [
        "Could you please help me find these? My English is limited.",
        "Could you cut the two plywood sheets for me, as shown on my cutting sheet?",
        "Which driver bit fits these screws?",
    ]
    rows.append(f'<rect x="60" y="{y-26}" width="{W-120}" height="36" fill="#7a5a2c"/>'
                f'<text x="76" y="{y}" font-size="20" fill="#fff" font-weight="bold">QUESTIONS FOR STAFF</text>')
    y += 46
    for hl in help_lines:
        rows.append(f'<text x="76" y="{y}" font-size="20" fill="#111">{hl}</text>')
        y += 34
    H = y + 30
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
           f'<rect width="{W}" height="{H}" fill="#fff"/>',
           f'<text x="{W/2}" y="52" font-size="30" text-anchor="middle" font-weight="bold">Shopping list – camper van bed</text>',
           f'<text x="{W/2}" y="86" font-size="17" text-anchor="middle" fill="#666">Bunnings 购物清单 · 给店员看英文，灰色小字是给你自己看的</text>']
    out += rows
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    with open(os.path.join(OUT, "shopping-en.svg"), "w", encoding="utf-8") as f:
        f.write(build())
    print("wrote shopping-en.svg")

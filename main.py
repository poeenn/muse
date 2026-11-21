"""Sum up 20 November 2026 world news in one image.

Python 3.13, standard library only, no network.
Writes one 1024x1024 PNG to /output/entry.png (or ./entry.png when
/output does not exist, e.g. local testing). Running it twice writes
identical bytes: fixed palette, fixed layout, zlib level 9.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---
BG = (13, 27, 48)
PANEL = (27, 47, 77)
PANEL2 = (22, 40, 66)
INK = (240, 244, 250)
MUTED = (168, 186, 210)
GOLD = (232, 184, 72)
WHITE = (255, 255, 255)
ACCENTS = [(232, 184, 72), (96, 196, 190), (235, 105, 95),
           (122, 162, 247), (196, 132, 232), (110, 200, 120)]

# --- 5x7 bitmap font (uppercase, digits, punctuation) ---
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# --- canvas ---
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)


def line(x0, y0, x1, y1, c, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        for a in range(thick):
            for b in range(thick):
                set_px(x + a, y + b, c)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def text(x, y, s, c, string):
    cx = x
    for ch in string:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            for col in range(5):
                if g[r][col] == '1':
                    rect(cx + col * s, y + r * s, s, s, c)
        cx += 6 * s
    return cx


def text_w(s, string):
    return len(string) * 6 * s - s


# --- stories: (place, headline lines, subline) ---
STORIES = [
    ("SHENZHEN",
     ["TRUMP, XI AND PUTIN", "HOLD FIRST 3-WAY", "SUMMIT IN SHENZHEN"],
     "JOINT PEACE DECLARATION"),
    ("THE HAGUE",
     ["ICJ RULES MYANMAR", "COMMITTED GENOCIDE", "AGAINST THE ROHINGYA"],
     "FIRST RULING VS A STATE"),
    ("KYIV / POLAND",
     ["RUSSIA STRIKES KYIV,", "MISSILES LAND IN", "POLAND, NATO ALERT"],
     "8 KILLED IN KYIV STRIKES"),
    ("MARKETS",
     ["STOCKS FALL FOR A", "FIFTH DAY, NIKKEI", "DOWN 4.8 PERCENT"],
     "AI SELL-OFF HITS TECH"),
    ("RIYADH",
     ["HOUTHI MISSILES HIT", "RIYADH TOWER, SAUDI", "INTERCEPTS MORE"],
     "PIF TOWER DAMAGED"),
    ("ANTALYA",
     ["COP31 DRAFT DROPS", "FOSSIL FUEL PHASE-", "OUT CALL"],
     "CLIMATE TALKS UNDER FIRE"),
]


def icon(kind, x, y, c):
    """Small pictogram in a 64x64 box at (x, y)."""
    if kind == 0:  # three leaders: three circles
        circle(x + 16, y + 22, 13, c)
        circle(x + 32, y + 14, 13, GOLD)
        circle(x + 48, y + 22, 13, c)
        rect(x + 8, y + 42, 48, 5, c)
    elif kind == 1:  # scales of justice
        line(x + 32, y + 8, x + 32, y + 52, c, 3)
        line(x + 10, y + 16, x + 54, y + 16, c, 3)
        line(x + 10, y + 16, x + 6, y + 34, c, 2)
        line(x + 54, y + 16, x + 58, y + 34, c, 2)
        rect(x + 2, y + 34, 12, 4, c)
        rect(x + 52, y + 34, 12, 4, c)
        rect(x + 20, y + 52, 24, 4, c)
    elif kind == 2:  # explosion / strikes
        circle(x + 32, y + 32, 10, c)
        for a, b in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0),
                     (-1, 1), (0, 1), (1, 1)]:
            line(x + 32, y + 32, x + 32 + a * 26, y + 32 + b * 26, c, 3)
    elif kind == 3:  # falling chart
        line(x + 8, y + 54, x + 8, y + 8, c, 3)
        line(x + 8, y + 54, x + 58, y + 54, c, 3)
        line(x + 10, y + 14, x + 24, y + 26, c, 3)
        line(x + 24, y + 26, x + 38, y + 22, c, 3)
        line(x + 38, y + 22, x + 56, y + 46, c, 3)
        line(x + 48, y + 38, x + 56, y + 46, c, 3)
        line(x + 56, y + 46, x + 48, y + 48, c, 3)
    elif kind == 4:  # tower
        rect(x + 24, y + 14, 16, 42, c)
        line(x + 24, y + 14, x + 32, y + 4, c, 3)
        line(x + 40, y + 14, x + 32, y + 4, c, 3)
        for yy in (22, 32, 42):
            rect(x + 28, yy, 8, 5, BG)
    else:  # globe
        circle(x + 32, y + 32, 24, c)
        circle(x + 32, y + 32, 19, BG)
        line(x + 10, y + 28, x + 54, y + 28, BG, 2)
        line(x + 12, y + 40, x + 52, y + 40, BG, 2)
        line(x + 32, y + 10, x + 32, y + 54, BG, 2)


def draw():
    rect(0, 0, W, H, BG)
    # header
    rect(0, 0, W, 6, GOLD)
    title = "WORLD NEWS"
    tw = text_w(9, title)
    text((W - tw) // 2, 28, 9, INK, title)
    sub = "20 NOVEMBER 2026 - FRIDAY"
    sw = text_w(3, sub)
    text((W - sw) // 2, 112, 3, GOLD, sub)
    rect(32, 152, W - 64, 2, (48, 74, 110))

    # panels: 2 cols x 3 rows
    pw, ph, gap = 496, 258, 16
    x0, y0 = 16, 170
    for i, (place, lines, subline) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = x0 + col * (pw + gap)
        y = y0 + row * (ph + gap)
        acc = ACCENTS[i]
        rect(x, y, pw, ph, PANEL)
        rect(x, y, 8, ph, acc)
        # number + place
        text(x + 24, y + 16, 3, acc, "%02d" % (i + 1))
        text(x + 88, y + 16, 3, GOLD, place)
        icon(i, x + pw - 84, y + 8, acc)
        # headline
        hy = y + 62
        for ln in lines:
            text(x + 24, hy, 3, INK, ln)
            hy += 26
        # subline
        rect(x + 24, hy + 10, pw - 48, 2, (48, 74, 110))
        text(x + 24, hy + 22, 2, MUTED, subline)

    # footer
    foot = "SIX STORIES THAT DEFINED 20 NOVEMBER 2026"
    fw = text_w(2, foot)
    text((W - fw) // 2, 988, 2, MUTED, foot)


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(px[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    draw()
    out = "/output/entry.png"
    if not os.path.isdir("/output"):
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
    with open(out, "wb") as f:
        f.write(png_bytes())
    print("wrote", out)


if __name__ == "__main__":
    main()

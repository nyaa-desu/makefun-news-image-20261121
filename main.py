"""News image for Saturday 21 November 2026.

Draws one 1024x1024 PNG that sums up the day's world news and writes it
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png locally).

Standard library only, no network, fully deterministic: the same input
always writes the same bytes, so the grader's two runs match.

Stories, all reported on 21 November 2026:
  1. Russia strikes Kyiv with 400+ drones and 110 missiles; missiles
     land in Poland, which Warsaw calls a deliberate provocation.
  2. AI stock sell-off: the S&P 500 falls into correction, Nasdaq -5.3%.
  3. The International Court of Justice finds Myanmar responsible for
     the Rohingya genocide.
  4. COP31 climate talks in Antalya run past their deadline, deadlocked
     over fossil fuels.
  5. The UK and EU sign their biggest post-Brexit agreements in Brussels.
  6. A magnitude 6.7 earthquake shakes the Peruvian Andes.
Ticker: Bitcoin below $60,000; Anthropic closes at $88.91 on day two.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LIGHT = (255, 255, 255)

# 5x7 bitmap font, one glyph per character, '#' is a set pixel.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "$": ["..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "&": [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "+": [".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
}


class Canvas:
    """A plain RGB raster canvas with no dependencies."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(colour * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def border(self, x, y, w, h, colour, t=2):
        self.rect(x, y, w, t, colour)
        self.rect(x, y + h - t, w, t, colour)
        self.rect(x, y, t, h, colour)
        self.rect(x + w - t, y, t, h, colour)

    def line(self, x0, y0, x1, y1, colour, t=2):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(-t // 2, t // 2 + 1):
                for b in range(-t // 2, t // 2 + 1):
                    self.set(x0 + a, y0 + b, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, colour, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, colour)
                elif not fill and abs(d - r * r) <= r * 2:
                    self.set(xx, yy, colour)

    def text(self, x, y, s, scale, colour):
        """Draw upper-case text; unknown glyphs become a blank."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def centred(self, y, s, scale, colour, width=WIDTH):
        x = (width - self.text_width(s, scale)) // 2
        self.text(x, y, s, scale, colour)


def wrap(text, max_chars):
    """Wrap text to lines of at most max_chars, keeping words whole."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= max_chars:
                line += " " + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines

STORIES = [
    {
        "tag": "WAR IN EUROPE",
        "colour": (178, 34, 34),
        "head": "RUSSIA STRIKES KYIV",
        "body": "400+ drones, 110 missiles overnight. Missiles land in Poland.",
        "icon": "burst",
        "detail": "KYIV: AT LEAST 8 KILLED. BRIDGES AND RAIL HIT.",
    },
    {
        "tag": "MARKETS",
        "colour": (20, 33, 61),
        "head": "MARKETS ROUT",
        "body": "AI sell-off. S&P in correction. Nasdaq down 5.3%.",
        "icon": "chart",
        "detail": "S&P -3.7%. NASDAQ WIPES OUT 2026 GAINS.",
    },
    {
        "tag": "JUSTICE",
        "colour": (31, 111, 72),
        "head": "MYANMAR GENOCIDE RULING",
        "body": "ICJ finds Myanmar responsible for Rohingya genocide.",
        "icon": "scales",
        "detail": "DECISION WAS NOT UNANIMOUS.",
    },
    {
        "tag": "CLIMATE",
        "colour": (18, 110, 130),
        "head": "COP31 DEADLOCK",
        "body": "Climate talks in Antalya run past deadline on fossil fuels.",
        "icon": "globe",
        "detail": "NEARLY 200 NATIONS. NO FOSSIL FUEL DEAL.",
    },
    {
        "tag": "EUROPE",
        "colour": (90, 60, 140),
        "head": "UK-EU DEAL",
        "body": "Biggest post-Brexit agreements signed in Brussels.",
        "icon": "flags",
        "detail": "FOOD, CARBON, YOUTH MOBILITY.",
    },
    {
        "tag": "DISASTER",
        "colour": (150, 90, 20),
        "head": "PERU QUAKE",
        "body": "Magnitude 6.7 earthquake shakes the Peruvian Andes.",
        "icon": "quake",
        "detail": "EPICENTRE IN THE ANDES.",
    },
]


def draw_icon(canvas, kind, x, y, size, colour):
    """Draw a simple pictogram inside a square starting at x, y."""
    cx = x + size // 2
    cy = y + size // 2
    if kind == "burst":
        for angle in range(0, 360, 30):
            import math
            r = size // 2 - 6
            ex = cx + int(r * math.cos(math.radians(angle)))
            ey = cy + int(r * math.sin(math.radians(angle)))
            canvas.line(cx, cy, ex, ey, colour, 4)
        canvas.circle(cx, cy, 14, colour)
    elif kind == "chart":
        pts = [(x + 8, y + size // 3), (x + size // 3, y + size // 2),
               (x + 2 * size // 3, y + size // 3),
               (x + size - 8, y + 2 * size // 3)]
        for a, b in zip(pts, pts[1:]):
            canvas.line(a[0], a[1], b[0], b[1], colour, 5)
        canvas.line(x + size - 8, y + 2 * size // 3, x + size - 22,
                    y + 2 * size // 3, colour, 5)
        canvas.line(x + size - 8, y + 2 * size // 3, x + size - 8,
                    y + 2 * size // 3 - 14, colour, 5)
    elif kind == "scales":
        canvas.line(cx, y + 10, cx, y + size - 10, colour, 4)
        canvas.line(cx - 28, y + 18, cx + 28, y + 18, colour, 4)
        canvas.line(cx - 28, y + 18, cx - 38, y + 48, colour, 3)
        canvas.line(cx - 28, y + 18, cx - 18, y + 48, colour, 3)
        canvas.line(cx + 28, y + 18, cx + 18, y + 48, colour, 3)
        canvas.line(cx + 28, y + 18, cx + 38, y + 48, colour, 3)
        canvas.line(cx - 38, y + 48, cx - 18, y + 48, colour, 3)
        canvas.line(cx + 18, y + 48, cx + 38, y + 48, colour, 3)
        canvas.rect(cx - 22, y + size - 12, 44, 6, colour)
    elif kind == "globe":
        canvas.circle(cx, cy, size // 2 - 8, colour, fill=False)
        canvas.line(cx, y + 8, cx, y + size - 8, colour, 3)
        canvas.line(x + 8, cy, x + size - 8, cy, colour, 3)
        canvas.line(x + 16, cy - 18, x + size - 16, cy - 18, colour, 3)
        canvas.line(x + 16, cy + 18, x + size - 16, cy + 18, colour, 3)
    elif kind == "flags":
        canvas.rect(x + 8, y + 14, 34, 24, (178, 34, 34))
        canvas.rect(x + 8, y + 14, 34, 8, (255, 255, 255))
        canvas.rect(x + 8, y + 30, 34, 8, (255, 255, 255))
        canvas.rect(x + 44, y + 30, 34, 24, (20, 33, 61))
        canvas.circle(x + 61, y + 42, 8, (255, 200, 0))
    elif kind == "quake":
        pts = [(x + 6, cy), (x + 20, cy), (x + 28, cy - 22),
               (x + 36, cy + 22), (x + 44, cy - 14), (x + 52, cy + 10),
               (x + 62, cy), (x + size - 6, cy)]
        for a, b in zip(pts, pts[1:]):
            canvas.line(a[0], a[1], b[0], b[1], colour, 4)


def render():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    # Masthead.
    canvas.rect(0, 0, WIDTH, 128, NAVY)
    canvas.centred(18, "WORLD NEWS", 7, WHITE)
    canvas.centred(84, "SATURDAY 21 NOVEMBER 2026", 3, (200, 210, 230))
    # Ticker strip.
    canvas.rect(0, 128, WIDTH, 36, RED)
    canvas.centred(138, "BTC BELOW $60,000 - ANTHROPIC $88.91 - NASDAQ -5.3%",
                   2, WHITE)
    # Story grid: 2 columns, 3 rows.
    margin = 24
    gap = 20
    panel_w = (WIDTH - 2 * margin - gap) // 2
    panel_h = 262
    top = 184
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = margin + col * (panel_w + gap)
        py = top + row * (panel_h + gap)
        canvas.rect(px, py, panel_w, panel_h, LIGHT)
        canvas.border(px, py, panel_w, panel_h, (200, 195, 180), 2)
        canvas.rect(px, py, panel_w, 30, story["colour"])
        canvas.text(px + 12, py + 7, story["tag"], 2, WHITE)
        # Icon box on the left.
        ix = px + 14
        iy = py + 48
        canvas.rect(ix, iy, 84, 84, (240, 236, 224))
        draw_icon(canvas, story["icon"], ix, iy, 84, story["colour"])
        # Headline and body on the right.
        tx = px + 112
        tw = panel_w - 112 - 14
        head_lines = wrap(story["head"], max(1, tw // 18))
        hy = py + 48
        for line in head_lines:
            canvas.text(tx, hy, line, 3, INK)
            hy += 24
        body_lines = wrap(story["body"], max(1, tw // 12))
        by = hy + 8
        for line in body_lines:
            canvas.text(tx, by, line, 2, GREY)
            by += 17
        if "detail" in story:
            by += 10
            canvas.rect(tx, by, 36, 4, story["colour"])
            by += 12
            for line in wrap(story["detail"], max(1, tw // 12)):
                canvas.text(tx, by, line, 2, INK)
                by += 17
    # Footer.
    canvas.text(margin, HEIGHT - 28,
                "SIX STORIES, ONE DAY - 21 NOVEMBER 2026", 2, GREY)
    return canvas


def write_png(canvas, path):
    """Write the canvas as a PNG with no timestamps, so runs match."""
    raw = bytearray()
    for y in range(canvas.height):
        raw.append(0)
        start = y * canvas.width * 3
        raw += canvas.pixels[start:start + canvas.width * 3]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    os.chmod(out_dir, 0o755)
    canvas = render()
    write_png(canvas, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()

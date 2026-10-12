"""picture.py: a proposal's card drawn as a PNG, in the standard library alone (code.1): an RGB canvas of filled and
outlined rectangles, solid and dashed lines and text in the bitmap font font.py carries, written with zlib and struct.
No browser and no renderer: the picture is only rectangles, lines and monospace text.

draw(sections) gives the PNG's bytes, 780 pixels wide, twice a phone's width, as tall as its rows need. A section is a
bolt, or a kit's queue, as the proposal leaves it: {"heading": its name, "counts": [(words, colour)...], "line": its
unit count before and after, "rows": [...]}, each row {"n": its number once approved, or "–", "name", "tag": drop,
amend, new, moved, out, split or None, "intent": what it builds, "old": the intent an amendment replaces, "under": a
dropped unit's reason or where a unit moved out goes, "struck": whether its name is struck, "outline": "dashed",
"solid" or None, "colour": the tag's and the outline's colour}. Nothing is read or written: the bytes are returned.
The wrapping the picture and the card's text share is here too."""
import struct
import zlib

import font

WIDTH = 780
MARGIN = 28
PALETTE = {"background": "#102b2f", "row": "#163a3e", "rule": "#2b4a4d", "text": "#ede7da", "muted": "#a3b4ae",
           "amended": "#c9a227", "moved": "#c9a227", "new": "#8fb9ae", "dropped": "#e07b4f"}
SMALL, LARGE = 2, 3  # the font drawn at two times (12x26 a character), and a heading at three
PAD, NUMBER, TAG = 12, 48, 72  # a row's padding, its number's column and its tag's
INTENT = 52  # characters of an intent a line, at most two lines


def rgb(colour):
    h = (PALETTE[colour] if colour in PALETTE else colour).lstrip("#")
    return bytes(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cut(text, width):
    """text in at most width characters, ending with … when it was cut."""
    return text if len(text) <= width else text[:max(width - 1, 0)].rstrip() + "…"


def wrap(text, width, lines=None):
    """text wrapped by whole words into lines of at most width characters; with lines, at most that many, the last
    ending with … when text was cut short. A word longer than a line, a long name, is wrapped at its hyphens."""
    out, cur = [], ""
    for word in " ".join(str(text).split()).split(" "):
        if len(word) > width:
            if cur:
                out.append(cur)
            *whole, word = hyphens(word, width)
            out += whole
            cur = ""
        if not word:
            continue
        if cur and len(cur) + 1 + len(word) > width:
            out.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    if cur:
        out.append(cur)
    if lines is not None and len(out) > lines:
        out, last = out[:lines], out[lines - 1]
        out[-1] = (last if len(last) < width else last[:width - 1].rstrip()) + "…"
    return out or [""]


def hyphens(name, width):
    """A name wrapped at its hyphens into lines of at most width characters, each hyphen kept at the end of its line;
    a part longer than a line is cut. A name is never shortened."""
    out, cur = [], ""
    parts = name.split("-")
    for i, part in enumerate(parts):
        piece = part + ("-" if i < len(parts) - 1 else "")
        while len(piece) > width:
            if cur:
                out.append(cur)
                cur = ""
            out.append(piece[:width])
            piece = piece[width:]
        if cur and len(cur) + len(piece) > width:
            out.append(cur)
            cur = piece
        else:
            cur += piece
    if cur:
        out.append(cur)
    return out or [""]


class Canvas:
    """An RGB canvas, top left at 0, 0, filled with the background."""

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.px = bytearray(rgb("background") * (width * height))

    def rect(self, x, y, w, h, colour):
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        c = rgb(colour) * (x1 - x0)
        for row in range(y0, y1):
            o = (row * self.w + x0) * 3
            self.px[o:o + len(c)] = c

    def outline(self, x, y, w, h, colour, dashed=False, t=2):
        if not dashed:
            for args in ((x, y, w, t), (x, y + h - t, w, t), (x, y, t, h), (x + w - t, y, t, h)):
                self.rect(*args, colour)
            return
        self.hline(x, y, w, colour, t, True)
        self.hline(x, y + h - t, w, colour, t, True)
        for yy in range(y, y + h, 14):
            self.rect(x, yy, t, min(8, y + h - yy), colour)
            self.rect(x + w - t, yy, t, min(8, y + h - yy), colour)

    def hline(self, x, y, w, colour, t=2, dashed=False):
        if not dashed:
            self.rect(x, y, w, t, colour)
            return
        for xx in range(x, x + w, 14):
            self.rect(xx, y, min(8, x + w - xx), t, colour)

    def text(self, x, y, s, colour, scale=SMALL, bold=False):
        """Draw s from x, y at scale; returns its width in pixels."""
        for dx in ((0, 1) if bold else (0,)):
            for i, ch in enumerate(s):
                gx = x + dx + i * font.WIDTH * scale
                for r, bits in enumerate(font.glyph(ch)):
                    for c in range(font.WIDTH):
                        if bits & (0x80 >> c):
                            self.rect(gx + c * scale, y + r * scale, scale, scale, colour)
        return len(s) * font.WIDTH * scale

    def png(self):
        raw = b"".join(b"\x00" + bytes(self.px[y * self.w * 3:(y + 1) * self.w * 3]) for y in range(self.h))

        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def char(scale):
    return font.WIDTH * scale, font.HEIGHT * scale


def layout(sections):
    """What draw draws, as calls on a canvas with their places, and the height they need."""
    ops, y = [], MARGIN
    inner = WIDTH - 2 * MARGIN
    cw, ch = char(SMALL)
    lw, lh = char(LARGE)
    line = ch + 4
    for k, s in enumerate(sections):
        if k:
            y += 18
            ops.append(("hline", MARGIN, y, inner, "rule", 2))
            y += 20
        for part in hyphens(s["heading"], inner // lw):
            ops.append(("text", MARGIN, y, part, "text", LARGE, True))
            y += lh + 6
        y += 6
        x = MARGIN
        for i, (words, colour) in enumerate(s["counts"]):
            if i:
                ops.append(("text", x, y, " · ", "muted", SMALL, False))
                x += len(" · ") * cw
            ops.append(("text", x, y, words, colour, SMALL, False))
            x += len(words) * cw
        if s["counts"]:
            y += line
        for part in wrap(s["line"], inner // cw):
            ops.append(("text", MARGIN, y, part, "muted", SMALL, False))
            y += line
        y += 14
        name_w = (inner - PAD - NUMBER - TAG - PAD) // cw
        for r in s["rows"]:
            top, x1 = y, MARGIN + PAD + NUMBER
            body, ty = [], top + PAD
            names = hyphens(r["name"], name_w)
            for part in names:
                body.append(("text", x1, ty, part, "muted" if r.get("struck") else "text", SMALL, not r.get("struck")))
                if r.get("struck"):
                    body.append(("hline", x1, ty + ch // 2, len(part) * cw, r.get("colour") or "dropped", 2))
                ty += line
            if r.get("old"):
                old = cut(r["old"], INTENT)
                body.append(("text", x1, ty, old, "amended", SMALL, False))
                body.append(("hline", x1, ty + ch // 2, len(old) * cw, "amended", 2))
                ty += line
            for part in (wrap(r["intent"], INTENT, 2) if r.get("intent") else []):
                body.append(("text", x1, ty, part, "text" if r.get("old") else "muted", SMALL, False))
                ty += line
            for part in (wrap(r["under"], INTENT, 2) if r.get("under") else []):
                body.append(("text", x1, ty, part, r.get("colour") or "dropped", SMALL, False))
                ty += line
            h = ty - top + PAD - 4
            ops.append(("rect", MARGIN, top, inner, h, "row"))
            if r.get("outline"):
                ops.append(("outline", MARGIN, top, inner, h, r.get("colour") or "rule", r["outline"] == "dashed"))
            ops.append(("text", MARGIN + PAD, top + PAD, str(r.get("n") or ""), "muted", SMALL, False))
            if r.get("tag"):
                tag = r["tag"]
                ops.append(("text", MARGIN + inner - PAD - len(tag) * cw, top + PAD, tag, r.get("colour") or "muted", SMALL, True))
            ops += body
            y = top + h + 10
    return ops, y + MARGIN - 10


def draw(sections):
    """The PNG of the sections, as bytes."""
    ops, height = layout(sections)
    c = Canvas(WIDTH, max(height, 2 * MARGIN))
    for op, *args in ops:
        if op == "text":
            x, y, s, colour, scale, bold = args
            c.text(x, y, s, colour, scale, bold)
        elif op == "hline":
            x, y, w, colour, t = args
            c.hline(x, y, w, colour, t)
        elif op == "rect":
            c.rect(*args)
        elif op == "outline":
            x, y, w, h, colour, dashed = args
            c.outline(x, y, w, h, colour, dashed)
    return c.png()

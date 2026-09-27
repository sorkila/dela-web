#!/usr/bin/env python3
"""Renders the site's brand images from the self-hosted fonts.

    python3 tools/brand.py                      # favicon.svg, favicon-16/32.png, favicon.ico, og.png
    python3 tools/brand.py --touch-icon PATH    # also apple-touch-icon.png from the app's 1024 icon

Run from the repo root. Needs Pillow and fontTools (with brotli, for woff2).
Not deployed: tools/ is excluded in .github/workflows/deploy.yml.
"""
import argparse
import io
import math
import random
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

# Palette, from the app's Theme.swift / LacquerBoard.swift.
BG = (19, 17, 16)            # Theme.background, the site's --bg
TABLE = (33, 28, 23)         # the lit centre of the table
GOLD = (232, 207, 139)       # Theme.gold #e8cf8b
MID = (168, 163, 158)        # site --mid
IVORY_TOP = (237, 230, 214)
IVORY_BOTTOM = (189, 176, 156)
GOLD_STOPS = [(0.0, (250, 224, 148)), (0.3, (219, 168, 71)), (0.58, (140, 94, 28)),
              (0.8, (204, 153, 61)), (1.0, (242, 209, 122))]


def ttf_bytes(woff2: Path) -> io.BytesIO:
    font = TTFont(str(woff2))
    font.flavor = None
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------- favicon

def glyph_path(char: str, box: float, height: float, nudge_y: float = 0.0):
    """SVG path data for one Pirata glyph, scaled to `height` and centred in a box×box square."""
    font = TTFont(str(FONTS / "pirata-one-latin.woff2"))
    glyphs = font.getGlyphSet()
    name = font.getBestCmap()[ord(char)]
    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    s = height / (y1 - y0)
    tx = (box - (x1 - x0) * s) / 2 - x0 * s
    ty = (box + (y1 - y0) * s) / 2 + y0 * s - nudge_y
    pen = SVGPathPen(glyphs)
    glyphs[name].draw(pen)
    return pen.getCommands(), tx, ty, s


def favicon_svg() -> str:
    d, tx, ty, s = glyph_path("D", 32, 20, nudge_y=0.25)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <!-- Pirata One capital 'D' in gold on the warm table, outlined from
       /fonts/pirata-one-latin.woff2 by tools/brand.py. The tile keeps the
       gold legible on light and dark tab bars alike. -->
  <rect width="32" height="32" rx="7" fill="#131110"/>
  <g fill="#E8CF8B" transform="translate({tx:.4f}, {ty:.4f}) scale({s:.6f}, {-s:.6f})">
    <path d="{d}"/>
  </g>
</svg>
"""


def favicon_png(size: int) -> Image.Image:
    k = 16
    big = size * k
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, big - 1, big - 1], radius=7 / 32 * big, fill=BG + (255,))
    # Size the glyph so its ink is 20/32 of the tile, like the SVG.
    probe = ImageFont.truetype(ttf_bytes(FONTS / "pirata-one-latin.woff2"), size=1000)
    l, t, r, b = probe.getbbox("D")
    px = int(1000 * (20 / 32 * big) / (b - t))
    font = ImageFont.truetype(ttf_bytes(FONTS / "pirata-one-latin.woff2"), size=px)
    l, t, r, b = font.getbbox("D")
    x = (big - (r - l)) / 2 - l
    y = (big - (b - t)) / 2 - t - 0.25 / 32 * big
    draw.text((x, y), "D", font=font, fill=GOLD + (255,))
    return img.resize((size, size), Image.LANCZOS)


# ---------------------------------------------------------------- og.png

def gradient(size, stops, angle_deg):
    """Linear gradient across `size` at `angle_deg` (0 = left to right, 90 = top to bottom)."""
    w, h = size
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    span = abs(w * dx) + abs(h * dy)
    lut = []
    for i in range(256):
        p = i / 255
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= p <= p1:
                f = (p - p0) / (p1 - p0) if p1 > p0 else 0
                lut.append(tuple(round(c0[j] + (c1[j] - c0[j]) * f) for j in range(3)))
                break
    ramp = Image.new("L", (w, h))
    px = ramp.load()
    ox = 0 if dx >= 0 else w
    oy = 0 if dy >= 0 else h
    for y in range(h):
        for x in range(w):
            px[x, y] = max(0, min(255, round(((x - ox) * dx + (y - oy) * dy) / span * 255)))
    rgb = [ramp.point([c[j] for c in lut]) for j in range(3)]
    return Image.merge("RGB", rgb)


def cells_mask(cells, cell, pad, round_px):
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    w = (max(xs) + 1) * cell + pad * 2
    h = (max(ys) + 1) * cell + pad * 2
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for x, y in cells:
        d.rectangle([pad + x * cell, pad + y * cell, pad + (x + 1) * cell - 1, pad + (y + 1) * cell - 1], fill=255)
    # Blur then re-threshold with a soft ramp: rounds outer and inner corners alike, antialiased.
    m = m.filter(ImageFilter.GaussianBlur(round_px))
    return m.point(lambda v: 0 if v < 110 else 255 if v > 146 else round((v - 110) / 36 * 255))


def piece(cells, cell, material):
    pad = 60
    mask = cells_mask(cells, cell, pad, cell * 0.06)
    w, h = mask.size
    if material == "ivory":
        fill = gradient((w, h), [(0.0, IVORY_TOP), (1.0, IVORY_BOTTOM)], 90)
    else:
        fill = gradient((w, h), GOLD_STOPS, 35)
        noise = Image.effect_noise((w, h), 40).filter(ImageFilter.GaussianBlur(0.6))
        fill = Image.blend(fill, Image.merge("RGB", [ImageChops.multiply(fill.getchannel(i), noise.point(lambda v: 200 + v // 5)) for i in range(3)]), 0.5)
    # Sheen from the top left, like the tilt light at rest.
    sheen = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sheen).ellipse([-w * 0.4, -h * 0.6, w * 0.7, h * 0.5], fill=60 if material == "ivory" else 70)
    sheen = sheen.filter(ImageFilter.GaussianBlur(w * 0.12))
    fill = Image.composite(Image.new("RGB", (w, h), (255, 250, 238)), fill, sheen)
    # Lit top rim: the mask minus itself shifted down.
    rim = ImageChops.subtract(mask, ImageChops.offset(mask, 0, 3)).filter(ImageFilter.GaussianBlur(0.8))
    fill = Image.composite(Image.new("RGB", (w, h), (255, 248, 230)), fill, rim.point(lambda v: v * 0.7))
    out = Image.new("RGBA", (w, h))
    out.paste(fill, (0, 0), mask)
    return out, mask


def shadow_layer(canvas_size, mask, at, blur, offset, alpha):
    layer = Image.new("L", canvas_size, 0)
    layer.paste(mask, (at[0] + offset[0], at[1] + offset[1]))
    layer = layer.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: round(v * alpha))
    return layer


def og_image() -> Image.Image:
    S = 2
    W, H = 1200 * S, 630 * S
    # Table: warm radial light over the canonical background.
    img = Image.new("RGB", (W, H), BG)
    light = Image.new("L", (W, H), 0)
    ImageDraw.Draw(light).ellipse([W * 0.30, -H * 0.35, W * 1.10, H * 1.05], fill=255)
    light = light.filter(ImageFilter.GaussianBlur(260 * S / 2))
    img = Image.composite(Image.new("RGB", (W, H), TABLE), img, light)
    grain = Image.effect_noise((W, H), 24).point(lambda v: v)
    img = ImageChops.add(img, Image.merge("RGB", [grain.point(lambda v: max(0, v - 128) // 10)] * 3))

    # Twin halves of a 4×3 staircase, parted along the line that made them.
    ivory = [(0, 0), (0, 1), (1, 1), (0, 2), (1, 2), (2, 2)]
    gold = [(1, 0), (2, 0), (3, 0), (2, 1), (3, 1), (3, 2)]
    cell = 84 * S
    ox, oy = 700 * S, 180 * S
    part = 11 * S
    pieces = []
    for cells, material, (dx, dy) in ((ivory, "ivory", (-part, part)), (gold, "gold", (part, -part))):
        tile, mask = piece(cells, cell, material)
        at = (ox - 60 + dx, oy - 60 + dy)
        pieces.append((tile, mask, at))
    shadows = Image.new("L", (W, H), 0)
    for _, mask, at in pieces:
        shadows = ImageChops.lighter(shadows, shadow_layer((W, H), mask, at, 34 * S, (0, 22 * S), 0.62))
        shadows = ImageChops.lighter(shadows, shadow_layer((W, H), mask, at, 4 * S, (0, 4 * S), 0.55))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shadows)
    img = img.convert("RGBA")
    for tile, _, at in pieces:
        img.alpha_composite(tile, at)

    # A few flecks of gold dust where the halves parted.
    rnd = random.Random(7)
    dust = Image.new("RGBA", (W, H))
    dd = ImageDraw.Draw(dust)
    for _ in range(26):
        t = rnd.random()
        # Along the staircase seam, drifting outward.
        sx = ox + (1 + t * 2.2) * cell + rnd.uniform(-40, 40) * S
        sy = oy + (0.9 + t * 2.1) * cell + rnd.uniform(-40, 40) * S
        r = rnd.uniform(1.2, 3.2) * S
        a = rnd.randint(90, 220)
        dd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 226, 160, a))
    glow = dust.filter(ImageFilter.GaussianBlur(5 * S))
    img.alpha_composite(glow)
    img.alpha_composite(dust)

    # Wordmark and pitch.
    draw = ImageDraw.Draw(img)
    pirata = ImageFont.truetype(ttf_bytes(FONTS / "pirata-one-latin.woff2"), size=210 * S)
    italic = ImageFont.truetype(ttf_bytes(FONTS / "inter-latin-italic.woff2"), size=34 * S)
    try:
        italic.set_variation_by_axes([400])
    except Exception:
        pass
    x = 96 * S
    l, t, r, b = pirata.getbbox("Dela")
    draw.text((x - l, 190 * S - t), "Dela", font=pirata, fill=GOLD)
    draw.text((x + 4 * S, 190 * S + (b - t) + 44 * S), "One line, two identical halves.", font=italic, fill=MID)
    return img.convert("RGB").resize((1200, 630), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--touch-icon", type=Path, help="the app's 1024 AppIcon.png")
    args = ap.parse_args()

    (ROOT / "favicon.svg").write_text(favicon_svg())
    p16, p32, p48 = favicon_png(16), favicon_png(32), favicon_png(48)
    p16.save(ROOT / "favicon-16x16.png", optimize=True)
    p32.save(ROOT / "favicon-32x32.png", optimize=True)
    p48.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[p16, p32])
    og_image().save(ROOT / "og.png", optimize=True)
    if args.touch_icon:
        Image.open(args.touch_icon).convert("RGB").resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png", optimize=True)
    print("ok")


if __name__ == "__main__":
    main()

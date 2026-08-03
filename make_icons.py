"""Generate the favicon and home-screen icons.

Run after changing the branding, same as make_og_image.py. Output is committed
so the published page can reference it.

v3, 2026-08-03: matched against a real photo of Kaufman Rossin's own
installed-app icon (kr.png): a soft gray rounded field, bold navy letters,
split by a thin lime pipe -- no bottom rule bar, no corner dot, which the
prior version (white field) had invented and KR's own icon doesn't use.
KR's icon splits two letters (K|R, one per word of the firm name); a single
product name has no second word to split, so the pipe now sits to the
right of the monogram instead, echoing the same "letter, pipe, letter"
shape without inventing a second initial. Same PRODUCT_NAME-driven
monogram as v2, so this file is identical for Mihari ("M") and ClearReg
("C") except for that one constant.
"""
import json

from PIL import Image, ImageDraw, ImageFont

PRODUCT_NAME = "Mihari"
MONOGRAM = PRODUCT_NAME[0].upper()

NAVY = (0, 59, 106)
GREEN = (174, 209, 54)
FIELD_GRAY = (225, 227, 230)   # matches the soft gray field in KR's own icon

CAP_FRACTION = 0.56       # target height of the letter, as a share of the field
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
PIPE_W_FRACTION = 0.045   # pipe stroke width, as a share of the field
PIPE_H_FRACTION = 0.85    # pipe height, as a share of the letter's own height
PIPE_GAP_FRACTION = 0.22  # gap between letter and pipe, as a share of letter height


def render(size, padding=0.0):
    """One icon. `padding` insets the artwork for maskable (croppable) icons."""
    img = Image.new("RGB", (size, size), FIELD_GRAY)
    d = ImageDraw.Draw(img)

    inset = round(size * padding)
    inner = size - 2 * inset

    # Binary-search the largest font size whose rendered glyph height fits
    # CAP_FRACTION of the field -- textbbox gives the real ink height for
    # this exact font, not a guessed cap-height ratio, so it holds at every
    # icon size from 16px up to 512px without a separate tuned constant per
    # size.
    target_h = inner * CAP_FRACTION
    lo, hi = 1, size * 2
    font = None
    bbox = (0, 0, 0, 0)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(FONT_PATH, mid)
        bbox = d.textbbox((0, 0), MONOGRAM, font=f)
        h = bbox[3] - bbox[1]
        if h <= target_h:
            font, lo = f, mid + 1
        else:
            hi = mid - 1
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pipe_w = max(1, round(inner * PIPE_W_FRACTION))
    pipe_h = text_h * PIPE_H_FRACTION
    gap = text_h * PIPE_GAP_FRACTION
    group_w = text_w + gap + pipe_w

    gx = inset + (inner - group_w) / 2
    gy = inset + (inner - text_h) / 2
    tx = gx - bbox[0]
    ty = gy - bbox[1]
    d.text((tx, ty), MONOGRAM, font=font, fill=NAVY)

    px0 = gx + text_w + gap
    py0 = gy + (text_h - pipe_h) / 2
    d.rectangle([px0, py0, px0 + pipe_w, py0 + pipe_h], fill=GREEN)
    return img


def main():
    written = []

    # Multi-size .ico still has the broadest support, and is what a browser
    # reaches for when no <link rel="icon"> matches.
    ico = render(48)
    ico.save("favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    written.append("favicon.ico")

    for size in (16, 32, 180, 192, 512):
        # 180 is Apple's home-screen size; iOS rounds the corners itself and
        # composites on black, so the artwork must stay full-bleed and opaque.
        name = "apple-touch-icon.png" if size == 180 else f"icon-{size}.png"
        render(size).save(name, "PNG", optimize=True)
        written.append(name)

    # Android masks icons to whatever shape the launcher uses and can crop up to
    # 20% off each edge. The padded variant keeps the mark inside that safe
    # zone; without it the spike loses its tip on a circular launcher.
    render(512, padding=0.20).save("icon-maskable-512.png", "PNG", optimize=True)
    written.append("icon-maskable-512.png")

    manifest = {
        "name": "Regulatory update tracker — community banks & fintechs",
        "short_name": PRODUCT_NAME,
        "description": "Daily federal regulatory updates for community banks and "
                       "fintechs, in plain English.",
        # Relative, because the site is served from a /regwatch/ subpath rather
        # than a domain root. An absolute "/" would break the installed app.
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        # Matches the icon's gray field colour (this is the splash-screen
        # colour a PWA launch briefly shows). theme_color stays navy since
        # that's the app's real in-use browser-chrome colour, unrelated to
        # the icon graphic.
        "background_color": "#e1e3e6",
        "theme_color": "#003b6a",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open("site.webmanifest", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    written.append("site.webmanifest")

    print("Wrote " + ", ".join(written))


if __name__ == "__main__":
    main()

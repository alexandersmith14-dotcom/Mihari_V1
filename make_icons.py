"""Generate the favicon and home-screen icons.

Run after changing the branding, same as make_og_image.py. Output is committed
so the published page can reference it.

v2, 2026-08-03: switched from a navy field with the Check Spike mark to a
white field with a bold navy monogram, at Alexander's request to read as
closer to Kaufman Rossin's own installed-app icon style (white circle, bold
navy letters) rather than a dark navy square. Keeps the product's own
identity rather than adopting KR's literal "K|R" mark: the monogram is
derived from PRODUCT_NAME below, so it says "M" here and "C" on ClearReg's
own copy of this file without any other change needed. A small lime dot at
the letter's upper-right is the one remaining nod to Check Spike's own
dot-at-the-peak motif, so the icon doesn't read as a total break from
everything else in the identity — just the one navy-square, white-mark
element flipped to match KR's lighter style.

The green rule stays a proportion of the icon (10%) rather than a fixed
pixel height: at 16px a fixed 14px rule (this card's proportion) would be
sub-pixel and vanish.
"""
import json

from PIL import Image, ImageDraw, ImageFont

PRODUCT_NAME = "Mihari"
MONOGRAM = PRODUCT_NAME[0].upper()

NAVY = (0, 59, 106)
GREEN = (174, 209, 54)
WHITE = (255, 255, 255)

RULE_FRACTION = 0.10      # green bar height, as a share of the icon
CAP_FRACTION = 0.62       # target height of the letter, as a share of the field
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
DOT_R_FRACTION = 0.05     # accent dot radius, as a share of the field


def render(size, padding=0.0):
    """One icon. `padding` insets the artwork for maskable (croppable) icons."""
    img = Image.new("RGB", (size, size), WHITE)
    d = ImageDraw.Draw(img)

    inset = round(size * padding)
    inner = size - 2 * inset

    rule = max(1, round(inner * RULE_FRACTION))
    d.rectangle([inset, size - inset - rule, size - inset, size - inset - 1], fill=GREEN)

    field_top, field_bottom = inset, size - inset - rule
    field_h = field_bottom - field_top

    # Binary-search the largest font size whose rendered glyph height fits
    # CAP_FRACTION of the field -- textbbox gives the real ink height for
    # this exact font, not a guessed cap-height ratio, so it holds at every
    # icon size from 16px up to 512px without a separate tuned constant per
    # size.
    target_h = field_h * CAP_FRACTION
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
    tx = inset + (inner - text_w) / 2 - bbox[0]
    ty = field_top + (field_h - text_h) / 2 - bbox[1]
    d.text((tx, ty), MONOGRAM, font=font, fill=NAVY)

    # Small lime accent dot at the letter's upper-right corner -- the one
    # carried-over nod to Check Spike's own dot-at-the-peak motif, so this
    # doesn't read as a total break from the rest of the identity.
    dr = inner * DOT_R_FRACTION
    dx = tx + text_w - dr * 1.6
    dy = ty + dr * 1.1
    d.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=GREEN)
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
        # White now, matching the icon's new field colour (this is the
        # splash-screen colour a PWA launch briefly shows). theme_color stays
        # navy since that's the app's real in-use browser-chrome colour and
        # hasn't changed, only the icon graphic has.
        "background_color": "#ffffff",
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

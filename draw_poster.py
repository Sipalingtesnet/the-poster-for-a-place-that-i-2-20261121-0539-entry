#!/usr/bin/env python3
"""VELMORA — The Floating Isles. A procedural travel poster generator.

100% procedural, deterministic, no randomness, no network. Produces
entry.png (1024x1024) at the repo root. Run twice -> byte-identical file.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024

# ---------------------------------------------------------------------------
# Palette (purposeful, restrained)
# ---------------------------------------------------------------------------
SKY_TOP = (18, 34, 58)        # deep teal-indigo
SKY_MID = (74, 52, 96)        # violet
SKY_HOR = (214, 138, 66)      # warm amber-gold
SUN_CORE = (255, 236, 190)    # cream-gold sun
SUN_HALO = (255, 196, 120)
CLOUD_HI = (255, 238, 200)    # cream cloud highlight
CLOUD_MID = (244, 196, 132)   # gold cloud
CLOUD_LO = (96, 112, 118)     # teal cloud shadow
ISLAND_TOP = (58, 92, 84)     # dark green-teal
ISLAND_UNDER = (26, 40, 44)   # darker underside
ISLAND_RIM = (255, 200, 120)  # warm rim light
LIGHTHOUSE = (244, 240, 226)  # ivory
LAMP = (255, 214, 120)
WATERFALL = (226, 226, 214)
PINE = (16, 26, 28)
TYPE = (250, 244, 224)        # cream-ivory type
TYPE_SHADOW = (30, 26, 40)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def build_sky():
    """Vertical gradient sky, teal-indigo -> violet -> amber-gold."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    horizon = 640
    for y in range(H):
        if y < horizon:
            t = y / horizon
            if t < 0.55:
                c = lerp(SKY_TOP, SKY_MID, t / 0.55)
            else:
                c = lerp(SKY_MID, SKY_HOR, (t - 0.55) / 0.45)
        else:
            c = SKY_HOR
        for x in range(W):
            px[x, y] = c
    return img


def add_sun(img):
    """Low glowing sun disc with soft halo, off-centre to the right."""
    sun_x, sun_y = 700, 560
    r_core = 92
    r_halo = 210

    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for rr in range(r_halo, r_core, -1):
        t = (r_halo - rr) / (r_halo - r_core)
        alpha = int(70 * (1 - t))
        hd.ellipse([sun_x - rr, sun_y - rr, sun_x + rr, sun_y + rr],
                   fill=SUN_HALO + (alpha,))
    halo = halo.filter(ImageFilter.GaussianBlur(30))
    img.paste(Image.alpha_composite(img.convert("RGBA"), halo).convert("RGB"),
              (0, 0))

    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    cd.ellipse([sun_x - r_core, sun_y - r_core, sun_x + r_core, sun_y + r_core],
               fill=SUN_CORE + (255,))
    core = core.filter(ImageFilter.GaussianBlur(6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), core).convert("RGB"),
              (0, 0))
    return img


def add_islands(img):
    """Chain of floating ROCKY islands with lighthouse + waterfalls."""
    base = img.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # --- Main island (largest, carries lighthouse) ---
    main_cx, main_cy = 470, 540
    main_w, main_h = 320, 170
    top = main_cy - main_h // 2
    bottom = main_cy + main_h // 2

    # Rocky grass-green top surface with an irregular edge.
    top_pts = [
        (main_cx - main_w // 2, top + 26),
        (main_cx - main_w // 2 + 34, top + 8),
        (main_cx - main_w // 2 + 78, top + 20),
        (main_cx - main_w // 2 + 120, top),
        (main_cx - main_w // 2 + 168, top + 14),
        (main_cx - main_w // 2 + 214, top + 4),
        (main_cx + main_w // 2 - 46, top + 18),
        (main_cx + main_w // 2, top + 30),
    ]
    d.polygon(top_pts, fill=ISLAND_TOP + (255,))

    # Tapered jagged rock underside with shaded facets.
    under_pts = [
        (main_cx - main_w // 2, top + 26),
        (main_cx - main_w // 2 + 40, bottom - 46),
        (main_cx - main_w // 2 + 96, bottom - 12),
        (main_cx - main_w // 2 + 150, bottom - 60),
        (main_cx - main_w // 2 + 200, bottom - 22),
        (main_cx + main_w // 2 - 60, bottom - 70),
        (main_cx + main_w // 2 - 20, bottom - 34),
        (main_cx + main_w // 2, top + 30),
    ]
    d.polygon(under_pts, fill=ISLAND_UNDER + (255,))

    # Shaded facets on the underside (darker wedges for depth).
    facet = [
        (main_cx - main_w // 2 + 40, bottom - 46),
        (main_cx - main_w // 2 + 96, bottom - 12),
        (main_cx - main_w // 2 + 150, bottom - 60),
        (main_cx - main_w // 2 + 96, bottom - 34),
    ]
    d.polygon(facet, fill=(18, 28, 32, 255))
    facet2 = [
        (main_cx - main_w // 2 + 150, bottom - 60),
        (main_cx - main_w // 2 + 200, bottom - 22),
        (main_cx + main_w // 2 - 60, bottom - 70),
        (main_cx - main_w // 2 + 176, bottom - 48),
    ]
    d.polygon(facet2, fill=(22, 34, 38, 255))

    # Warm amber rim light along the sunlit (right) top edge.
    rim = top_pts[4:] + [top_pts[0]]
    d.line(rim, fill=ISLAND_RIM + (255,), width=6)
    # a softer rim hint along the right underside edge
    d.line([(main_cx + main_w // 2 - 60, bottom - 70),
            (main_cx + main_w // 2 - 20, bottom - 34),
            (main_cx + main_w // 2, top + 30)],
           fill=(255, 190, 110, 200), width=4)

    # --- Lighthouse on the main island ---
    lh_x = main_cx + 40
    lh_base_y = top + 6
    lh_h = 150
    lh_w = 34
    d.rectangle([lh_x - lh_w // 2, lh_base_y - lh_h,
                 lh_x + lh_w // 2, lh_base_y], fill=LIGHTHOUSE + (255,))
    d.rectangle([lh_x - lh_w // 2, lh_base_y - lh_h + 40,
                 lh_x + lh_w // 2, lh_base_y - lh_h + 62],
                fill=(196, 92, 70, 255))
    d.rectangle([lh_x - lh_w // 2 - 4, lh_base_y - lh_h - 22,
                 lh_x + lh_w // 2 + 4, lh_base_y - lh_h], fill=(70, 70, 70, 255))
    lamp_y = lh_base_y - lh_h - 11
    d.ellipse([lh_x - 12, lamp_y - 12, lh_x + 12, lamp_y + 12],
              fill=LAMP + (255,))
    d.polygon([(lh_x - lh_w // 2 - 8, lh_base_y - lh_h - 22),
               (lh_x + lh_w // 2 + 8, lh_base_y - lh_h - 22),
               (lh_x, lh_base_y - lh_h - 46)], fill=(60, 60, 60, 255))

    # --- Waterfalls: narrow, semi-transparent, tapered pale streaks ---
    wf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wf)

    def draw_waterfall(cx, y_top, y_bot, half_w_top):
        # Tapered streak: wider at the spill point, feathering out downward.
        steps = 12
        for i in range(steps):
            t0 = i / steps
            t1 = (i + 1) / steps
            y0 = int(y_top + (y_bot - y_top) * t0)
            y1 = int(y_top + (y_bot - y_top) * t1)
            hw = half_w_top * (1.0 - 0.55 * t0)   # narrows as it falls
            alpha = int(120 * (1.0 - 0.75 * t0))  # fades toward the bottom
            wd.rectangle([cx - hw, y0, cx + hw, y1],
                         fill=WATERFALL + (alpha,))
        # a faint bright core line for a watery sheen
        wd.rectangle([cx - 2, y_top, cx + 2, y_bot],
                     fill=(250, 250, 242, 90))

    # left waterfall spilling off the left edge of the main island
    draw_waterfall(main_cx - main_w // 2 + 26, top + 20, bottom + 90, 16)
    # right waterfall spilling off the right edge of the main island
    draw_waterfall(main_cx + main_w // 2 - 46, top + 16, bottom + 110, 18)

    wf = wf.filter(ImageFilter.GaussianBlur(2))
    layer = Image.alpha_composite(layer, wf)

    # --- Two smaller flanking islets, clearly separate, at different heights ---
    def draw_islet(cx, cy, ww, hh):
        t = cy - hh // 2
        b = cy + hh // 2
        # rocky top with an irregular edge
        tp = [(cx - ww // 2, t + 12), (cx - ww // 2 + 22, t + 2),
              (cx - ww // 2 + 46, t + 10), (cx + ww // 2 - 24, t),
              (cx + ww // 2, t + 12)]
        d.polygon(tp, fill=ISLAND_TOP + (255,))
        # tapered jagged underside
        up = [(cx - ww // 2, t + 12), (cx - ww // 2 + 18, b - 24),
              (cx + ww // 2 - 18, b - 8), (cx + ww // 2, t + 12)]
        d.polygon(up, fill=ISLAND_UNDER + (255,))
        # warm rim light on the sunlit (right) edge
        d.line([(cx + ww // 2 - 24, t), (cx + ww // 2, t + 12)],
               fill=ISLAND_RIM + (255,), width=4)

    # left islet: clearly left of the main island, a touch higher
    draw_islet(150, 430, 130, 70)
    # right islet: clearly right of the main island, a touch lower
    draw_islet(850, 560, 140, 75)

    layer = layer.filter(ImageFilter.GaussianBlur(1))
    out = Image.alpha_composite(base, layer).convert("RGB")
    return out


def add_clouds(img):
    """Sea of clouds in the bottom third: luminous cream/gold billows."""
    base = img.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    for i in range(14):
        cx = (i * 160 + 40) % (W + 200) - 100
        cy = 700 + (i % 4) * 40
        rw = 260 + (i % 3) * 60
        rh = 60 + (i % 3) * 20
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                  fill=CLOUD_LO + (90,))

    for i in range(12):
        cx = (i * 190 + 90) % (W + 240) - 120
        cy = 660 + (i % 5) * 34
        rw = 220 + (i % 3) * 70
        rh = 46 + (i % 3) * 16
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                  fill=CLOUD_MID + (170,))

    for i in range(10):
        cx = (i * 230 + 30) % (W + 260) - 130
        cy = 640 + (i % 4) * 30
        rw = 180 + (i % 3) * 60
        rh = 34 + (i % 3) * 12
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh],
                  fill=CLOUD_HI + (200,))

    layer = layer.filter(ImageFilter.GaussianBlur(8))
    out = Image.alpha_composite(base, layer).convert("RGB")
    return out


def add_birds(img):
    """A few tiny birds in the sky for scale and life."""
    d = ImageDraw.Draw(img)
    birds = [(250, 300), (290, 285), (330, 305), (820, 240), (850, 255)]
    for (bx, by) in birds:
        span = 14
        d.arc([bx - span, by - 5, bx, by + 5], 200, 340, fill=(30, 40, 50), width=3)
        d.arc([bx, by - 5, bx + span, by + 5], 200, 340, fill=(30, 40, 50), width=3)
    return img


def add_title(img):
    """VELMORA in huge letterspaced DejaVu Bold, cream with soft shadow."""
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 120)
    text = "VELMORA"
    spacing = 16

    widths = [font.getbbox(ch)[2] for ch in text]
    total_w = sum(widths) + spacing * (len(text) - 1)
    asc, desc = font.getmetrics()
    text_h = asc + desc

    x0 = (W - total_w) // 2
    y0 = 80

    # shadow layer
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    cx = x0
    for ch, w in zip(text, widths):
        sd.text((cx, y0 + 6), ch, font=font, fill=TYPE_SHADOW + (200,))
        cx += w + spacing
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"),
              (0, 0))

    d = ImageDraw.Draw(img)
    cx = x0
    for ch, w in zip(text, widths):
        d.text((cx, y0), ch, font=font, fill=TYPE)
        cx += w + spacing

    return (x0, y0, x0 + total_w, y0 + text_h)


def main():
    img = build_sky()
    img = add_sun(img)
    img = add_islands(img)
    img = add_clouds(img)
    img = add_birds(img)
    bbox = add_title(img)

    # Verify title placement
    x0, y0, x1, y1 = bbox
    assert x0 > 40 and x1 < W - 40, f"Title touches edges: {bbox}"
    assert y0 > 40 and y1 < 640, f"Title overlaps horizon: {bbox}"
    # Title must not overlap lighthouse (lighthouse around x 430-540, y 290-480)
    lh_box = (430, 250, 540, 480)
    overlap = not (x1 < lh_box[0] or x0 > lh_box[2] or y1 < lh_box[1] or y0 > lh_box[3])
    assert not overlap, f"Title overlaps lighthouse: {bbox}"

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "entry.png")
    img.save(out_path, "PNG", optimize=True)
    print(f"Wrote {out_path}  {img.size}  bbox={bbox}")


if __name__ == "__main__":
    main()
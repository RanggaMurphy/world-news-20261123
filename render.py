#!/usr/bin/env python3
"""Render entry.png (1024x1024) for The World Today, 23 November 2026.

Reads sources.json + thumbs/ in this folder and draws a one-image newspaper
front page: navy masthead, big centred date line, 3 feature stories with
photos, an Around the World grid, a By the Numbers strip and a sources
footer. Deterministic: same inputs always produce the same bytes.
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
NAVY = (14, 30, 74)
NAVY_DARK = (10, 22, 56)
GOLD = (201, 162, 39)
GOLD_LIGHT = (212, 175, 55)
PAPER = (247, 243, 234)
INK = (17, 17, 17)
GREY = (90, 90, 90)
RULE = (180, 175, 160)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def spaced_text(draw, cx, y, text, fnt, fill, tracking=4, align="center"):
    """Draw letterspaced text centred on cx (align='center') or starting
    at cx (align='left')."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2 if align == "center" else cx
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def cover_thumb(path, tw, th):
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    left = (img.width - tw) // 2
    top = (img.height - th) // 2
    return img.crop((left, top, left + tw, top + th))


def globe_tile(tw, th, label):
    tile = Image.new("RGB", (tw, th), NAVY)
    d = ImageDraw.Draw(tile)
    cx, cy = tw // 2, th // 2 - 6
    r = min(tw, th) // 2 - 14
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD_LIGHT, width=2)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=GOLD_LIGHT, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=GOLD_LIGHT, width=2)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360, fill=GOLD_LIGHT, width=2)
    f = font(SANS_B, 15)
    d.text((cx, th - 22), label, font=f, fill=(255, 255, 255), anchor="ma")
    return tile


def main():
    with open(os.path.join(HERE, "sources.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.rectangle([0, 0, W, 118], fill=NAVY)
    spaced_text(d, W // 2, 18, "WORLD NEWS IN ONE IMAGE",
                font(SANS_B, 20), GOLD_LIGHT, tracking=6)
    title_f = font(SERIF_B, 66)
    d.text((W // 2, 40), "The World Today", font=title_f,
           fill=(255, 255, 255), anchor="ma")
    d.rectangle([0, 118, W, 122], fill=GOLD)

    # Date line: big, bold, centred directly under the masthead.
    date_f = font(SERIF_B, 44)
    d.text((W // 2, 136), data["date_line"], font=date_f, fill=NAVY, anchor="ma")
    d.line([28, 196, W - 28, 196], fill=NAVY, width=2)

    # Feature stories: three across.
    margin, gutter = 28, 16
    col_w = (W - 2 * margin - 2 * gutter) // 3  # 312
    thumb_h = 185
    head_f = font(SERIF_B, 25)
    y_thumb = 210
    y_head = y_thumb + thumb_h + 12
    for i, story in enumerate(data["features"]):
        x = margin + i * (col_w + gutter)
        thumb = cover_thumb(os.path.join(HERE, "thumbs", story["thumb"]),
                            col_w, thumb_h)
        img.paste(thumb, (x, y_thumb))
        lines = wrap(d, story["headline"], head_f, col_w)
        draw_lines(d, lines[:5], x, y_head, head_f, INK, 31)

    # Around the World header.
    y_atw = 586
    d.line([margin, y_atw, W - margin, y_atw], fill=RULE, width=1)
    spaced_text(d, margin, y_atw + 10, "AROUND THE WORLD",
                font(SANS_B, 21), NAVY, tracking=5, align="left")
    d.line([margin, y_atw + 44, W - margin, y_atw + 44], fill=NAVY, width=2)

    # Around the World grid: 2 x 2, small thumb + headline.
    grid_f = font(SERIF_B, 21)
    cell_w = (W - 2 * margin - gutter) // 2  # 476
    tw, th = 150, 94
    row_h = 112
    for i, story in enumerate(data["around"]):
        gx = margin + (i % 2) * (cell_w + gutter)
        gy = y_atw + 58 + (i // 2) * row_h
        if story.get("thumb"):
            tile = cover_thumb(os.path.join(HERE, "thumbs", story["thumb"]),
                               tw, th)
        else:
            tile = globe_tile(tw, th, story.get("tile_label", ""))
        img.paste(tile, (gx, gy))
        lines = wrap(d, story["headline"], grid_f, cell_w - tw - 14)
        draw_lines(d, lines[:4], gx + tw + 14, gy + 2, grid_f, INK, 26)

    # By the Numbers strip.
    y_num = 862
    d.rectangle([0, y_num, W, y_num + 84], fill=NAVY)
    label_f = font(SANS_B, 19)
    d.text((margin, y_num + 14), "BY THE", font=label_f, fill=GOLD_LIGHT)
    d.text((margin, y_num + 38), "NUMBERS", font=label_f, fill=GOLD_LIGHT)
    stat_f = font(SERIF_B, 40)
    stat_l = font(SANS, 16)
    sx = 200
    for stat in data["stats"]:
        d.text((sx, y_num + 8), stat["value"], font=stat_f, fill=(255, 255, 255))
        d.text((sx, y_num + 56), stat["label"], font=stat_l, fill=(220, 220, 220))
        sx += 420

    # Footer: sources.
    foot_f = font(SANS, 15)
    sources = "Sources: " + " · ".join(data["sources"])
    lines = wrap(d, sources, foot_f, W - 2 * margin)
    draw_lines(d, lines[:2], margin, y_num + 96, foot_f, GREY, 20)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()

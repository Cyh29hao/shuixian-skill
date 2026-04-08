#!/usr/bin/env python3
"""
Render a README hero image as PNG to avoid SVG font/layout issues on GitHub.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "hero-preview-v5.png"

WIDTH = 1600
HEIGHT = 980

BG_TOP = (249, 240, 231)
BG_BOTTOM = (243, 230, 219)
CARD = (255, 250, 244)
CARD_BORDER = (222, 202, 184)
TEXT = (40, 29, 22)
TEXT_SOFT = (118, 90, 71)
PILL_BG = (245, 232, 218)
PILL_TEXT = (131, 94, 71)
DARK_PILL = (45, 34, 28)
LIGHT = (255, 247, 240)
ACCENT_A = (230, 155, 111)
ACCENT_B = (199, 104, 69)
CHAT_SOFT = (244, 231, 220)
CHAT_TRACK = (216, 195, 178)
CHAT_FILL = (183, 140, 114)

FONT_SANS = Path("C:/Windows/Fonts/msyh.ttc")
FONT_SANS_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
FONT_SERIF = Path("C:/Windows/Fonts/STZHONGS.TTF")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_vertical_gradient(base: Image.Image, top, bottom) -> None:
    px = base.load()
    for y in range(base.height):
        t = y / max(base.height - 1, 1)
        color = tuple(lerp(top[i], bottom[i], t) for i in range(3))
        for x in range(base.width):
            px[x, y] = color


def draw_glow(layer: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int, int]) -> None:
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    x, y = center
    glow_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 2))
    layer.alpha_composite(glow)


def main() -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_TOP)
    draw_vertical_gradient(canvas, BG_TOP, BG_BOTTOM)
    art = canvas.convert("RGBA")

    draw_glow(art, (1310, 160), 260, (243, 202, 173, 170))
    draw_glow(art, (230, 830), 300, (231, 214, 197, 150))

    shadow = Image.new("RGBA", art.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((90, 82, 1510, 862), radius=54, fill=(130, 92, 70, 42))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    art.alpha_composite(shadow)

    draw = ImageDraw.Draw(art)
    rounded_panel(draw, (86, 70, 1514, 850), 52, CARD, CARD_BORDER, 3)
    rounded_panel(draw, (128, 114, 1472, 808), 40, (251, 244, 236), (230, 213, 198), 2)

    title_font = font(FONT_SERIF if FONT_SERIF.exists() else FONT_SANS_BOLD, 78)
    small_caps = font(FONT_SANS_BOLD, 22)
    subtitle_font = font(FONT_SANS, 34)
    pill_font = font(FONT_SANS_BOLD, 34)
    mono_font = font(FONT_SANS, 28)
    headline_font = font(FONT_SANS_BOLD, 54)
    body_font = font(FONT_SANS, 30)
    body_font_small = font(FONT_SANS, 28)
    bubble_font = font(FONT_SANS, 27)
    bubble_font_small = font(FONT_SANS, 31)

    rounded_panel(draw, (170, 154, 422, 202), 24, PILL_BG)
    draw.text((202, 168), "SELF-MIRROR SKILL", fill=PILL_TEXT, font=small_caps)

    draw.text((158, 248), "水仙.skill", fill=TEXT, font=title_font)
    draw.text((164, 360), "把你的语气、偏好和聊天片段，", fill=TEXT_SOFT, font=subtitle_font)
    draw.text((164, 408), "长成一个可继续修正的镜像伴侣。", fill=TEXT_SOFT, font=subtitle_font)

    rounded_panel(draw, (160, 500, 520, 590), 28, LIGHT, (232, 217, 204), 2)
    draw.text((196, 530), "同频，不装懂", fill=TEXT, font=pill_font)

    rounded_panel(draw, (160, 614, 590, 704), 28, LIGHT, (232, 217, 204), 2)
    draw.text((196, 644), "可纠偏，可继续长", fill=TEXT, font=pill_font)

    rounded_panel(draw, (160, 740, 592, 804), 32, DARK_PILL)
    draw.text((198, 758), "$shuixian-sweet-demo", fill=LIGHT, font=mono_font)

    rounded_panel(draw, (728, 168, 1360, 370), 34, LIGHT, (228, 212, 198), 2)
    draw.text((780, 232), "先试一个更懂你的自己", fill=TEXT, font=headline_font)
    draw.text((782, 300), "先确认气质对，再导入真正私密的材料。", fill=TEXT_SOFT, font=body_font)

    rounded_panel(draw, (782, 410, 1056, 470), 30, PILL_BG)
    draw.text((830, 426), "selective mirror", fill=PILL_TEXT, font=body_font_small)
    rounded_panel(draw, (1082, 410, 1320, 470), 30, PILL_BG)
    draw.text((1122, 426), "gender-flipped", fill=PILL_TEXT, font=body_font_small)

    rounded_panel(draw, (730, 500, 1362, 778), 36, (255, 255, 255), (228, 212, 198), 2)
    for i, c in enumerate(((234, 180, 144), (228, 202, 171), (211, 133, 95))):
        draw.ellipse((782 + i * 34, 540, 802 + i * 34, 560), fill=c)
    draw.text((1200, 534), "mirror chat", fill=(146, 112, 92), font=body_font_small)

    rounded_panel(draw, (1066, 584, 1316, 686), 30, CHAT_SOFT)
    draw.text((1112, 612), "今天又把自己", fill=(94, 71, 58), font=bubble_font_small)
    draw.text((1112, 650), "搞得很累。", fill=(94, 71, 58), font=bubble_font_small)

    accent_box = Image.new("RGBA", art.size, (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent_box)
    accent_draw.rounded_rectangle((784, 626, 1240, 754), radius=34, fill=(0, 0, 0, 0))
    for y in range(626, 754):
        t = (y - 626) / (754 - 626)
        color = tuple(lerp(ACCENT_A[i], ACCENT_B[i], t) for i in range(3)) + (255,)
        accent_draw.line((784, y, 1240, y), fill=color, width=1)
    mask = Image.new("L", art.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((784, 626, 1240, 754), radius=34, fill=255)
    art.paste(accent_box, mask=mask)

    draw.text((828, 664), "那先别急着总结自己。", fill=LIGHT, font=bubble_font)
    draw.text((828, 706), "先告诉我，哪一步拖垮了你？", fill=LIGHT, font=bubble_font)

    rounded_panel(draw, (786, 786, 1028, 798), 6, CHAT_TRACK)
    rounded_panel(draw, (786, 786, 930, 798), 6, CHAT_FILL)

    art.convert("RGB").save(OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {OUTPUT}")


if __name__ == "__main__":
    main()

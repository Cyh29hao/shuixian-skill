#!/usr/bin/env python3
"""
Render README PNG assets with fixed text layout for GitHub.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
HERO_OUTPUT = ASSETS / "hero-preview-v9.png"
FLOW_OUTPUT = ASSETS / "quickstart-flow-v8.png"

FONT_SANS = Path("C:/Windows/Fonts/msyh.ttc")
FONT_SANS_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
FONT_SERIF = Path("C:/Windows/Fonts/STZHONGS.TTF")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")


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


def shadowed_panel(layer: Image.Image, box: tuple[int, int, int, int], radius: int, fill, outline=None, outline_width=1):
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(box, radius=radius, fill=(124, 89, 64, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    layer.alpha_composite(shadow)
    draw = ImageDraw.Draw(layer)
    rounded_panel(draw, box, radius, fill, outline, outline_width)


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font_obj)
    return right - left


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line:
            lines.append("")
            continue

        current = ""
        for char in raw_line:
            tentative = current + char
            if current and text_width(draw, tentative, font_obj) > max_width:
                lines.append(current)
                current = char
            else:
                current = tentative
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font_obj: ImageFont.FreeTypeFont,
    fill,
    max_width: int,
    line_gap: int,
) -> tuple[int, int]:
    x, y = xy
    lines = wrap_text(draw, text, font_obj, max_width)
    _, top, _, bottom = draw.textbbox((0, 0), "国A", font=font_obj)
    line_height = bottom - top
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * (line_height + line_gap)), line, fill=fill, font=font_obj)
    total_height = len(lines) * line_height + max(0, len(lines) - 1) * line_gap
    return max((text_width(draw, line, font_obj) for line in lines), default=0), total_height


def draw_code_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    code: str,
    label_font: ImageFont.FreeTypeFont,
    code_font: ImageFont.FreeTypeFont,
):
    x1, y1, x2, y2 = box
    rounded_panel(draw, box, 22, (47, 37, 31))
    rounded_panel(draw, (x1 + 18, y1 - 28, x1 + 142, y1 + 8), 18, (236, 219, 203))
    draw.text((x1 + 36, y1 - 21), label, fill=(104, 76, 59), font=label_font)
    draw_wrapped(draw, code, (x1 + 24, y1 + 22), code_font, (255, 245, 236), x2 - x1 - 48, 8)


def draw_note_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    note: str,
    label_font: ImageFont.FreeTypeFont,
    note_font: ImageFont.FreeTypeFont,
):
    x1, y1, x2, y2 = box
    rounded_panel(draw, box, 22, (255, 251, 246), (228, 210, 194), 2)
    rounded_panel(draw, (x1 + 18, y1 - 28, x1 + 154, y1 + 8), 18, (244, 233, 222))
    draw.text((x1 + 36, y1 - 21), label, fill=(133, 96, 72), font=label_font)
    draw_wrapped(draw, note, (x1 + 24, y1 + 22), note_font, (80, 60, 48), x2 - x1 - 48, 10)


def render_hero() -> None:
    width, height = 1540, 940
    bg_top = (249, 240, 231)
    bg_bottom = (243, 230, 219)
    card = (255, 250, 244)
    border = (224, 204, 186)
    panel_fill = (252, 245, 237)
    text = (40, 29, 22)
    text_soft = (118, 90, 71)
    pill_bg = (245, 232, 218)
    pill_text = (131, 94, 71)
    dark = (45, 34, 28)
    light = (255, 247, 240)
    accent_a = (233, 159, 116)
    accent_b = (200, 108, 72)
    chat_soft = (244, 231, 220)
    track = (216, 195, 178)
    fill = (183, 140, 114)

    canvas = Image.new("RGB", (width, height), bg_top)
    draw_vertical_gradient(canvas, bg_top, bg_bottom)
    art = canvas.convert("RGBA")
    draw_glow(art, (1300, 150), 240, (242, 199, 168, 155))
    draw_glow(art, (220, 820), 280, (230, 212, 194, 135))

    shadowed_panel(art, (74, 58, 1466, 878), 52, card, border, 3)
    draw = ImageDraw.Draw(art)
    rounded_panel(draw, (116, 102, 1424, 834), 42, panel_fill, (230, 213, 198), 2)

    sans = font(FONT_SANS, 34)
    sans_bold = font(FONT_SANS_BOLD, 34)
    sans_small = font(FONT_SANS, 28)
    sans_label = font(FONT_SANS_BOLD, 22)
    sans_head = font(FONT_SANS_BOLD, 68)
    serif = font(FONT_SERIF if FONT_SERIF.exists() else FONT_SANS_BOLD, 98)
    mono = font(FONT_MONO if FONT_MONO.exists() else FONT_SANS, 30)
    bubble_user = font(FONT_SANS, 36)
    bubble_mirror = font(FONT_SANS_BOLD, 38)

    rounded_panel(draw, (156, 150, 458, 198), 24, pill_bg)
    draw.text((190, 164), "SELF-MIRROR COMPANION", fill=pill_text, font=sans_label)

    draw.text((154, 246), "水仙.skill", fill=text, font=serif)
    draw_wrapped(draw, "把你的语气、关系和价值观，长成一个会继续修正的镜像陪伴体。", (158, 388), sans, text_soft, 520, 12)

    rounded_panel(draw, (156, 560, 512, 646), 28, light, (232, 217, 204), 2)
    draw.text((204, 593), "同频，不装懂", fill=text, font=sans_bold)

    rounded_panel(draw, (156, 676, 576, 762), 28, light, (232, 217, 204), 2)
    draw.text((204, 709), "可慢热，可纠偏", fill=text, font=sans_bold)

    rounded_panel(draw, (156, 786, 624, 852), 32, dark)
    draw.text((198, 806), "$shuixian-sweet-demo", fill=light, font=mono)

    headline_x = 760
    _, headline_h = draw_wrapped(draw, "先试一个更懂你的自己", (headline_x, 164), sans_head, text, 520, 14)
    subtitle_y = 164 + headline_h + 30
    draw_wrapped(draw, "可以是恋人，也可以只是最懂你的朋友。先确认气质，再导入真正私密的材料。", (headline_x, subtitle_y), sans, text_soft, 520, 10)

    rounded_panel(draw, (920, 438, 1304, 566), 34, chat_soft, None, 0)
    draw_wrapped(draw, "今天有点被掏空了。", (970, 480), bubble_user, (94, 71, 58), 260, 8)

    accent = Image.new("RGBA", art.size, (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent)
    accent_box = (744, 616, 1298, 784)
    for y in range(accent_box[1], accent_box[3]):
        t = (y - accent_box[1]) / max(accent_box[3] - accent_box[1], 1)
        color = tuple(lerp(accent_a[i], accent_b[i], t) for i in range(3)) + (255,)
        accent_draw.line((accent_box[0], y, accent_box[2], y), fill=color, width=1)
    mask = Image.new("L", art.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(accent_box, radius=36, fill=255)
    art.paste(accent, mask=mask)
    draw = ImageDraw.Draw(art)
    draw_wrapped(draw, "先别急着怪自己。", (800, 660), bubble_mirror, light, 420, 10)
    draw_wrapped(draw, "告诉我，哪一刻最累？", (800, 714), bubble_mirror, light, 420, 10)

    rounded_panel(draw, (756, 834, 1068, 846), 6, track)
    rounded_panel(draw, (756, 834, 940, 846), 6, fill)

    art.convert("RGB").save(HERO_OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {HERO_OUTPUT}")


def render_flow() -> None:
    width, height = 1540, 1180
    bg_top = (249, 240, 231)
    bg_bottom = (244, 233, 221)
    card = (255, 250, 244)
    border = (224, 204, 186)
    panel_fill = (251, 244, 236)
    text = (40, 29, 22)
    text_soft = (118, 90, 71)
    pill_bg = (244, 232, 220)
    pill_text = (133, 96, 72)
    code_bg = (45, 34, 28)
    code_fg = (255, 246, 239)
    arrow = (204, 139, 103)

    canvas = Image.new("RGB", (width, height), bg_top)
    draw_vertical_gradient(canvas, bg_top, bg_bottom)
    art = canvas.convert("RGBA")
    draw_glow(art, (1220, 120), 220, (242, 203, 172, 140))
    draw_glow(art, (240, 660), 240, (232, 216, 199, 135))
    shadowed_panel(art, (70, 62, 1470, 1114), 46, card, border, 3)
    draw = ImageDraw.Draw(art)
    rounded_panel(draw, (112, 102, 1428, 1070), 36, panel_fill, (230, 213, 198), 2)

    title = font(FONT_SANS_BOLD, 56)
    subtitle = font(FONT_SANS, 30)
    step_label = font(FONT_SANS_BOLD, 22)
    step_title = font(FONT_SANS_BOLD, 34)
    note_font = font(FONT_SANS, 28)
    code_font = font(FONT_MONO if FONT_MONO.exists() else FONT_SANS, 24)

    draw.text((164, 164), "Quick Start Flow", fill=text, font=title)
    draw.text((164, 230), "先试玩，再决定要不要导入私密数据。", fill=text_soft, font=subtitle)

    rows = [
        {
            "box": (164, 288, 1376, 512),
            "step": "Step 1",
            "title": "列出可试玩预设",
            "command": "python tools/demo_builder.py\n--list-presets",
            "note": "看到可用的演示列表。",
        },
        {
            "box": (164, 542, 1376, 766),
            "step": "Step 2",
            "title": "生成 demo 镜像",
            "command": "python tools/demo_builder.py\n--preset sweet-gender-flipped\n--base-dir ./.agents/skills",
            "note": "生成一个无需私密数据的镜像。",
        },
        {
            "box": (164, 796, 1376, 1020),
            "step": "Step 3",
            "title": "开始和它对话",
            "command": "$shuixian-sweet-\ngender-flipped-demo",
            "note": "直接开始对话，再决定是否继续导入。",
        },
    ]

    for row in rows:
        x1, y1, x2, y2 = row["box"]
        rounded_panel(draw, row["box"], 30, (255, 253, 250), (224, 204, 186), 2)
        draw.text((x1 + 34, y1 + 24), row["step"], fill=pill_text, font=step_label)
        draw.text((x1 + 34, y1 + 66), row["title"], fill=text, font=step_title)

        draw_code_box(
            draw,
            (x1 + 34, y1 + 126, x1 + 650, y1 + 220),
            "输入命令",
            row["command"],
            step_label,
            code_font,
        )
        draw_note_box(
            draw,
            (x1 + 780, y1 + 126, x2 - 34, y1 + 220),
            "效果说明",
            row["note"],
            step_label,
            note_font,
        )

        arrow_y = y1 + 168
        draw.line((x1 + 674, arrow_y, x1 + 732, arrow_y), fill=arrow, width=8)
        draw.polygon([(x1 + 716, arrow_y - 16), (x1 + 748, arrow_y), (x1 + 716, arrow_y + 16)], fill=arrow)

    art.convert("RGB").save(FLOW_OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {FLOW_OUTPUT}")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_hero()
    render_flow()


if __name__ == "__main__":
    main()

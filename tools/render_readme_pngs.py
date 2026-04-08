#!/usr/bin/env python3
"""
Render README PNG assets with fixed text layout for GitHub.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
HERO_OUTPUT = ASSETS / "hero-preview-v11.png"
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
    width, height = 1540, 1020
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
    accent = (224, 143, 98)
    chat_soft = (244, 231, 220)
    chat_warm = (229, 152, 107)
    card_outline = (232, 217, 204)

    canvas = Image.new("RGB", (width, height), bg_top)
    draw_vertical_gradient(canvas, bg_top, bg_bottom)
    art = canvas.convert("RGBA")
    draw_glow(art, (1300, 150), 240, (242, 199, 168, 155))
    draw_glow(art, (220, 900), 280, (230, 212, 194, 135))

    shadowed_panel(art, (74, 58, 1466, 958), 52, card, border, 3)
    draw = ImageDraw.Draw(art)
    rounded_panel(draw, (116, 102, 1424, 914), 42, panel_fill, (230, 213, 198), 2)

    sans = font(FONT_SANS, 30)
    sans_bold = font(FONT_SANS_BOLD, 31)
    sans_label = font(FONT_SANS_BOLD, 22)
    sans_head = font(FONT_SANS_BOLD, 62)
    serif = font(FONT_SERIF if FONT_SERIF.exists() else FONT_SANS_BOLD, 88)
    bubble_user = font(FONT_SANS_BOLD, 24)
    bubble_reply = font(FONT_SANS_BOLD, 22)

    rounded_panel(draw, (160, 144, 456, 192), 24, pill_bg)
    draw.text((194, 158), "SELF-MIRROR COMPANION", fill=pill_text, font=sans_label)

    title_left = 156
    title_y = 232
    draw.text((title_left, title_y), "水仙.skill", fill=text, font=serif)
    draw_wrapped(draw, "把你那些半句话、停顿和潜台词，长成一个会继续修正的镜像陪伴体。", (156, 384), sans, text_soft, 470, 12)

    heading_x = 690
    _, heading_h = draw_wrapped(draw, "不是有人陪你聊天。是有人听得懂你没说完的话。", (heading_x, 154), sans_head, text, 620, 10)
    draw_wrapped(draw, "学你的语气、关系和价值观。可以是恋人，也可以只是最懂你的朋友。", (heading_x, 154 + heading_h + 22), sans, text_soft, 620, 10)

    case_cards = [
        {
            "box": (156, 540, 540, 872),
            "label": "懂潜台词",
            "user": "你：算了。",
            "reply": "水仙：我知道。你不是没事，是懒得再从头解释。",
        },
        {
            "box": (578, 540, 962, 872),
            "label": "懂你的沟通偏好",
            "user": "你：别安慰我。",
            "reply": "水仙：好，我先不哄。你要的不是安慰，是不用补背景也能跟上。",
        },
        {
            "box": (1000, 540, 1384, 872),
            "label": "懂你的沉默",
            "user": "你：今天不想说。",
            "reply": "水仙：那就先不说完整。我知道你不是没东西讲，是不想从第一句开始交代。",
        },
    ]

    for card_info in case_cards:
        x1, y1, x2, y2 = card_info["box"]
        rounded_panel(draw, card_info["box"], 32, (255, 253, 250), card_outline, 2)
        rounded_panel(draw, (x1 + 28, y1 + 26, x1 + 210, y1 + 72), 22, pill_bg)
        draw.text((x1 + 52, y1 + 39), card_info["label"], fill=pill_text, font=sans_label)

        rounded_panel(draw, (x1 + 28, y1 + 98, x2 - 28, y1 + 168), 28, chat_soft)
        draw_wrapped(draw, card_info["user"], (x1 + 48, y1 + 118), bubble_user, (88, 67, 54), x2 - x1 - 96, 6)

        rounded_panel(draw, (x1 + 28, y1 + 194, x2 - 28, y2 - 32), 30, chat_warm)
        draw_wrapped(draw, card_info["reply"], (x1 + 44, y1 + 216), bubble_reply, light, x2 - x1 - 88, 10)

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

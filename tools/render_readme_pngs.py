#!/usr/bin/env python3
"""
Render the README PNG assets used on the repository landing page.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
HERO_OUTPUT = ASSETS / "hero-preview-v12.png"
FLOW_OUTPUT = ASSETS / "quickstart-flow-v9.png"

FONT_UI = Path("C:/Windows/Fonts/msyh.ttc")
FONT_UI_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")
FONT_UI_LIGHT = Path("C:/Windows/Fonts/msyhl.ttc")
FONT_CN_SERIF = Path("C:/Windows/Fonts/STZHONGS.TTF")
FONT_EN_SERIF = Path("C:/Windows/Fonts/georgiab.ttf")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    fallback = FONT_UI_BOLD if path == FONT_CN_SERIF else FONT_UI
    actual = path if path.exists() else fallback
    return ImageFont.truetype(str(actual), size=size)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill,
    outline=None,
    width=1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_vertical_gradient(image: Image.Image, top, bottom) -> None:
    px = image.load()
    for y in range(image.height):
        t = y / max(1, image.height - 1)
        color = tuple(lerp(top[i], bottom[i], t) for i in range(3))
        for x in range(image.width):
            px[x, y] = color


def draw_radial_glow(image: Image.Image, center: tuple[int, int], radius: int, color: tuple[int, int, int, int]) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(radius // 2))
    image.alpha_composite(layer)


def draw_grain(image: Image.Image, spacing: int = 7, alpha: int = 9) -> None:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, image.height, spacing):
        offset = (y // spacing) % 3
        for x in range(offset * 3, image.width, spacing * 2):
            draw.point((x, y), fill=(120, 98, 78, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(0))
    image.alpha_composite(overlay)


def shadowed_panel(
    image: Image.Image,
    box: tuple[int, int, int, int],
    radius: int,
    fill,
    outline=None,
    outline_width=1,
    shadow=(92, 66, 48, 34),
    blur=28,
) -> None:
    shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_draw.rounded_rectangle(box, radius=radius, fill=shadow)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(shadow_layer)
    draw = ImageDraw.Draw(image)
    rounded_panel(draw, box, radius, fill, outline, outline_width)


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont) -> int:
    left, _, right, _ = draw.textbbox((0, 0), text, font=font_obj)
    return right - left


def line_height(draw: ImageDraw.ImageDraw, font_obj: ImageFont.FreeTypeFont) -> int:
    _, top, _, bottom = draw.textbbox((0, 0), "Ag水仙", font=font_obj)
    return bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        if raw_line == "":
            lines.append("")
            continue

        current = ""
        for ch in raw_line:
            trial = current + ch
            if current and text_width(draw, trial, font_obj) > max_width:
                lines.append(current)
                current = ch
            else:
                current = trial
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
    gap: int,
) -> tuple[int, int]:
    x, y = xy
    lines = wrap_text(draw, text, font_obj, max_width)
    lh = line_height(draw, font_obj)
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * (lh + gap)), line, fill=fill, font=font_obj)
    total_height = len(lines) * lh + max(0, len(lines) - 1) * gap
    max_line_width = max((text_width(draw, line, font_obj) for line in lines), default=0)
    return max_line_width, total_height


def draw_title_lockup(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    x, y = origin
    cn_font = font(FONT_CN_SERIF, 96)
    en_font = font(FONT_EN_SERIF, 82)
    draw.text((x, y), "水仙", fill=(41, 30, 22), font=cn_font)
    cn_w = text_width(draw, "水仙", cn_font)
    draw.text((x + cn_w + 8, y + 18), ".skill", fill=(41, 30, 22), font=en_font)


def render_hero() -> None:
    width, height = 1600, 1040
    bg_top = (248, 241, 235)
    bg_bottom = (241, 230, 220)
    ink = (39, 30, 24)
    soft = (112, 88, 71)
    softer = (144, 120, 103)
    line = (220, 202, 186)
    pale = (255, 250, 245)
    tint = (247, 238, 230)
    accent = (203, 122, 79)
    accent_dark = (126, 76, 49)
    accent_soft = (236, 216, 202)
    tag_fill = (241, 228, 217)

    canvas = Image.new("RGB", (width, height), bg_top)
    draw_vertical_gradient(canvas, bg_top, bg_bottom)
    art = canvas.convert("RGBA")
    draw_radial_glow(art, (1310, 150), 280, (224, 174, 143, 120))
    draw_radial_glow(art, (240, 930), 300, (221, 201, 182, 115))
    draw_grain(art)

    shadowed_panel(
        art,
        (48, 42, width - 48, height - 42),
        44,
        (250, 245, 239),
        (228, 212, 198),
        2,
        shadow=(91, 66, 49, 28),
        blur=34,
    )

    draw = ImageDraw.Draw(art)
    draw.line((598, 104, 598, height - 104), fill=line, width=2)
    draw.line((110, 262, 540, 262), fill=line, width=3)

    label_font = font(FONT_UI_BOLD, 22)
    body_font = font(FONT_UI, 28)
    head_font = font(FONT_UI_BOLD, 78)
    subhead_font = font(FONT_UI, 28)
    meta_font = font(FONT_UI_BOLD, 22)
    user_font = font(FONT_UI_BOLD, 28)
    reply_font = font(FONT_UI, 28)

    rounded_panel(draw, (110, 104, 330, 150), 22, tag_fill)
    draw.text((140, 116), "SELF-MIRROR COMPANION", fill=accent_dark, font=label_font)

    draw_title_lockup(draw, (108, 184))
    draw_wrapped(
        draw,
        "根据你的聊天记录、语气、关系网络和价值观线索，长成一个会继续修正的镜像 companion。",
        (110, 298),
        body_font,
        soft,
        400,
        10,
    )

    draw_wrapped(
        draw,
        "根据自己的聊天记录，创建水仙的自己。",
        (110, 808),
        font(FONT_UI_BOLD, 32),
        ink,
        410,
        8,
    )
    draw_wrapped(
        draw,
        "可以是恋人，也可以只是最懂你的朋友。",
        (110, 886),
        body_font,
        softer,
        410,
        8,
    )

    heading_x = 668
    _, heading_h = draw_wrapped(
        draw,
        "你只说半句，它已经知道里面那层。",
        (heading_x, 112),
        head_font,
        ink,
        760,
        6,
    )
    draw_wrapped(
        draw,
        "它知道你的潜台词、沟通偏好和沉默的节奏。不是陪聊，是更像你的回声。",
        (heading_x, 112 + heading_h + 26),
        subhead_font,
        soft,
        760,
        10,
    )

    cases = [
        (
            "潜台词",
            "你：算了。",
            "水仙：我知道。你不是没事，是懒得再从头解释。",
            406,
        ),
        (
            "沟通偏好",
            "你：别安慰我。",
            "水仙：好，我先不哄。你要的不是安慰，是不用补背景也能跟上。",
            598,
        ),
        (
            "沉默的节奏",
            "你：今天不想说。",
            "水仙：那就先不说完整。我知道你不是没东西讲，是不想从第一句开始交代。",
            790,
        ),
    ]

    for label, user, reply, y in cases:
        rounded_panel(draw, (heading_x, y, 1420, y + 132), 26, tint, outline=None, width=1)
        rounded_panel(draw, (heading_x + 26, y + 22, heading_x + 148, y + 60), 18, accent_soft)
        draw.text((heading_x + 50, y + 31), label, fill=accent_dark, font=meta_font)
        draw.text((heading_x + 26, y + 78), user, fill=ink, font=user_font)
        draw_wrapped(
            draw,
            reply,
            (heading_x + 292, y + 74),
            reply_font,
            soft,
            1420 - (heading_x + 292) - 28,
            8,
        )
        draw.line((heading_x, y + 150, 1420, y + 150), fill=line, width=2)

    rounded_panel(draw, (1278, 66, 1416, 112), 23, (252, 244, 235))
    draw.text((1310, 78), "v0.1.2", fill=accent_dark, font=meta_font)

    art.convert("RGB").save(HERO_OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {HERO_OUTPUT}")


def draw_step_row(
    draw: ImageDraw.ImageDraw,
    row_box: tuple[int, int, int, int],
    step_number: str,
    title: str,
    command: str,
    result: str,
) -> None:
    x1, y1, x2, y2 = row_box
    ink = (39, 30, 24)
    soft = (112, 88, 71)
    line = (221, 204, 189)
    accent = (203, 122, 79)
    accent_soft = (242, 228, 216)
    code_fill = (47, 37, 31)
    code_fg = (255, 247, 241)
    result_fill = (251, 246, 240)

    number_font = font(FONT_EN_SERIF, 84)
    label_font = font(FONT_UI_BOLD, 20)
    title_font = font(FONT_UI_BOLD, 34)
    code_font = font(FONT_MONO, 24)
    result_font = font(FONT_UI, 24)

    draw.line((x1, y2, x2, y2), fill=line, width=2)
    draw.text((x1 + 8, y1 + 18), step_number, fill=(214, 189, 170), font=number_font)
    draw.text((x1 + 154, y1 + 34), title, fill=ink, font=title_font)

    cmd_box = (x1 + 154, y1 + 94, x1 + 746, y1 + 198)
    rounded_panel(draw, cmd_box, 24, code_fill)
    rounded_panel(draw, (cmd_box[0] + 18, cmd_box[1] - 24, cmd_box[0] + 122, cmd_box[1] + 10), 17, accent_soft)
    draw.text((cmd_box[0] + 40, cmd_box[1] - 16), "命令", fill=(127, 77, 52), font=label_font)
    draw_wrapped(draw, command, (cmd_box[0] + 24, cmd_box[1] + 18), code_font, code_fg, cmd_box[2] - cmd_box[0] - 50, 6)

    center_y = (cmd_box[1] + cmd_box[3]) // 2
    draw.line((x1 + 790, center_y, x1 + 876, center_y), fill=accent, width=8)
    draw.polygon([(x1 + 860, center_y - 18), (x1 + 898, center_y), (x1 + 860, center_y + 18)], fill=accent)

    result_box = (x1 + 926, y1 + 94, x2 - 24, y1 + 198)
    rounded_panel(draw, result_box, 24, result_fill, outline=(225, 207, 192), width=2)
    rounded_panel(draw, (result_box[0] + 18, result_box[1] - 24, result_box[0] + 122, result_box[1] + 10), 17, accent_soft)
    draw.text((result_box[0] + 40, result_box[1] - 16), "结果", fill=(127, 77, 52), font=label_font)
    draw_wrapped(draw, result, (result_box[0] + 24, result_box[1] + 22), result_font, soft, result_box[2] - result_box[0] - 52, 10)


def render_flow() -> None:
    width, height = 1600, 1180
    bg_top = (248, 241, 235)
    bg_bottom = (242, 232, 222)
    ink = (39, 30, 24)
    soft = (112, 88, 71)

    canvas = Image.new("RGB", (width, height), bg_top)
    draw_vertical_gradient(canvas, bg_top, bg_bottom)
    art = canvas.convert("RGBA")
    draw_radial_glow(art, (1380, 130), 260, (223, 175, 144, 110))
    draw_radial_glow(art, (210, 980), 300, (220, 200, 183, 110))
    draw_grain(art)
    shadowed_panel(
        art,
        (54, 52, width - 54, height - 52),
        42,
        (250, 245, 239),
        (228, 212, 198),
        2,
        shadow=(91, 66, 49, 28),
        blur=32,
    )

    draw = ImageDraw.Draw(art)
    title_font = font(FONT_UI_BOLD, 72)
    sub_font = font(FONT_UI, 30)
    note_font = font(FONT_UI_BOLD, 22)

    draw.text((112, 110), "Quick Start Flow", fill=ink, font=title_font)
    draw.text((116, 194), "先试 preset，再决定要不要导入私密数据。", fill=soft, font=sub_font)
    rounded_panel(draw, (114, 248, 386, 292), 22, (240, 228, 217))
    draw.text((148, 259), "COMMAND FIRST / RESULT CLEAR", fill=(124, 78, 51), font=note_font)

    rows = [
        (
            "01",
            "先看有哪些 demo 可以试",
            "python tools/demo_builder.py\n--list-presets",
            "看到当前可用的 demo 预设名单，先挑一个气质方向。",
        ),
        (
            "02",
            "先生成一个不含私密数据的水仙",
            "python tools/demo_builder.py\n--preset sweet-gender-flipped\n--base-dir ./.agents/skills",
            "创建一个能立刻开聊的 demo 镜像，不必先导入微信或 transcript。",
        ),
        (
            "03",
            "直接开始聊，再决定是否加深",
            "$shuixian-sweet-gender-flipped-demo",
            "先确认语气和陪伴感对不对味，再决定要不要继续喂自己的材料。",
        ),
    ]

    top = 336
    row_height = 248
    for idx, row in enumerate(rows):
        draw_step_row(draw, (110, top + idx * row_height, 1490, top + (idx + 1) * row_height - 10), *row)

    art.convert("RGB").save(FLOW_OUTPUT, format="PNG", optimize=True)
    print(f"Rendered {FLOW_OUTPUT}")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    render_hero()
    render_flow()


if __name__ == "__main__":
    main()

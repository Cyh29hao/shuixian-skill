#!/usr/bin/env python3
"""Render original README artwork using Pillow and locally available fonts.

No network requests, generated-image service, or private input is used. Previous
asset versions are deliberately retained. Run --help for output/font overrides.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
INK = "#253E3B"
CREAM = "#FAF5EB"
MUTED = "#596B64"
GOLD = "#B18440"
LINE = "#DAD7C6"
FONTS: dict[str, str] = {}
LAYOUT_CHECKS: list[str] = []


def discover_font(role: str, override: Path | None = None) -> str:
    """Find CJK-capable fonts on Windows, macOS or common Linux distributions."""
    if override is not None:
        if not override.is_file():
            raise FileNotFoundError(f"Font does not exist: {override}")
        return str(override)
    windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates = {
        "sans": [windows / "msyh.ttc", windows / "NotoSansSC-VF.ttf"],
        "bold": [windows / "msyhbd.ttc", windows / "Noto Sans SC Bold (TrueType).otf"],
        "serif": [windows / "NotoSerifSC-VF.ttf", windows / "STZHONGS.TTF"],
        "latin": [windows / "georgia.ttf"],
    }[role]
    candidates += [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    if role in {"bold", "serif", "latin"} and "sans" in FONTS:
        return FONTS["sans"]
    raise FileNotFoundError("A CJK font is required; pass --font-sans /path/to/font.ttf")


def font(size: int, role: str = "sans") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[role], size)


def write(draw, xy, text, size=30, color=INK, role="sans", max_width=None):
    """Draw literal, intentional lines and fail if one exceeds its column."""
    f = font(size, role)
    x, y = xy
    for row, line in enumerate(text.split("\n")):
        width = draw.textlength(line, font=f)
        if max_width is not None and width > max_width:
            raise ValueError(f"Text overflow ({width:.0f} > {max_width}): {line}")
        draw.text((x, y + row * int(size * 1.6)), line, font=f, fill=color)
    LAYOUT_CHECKS.append(text.split("\n")[0])


def paper(size):
    art = Image.new("RGB", size, CREAM)
    d = ImageDraw.Draw(art)
    for y in range(9, size[1], 16):
        for x in range(7 + (y % 3) * 4, size[0], 27):
            d.point((x, y), fill="#E5E0D1")
    return art


def petal(draw, center, length, width, angle, fill):
    cx, cy = center
    vx, vy = math.cos(angle), math.sin(angle)
    nx, ny = -vy, vx
    points = []
    for i in range(61):
        t = i / 60
        half = math.sin(math.pi * t) ** 0.8 * width
        points.append((cx + vx * t * length + nx * half, cy + vy * t * length + ny * half))
    for i in range(60, -1, -1):
        t = i / 60
        half = math.sin(math.pi * t) ** 0.8 * width
        points.append((cx + vx * t * length - nx * half, cy + vy * t * length - ny * half))
    draw.polygon(points, fill=fill)


def flower(draw, center, scale=1):
    cx, cy = center
    for i in range(6):
        petal(draw, center, 72 * scale, 24 * scale, i * math.pi / 3 - math.pi / 2, "#F7EED5")
    r = 20 * scale
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill="#D1A756", outline="#E8CB83", width=3)
    draw.ellipse((cx-r*.45, cy-r*.45, cx+r*.45, cy+r*.45), fill="#94733D")


def mirror_art():
    """A narcissus over a rippled reflection, drawn entirely from paths."""
    scene = Image.new("RGB", (650, 680), "#263F3B")
    d = ImageDraw.Draw(scene)
    for y in range(680):
        c = (38 + y // 60, 63 + y // 60, 59 + y // 65)
        d.line((0, y, 650, y), fill=c)
    d.ellipse((200, 36, 544, 380), fill="#314B44")
    d.arc((58, 72, 596, 606), 197, 337, fill="#657766", width=2)
    d.arc((78, 92, 576, 588), 215, 319, fill="#445E50", width=1)
    for stem in [(349, 218, 304, 450), (422, 303, 336, 458), (224, 323, 279, 458)]:
        d.line(stem, fill="#A0AC80", width=5)
    petal(d, (300, 462), 227, 18, -1.96, "#738D6A")
    petal(d, (315, 463), 192, 13, -1.02, "#8A9E72")
    petal(d, (318, 459), 156, 10, -1.45, "#BAC19A")
    flower(d, (351, 218), 1.18)
    flower(d, (423, 303), .72)
    flower(d, (224, 323), .57)
    reflection = scene.crop((0, 192, 650, 460)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    reflection = reflection.resize((650, 180)).filter(ImageFilter.GaussianBlur(1))
    reflection = Image.blend(Image.new("RGB", reflection.size, "#304B46"), reflection, .40)
    rippled = Image.new("RGB", reflection.size, "#304B46")
    for y in range(reflection.height):
        shift = int(math.sin(y * .24) * (3 + y / 20))
        rippled.paste(reflection.crop((0, y, 650, y+1)), (shift, y))
    scene.paste(rippled, (0, 460))
    d = ImageDraw.Draw(scene)
    d.line((38, 460, 612, 460), fill="#76856D", width=2)
    for x, y, w, h in [(322, 473, 205, 18), (320, 508, 265, 26), (321, 555, 355, 33), (323, 608, 457, 42)]:
        d.arc((x-w/2, y-h/2, x+w/2, y+h/2), 8, 173, fill="#8E9B7B", width=2)
    for x, y, r in [(120, 220, 2), (506, 154, 3), (517, 382, 2), (159, 410, 2)]:
        d.ellipse((x-r, y-r, x+r, y+r), fill="#D5B575")
    return scene


def render_hero(output):
    art = paper((1840, 1340))
    d = ImageDraw.Draw(art)
    write(d, (100, 68), "水仙", 54, role="serif")
    write(d, (225, 88), "/  SHUIXIAN.SKILL", 23, role="latin", color=MUTED)
    write(d, (1338, 88), "A MIRROR, STILL BECOMING", 21, role="latin", color=MUTED)
    d.line((100, 158, 1740, 158), fill=LINE, width=2)
    write(d, (100, 215), "遇见另一个自己。", 88, role="serif", max_width=950)
    write(d, (104, 344), "同一种底色，不同的靠近方式。", 37, max_width=910)
    write(d, (106, 429), "把你的表达、偏好与边界，写成一个\n可以相处、可以纠正的 AI 镜像伙伴。", 32, color=MUTED, max_width=870)
    d.line((108, 581, 165, 581), fill=GOLD, width=3)
    write(d, (184, 558), "先试一段对话，再决定靠近多少。", 29, color=MUTED)
    write(d, (106, 657), "像你，但不必句句附和。", 36, role="serif")
    write(d, (108, 723), "关系由你选  ·  材料由你定  ·  语气随时改", 27, color=MUTED)
    scene = mirror_art()
    mask = Image.new("L", scene.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 649, 679), radius=320, fill=255)
    art.paste(scene, (1090, 199), mask)
    d = ImageDraw.Draw(art)
    d.rounded_rectangle((1077, 186, 1752, 892), radius=335, outline="#CBCAB4", width=2)
    d.line((1676, 826, 1765, 826), fill=GOLD, width=2)
    d.ellipse((1760, 821, 1770, 831), fill=GOLD)
    d.line((100, 935, 1740, 935), fill=LINE, width=2)
    write(d, (104, 966), "同一句：今天不想解释了。", 29, role="bold")
    write(d, (1128, 973), "以下为创作示例，非实测效果", 25, color=MUTED)
    cards = [
        (100, "01", "甜系恋人", "亲近一点，留有余地", "那就先不解释。\n想靠近一点，还是各自待会儿？", "#EDE5D8"),
        (658, "02", "深夜共脑", "一起想，不急着定论", "先放着。等你想聊时，\n我们只拆最卡住的那一点。", "#E4E8DF"),
        (1216, "03", "同频朋友", "松弛相处，有话直说", "行，今天跳过交代背景。\n陪你吐槽，还是聊点别的？", "#EBE6DC"),
    ]
    for x, number, name, caption, sample, fill in cards:
        d.rounded_rectangle((x, 1040, x+524, 1288), radius=22, fill=fill)
        write(d, (x+28, 1062), number, 26, color=GOLD, role="latin")
        write(d, (x+79, 1057), name, 33, role="bold", max_width=410)
        write(d, (x+28, 1120), caption, 25, color=MUTED, max_width=468)
        d.line((x+28, 1170, x+496, 1170), fill="#C9CABB", width=1)
        write(d, (x+28, 1190), sample, 27, max_width=468)
    art.save(output, optimize=True)
    return art


def step_icon(d, x, y, kind):
    if kind == 0:
        for offset, height in [(0, 64), (33, 86), (66, 54)]:
            d.rounded_rectangle((x+offset, y+92-height, x+offset+21, y+92), radius=10, fill=INK)
    elif kind == 1:
        d.rounded_rectangle((x, y+20, x+96, y+88), radius=22, outline=INK, width=3)
        d.polygon([(x+18, y+83), (x+17, y+102), (x+39, y+87)], fill=INK)
        for offset in [24, 46, 68]:
            d.ellipse((x+offset, y+49, x+offset+7, y+56), fill=GOLD)
    elif kind == 2:
        for offset in [0, 22, 44]:
            d.rounded_rectangle((x+offset, y+20+offset//2, x+57+offset, y+80+offset//2), radius=9, fill=CREAM, outline=INK, width=3)
    else:
        d.arc((x, y+12, x+98, y+106), 25, 322, fill=INK, width=4)
        d.polygon([(x+90, y+17), (x+96, y+48), (x+69, y+36)], fill=INK)
        d.line((x+30, y+60, x+44, y+73, x+70, y+44), fill=GOLD, width=4)


def render_flow(output):
    art = paper((1840, 1020))
    d = ImageDraw.Draw(art)
    write(d, (100, 65), "从一段对话开始。", 68, role="serif")
    write(d, (104, 173), "不用一次交代完整个自己。先试、再校准，始终留着修改的余地。", 30, color=MUTED, max_width=1640)
    d.line((100, 258, 1740, 258), fill=LINE, width=2)
    steps = [
        ("选一种关系", "恋人感、共脑或朋友。\n先定距离，再调语气。", "关系可以换，不必一次选对。"),
        ("零隐私试玩", "先用公开预设。\n不导入私密聊天记录。", "先判断：我想不想继续聊？"),
        ("三段样本校准", "自选脱敏短句。\n对照语气、判断与边界。", "材料少一点，反馈具体一点。"),
        ("一句话纠偏", "“少分析，先陪我。”\n把不合适的地方直接说清。", "改完重聊，看看是否更合拍。"),
    ]
    for i, (title, body, note) in enumerate(steps):
        x = 100+i*418
        d.rounded_rectangle((x, 306, x+386, 813), radius=24, fill="#E5E9E0" if i == 2 else "#EFE9DD")
        write(d, (x+28, 330), f"0{i+1}", 27, color=GOLD, role="latin")
        step_icon(d, x+29, 384, i)
        write(d, (x+28, 529), title, 36, role="bold", max_width=335)
        write(d, (x+28, 609), body, 27, max_width=335)
        d.line((x+28, 722, x+358, 722), fill="#CDCFBF", width=1)
        write(d, (x+28, 750), note, 23, color=MUTED, max_width=335)
        if i < 3:
            d.line((x+394, 566, x+410, 566), fill=GOLD, width=2)
            d.polygon([(x+406, 561), (x+414, 566), (x+406, 571)], fill=GOLD)
    write(d, (104, 871), "像不像你，不靠一句设定。", 36, role="serif")
    write(d, (104, 936), "靠一次次表达、反馈和修正。具体操作见下方可复制的命令。", 28, color=MUTED)
    art.save(output, optimize=True)
    return art


def render_mobile_hero(output):
    """Reflow at 2x for a 390px viewport; do not shrink three columns."""
    art = paper((780, 1480))
    d = ImageDraw.Draw(art)
    write(d, (48, 36), "水仙", 42, role="serif")
    write(d, (160, 53), "/ SHUIXIAN.SKILL", 24, color=MUTED, role="latin")
    d.line((48, 114, 732, 114), fill=LINE, width=2)
    write(d, (48, 154), "遇见另一个\n自己。", 64, role="serif", max_width=400)
    scene = mirror_art().resize((260, 272), Image.Resampling.LANCZOS)
    mask = Image.new("L", scene.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 259, 271), radius=130, fill=255)
    art.paste(scene, (472, 144), mask)
    d = ImageDraw.Draw(art)
    write(d, (48, 393), "同一种底色，不同的靠近方式。", 32, max_width=684)
    write(d, (48, 466), "把你的表达、偏好与边界，\n写成可以相处、可以纠正的镜像伙伴。", 32, color=MUTED, max_width=684)
    d.line((48, 596, 732, 596), fill=LINE, width=2)
    write(d, (48, 622), "同一句：今天不想解释了。", 32, role="bold", max_width=684)
    write(d, (48, 676), "创作示例 · 非实测效果", 26, color=MUTED)
    cards = [
        ("01", "甜系恋人", "亲近一点，留有余地", "那就先不解释。\n想靠近一点，还是各自待会儿？", "#EDE5D8"),
        ("02", "深夜共脑", "一起想，不急着定论", "先放着。等你想聊时，\n我们只拆最卡住的那一点。", "#E4E8DF"),
        ("03", "同频朋友", "松弛相处，有话直说", "行，今天跳过交代背景。\n陪你吐槽，还是聊点别的？", "#EBE6DC"),
    ]
    for i, (number, name, caption, sample, fill) in enumerate(cards):
        y = 738 + i * 238
        d.rounded_rectangle((48, y, 732, y+216), radius=22, fill=fill)
        write(d, (76, y+20), number, 28, color=GOLD, role="latin")
        write(d, (134, y+16), name, 36, role="bold", max_width=560)
        write(d, (76, y+71), caption, 28, color=MUTED, max_width=628)
        write(d, (76, y+118), sample, 32, max_width=628)
    art.save(output, optimize=True)
    return art


def render_mobile_flow(output):
    art = paper((780, 1400))
    d = ImageDraw.Draw(art)
    write(d, (48, 42), "从一段对话开始。", 56, role="serif", max_width=684)
    write(d, (48, 148), "不用一次交代完整个自己。\n先试，再慢慢校准。", 32, color=MUTED, max_width=684)
    d.line((48, 272, 732, 272), fill=LINE, width=2)
    steps = [
        ("选一种关系", "恋人感、共脑或朋友。\n先定距离，再调语气。"),
        ("零隐私试玩", "先用公开预设。\n不导入私密聊天记录。"),
        ("三段样本校准", "自选脱敏短句。\n对照语气、判断与边界。"),
        ("一句话纠偏", "“少分析，先陪我。”\n改完重聊，看看是否合拍。"),
    ]
    for i, (title, body) in enumerate(steps):
        y = 310 + i * 238
        d.rounded_rectangle((48, y, 732, y+212), radius=24,
                            fill="#E5E9E0" if i == 2 else "#EFE9DD")
        step_icon(d, 78, y+65, i)
        write(d, (80, y+17), f"0{i+1}", 28, color=GOLD, role="latin")
        write(d, (216, y+24), title, 36, role="bold", max_width=488)
        write(d, (216, y+93), body, 32, max_width=488)
    write(d, (48, 1280), "像不像你，靠表达、反馈和修正。", 32, role="serif", max_width=684)
    write(d, (48, 1340), "可复制的命令就在下方。", 28, color=MUTED)
    art.save(output, optimize=True)
    return art


def runtime_card(width, index, sample):
    """Render literal, source-checked replies; line breaks are the only edits."""
    padding = 28 if width < 750 else 36
    line_height = int(32 * 1.6)
    user_y = 128
    reply_y = user_y + len(sample['user_lines']) * line_height + 26
    reply_height = 82 + len(sample['reply_lines']) * line_height
    height = reply_y + reply_height + 32
    card = Image.new('RGB', (width, height), CREAM)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, width-1, height-1), radius=24, fill='#E6EAE1' if index == 0 else '#EFE7DA', outline=LINE, width=2)
    write(d, (padding, 23), f'0{index+1}', 28, color=GOLD, role='latin')
    write(d, (padding+60, 18), sample['title'], 32, role='bold', max_width=width-padding*2-60)
    write(d, (padding, 87), '你', 24, color=MUTED)
    write(d, (padding, user_y), '\n'.join(sample['user_lines']), 32, max_width=width-padding*2)
    d.rounded_rectangle((padding-10, reply_y, width-padding+10, reply_y+reply_height), radius=18, fill=INK)
    write(d, (padding+12, reply_y+15), '灯 / 同频朋友', 24, color='#DCC692')
    write(d, (padding+12, reply_y+58), '\n'.join(sample['reply_lines']), 32, color=CREAM, max_width=width-padding*2-24)
    return card


def render_runtime(output, mobile=False):
    data = json.loads((ROOT / 'assets/runtime-dialogue.json').read_text(encoding='utf-8'))
    report = (ROOT / data['source_report']).read_text(encoding='utf-8')
    for sample in data['cards']:
        assert ''.join(sample['user_lines']) in report
        assert ''.join(sample['reply_lines']) in report
    width, margin, gap = (780, 48, 24) if mobile else (1840, 100, 40)
    card_width = width-margin*2 if mobile else (width-margin*2-gap)//2
    cards = [runtime_card(card_width, i, sample) for i, sample in enumerate(data['cards'])]
    top = 270 if mobile else 320
    content_height = sum(card.height for card in cards)+gap if mobile else max(card.height for card in cards)
    art = paper((width, top+content_height+108))
    d = ImageDraw.Draw(art)
    write(d, (margin, 35 if mobile else 52), '水仙 / 真实试聊', 28, color=MUTED)
    write(d, (margin, 94 if mobile else 110), '先聊一点小事。', 54 if mobile else 74, role='serif', max_width=width-margin*2)
    write(d, (margin, 186 if mobile else 228), '你可以随口说，也可以随时改。', 30 if mobile else 34, color=MUTED, max_width=width-margin*2)
    if not mobile:
        flower(d, (width-171, 147), .8)
        d.line((margin, 287, width-margin, 287), fill=LINE, width=2)
    y = top
    for index, card in enumerate(cards):
        x = margin if mobile else margin+index*(card_width+gap)
        art.paste(card, (x, y))
        if mobile: y += card.height+gap
    d = ImageDraw.Draw(art)
    footer = '公开合成材料 · 两轮实际原文'
    write(d, (margin, art.height-78), footer, 27 if mobile else 28, color=MUTED, max_width=width-margin*2)
    write(d, (margin, art.height-39), '完整第三轮、配置与试法见正文。', 24, color=MUTED, max_width=width-margin*2)
    art.save(output, optimize=True)
    return art


def roadside_flower(size):
    """An authored botanical vignette, not a photo or evidence of the user's flower."""
    width, height = size
    art = Image.new('RGB', size, INK)
    d = ImageDraw.Draw(art)
    cx, cy = width*.52, height*.37
    scale = min(width/600, height/560)
    d.ellipse((cx-155*scale, cy-155*scale, cx+155*scale, cy+155*scale), fill='#344D44')
    bottom = height*.90
    d.line((cx, cy+18*scale, cx-28*scale, bottom), fill='#A5B38B', width=max(3, round(6*scale)))
    petal(d, (cx-19*scale, bottom-25*scale), 155*scale, 22*scale, -2.25, '#7E9778')
    petal(d, (cx-21*scale, bottom-66*scale), 139*scale, 17*scale, -1.02, '#A0AE86')
    for index in range(8):
        petal(d, (cx, cy), 114*scale, 31*scale, index*math.pi/4-.22, '#F9F3DF')
    radius = 44*scale
    d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill='#DEB45B')
    d.ellipse((cx-radius*.72, cy-radius*.72, cx+radius*.72, cy+radius*.72), fill='#F0C565')
    d.arc((cx-radius*.58, cy-radius*.58, cx+radius*.58, cy+radius*.58), 208, 286, fill='#FAE1A1', width=max(2, round(4*scale)))
    for x, y in ((width*.19,height*.24),(width*.81,height*.59),(width*.23,height*.74)):
        d.ellipse((x-2,y-2,x+2,y+2), fill='#CBB57E')
    return art


def render_sweet_moment(output, mobile=False):
    data = json.loads((ROOT / 'assets/sweet-moment.json').read_text(encoding='utf-8'))
    report = (ROOT / data['source_report']).read_text(encoding='utf-8')
    for key in ('user_lines', 'reply_lines'):
        assert ''.join(data[key]) in report
    art = paper((780, 1290) if mobile else (1840, 1040))
    d = ImageDraw.Draw(art)
    margin = 48 if mobile else 100
    text_width = 684 if mobile else 800
    write(d, (margin, 35 if mobile else 56), '水仙 / 一次真实接话', 28, color=MUTED)
    write(d, (margin, 106 if mobile else 137), '一点小事，\n也可以分享。', 58 if mobile else 78,
          role='serif', max_width=text_width)
    write(d, (margin, 300 if mobile else 408), '没有照片，也不必补一个故事。', 32, color=MUTED, max_width=text_width)
    vignette = roadside_flower((684, 354) if mobile else (720, 820))
    mask = Image.new('L', vignette.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,vignette.width-1,vignette.height-1), radius=28, fill=255)
    art.paste(vignette, (48, 371) if mobile else (1020, 100), mask)
    d = ImageDraw.Draw(art)
    user_y = 762 if mobile else 497
    write(d, (margin, user_y), '你 / 今天的开心', 26, color=MUTED)
    write(d, (margin, user_y+51), '\n'.join(data['user_lines']), 32, max_width=text_width)
    context_y = 951 if mobile else 681
    write(d, (margin, context_y), data['context_caption'], 28, color=MUTED, max_width=text_width)
    box_y = 1011 if mobile else 746
    d.rounded_rectangle((margin-12, box_y, margin+text_width+12, box_y+182), radius=22, fill='#E5E9DF')
    write(d, (margin+16, box_y+16), '甜系预设 / 实际回复', 26, color=MUTED)
    write(d, (margin+16, box_y+62), '\n'.join(data['reply_lines']), 36, max_width=text_width-32)
    write(d, (margin, 1236 if mobile else 974), '公开预设实聊 · 插画为创作 · 完整两轮见正文',
          26 if mobile else 28, color=MUTED, max_width=art.width-margin*2)
    art.save(output, optimize=True)
    return art


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets")
    parser.add_argument("--hero-name", default="hero-preview-v13.png")
    parser.add_argument("--flow-name", default="quickstart-flow-v10.png")
    parser.add_argument("--mobile-only", action="store_true", help="Render narrow single-column artwork only")
    parser.add_argument("--runtime-only", action="store_true", help="Render source-checked actual dialogue artwork only")
    parser.add_argument("--sweet-only", action="store_true", help="Render the source-checked everyday sweet moment only")
    parser.add_argument("--mobile-hero-name", default="hero-mobile-v1.png")
    parser.add_argument("--mobile-flow-name", default="quickstart-mobile-v1.png")
    parser.add_argument("--font-sans", type=Path)
    parser.add_argument("--font-bold", type=Path)
    parser.add_argument("--font-serif", type=Path)
    parser.add_argument("--font-latin", type=Path)
    parser.add_argument("--preview-dir", type=Path, help="Also save 390px and 920px reading previews")
    args = parser.parse_args()
    for role in ["sans", "bold", "serif", "latin"]:
        FONTS[role] = discover_font(role, getattr(args, f"font_{role}"))
    for name in [args.hero_name, args.flow_name, args.mobile_hero_name, args.mobile_flow_name]:
        if Path(name).name != name or Path(name).suffix.lower() != ".png":
            parser.error("Asset names must be plain .png filenames")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.sweet_only:
        renders = [('sweet-moment-v1.png', render_sweet_moment), ('sweet-moment-mobile-v1.png', lambda output: render_sweet_moment(output, mobile=True))]
    elif args.runtime_only:
        renders = [('runtime-dialogue-v1.png', render_runtime), ('runtime-dialogue-mobile-v1.png', lambda output: render_runtime(output, mobile=True))]
    else:
        renders = [(args.mobile_hero_name, render_mobile_hero), (args.mobile_flow_name, render_mobile_flow)] if args.mobile_only else [(args.hero_name, render_hero), (args.flow_name, render_flow)]
    for name, render in renders:
        destination = args.output_dir / name
        art = render(destination)
        if args.preview_dir:
            args.preview_dir.mkdir(parents=True, exist_ok=True)
            for width in [390, 920]:
                preview = args.preview_dir / f"{width}-{name}"
                art.resize((width, round(art.height * width / art.width)), Image.Resampling.LANCZOS).save(preview)
            # Keep the existing 920px preview path for previous commands.
            art.resize((920, round(art.height * 920 / art.width)), Image.Resampling.LANCZOS).save(args.preview_dir / name)
        print(f"Rendered {destination} ({art.width}x{art.height})")
    print(f"Checked {len(LAYOUT_CHECKS)} text blocks against explicit column widths where supplied.")


if __name__ == "__main__":
    for cli_stream in (sys.stdout, sys.stderr):
        if hasattr(cli_stream, "reconfigure"):
            cli_stream.reconfigure(encoding="utf-8")
    main()

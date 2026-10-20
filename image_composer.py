"""Graphic Composer Module (Multi-Template High-Resolution 9:16 Poster Renderer).

Solves design monotony by dynamically switching between 3 distinct layouts:
1. LAYOUT_CARDS: Modern Glassmorphic 3-Card structure (Actionable points)
2. LAYOUT_SCRIPTURE_HERO: Majestic Gold Border Frame with Large Scripture Highlight
3. LAYOUT_EDITORIAL: Modern Clean Magazine Style with elegant typography
"""

from datetime import datetime
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from utils.font_downloader import ensure_fonts_exist

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Color Palette Constants
COLOR_GOLD = (245, 208, 98, 255)
COLOR_LIGHT_GOLD = (255, 238, 173, 255)
COLOR_WHITE = (255, 255, 255, 255)
COLOR_OFFWHITE = (240, 245, 252, 255)
COLOR_SCRIPTURE = (215, 235, 255, 255)
COLOR_ACCENT_BG = (220, 165, 35, 240)
CARD_BG_COLOR = (12, 18, 32, 120)
CARD_BORDER_COLOR = (245, 208, 98, 85)


def _load_font(
    font_path: Optional[Path], size: int, fallback_family: str = "arial.ttf"
) -> ImageFont.FreeTypeFont:
    if font_path and font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            pass
    for cand in ["malgun.ttf", "gulim.ttc", "AppleGothic.ttf", fallback_family]:
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple[int, int, int, int] = COLOR_WHITE,
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 170),
    shadow_offset: Tuple[int, int] = (2, 3),
    align: str = "left",
) -> None:
    x, y = xy
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color, align=align)
    draw.text((x, y), text, font=font, fill=fill_color, align=align)


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    lines: List[str] = []
    paragraphs = text.split("\n")
    for paragraph in paragraphs:
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    sub_line = ""
                    for ch in word:
                        test_sub = sub_line + ch
                        sub_bbox = font.getbbox(test_sub)
                        if (sub_bbox[2] - sub_bbox[0]) <= max_width:
                            sub_line = test_sub
                        else:
                            lines.append(sub_line)
                            sub_line = ch
                    current_line = sub_line
        if current_line:
            lines.append(current_line)
    return lines


# ===========================================================================
# Layout Engine 1: Modern Glassmorphic Cards (실천 지침 3단 카드형)
# ===========================================================================
def _render_layout_cards(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    current_y = 110

    # Top Pill Badge
    tag_text = "✦ 오늘의 말씀 실천 지침 ✦"
    tag_bbox = fonts["category"].getbbox(tag_text)
    tag_w = tag_bbox[2] - tag_bbox[0]
    pill_padding = 18
    draw.rounded_rectangle(
        [(width - tag_w) // 2 - pill_padding, current_y, (width + tag_w) // 2 + pill_padding, current_y + 44],
        radius=20, fill=(15, 24, 42, 210), outline=COLOR_GOLD, width=1
    )
    draw.text(((width - tag_w) // 2, current_y + 7), tag_text, font=fonts["category"], fill=COLOR_GOLD)
    current_y += 75

    # Headline
    headline = content.get("headline", "")
    for line in _wrap_text(headline, fonts["headline"], width - 180):
        lw = fonts["headline"].getbbox(line)[2] - fonts["headline"].getbbox(line)[0]
        _draw_text_with_shadow(draw, ((width - lw) // 2, current_y), line, fonts["headline"], COLOR_WHITE, shadow_offset=(3, 5))
        current_y += 82

    # Sub-headline
    sub = content.get("sub_headline", "")
    if sub:
        for sline in _wrap_text(sub, fonts["sub_headline"], width - 200):
            sw = fonts["sub_headline"].getbbox(sline)[2] - fonts["sub_headline"].getbbox(sline)[0]
            _draw_text_with_shadow(draw, ((width - sw) // 2, current_y), sline, fonts["sub_headline"], COLOR_LIGHT_GOLD)
            current_y += 44
    current_y += 20

    # 3 Glass Cards
    card_x = 80
    card_w = width - (card_x * 2)
    for i, pt in enumerate(content.get("points", [])[:3], 1):
        p_title = pt.get("title", "")
        p_desc = pt.get("description", "")
        sc = pt.get("scripture", {})
        sc_txt = f"\"{sc.get('text', '')}\" ({sc.get('reference', '')})"

        desc_lines = _wrap_text(p_desc, fonts["point_desc"], card_w - 130)
        sc_lines = _wrap_text(sc_txt, fonts["scripture_txt"], card_w - 130)
        card_h = 55 + (len(desc_lines) * 34) + (len(sc_lines) * 32) + 26

        draw.rounded_rectangle([card_x, current_y, card_x + card_w, current_y + card_h], radius=18, fill=CARD_BG_COLOR, outline=CARD_BORDER_COLOR, width=2)

        # Badge
        bx, by = card_x + 22, current_y + 20
        draw.rounded_rectangle([bx, by, bx + 44, by + 44], radius=12, fill=COLOR_ACCENT_BG)
        b_txt = str(i)
        btw = fonts["badge"].getbbox(b_txt)[2] - fonts["badge"].getbbox(b_txt)[0]
        draw.text((bx + (44 - btw) // 2, by + 6), b_txt, font=fonts["badge"], fill=(20, 20, 20, 255))

        # Title
        _draw_text_with_shadow(draw, (bx + 62, by + 6), p_title, fonts["point_title"], COLOR_GOLD)

        ty = by + 58
        for dl in desc_lines:
            _draw_text_with_shadow(draw, (bx + 10, ty), dl, fonts["point_desc"], COLOR_OFFWHITE)
            ty += 34
        ty += 4
        for sl in sc_lines:
            _draw_text_with_shadow(draw, (bx + 15, ty), sl, fonts["scripture_txt"], COLOR_SCRIPTURE)
            ty += 32

        current_y += card_h + 20

    # CTA
    cta = content.get("call_to_action", "")
    for cl in _wrap_text(f"“ {cta} ”", fonts["cta"], width - 180):
        cw = fonts["cta"].getbbox(cl)[2] - fonts["cta"].getbbox(cl)[0]
        _draw_text_with_shadow(draw, ((width - cw) // 2, current_y + 10), cl, fonts["cta"], COLOR_LIGHT_GOLD)
        current_y += 42


# ===========================================================================
# Layout Engine 2: Scripture Hero (성경 본문 강조형 / 황금 프레임 묵상)
# ===========================================================================
def _render_layout_scripture_hero(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    current_y = 120

    # Top Scripture Banner Tag
    tag_text = "✦ 오늘의 핵심 성경 말씀 ✦"
    tw = fonts["category"].getbbox(tag_text)[2] - fonts["category"].getbbox(tag_text)[0]
    _draw_text_with_shadow(draw, ((width - tw) // 2, current_y), tag_text, fonts["category"], COLOR_GOLD)
    current_y += 50

    # Headline
    headline = content.get("headline", "")
    for line in _wrap_text(headline, fonts["headline"], width - 180):
        lw = fonts["headline"].getbbox(line)[2] - fonts["headline"].getbbox(line)[0]
        _draw_text_with_shadow(draw, ((width - lw) // 2, current_y), line, fonts["headline"], COLOR_WHITE, shadow_offset=(3, 5))
        current_y += 84
    current_y += 25

    # Center Ornate Golden Frame for Primary Scripture
    frame_x = 75
    frame_w = width - (frame_x * 2)
    first_pt = content.get("points", [{}])[0]
    sc_obj = first_pt.get("scripture", {})
    main_sc_text = sc_obj.get("text", "")
    main_sc_ref = sc_obj.get("reference", "")

    sc_lines = _wrap_text(f"“ {main_sc_text} ”", fonts["sub_headline"], frame_w - 80)
    frame_h = max(240, 90 + len(sc_lines) * 50)

    # Multi-layered frame
    draw.rounded_rectangle([frame_x, current_y, frame_x + frame_w, current_y + frame_h], radius=22, fill=(10, 16, 32, 160), outline=COLOR_GOLD, width=3)
    draw.rounded_rectangle([frame_x + 8, current_y + 8, frame_x + frame_w - 8, current_y + frame_h - 8], radius=16, fill=None, outline=(245, 208, 98, 70), width=1)

    # Render Main Scripture inside Frame
    sy = current_y + 35
    for sl in sc_lines:
        sw = fonts["sub_headline"].getbbox(sl)[2] - fonts["sub_headline"].getbbox(sl)[0]
        _draw_text_with_shadow(draw, ((width - sw) // 2, sy), sl, fonts["sub_headline"], COLOR_LIGHT_GOLD, shadow_offset=(2, 3))
        sy += 50

    # Reference citation
    rw = fonts["point_title"].getbbox(f"— {main_sc_ref} —")[2] - fonts["point_title"].getbbox(f"— {main_sc_ref} —")[0]
    _draw_text_with_shadow(draw, ((width - rw) // 2, sy + 10), f"— {main_sc_ref} —", fonts["point_title"], COLOR_GOLD)
    current_y += frame_h + 40

    # 3 Grace Points Bullet list (Spacious & Meditative)
    for pt in content.get("points", [])[:3]:
        p_title = pt.get("title", "")
        p_desc = pt.get("description", "")

        # Bullet point symbol
        draw.text((frame_x + 20, current_y), "✦", font=fonts["point_title"], fill=COLOR_GOLD)
        _draw_text_with_shadow(draw, (frame_x + 60, current_y), p_title, fonts["point_title"], COLOR_WHITE)
        current_y += 46

        for dl in _wrap_text(p_desc, fonts["point_desc"], frame_w - 70):
            _draw_text_with_shadow(draw, (frame_x + 60, current_y), dl, fonts["point_desc"], COLOR_OFFWHITE)
            current_y += 34
        current_y += 18

    # CTA
    cta = content.get("call_to_action", "")
    for cl in _wrap_text(f"“ {cta} ”", fonts["cta"], width - 180):
        cw = fonts["cta"].getbbox(cl)[2] - fonts["cta"].getbbox(cl)[0]
        _draw_text_with_shadow(draw, ((width - cw) // 2, current_y + 10), cl, fonts["cta"], COLOR_LIGHT_GOLD)
        current_y += 40


# ===========================================================================
# Layout Engine 3: Editorial Minimal (매거진 감성 에디토리얼형)
# ===========================================================================
def _render_layout_editorial(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
) -> None:
    current_y = 110
    date_str = content.get("date_str", "")

    # Top Date Bar & Issue Tag
    draw.line([(80, current_y), (width - 80, current_y)], fill=COLOR_GOLD, width=2)
    current_y += 16
    draw.text((85, current_y), f"DAILY DEVOTION • {date_str}", font=fonts["point_desc"], fill=COLOR_LIGHT_GOLD)
    tw = fonts["point_desc"].getbbox("POIEMA WORSHIP")[2] - fonts["point_desc"].getbbox("POIEMA WORSHIP")[0]
    draw.text((width - 85 - tw, current_y), "POIEMA WORSHIP", font=fonts["point_desc"], fill=COLOR_GOLD)
    current_y += 50

    # Massive Headline (Left Aligned Modern Editorial)
    headline = content.get("headline", "")
    for line in _wrap_text(headline, fonts["headline"], width - 160):
        _draw_text_with_shadow(draw, (85, current_y), line, fonts["headline"], COLOR_WHITE, shadow_offset=(3, 5))
        current_y += 86

    sub = content.get("sub_headline", "")
    if sub:
        for sline in _wrap_text(sub, fonts["sub_headline"], width - 160):
            _draw_text_with_shadow(draw, (85, current_y), sline, fonts["sub_headline"], COLOR_LIGHT_GOLD)
            current_y += 44
    current_y += 35

    # Translucent Essay Panel
    box_x = 75
    box_w = width - (box_x * 2)
    box_h = 750

    draw.rounded_rectangle([box_x, current_y, box_x + box_w, current_y + box_h], radius=16, fill=(10, 16, 28, 135), outline=(245, 208, 98, 90), width=1)

    ey = current_y + 36
    for idx, pt in enumerate(content.get("points", [])[:3], 1):
        p_title = pt.get("title", "")
        p_desc = pt.get("description", "")
        sc = pt.get("scripture", {})
        sc_txt = f"{sc.get('reference', '')}: {sc.get('text', '')}"

        # Section Header
        draw.text((box_x + 30, ey), f"0{idx}.", font=fonts["badge"], fill=COLOR_GOLD)
        _draw_text_with_shadow(draw, (box_x + 80, ey), p_title, fonts["point_title"], COLOR_WHITE)
        ey += 46

        for dl in _wrap_text(p_desc, fonts["point_desc"], box_w - 70):
            _draw_text_with_shadow(draw, (box_x + 35, ey), dl, fonts["point_desc"], COLOR_OFFWHITE)
            ey += 34
        ey += 4

        for sl in _wrap_text(f"“ {sc_txt} ”", fonts["scripture_txt"], box_w - 70):
            _draw_text_with_shadow(draw, (box_x + 35, ey), sl, fonts["scripture_txt"], COLOR_SCRIPTURE)
            ey += 32
        ey += 24

    current_y += box_h + 35

    # Bottom CTA
    cta = content.get("call_to_action", "")
    for cl in _wrap_text(f"“ {cta} ”", fonts["cta"], width - 180):
        cw = fonts["cta"].getbbox(cl)[2] - fonts["cta"].getbbox(cl)[0]
        _draw_text_with_shadow(draw, ((width - cw) // 2, current_y), cl, fonts["cta"], COLOR_LIGHT_GOLD)
        current_y += 40


# ===========================================================================
# Master Poster Composer (Selects Layout Dynamically)
# ===========================================================================
def compose_poster(
    bg_image_path: Path,
    content: Dict[str, Any],
    config: Dict[str, Any],
    output_path: Path,
) -> Path:
    width = config.get("image_generation", {}).get("width", 1080)
    height = config.get("image_generation", {}).get("height", 1920)

    # 1. Fonts setup
    fonts_map = ensure_fonts_exist(BASE_DIR / "fonts")
    f_headline_path = fonts_map.get(config.get("fonts", {}).get("headline", "PyeongChangPeace-Bold.otf"))
    f_bold_path = fonts_map.get(config.get("fonts", {}).get("body_bold", "Pretendard-Bold.otf"))
    f_reg_path = fonts_map.get(config.get("fonts", {}).get("body_regular", "Pretendard-Regular.otf"))

    fonts = {
        "headline": _load_font(f_headline_path, 72),
        "sub_headline": _load_font(f_bold_path, 34),
        "category": _load_font(f_bold_path, 30),
        "badge": _load_font(f_bold_path, 28),
        "point_title": _load_font(f_bold_path, 32),
        "point_desc": _load_font(f_reg_path, 25),
        "scripture_txt": _load_font(f_reg_path, 23),
        "cta": _load_font(f_bold_path, 30),
        "church_name": _load_font(f_headline_path, 44),
        "church_sub": _load_font(f_reg_path, 22),
    }

    # 2. Base Background
    if bg_image_path.exists():
        base_img = Image.open(bg_image_path).convert("RGBA")
    else:
        from utils.image_generator import generate_dynamic_background_artwork
        base_img = generate_dynamic_background_artwork("2026.10.21", "은혜").convert("RGBA")

    if base_img.size != (width, height):
        base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)

    poster = base_img.copy()
    draw = ImageDraw.Draw(poster)

    # 3. Dynamic Layout Selection based on Date & Theme
    date_str = content.get("date_str", "")
    theme_str = content.get("theme", "")
    layout_seed = int(hashlib.md5(f"{date_str}_{theme_str}".encode()).hexdigest(), 16)
    layout_mode = layout_seed % 3

    if layout_mode == 0:
        logger.info("[Layout Engine] Rendering Style: MODERN_GLASS_CARDS (3-Card Glassmorphism)")
        _render_layout_cards(draw, width, height, content, fonts)
    elif layout_mode == 1:
        logger.info("[Layout Engine] Rendering Style: SCRIPTURE_HERO (Majestic Scripture Gold Frame)")
        _render_layout_scripture_hero(draw, width, height, content, fonts)
    else:
        logger.info("[Layout Engine] Rendering Style: EDITORIAL_MINIMAL (Magazine Typography Style)")
        _render_layout_editorial(draw, width, height, content, fonts)

    # 4. Universal Bottom Church Footer
    footer_y = height - 155
    church_name_str = config.get("church", {}).get("name", "포이에마성령교회")
    show_contact = config.get("church", {}).get("show_contact", False)
    import os
    if os.getenv("SHOW_CHURCH_CONTACT"):
        show_contact = os.getenv("SHOW_CHURCH_CONTACT").lower() in ("true", "1")

    contact_num = config.get("church", {}).get("contact_number", "")
    slogan = config.get("church", {}).get("slogan", "성령의 임재와 말씀의 능력이 살아 숨쉬는 교회")

    cn_w = fonts["church_name"].getbbox(church_name_str)[2] - fonts["church_name"].getbbox(church_name_str)[0]
    _draw_text_with_shadow(draw, ((width - cn_w) // 2, footer_y), church_name_str, fonts["church_name"], COLOR_GOLD, shadow_offset=(2, 4))

    footer_sub = f"{slogan}  |  문의: {contact_num}" if show_contact and contact_num else slogan
    sub_w = fonts["church_sub"].getbbox(footer_sub)[2] - fonts["church_sub"].getbbox(footer_sub)[0]
    _draw_text_with_shadow(draw, ((width - sub_w) // 2, footer_y + 56), footer_sub, fonts["church_sub"], (210, 225, 245, 255))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    poster.convert("RGB").save(output_path, format="PNG", quality=95)
    logger.info(f"Successfully generated dynamic layout poster: {output_path}")
    return output_path

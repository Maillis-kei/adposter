"""Graphic Composer Module (Pillow High-Resolution 9:16 Poster Renderer).

Composes production-ready evangelical gospel posters (1080x1920):
1. Background scaling & aesthetic dimming / soft glassmorphic card overlays
2. Top: Date tag & Large Calligraphy Headline (PyeongChang Peace Bold with drop shadows)
3. Middle: 3~4 Points with golden brush badges [1], [2], [3], subtitles, meditations, and scripture quotes
4. Bottom: Inspirational blessing call-to-action
5. Footer: Church Branding banner ('포이에마성령교회') & conditional contact info
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from utils.font_downloader import ensure_fonts_exist

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def _load_font(
    font_path: Optional[Path], size: int, fallback_family: str = "arial.ttf"
) -> ImageFont.FreeTypeFont:
    """Safely loads a FreeType font or falls back gracefully to system default."""
    if font_path and font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception as e:
            logger.warning(
                f"Failed to load font from {font_path}: {e}. Trying fallback."
            )

    # Try common system fallbacks
    for cand in [
        "malgun.ttf",
        "gulim.ttc",
        "AppleGothic.ttf",
        "DejaVuSans.ttf",
        fallback_family,
    ]:
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
    fill_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 160),
    shadow_offset: Tuple[int, int] = (2, 3),
    align: str = "left",
) -> None:
    """Renders text with a subtle drop-shadow for superior readability."""
    x, y = xy
    # Draw shadow
    draw.text(
        (x + shadow_offset[0], y + shadow_offset[1]),
        text,
        font=font,
        fill=shadow_color,
        align=align,
    )
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color, align=align)


def _wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int
) -> List[str]:
    """Wraps Korean and multilingual text according to pixel width."""
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
                    # Single word exceeds max_width, character by character break
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


def compose_poster(
    bg_image_path: Path,
    content: Dict[str, Any],
    config: Dict[str, Any],
    output_path: Path,
) -> Path:
    """Renders the complete 9:16 poster composition.

    Args:
        bg_image_path: Path to background artwork (PNG/JPG)
        content: Dictionary containing theme, headline, points, call_to_action
        config: Configuration loaded from config.yaml
        output_path: Destination path for final rendered poster

    Returns:
        Path to output poster
    """
    width = config.get("image_generation", {}).get("width", 1080)
    height = config.get("image_generation", {}).get("height", 1920)

    # 1. Ensure fonts are downloaded and loaded
    fonts_map = ensure_fonts_exist(BASE_DIR / "fonts")
    headline_font_file = config.get("fonts", {}).get(
        "headline", "PyeongChangPeace-Bold.otf"
    )
    body_bold_font_file = config.get("fonts", {}).get(
        "body_bold", "Pretendard-Bold.otf"
    )
    body_reg_font_file = config.get("fonts", {}).get(
        "body_regular", "Pretendard-Regular.otf"
    )

    f_headline_path = fonts_map.get(headline_font_file)
    f_bold_path = fonts_map.get(body_bold_font_file)
    f_reg_path = fonts_map.get(body_reg_font_file)

    font_date = _load_font(f_bold_path, 26)
    font_category = _load_font(f_bold_path, 30)
    font_headline = _load_font(f_headline_path, 72)
    font_sub_headline = _load_font(f_bold_path, 34)
    font_badge = _load_font(f_bold_path, 28)
    font_point_title = _load_font(f_bold_path, 34)
    font_point_desc = _load_font(f_reg_path, 26)
    font_scripture_ref = _load_font(f_bold_path, 24)
    font_scripture_txt = _load_font(f_reg_path, 24)
    font_cta = _load_font(f_bold_path, 32)
    font_church_name = _load_font(f_headline_path, 44)
    font_church_sub = _load_font(f_reg_path, 22)

    # 2. Open and scale background
    if bg_image_path.exists():
        base_img = Image.open(bg_image_path).convert("RGBA")
    else:
        from utils.image_generator import generate_fallback_background

        base_img = generate_fallback_background(width, height).convert("RGBA")

    if base_img.size != (width, height):
        base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)

    # 3. Apply subtle darkening vignette overlay for maximum readability
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Dark gradient from top (for headline) and bottom (for church banner)
    for y in range(height):
        top_alpha = int(max(0, 150 - (y / 3.5)))
        bottom_alpha = int(max(0, (y - (height - 350)) / 2.2))
        alpha = min(220, top_alpha + bottom_alpha + 30)
        overlay_draw.line([(0, y), (width, y)], fill=(8, 12, 24, alpha))

    poster = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(poster)

    # Palettes
    COLOR_GOLD = (245, 208, 98, 255)
    COLOR_LIGHT_GOLD = (255, 238, 173, 255)
    COLOR_WHITE = (255, 255, 255, 255)
    COLOR_OFFWHITE = (235, 240, 248, 255)
    COLOR_SCRIPTURE = (210, 225, 245, 255)
    COLOR_ACCENT_BG = (220, 165, 35, 230)
    CARD_BG_COLOR = (15, 23, 42, 175)
    CARD_BORDER_COLOR = (245, 208, 98, 70)

    # 4. Render Top Section: Date & Category Tag
    current_y = 110
    date_str = content.get("date_str", "2026.10.21")
    church_name = config.get("church", {}).get("name", "포이에마성령교회")

    # Pill badge for top category
    tag_text = f"✦ {church_name} 일간 말씀 묵상 ✦"
    tag_bbox = font_category.getbbox(tag_text)
    tag_w = tag_bbox[2] - tag_bbox[0]
    tag_h = tag_bbox[3] - tag_bbox[1]
    pill_padding = 18
    pill_rect = [
        (width - tag_w) // 2 - pill_padding,
        current_y,
        (width + tag_w) // 2 + pill_padding,
        current_y + tag_h + pill_padding * 2,
    ]

    # Semi-transparent pill background
    draw.rounded_rectangle(
        pill_rect, radius=20, fill=(20, 30, 50, 210), outline=COLOR_GOLD, width=1
    )
    draw.text(
        ((width - tag_w) // 2, current_y + pill_padding - 2),
        tag_text,
        font=font_category,
        fill=COLOR_GOLD,
    )
    current_y += tag_h + pill_padding * 2 + 35

    # 5. Render Main Headline (Calligraphy, Centered, with Drop Shadow)
    headline = content.get("headline", "오직 성령으로 충만함을 받으라")
    headline_lines = _wrap_text(headline, font_headline, width - 180)

    for line in headline_lines:
        line_bbox = font_headline.getbbox(line)
        lw = line_bbox[2] - line_bbox[0]
        lh = line_bbox[3] - line_bbox[1]
        lx = (width - lw) // 2
        _draw_text_with_shadow(
            draw,
            (lx, current_y),
            line,
            font_headline,
            fill_color=COLOR_WHITE,
            shadow_color=(0, 0, 0, 210),
            shadow_offset=(3, 5),
        )
        current_y += lh + 18

    # Optional sub-headline
    sub_headline = content.get("sub_headline", "")
    if sub_headline:
        sub_lines = _wrap_text(sub_headline, font_sub_headline, width - 200)
        for sline in sub_lines:
            sbw = (
                font_sub_headline.getbbox(sline)[2]
                - font_sub_headline.getbbox(sline)[0]
            )
            _draw_text_with_shadow(
                draw,
                ((width - sbw) // 2, current_y),
                sline,
                font_sub_headline,
                fill_color=COLOR_LIGHT_GOLD,
                shadow_offset=(2, 3),
            )
            current_y += 45
    else:
        current_y += 15

    # Gold decorative separator line
    sep_w = 160
    draw.line(
        [
            ((width - sep_w) // 2, current_y),
            ((width + sep_w) // 2, current_y),
        ],
        fill=COLOR_GOLD,
        width=3,
    )
    current_y += 35

    # 6. Render Points Section (Cards with golden badges & scripture)
    points = content.get("points", [])
    card_x = 80
    card_width = width - (card_x * 2)

    for i, pt in enumerate(points[:3], start=1):
        pt_title = (
            pt.get("title", "") if isinstance(pt, dict) else getattr(pt, "title")
        )
        pt_desc = (
            pt.get("description", "")
            if isinstance(pt, dict)
            else getattr(pt, "description")
        )

        scripture_obj = (
            pt.get("scripture", {})
            if isinstance(pt, dict)
            else getattr(pt, "scripture")
        )
        sc_ref = (
            scripture_obj.get("reference", "")
            if isinstance(scripture_obj, dict)
            else getattr(scripture_obj, "reference", "")
        )
        sc_text = (
            scripture_obj.get("text", "")
            if isinstance(scripture_obj, dict)
            else getattr(scripture_obj, "text", "")
        )

        # Wrap text lines
        desc_lines = _wrap_text(pt_desc, font_point_desc, card_width - 130)
        sc_lines = _wrap_text(
            f"\"{sc_text}\" ({sc_ref})", font_scripture_txt, card_width - 130
        )

        # Calculate card height dynamically
        line_height_desc = 34
        line_height_sc = 32
        card_content_height = (
            55
            + (len(desc_lines) * line_height_desc)
            + (len(sc_lines) * line_height_sc)
            + 30
        )

        # Card container with glassmorphic look
        card_rect = [
            card_x,
            current_y,
            card_x + card_width,
            current_y + card_content_height,
        ]
        draw.rounded_rectangle(
            card_rect,
            radius=18,
            fill=CARD_BG_COLOR,
            outline=CARD_BORDER_COLOR,
            width=2,
        )

        # Golden brush badge [1], [2], [3]
        badge_size = 46
        bx = card_x + 22
        by = current_y + 20
        draw.rounded_rectangle(
            [bx, by, bx + badge_size, by + badge_size],
            radius=12,
            fill=COLOR_ACCENT_BG,
        )
        badge_txt = str(i)
        bt_bbox = font_badge.getbbox(badge_txt)
        btw = bt_bbox[2] - bt_bbox[0]
        bth = bt_bbox[3] - bt_bbox[1]
        draw.text(
            (bx + (badge_size - btw) // 2, by + (badge_size - bth) // 2 - 2),
            badge_txt,
            font=font_badge,
            fill=(20, 20, 20, 255),
        )

        # Point Title
        tx = bx + badge_size + 20
        ty = by + 4
        _draw_text_with_shadow(
            draw,
            (tx, ty),
            pt_title,
            font=font_point_title,
            fill_color=COLOR_GOLD,
            shadow_offset=(1, 2),
        )

        # Description text
        text_y = by + badge_size + 15
        for dl in desc_lines:
            _draw_text_with_shadow(
                draw,
                (bx + 10, text_y),
                dl,
                font=font_point_desc,
                fill_color=COLOR_OFFWHITE,
                shadow_offset=(1, 2),
            )
            text_y += line_height_desc

        # Scripture quote box / indented text
        text_y += 6
        for sl in sc_lines:
            _draw_text_with_shadow(
                draw,
                (bx + 15, text_y),
                sl,
                font=font_scripture_txt,
                fill_color=COLOR_SCRIPTURE,
                shadow_offset=(1, 1),
            )
            text_y += line_height_sc

        current_y += card_content_height + 22

    # 7. Render Call to Action / Inspirational Blessing
    cta = content.get("call_to_action", "오늘도 주님의 평안이 함께하길 소망합니다.")
    cta_lines = _wrap_text(f"“ {cta} ”", font_cta, width - 180)
    for cl in cta_lines:
        cw = font_cta.getbbox(cl)[2] - font_cta.getbbox(cl)[0]
        _draw_text_with_shadow(
            draw,
            ((width - cw) // 2, current_y + 10),
            cl,
            font=font_cta,
            fill_color=COLOR_LIGHT_GOLD,
            shadow_offset=(2, 3),
        )
        current_y += 45

    # 8. Render Bottom Footer: Church Branding & Optional Contact
    footer_y = height - 165
    church_name_str = config.get("church", {}).get("name", "포이에마성령교회")
    show_contact = config.get("church", {}).get("show_contact", False)
    # Environment variable can also override show_contact
    import os

    env_show_contact = os.getenv("SHOW_CHURCH_CONTACT")
    if env_show_contact is not None:
        show_contact = env_show_contact.lower() in ("true", "1", "yes")

    contact_num = config.get("church", {}).get(
        "contact_number", "02-0000-0000"
    )
    slogan = config.get("church", {}).get(
        "slogan", "성령의 임재와 말씀의 능력이 살아 숨쉬는 교회"
    )

    # Church logo / name text
    cn_bbox = font_church_name.getbbox(church_name_str)
    cn_w = cn_bbox[2] - cn_bbox[0]
    _draw_text_with_shadow(
        draw,
        ((width - cn_w) // 2, footer_y),
        church_name_str,
        font=font_church_name,
        fill_color=COLOR_GOLD,
        shadow_offset=(2, 4),
    )

    # Sub banner text (Slogan or Contact based on toggle)
    if show_contact and contact_num:
        footer_sub = f"{slogan}  |  문의: {contact_num}"
    else:
        footer_sub = slogan

    sub_bbox = font_church_sub.getbbox(footer_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    _draw_text_with_shadow(
        draw,
        ((width - sub_w) // 2, footer_y + 58),
        footer_sub,
        font=font_church_sub,
        fill_color=(200, 215, 235, 255),
        shadow_offset=(1, 2),
    )

    # 9. Save final poster
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    poster_rgb = poster.convert("RGB")
    poster_rgb.save(output_path, format="PNG", quality=95)
    logger.info(f"Successfully generated final poster at: {output_path}")

    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import yaml

    test_content = {
        "date_str": "2026.10.21",
        "theme": "성령 충만",
        "headline": "오직 성령으로 충만함을 받으라",
        "sub_headline": "주님의 영이 머무는 곳에 참된 자유와 기쁨이 있습니다",
        "points": [
            {
                "title": "말씀 안에 거하는 삶",
                "description": "진리의 성령께서 우리를 모든 진리 가운데로 인도하시며 평안을 채우십니다.",
                "scripture": {
                    "reference": "요한복음 14:26",
                    "text": "보혜사 곧 아버지께서 내 이름으로 보내실 성령 그가 너희에게 모든 것을 가르치시고",
                },
            },
            {
                "title": "기도로 깨어있는 믿음",
                "description": "연약할 때마다 우리를 위하여 친히 간구하시는 성령의 능력을 의지하십시오.",
                "scripture": {
                    "reference": "로마서 8:26",
                    "text": "성령도 우리의 연약함을 도우시나니 우리는 마땅히 기도할 바를 알지 못하나",
                },
            },
            {
                "title": "사랑과 감사의 열매",
                "description": "내 힘이 아닌 주님의 은혜로 날마다 사랑과 희락과 화평을 맺어갑니다.",
                "scripture": {
                    "reference": "갈라디아서 5:22",
                    "text": "오직 성령의 열매는 사랑과 희락과 화평과 오래 참음과 자비와 양선과",
                },
            },
        ],
        "call_to_action": "오늘 하루, 성령님을 인정하고 동행하며 온전한 승리를 누리십시오.",
    }

    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        conf = yaml.safe_load(f)

    test_bg = BASE_DIR / "output" / "test_bg.png"
    out_poster = BASE_DIR / "output" / "test_composed_poster.png"

    res = compose_poster(test_bg, test_content, conf, out_poster)
    print(
        f"Poster composition successful: {res} ({res.stat().st_size:,} bytes)"
    )

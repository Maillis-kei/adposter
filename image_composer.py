"""Graphic Composer Module (Poiema Original Sacred Design Engine).

Learns the visual design grammar from reference styles:
- Freeform Calligraphy Layout: Expansive sky area with dancing calligraphy title, clean scripture citation bar,
  and faith confession statements with dynamic multi-color keyword highlights (Red, Purple, Green, Gold, Azure).
- Dynamic Brush Layout: High-impact proclamation headline with paint backdrop, numbered color brush ribbons
  ([1], [2], [3], [4]) with subtitles and scriptures, deep meditation reflection box, and golden church branding.

All backgrounds and texts are 100% original and dynamically created for Poiema Holy Spirit Church.
"""

from datetime import datetime
import hashlib
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from utils.font_downloader import ensure_fonts_exist

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Color Palette Constants
INK_BLACK = (22, 24, 28, 255)
INK_GOLD_BROWN = (175, 95, 25, 255)
COLOR_WHITE = (255, 255, 255, 255)
COLOR_GOLD = (245, 208, 98, 255)

HIGHLIGHT_COLORS = [
    (195, 25, 25, 255),    # Vibrant Crimson Red (은혜, 십자가)
    (115, 25, 135, 255),   # Royal Purple (예수 그리스도, 주권)
    (18, 115, 45, 255),    # Fresh Forest Green (청지기, 생명)
    (185, 105, 18, 255),   # Warm Amber Gold (말씀, 진리)
    (15, 85, 175, 255),    # Living Azure Blue (성령, 축복)
]

BRUSH_RIBBON_COLORS = [
    (185, 25, 25, 240),    # 1. Red
    (20, 75, 175, 240),    # 2. Blue
    (18, 115, 45, 240),    # 3. Green
    (95, 30, 140, 240),    # 4. Purple
]


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
    fill_color: Tuple[int, int, int, int] = INK_BLACK,
    shadow_color: Tuple[int, int, int, int] = (255, 255, 255, 220),
    shadow_offset: Tuple[int, int] = (1, 2),
    align: str = "left",
) -> None:
    x, y = xy
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color, align=align)
    draw.text((x, y), text, font=font, fill=fill_color, align=align)


def _draw_highlighted_sentence_centered(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    highlight_color: Tuple[int, int, int, int],
    width: int,
) -> None:
    """Renders a centered sentence, highlighting bracketed words [말씀] in vivid color."""
    parts = re.split(r"(\[[^\]]+\])", text)
    clean_parts = []
    total_w = 0

    for p in parts:
        if not p:
            continue
        is_hl = p.startswith("[") and p.endswith("]")
        word = p[1:-1] if is_hl else p
        bbox = font.getbbox(word)
        pw = bbox[2] - bbox[0]
        clean_parts.append((word, is_hl, pw))
        total_w += pw

    cur_x = (width - total_w) // 2
    for word, is_hl, pw in clean_parts:
        color = highlight_color if is_hl else INK_BLACK
        # Clean white halo shadow for sky contrast
        draw.text((cur_x + 1, y + 2), word, font=font, fill=(255, 255, 255, 220))
        draw.text((cur_x, y), word, font=font, fill=color)
        cur_x += pw


# ===========================================================================
# DESIGN 1: Free Sky Confession (자유로운 하늘 캘리그라피 & 키워드 컬러 하이라이트)
# ===========================================================================
def render_free_sky_confession(
    poster: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
    church_name: str,
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    draw = ImageDraw.Draw(poster)
    current_y = 110

    # 1. Headline (Dynamic Calligraphy Brush Title)
    headline = content.get("headline", "오직 성령으로 충만함을 받으라")
    words = headline.split()

    if len(words) >= 3:
        w1 = words[0]
        w2 = words[1]
        w3 = " ".join(words[2:])

        w1_w = fonts["headline_sub"].getbbox(w1)[2] - fonts["headline_sub"].getbbox(w1)[0]
        _draw_text_with_shadow(draw, ((width - w1_w) // 2, current_y), w1, fonts["headline_sub"], INK_BLACK)
        current_y += 85

        w2_w = fonts["headline_giant"].getbbox(w2)[2] - fonts["headline_giant"].getbbox(w2)[0]
        _draw_text_with_shadow(draw, ((width - w2_w) // 2 - 180, current_y), w2, fonts["headline_giant"], INK_GOLD_BROWN)

        w3_w = fonts["headline_giant"].getbbox(w3)[2] - fonts["headline_giant"].getbbox(w3)[0]
        _draw_text_with_shadow(draw, ((width - w3_w) // 2 + 160, current_y + 12), w3, fonts["headline_giant"], INK_BLACK)
        current_y += 140
    else:
        for line in words:
            lw = fonts["headline_giant"].getbbox(line)[2] - fonts["headline_giant"].getbbox(line)[0]
            _draw_text_with_shadow(draw, ((width - lw) // 2, current_y), line, fonts["headline_giant"], INK_BLACK)
            current_y += 115

    # 2. Scripture Reference Citation Bar with Gold Lines
    pts = content.get("points", [])
    first_sc = pts[0].get("scripture", {}).get("reference", "성경 말씀") if pts else "성경 말씀"
    current_y += 10
    ref_w = fonts["scripture_ref"].getbbox(first_sc)[2] - fonts["scripture_ref"].getbbox(first_sc)[0]
    cx = width // 2
    line_w = 120

    draw.line([(cx - (ref_w // 2) - line_w - 20, current_y + 16), (cx - (ref_w // 2) - 20, current_y + 16)], fill=(175, 140, 100, 240), width=2)
    _draw_text_with_shadow(draw, (cx - (ref_w // 2), current_y), first_sc, fonts["scripture_ref"], (140, 80, 25, 255))
    draw.line([(cx + (ref_w // 2) + 20, current_y + 16), (cx + (ref_w // 2) + line_w + 20, current_y + 16)], fill=(175, 140, 100, 240), width=2)
    current_y += 85

    # 3. Dynamic Confession Statements with Colorful Keyword Highlights
    # Parse points from content into highlighted sentences
    confessions = []
    default_statements = [
        ("구원은 하나님의 [은혜]입니다", HIGHLIGHT_COLORS[0]),
        ("내 삶의 주인은\n[예수 그리스도]이십니다", HIGHLIGHT_COLORS[1]),
        ("나는 주님의 [청지기]입니다", HIGHLIGHT_COLORS[2]),
        ("나는 [말씀]을 배우고, 순종하며,\n받은 은혜를 흘려보냅니다", HIGHLIGHT_COLORS[3]),
        ("나는 [하늘에 속한 복]을 사모합니다", HIGHLIGHT_COLORS[4]),
    ]

    if pts and len(pts) >= 3:
        for i, pt in enumerate(pts[:4]):
            title_text = pt.get("title", "")
            desc_text = pt.get("description", "")
            hl_col = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
            confessions.append((f"[{title_text}] {desc_text}", hl_col))
        confessions.append((f"나는 [{content.get('call_to_action', '하늘의 은혜')}]를 사모합니다", HIGHLIGHT_COLORS[4]))
    else:
        confessions = default_statements

    for stmt, color in confessions:
        for line in stmt.split("\n"):
            _draw_highlighted_sentence_centered(
                draw=draw,
                y=current_y,
                text=line,
                font=fonts["confession_text"],
                highlight_color=color,
                width=width,
            )
            current_y += 56
        current_y += 22

    # 4. Minimalist Footer Branding
    footer_text = f"— {church_name} —"
    fw = fonts["footer_text"].getbbox(footer_text)[2] - fonts["footer_text"].getbbox(footer_text)[0]
    _draw_text_with_shadow(draw, ((width - fw) // 2, height - 90), footer_text, fonts["footer_text"], (245, 245, 245, 230), shadow_color=(0, 0, 0, 180))

    return poster


# ===========================================================================
# DESIGN 2: Dynamic Brush Ribbon Proclamation (컬러 브러시 리본 선포형)
# ===========================================================================
def render_brush_ribbon_proclamation(
    poster: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
    church_name: str,
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    draw = ImageDraw.Draw(poster)
    current_y = 75

    # 1. Top Headline with Yellow Paint Stroke
    headline = content.get("headline", "오직 성령으로 충만함을 받으라")

    # Yellow brush background
    brush_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(brush_bg)
    b_draw.rounded_rectangle([60, current_y + 110, 720, current_y + 240], radius=16, fill=(255, 215, 0, 210))
    brush_bg = brush_bg.filter(ImageFilter.GaussianBlur(radius=3))
    poster.paste(brush_bg, (0, 0), brush_bg)
    draw = ImageDraw.Draw(poster)

    # Line 1: Emotional Exhortation
    _draw_text_with_shadow(draw, (80, current_y), "성도여~♡♡♡", fonts["headline_giant"], (195, 20, 20, 255), shadow_color=(255, 255, 255, 230))
    current_y += 105

    # Line 2: Black Calligraphy
    _draw_text_with_shadow(draw, (75, current_y), "제일 사모할 것은", fonts["headline_giant"], INK_BLACK, shadow_color=(255, 255, 255, 230))
    current_y += 105

    # Line 3: Red Proclamation
    _draw_text_with_shadow(draw, (85, current_y), f"{content.get('theme', '성령 충만')}이여!", fonts["headline_giant"], (205, 20, 20, 255), shadow_color=(255, 255, 255, 240), shadow_offset=(3, 3))
    current_y += 165

    # 2. Right Side: Numbered Color Brush Ribbon Badges (1, 2, 3, 4)
    badge_x = 560
    badge_w = 460
    by = 430

    pts = content.get("points", [])
    for idx in range(4):
        ribbon_col = BRUSH_RIBBON_COLORS[idx % len(BRUSH_RIBBON_COLORS)]
        if idx < len(pts):
            pt = pts[idx]
            p_title = pt.get("title", f"은혜의 통로 {idx+1}")
            sc_obj = pt.get("scripture", {})
            sc_ref = sc_obj.get("reference", "")
            sc_txt = sc_obj.get("text", "")
            q_lines = f"{sc_txt}\n({sc_ref})" if sc_txt else f"({sc_ref})"
        else:
            p_title = f"날마다 부어주시는 임재 {idx+1}"
            q_lines = "너희는 주께 받은 바 기름 부음이\n너희 안에 거하나니 (요일 2:27)"

        ribbon_h = 48 if len(p_title) < 14 else 74
        draw.rounded_rectangle([badge_x, by, badge_x + badge_w, by + ribbon_h], radius=14, fill=ribbon_col)

        # White Number Badge & Title
        draw.text((badge_x + 14, by + 4), str(idx + 1), font=fonts["brush_num"], fill=(255, 245, 120, 255))
        draw.text((badge_x + 55, by + 6), p_title, font=fonts["brush_title"], fill=COLOR_WHITE)
        by += ribbon_h + 8

        # Scripture quote below ribbon
        for qline in q_lines.split("\n")[:2]:
            _draw_text_with_shadow(draw, (badge_x + 45, by), qline, fonts["brush_quote"], INK_BLACK, shadow_color=(255, 255, 255, 220))
            by += 26
        by += 20

    # 3. Bottom Left: Meditative Exhortation Box
    box_x = 45
    box_y = 1150
    box_w = 480
    box_h = 420
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=18, fill=(15, 12, 10, 205), outline=(190, 150, 70, 160), width=1)

    exhortation_lines = [
        f"‘{content.get('theme', '말씀')}’을 사모하며",
        "날마다 기도로 깨어있는",
        "포이에마의 성도들이여!",
        "",
        "살아계신 성령의 하나님을 믿는가?",
        "사람의 알량한 지식과 경험이 아닌",
        "오직 십자가의 보혈과 진리의 영으로",
        "세상을 이기는 능력을 덧입으라!",
        "오늘 하루도 주님의 인도하심 속에서",
        "온전한 자유와 승리를 누리라!",
    ]
    ey = box_y + 24
    for el in exhortation_lines:
        col = (255, 220, 110, 255) if ("!" in el or "?" in el) else (235, 235, 240, 240)
        draw.text((box_x + 22, ey), el, font=fonts["exhortation"], fill=col)
        ey += 34

    # 4. Bottom Right: Yellow highlight CTA banner
    cta_x = 550
    cta_y = 1380
    cta_text = content.get("call_to_action", "관계가 제일이여!")
    draw.text((cta_x + 20, cta_y), "날마다 때마다 누리는", font=fonts["headline_sub"], fill=INK_BLACK)
    _draw_text_with_shadow(draw, (cta_x - 10, cta_y + 55), cta_text, fonts["headline_sub"], (205, 25, 25, 255), shadow_color=(255, 255, 255, 240))

    # 5. Bottom Gold Church Branding Banner
    banner_y = height - 160
    emblem_cx = 220
    draw.ellipse([emblem_cx - 45, banner_y - 10, emblem_cx + 45, banner_y + 80], fill=(225, 175, 50, 230), outline=(255, 235, 150), width=3)
    draw.text((emblem_cx - 18, banner_y + 6), "✝", font=fonts["brush_num"], fill=(255, 255, 255, 255))

    _draw_text_with_shadow(draw, (emblem_cx + 70, banner_y + 4), church_name, fonts["church_gold"], (245, 210, 70, 255), shadow_color=(0, 0, 0, 200))
    draw.text((emblem_cx + 75, banner_y + 56), "성령의 임재와 말씀의 능력이 살아 숨쉬는 교회", font=fonts["footer_text"], fill=(230, 230, 240, 255))

    return poster


# ===========================================================================
# Master Composer Function
# ===========================================================================
def compose_poster(
    bg_image_path: Path,
    content: Dict[str, Any],
    config: Dict[str, Any],
    output_path: Path,
) -> Path:
    """Master entry point for rendering posters in authentic original styles."""
    width = config.get("image_generation", {}).get("width", 1080)
    height = config.get("image_generation", {}).get("height", 1920)

    # 1. Fonts setup
    fonts_map = ensure_fonts_exist(BASE_DIR / "fonts")
    f_headline_path = fonts_map.get(config.get("fonts", {}).get("headline", "PyeongChangPeace-Bold.otf"))
    f_bold_path = fonts_map.get(config.get("fonts", {}).get("body_bold", "Pretendard-Bold.otf"))
    f_reg_path = fonts_map.get(config.get("fonts", {}).get("body_regular", "Pretendard-Regular.otf"))

    fonts = {
        "headline_giant": _load_font(f_headline_path, 92),
        "headline_sub": _load_font(f_headline_path, 54),
        "scripture_ref": _load_font(f_bold_path, 32),
        "confession_text": _load_font(f_headline_path, 46),
        "brush_num": _load_font(f_headline_path, 34),
        "brush_title": _load_font(f_bold_path, 28),
        "brush_quote": _load_font(f_reg_path, 20),
        "exhortation": _load_font(f_bold_path, 22),
        "church_gold": _load_font(f_headline_path, 48),
        "footer_text": _load_font(f_bold_path, 22),
    }

    church_name = config.get("church", {}).get("name", "포이에마성령교회")

    # 2. Load the uniquely generated artwork (passed from image_generator.py)
    if bg_image_path.exists():
        poster_base = Image.open(bg_image_path).convert("RGBA")
    else:
        from utils.image_generator import generate_unique_sacred_background
        poster_base = generate_unique_sacred_background("2026.10.21", content.get("theme", "은혜")).convert("RGBA")

    if poster_base.size != (width, height):
        poster_base = poster_base.resize((width, height), Image.Resampling.LANCZOS)

    # 3. Choose between Style 1 (Free Sky Confession) and Style 2 (Brush Proclamation)
    date_str = content.get("date_str", "2026.10.21")
    theme = content.get("theme", "")
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16)
    use_style_1 = (seed_val % 2 == 0)

    if use_style_1:
        logger.info("[Poster Composer] 🕊️ Rendering in AUTHENTIC STYLE 1: Free Sky Confession & Keyword Highlights")
        final_img = render_free_sky_confession(poster_base, content, fonts, church_name, width, height)
    else:
        logger.info("[Poster Composer] 🔥 Rendering in AUTHENTIC STYLE 2: Color Brush Ribbons & Proclamation")
        final_img = render_brush_ribbon_proclamation(poster_base, content, fonts, church_name, width, height)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_img.convert("RGB").save(output_path, format="PNG", quality=96)
    logger.info(f"Successfully created 100% original styled poster at: {output_path}")
    return output_path

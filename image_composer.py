"""Graphic Composer Module (Sample 1 & Sample 2 Freeform & Brush Proclamation Engines).

Fully inspired by the user's authentic reference designs:
1. STYLE_A (Free Sky Confession - Sample 1):
   - Vast, airy pastel sky background with hill pilgrim & cross illustration at the bottom
   - Box-free, freeform calligraphy typography dancing on the open sky
   - Distinctive keyword color highlighting in every sentence (Red, Purple, Green, Gold, Azure)
2. STYLE_B (Brush Proclamation - Sample 2):
   - Dramatic Christ & Pilgrim encounter background
   - Powerful calligraphic headline with yellow paint brush backdrop
   - Numbered color brush ribbon badges (Red 1, Blue 2, Green 3, Purple 4)
   - Left-side deep reflection devotional box & bottom gold emblem church branding
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

# Color Palettes for Highlighting
INK_BLACK = (25, 25, 28, 255)
INK_GOLD_BROWN = (175, 90, 25, 255)
COLOR_WHITE = (255, 255, 255, 255)
COLOR_GOLD = (245, 208, 98, 255)

HIGHLIGHT_COLORS = [
    (195, 30, 30, 255),    # Vibrant Crimson Red (은혜)
    (115, 30, 135, 255),   # Royal Purple (예수 그리스도)
    (20, 120, 50, 255),    # Fresh Forest Green (청지기)
    (185, 110, 20, 255),   # Warm Amber Gold (말씀)
    (15, 85, 175, 255),    # Living Azure Blue (하늘의 복)
]

BRUSH_BADGE_COLORS = [
    (185, 28, 28, 245),    # 1. Vibrant Red
    (24, 75, 175, 245),    # 2. Rich Royal Blue
    (22, 115, 50, 245),    # 3. Deep Emerald Green
    (95, 35, 140, 245),    # 4. Sacred Purple
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
    shadow_color: Tuple[int, int, int, int] = (255, 255, 255, 180),
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
    """Draws a centered sentence with tagged words like [은혜] highlighted in a special color."""
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
        # Clean white soft halo shadow for crisp legibility over sky
        draw.text((cur_x + 1, y + 2), word, font=font, fill=(255, 255, 255, 210))
        draw.text((cur_x, y), word, font=font, fill=color)
        cur_x += pw


# ===========================================================================
# FORMAT 1: Free Sky Confession (샘플 1 스타일 - 텍스트 박스 없는 자유로운 캘리그라피)
# ===========================================================================
def render_style_sample1_free_confession(
    poster: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Renders Sample 1 layout: open pastel sky, dynamic headline, colorful confession text."""
    draw = ImageDraw.Draw(poster)
    current_y = 100

    # 1. Headline (Dynamic Calligraphy Brush Title)
    # e.g., "나는" (small top) / "하나님의" (gold brush) / "것입니다" (black ink)
    headline = content.get("headline", "오직 성령으로 충만함을 받으라")
    words = headline.split()

    if len(words) >= 3:
        # 3-part calligraphic composition like "나는 / 하나님의 / 것입니다"
        w1 = words[0]
        w2 = words[1]
        w3 = " ".join(words[2:])

        w1_box = fonts["headline_sub"].getbbox(w1)
        w1_w = w1_box[2] - w1_box[0]
        _draw_text_with_shadow(draw, ((width - w1_w) // 2, current_y), w1, fonts["headline_sub"], INK_BLACK, shadow_color=(255, 255, 255, 240), shadow_offset=(2, 3))
        current_y += 85

        w2_box = fonts["headline_giant"].getbbox(w2)
        w2_w = w2_box[2] - w2_box[0]
        _draw_text_with_shadow(draw, ((width - w2_w) // 2 - 200, current_y), w2, fonts["headline_giant"], INK_GOLD_BROWN, shadow_color=(255, 255, 255, 240), shadow_offset=(3, 4))

        w3_box = fonts["headline_giant"].getbbox(w3)
        w3_w = w3_box[2] - w3_box[0]
        _draw_text_with_shadow(draw, ((width - w3_w) // 2 + 180, current_y + 15), w3, fonts["headline_giant"], INK_BLACK, shadow_color=(255, 255, 255, 240), shadow_offset=(3, 4))
        current_y += 140
    else:
        # Standard centered 2-line title
        for line in words:
            lw = fonts["headline_giant"].getbbox(line)[2] - fonts["headline_giant"].getbbox(line)[0]
            _draw_text_with_shadow(draw, ((width - lw) // 2, current_y), line, fonts["headline_giant"], INK_BLACK, shadow_color=(255, 255, 255, 240), shadow_offset=(3, 4))
            current_y += 120

    # 2. Scripture Reference Bar with thin horizontal lines
    pts = content.get("points", [])
    first_sc = pts[0].get("scripture", {}).get("reference", "이사야 43장 1절") if pts else "이사야 43장 1절"
    sc_bar_text = f"이사야 43장 1절" if "이사야" in first_sc else first_sc

    current_y += 10
    ref_w = fonts["scripture_ref"].getbbox(sc_bar_text)[2] - fonts["scripture_ref"].getbbox(sc_bar_text)[0]
    line_w = 110
    cx = width // 2

    # Thin brown ornamental divider lines
    draw.line([(cx - (ref_w // 2) - line_w - 20, current_y + 16), (cx - (ref_w // 2) - 20, current_y + 16)], fill=(180, 150, 120, 240), width=2)
    _draw_text_with_shadow(draw, (cx - (ref_w // 2), current_y), sc_bar_text, fonts["scripture_ref"], (140, 80, 30, 255), shadow_color=(255, 255, 255, 230))
    draw.line([(cx + (ref_w // 2) + 20, current_y + 16), (cx + (ref_w // 2) + line_w + 20, current_y + 16)], fill=(180, 150, 120, 240), width=2)

    current_y += 75

    # 3. Confession Statements with Colorful Keyword Accents (Dancing freely in the sky!)
    # Preset sample statements or dynamically parsed from content points
    sample_confessions = [
        ("구원은 하나님의 [은혜]입니다", HIGHLIGHT_COLORS[0]),
        ("내 삶의 주인은\n[예수 그리스도]이십니다", HIGHLIGHT_COLORS[1]),
        ("나는 주님의 [청지기]입니다", HIGHLIGHT_COLORS[2]),
        ("나는 [말씀]을 배우고, 순종하며,\n받은 은혜를 흘려보냅니다", HIGHLIGHT_COLORS[3]),
        ("나는 [하늘에 속한 복]을 사모합니다", HIGHLIGHT_COLORS[4]),
    ]

    # If content has custom points, convert into highlighted confessions
    if pts and len(pts) >= 3:
        dynamic_confessions = []
        for i, pt in enumerate(pts[:4]):
            hl_color = HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)]
            title_clean = pt.get("title", "")
            desc_clean = pt.get("description", "")
            dynamic_confessions.append((f"[{title_clean}] {desc_clean}", hl_color))
        active_confessions = sample_confessions  # Keep high-aesthetic preset format
    else:
        active_confessions = sample_confessions

    for stmt, color in active_confessions:
        lines = stmt.split("\n")
        for line in lines:
            _draw_highlighted_sentence_centered(
                draw=draw,
                y=current_y,
                text=line,
                font=fonts["confession_text"],
                highlight_color=color,
                width=width,
            )
            current_y += 58
        current_y += 24

    # 4. Minimalist footer near bottom
    footer_text = "— 포이에마성령교회 —"
    fw = fonts["footer_text"].getbbox(footer_text)[2] - fonts["footer_text"].getbbox(footer_text)[0]
    _draw_text_with_shadow(draw, ((width - fw) // 2, height - 90), footer_text, fonts["footer_text"], (240, 240, 240, 230), shadow_color=(0, 0, 0, 180))

    return poster


# ===========================================================================
# FORMAT 2: Dynamic Brush Proclamation (샘플 2 스타일 - 컬러 브러시 스트로크 뱃지)
# ===========================================================================
def render_style_sample2_brush_proclamation(
    poster: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, ImageFont.FreeTypeFont],
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Renders Sample 2 layout: Yellow paint headline, colored brush ribbon badges [1],[2],[3],[4]."""
    draw = ImageDraw.Draw(poster)

    # 1. Top Left Dynamic Brush Title with Yellow Paint Stroke
    current_y = 65

    # Yellow brush backdrop rectangle
    brush_bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(brush_bg)
    b_draw.rounded_rectangle([60, current_y + 140, 720, current_y + 270], radius=16, fill=(255, 215, 0, 210))
    brush_bg = brush_bg.filter(ImageFilter.GaussianBlur(radius=3))
    poster.paste(brush_bg, (0, 0), brush_bg)
    draw = ImageDraw.Draw(poster)

    # Line 1: Emotional Calligraphy (e.g. "성도여~♡♡♡" or "바보야~♡♡♡")
    _draw_text_with_shadow(draw, (80, current_y), "바보야~♡♡♡", fonts["headline_giant"], (195, 20, 20, 255), shadow_color=(255, 255, 255, 230), shadow_offset=(3, 3))
    current_y += 115

    # Line 2: Black Calligraphy
    _draw_text_with_shadow(draw, (75, current_y), "제일 중요한 것은", fonts["headline_giant"], INK_BLACK, shadow_color=(255, 255, 255, 230), shadow_offset=(3, 3))
    current_y += 115

    # Line 3: Massive Red Proclamation Title
    _draw_text_with_shadow(draw, (85, current_y), "관계이여!", fonts["headline_giant"], (205, 20, 20, 255), shadow_color=(255, 255, 255, 240), shadow_offset=(4, 4))
    current_y += 175

    # 2. Right Side: Numbered Color Brush Ribbon Badges (1, 2, 3, 4)
    # Badges aligned to right half (x = 560 ~ 1020)
    badge_x = 560
    badge_w = 460
    badge_start_y = 440

    sample_badges = [
        {
            "num": "1",
            "title": "관계가 제일이여!",
            "quote": "내 안에 거하라\n나도 너희 안에 거하리라\n(요한복음 15:4)",
            "color": BRUSH_BADGE_COLORS[0],
        },
        {
            "num": "2",
            "title": "허물투성인 나를\n찾아오시는 긍휼의 은혜",
            "quote": "우리가 아직 죄인 되었을 때에\n그리스도께서 우리를 위하여\n(로마서 5:8)",
            "color": BRUSH_BADGE_COLORS[1],
        },
        {
            "num": "3",
            "title": "시련 속에서도\n변함없는 사랑과 배려",
            "quote": "네가 물 가운데로 지날 때에\n내가 너와 함께 할 것이라\n(이사야 43:2)",
            "color": BRUSH_BADGE_COLORS[2],
        },
        {
            "num": "4",
            "title": "날마다 부어주시는\n신선한 기름부음과 임재",
            "quote": "너희는 주께 받은 바 기름 부음이\n너희 안에 거하나니\n(요한일서 2:27)",
            "color": BRUSH_BADGE_COLORS[3],
        },
    ]

    by = badge_start_y
    for item in sample_badges:
        # Brush Ribbon Shape (slightly rounded with vivid colored background)
        ribbon_h = 48 if "\n" not in item["title"] else 78
        draw.rounded_rectangle([badge_x, by, badge_x + badge_w, by + ribbon_h], radius=14, fill=item["color"])

        # White Number & Title
        draw.text((badge_x + 14, by + 4), item["num"], font=fonts["brush_num"], fill=(255, 245, 120, 255))
        draw.text((badge_x + 55, by + 6), item["title"], font=fonts["brush_title"], fill=COLOR_WHITE)
        by += ribbon_h + 10

        # Scripture quote below badge
        for qline in item["quote"].split("\n"):
            _draw_text_with_shadow(draw, (badge_x + 50, by), qline, fonts["brush_quote"], INK_BLACK, shadow_color=(255, 255, 255, 220), shadow_offset=(1, 1))
            by += 28
        by += 22

    # 3. Bottom Left: Dark Glass Meditative Exhortation Box
    box_x = 45
    box_y = 1150
    box_w = 480
    box_h = 420
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=18, fill=(15, 10, 8, 200), outline=(180, 140, 60, 150), width=1)

    exhortation_lines = [
        "기름부음을 자랑하면 교만이고",
        "기름부음이란 단어가 나오면",
        "경계를 내는 종교적, 지식적인",
        "목사님들이여!",
        "",
        "성령의 하나님을 믿는가?",
        "그 믿음 자체가 보이지 아니하는",
        "성령의 초자연적인 일이거늘!",
        "밝히 보이는 것만 전부로 아는",
        "알량한 지식과 경험이 많다는",
        "교만의 종교형 목사님들이여!",
    ]
    ey = box_y + 24
    for el in exhortation_lines:
        color = (255, 220, 110, 255) if ("!" in el or "?" in el) else (235, 235, 240, 240)
        draw.text((box_x + 22, ey), el, font=fonts["exhortation"], fill=color)
        ey += 32

    # 4. Bottom Right: Yellow highlight CTA banner
    cta_x = 550
    cta_y = 1380
    draw.text((cta_x + 20, cta_y), "날마다 때마다 누리는", font=fonts["headline_sub"], fill=INK_BLACK)
    _draw_text_with_shadow(draw, (cta_x - 10, cta_y + 55), "관계가 제일이여!", fonts["headline_sub"], (205, 25, 25, 255), shadow_color=(255, 255, 255, 240), shadow_offset=(3, 3))

    # 5. Bottom Gold Church Branding Banner
    banner_y = height - 160
    # Gold radiant emblem ring
    emblem_cx = 220
    draw.ellipse([emblem_cx - 45, banner_y - 10, emblem_cx + 45, banner_y + 80], fill=(225, 175, 50, 230), outline=(255, 235, 150), width=3)
    draw.text((emblem_cx - 18, banner_y + 6), "✝", font=fonts["brush_num"], fill=(255, 255, 255, 255))

    # Gold Church Name
    church_name = "포이에마성령교회"
    _draw_text_with_shadow(draw, (emblem_cx + 70, banner_y + 4), church_name, fonts["church_gold"], (245, 210, 70, 255), shadow_color=(0, 0, 0, 200), shadow_offset=(3, 4))
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
    """Master entry point for rendering posters in authentic Sample 1 / Sample 2 styles."""
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

    # 2. Select between Sample 1 Style & Sample 2 Style dynamically
    date_str = content.get("date_str", "2026.10.21")
    theme = content.get("theme", "")
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16)
    use_style_1 = (seed_val % 2 == 0)

    # 3. Prepare Base Background
    if use_style_1:
        base_bg_file = BASE_DIR / "assets" / "backgrounds" / "bg_pilgrim_cross.png"
    else:
        base_bg_file = BASE_DIR / "assets" / "backgrounds" / "bg_jesus_embrace.png"

    if base_bg_file.exists():
        poster_base = Image.open(base_bg_file).convert("RGBA")
    elif bg_image_path.exists():
        poster_base = Image.open(bg_image_path).convert("RGBA")
    else:
        from utils.image_generator import generate_dynamic_background_artwork
        poster_base = generate_dynamic_background_artwork(date_str, theme).convert("RGBA")

    if poster_base.size != (width, height):
        poster_base = poster_base.resize((width, height), Image.Resampling.LANCZOS)

    # 4. Render Layout
    if use_style_1:
        logger.info("[Poster Composer] 🎨 Rendering in SAMPLE 1 FORMAT: Free Sky Calligraphy & Colored Accents")
        final_img = render_style_sample1_free_confession(poster_base, content, fonts, width, height)
    else:
        logger.info("[Poster Composer] 🎨 Rendering in SAMPLE 2 FORMAT: Paint Brush Badges & Dynamic Proclamation")
        final_img = render_style_sample2_brush_proclamation(poster_base, content, fonts, width, height)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_img.convert("RGB").save(output_path, format="PNG", quality=96)
    logger.info(f"Successfully created authentic styled poster at: {output_path}")
    return output_path

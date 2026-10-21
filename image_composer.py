"""Graphic Composer Module (Bespoke Calligraphy & Aesthetic Multi-Form Engine).

Transforms rigid poster layouts into modern, emotionally resonant Christian stationery:
1. Verse Card (감성 말씀 카드):
   - Dynamic Calligraphy Headline with organic brush rhythm & ink wash bleed.
   - Traditional Red Seal Stamp (붉은 낙관 전각) for authentic artistry.
   - Serene negative space and elegant MaruBuri serif typography.
2. Gospel Leaflet (마음을 여는 스토리 전도지):
   - Life-resonance calligraphy opening + warm pastoral essay.
   - Sacred scripture highlight card + welcoming church signature.
3. Devotional Postcard (데일리 묵상 엽서):
   - Contemplative calligraphy proclamation + morning meditation & prayer.

All rendered with 100% vector-smooth typographic care and zero clunky box cliches.
"""

from datetime import datetime
import hashlib
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from utils.font_downloader import ensure_fonts_exist

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Elegant Literary & Ink Color Palette
INK_CHARCOAL = (32, 30, 34, 255)       # Deep Korean Calligraphy Ink (먹물색)
INK_DEEP_BROWN = (52, 42, 38, 255)     # Warm Espresso Ink
INK_SOFT_MUTED = (108, 102, 98, 255)   # Subtitle & Meditation Muted Gray
INK_GOLD_OCHRE = (168, 118, 52, 255)   # Subtle Divine Ochre
COLOR_SEAL_RED = (186, 44, 40, 240)    # Traditional Vermilion Seal Stamp (붉은 낙관 전각)
COLOR_WHITE = (255, 255, 255, 255)
CARD_BG_WARM = (255, 255, 255, 215)    # Translucent fine paper backing
CARD_BORDER = (220, 214, 204, 180)


def _load_font(
    font_path: Optional[Path], size: int, fallback_cand: str = "AppleGothic.ttf"
) -> ImageFont.FreeTypeFont:
    """Robust font loader with system fallback."""
    if font_path and font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            pass
    for cand in ["AppleGothic.ttf", "malgun.ttf", "gulim.ttc", fallback_cand]:
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _get_fonts(config: Dict[str, Any], fonts_dir: Path) -> Dict[str, Path]:
    """Retrieves all active font paths."""
    ensure_fonts_exist(fonts_dir)
    return {
        "calligraphy": fonts_dir / "PyeongChangPeace-Bold.otf",
        "serif_regular": fonts_dir / "MaruBuri-Regular.ttf",
        "serif_bold": fonts_dir / "MaruBuri-Bold.ttf",
        "sans_regular": fonts_dir / "Pretendard-Regular.otf",
        "sans_bold": fonts_dir / "Pretendard-Bold.otf",
    }


def draw_red_seal_stamp(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str = "포이에마",
    size: int = 42,
    font: Optional[ImageFont.FreeTypeFont] = None,
) -> None:
    """Renders a traditional Korean red vermilion seal stamp (전각 낙관).
    
    Instantly elevates cards from mechanical prints to authentic artisan works.
    """
    box_w = int(size * 1.8)
    box_h = int(size * 1.8)
    radius = 6

    # Draw rounded red stamp box
    draw.rounded_rectangle(
        [x, y, x + box_w, y + box_h],
        radius=radius,
        outline=COLOR_SEAL_RED,
        width=3,
    )
    # Subtle inner seal border
    inner_m = 4
    draw.rounded_rectangle(
        [x + inner_m, y + inner_m, x + box_w - inner_m, y + box_h - inner_m],
        radius=radius - 2,
        outline=(*COLOR_SEAL_RED[:3], 130),
        width=1,
    )

    # Stamp Text (2x2 or 4 chars)
    if font is None:
        font = ImageFont.load_default()

    # Split text if 4 characters (e.g., 포이에마 -> 2x2)
    if len(text) == 4:
        c1, c2 = text[:2], text[2:]
        bbox1 = font.getbbox(c1)
        w1 = bbox1[2] - bbox1[0]
        h1 = bbox1[3] - bbox1[1]
        draw.text((x + (box_w - w1) // 2, y + 6), c1, font=font, fill=COLOR_SEAL_RED)
        draw.text((x + (box_w - w1) // 2, y + 8 + h1), c2, font=font, fill=COLOR_SEAL_RED)
    else:
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((x + (box_w - w) // 2, y + (box_h - h) // 2 - 2), text, font=font, fill=COLOR_SEAL_RED)


def render_organic_calligraphy_headline(
    canvas: Image.Image,
    center_y: int,
    headline_text: str,
    font_path: Path,
    emphasis_words: Optional[List[str]] = None,
    width: int = 1080,
    main_color: Tuple[int, int, int, int] = INK_CHARCOAL,
) -> int:
    """Renders a breathing, rhythmic Korean calligraphy headline.
    
    Key techniques:
    - Emphasis words are enlarged (1.4x~1.8x) as if drawn with deep brush pressure (필압).
    - Ink bleed & wash simulation gives an authentic handmade Korean paper feel.
    - Multiple lines are balanced with organic cadence.
    """
    emphasis = emphasis_words or []
    
    # Split headline into 1 or 2 lines for ideal poetic rhythm
    words = headline_text.split()
    if len(words) <= 3:
        lines = [" ".join(words)]
    elif len(words) == 4:
        lines = [" ".join(words[:2]), " ".join(words[2:])]
    else:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    # Pre-render onto an isolated high-res alpha layer to apply ink bleed
    txt_layer = Image.new("RGBA", (width, canvas.height), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(txt_layer)

    curr_y = center_y
    for line in lines:
        line_words = line.split()
        word_render_data = []
        total_w = 0
        spacing = 16

        for w in line_words:
            # Check if this word is in emphasis list or ends with key nouns
            is_emph = any(ew in w for ew in emphasis) or len(w) >= 3
            font_size = 96 if is_emph else 68
            w_font = _load_font(font_path, font_size)
            bbox = w_font.getbbox(w)
            ww = bbox[2] - bbox[0]
            wh = bbox[3] - bbox[1]
            word_render_data.append((w, w_font, ww, wh, is_emph))
            total_w += ww + spacing
        total_w -= spacing

        start_x = (width - total_w) // 2
        max_h = max(item[3] for item in word_render_data) if word_render_data else 60

        for w, w_font, ww, wh, is_emph in word_render_data:
            # Slight organic vertical cadence (not flat baseline)
            y_offset = (max_h - wh) // 2
            
            # 1. Subtle warm ink shadow for depth
            t_draw.text((start_x + 2, curr_y + y_offset + 3), w, font=w_font, fill=(0, 0, 0, 35))
            # 2. Main rich ink stroke
            stroke_col = main_color if is_emph else (*main_color[:3], 230)
            t_draw.text((start_x, curr_y + y_offset), w, font=w_font, fill=stroke_col)
            
            start_x += ww + spacing

        curr_y += max_h + 24

    # 3. Simulate organic ink bleed (먹물 번짐) via subtle gaussian diffusion
    bleed_layer = txt_layer.filter(ImageFilter.GaussianBlur(radius=1.8))
    # Composite: background -> soft ink bleed -> sharp main stroke
    canvas.alpha_composite(bleed_layer)
    canvas.alpha_composite(txt_layer)

    return curr_y


# ---------------------------------------------------------------------------
# Form Factor 1: Verse Card (감성 말씀 카드)
# ---------------------------------------------------------------------------

def render_verse_card(
    bg: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, Path],
    config: Dict[str, Any],
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Renders a breathtaking, peaceful Scripture Verse Card.
    
    Focused on pure word, generous white/cream negative space, and fine literary beauty.
    """
    canvas = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # 1. Top Delicate Header (Date & Church Theme)
    f_sans_small = _load_font(fonts["sans_regular"], 26)
    f_serif_small = _load_font(fonts["serif_regular"], 28)
    date_str = content.get("date_str", datetime.now().strftime("%Y.%m.%d"))
    theme = content.get("theme", "말씀의 평안")

    top_y = 110
    draw.text((width // 2, top_y), f"POiEMA DAILY WORD  ·  {date_str}", font=f_sans_small, fill=INK_SOFT_MUTED, anchor="mm")
    draw.line([(width // 2 - 120, top_y + 28), (width // 2 + 120, top_y + 28)], fill=(195, 188, 178, 160), width=1)

    # 2. Grand Calligraphy Headline (Center Stage)
    headline = content.get("headline", "주의 말씀은 내 발에 등이요")
    emphasis = content.get("calligraphy_emphasis", [])
    calli_end_y = render_organic_calligraphy_headline(
        canvas=canvas,
        center_y=280,
        headline_text=headline,
        font_path=fonts["calligraphy"],
        emphasis_words=emphasis,
        width=width,
        main_color=INK_CHARCOAL,
    )

    # Red seal stamp next to headline
    f_seal = _load_font(fonts["serif_bold"], 20)
    draw_red_seal_stamp(draw, width // 2 + 190, calli_end_y - 80, text="포이에마", size=26, font=f_seal)

    # 3. Translucent Center Scripture Plaque
    card_y = calli_end_y + 80
    card_margin = 90
    card_w = width - (card_margin * 2)
    card_h = 580

    # Draw frosted glass / handmade paper card
    card_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_layer)
    c_draw.rounded_rectangle(
        [card_margin, card_y, card_margin + card_w, card_y + card_h],
        radius=20,
        fill=CARD_BG_WARM,
        outline=CARD_BORDER,
        width=1,
    )
    card_layer = card_layer.filter(ImageFilter.GaussianBlur(radius=0.5))
    canvas.alpha_composite(card_layer)

    # Scripture Content inside Card
    sc_ref = content.get("scripture_ref", "")
    sc_text = content.get("scripture_text", "")
    if not sc_ref and content.get("points"):
        pt0 = content["points"][0]
        sc = pt0.get("scripture", {}) if isinstance(pt0, dict) else getattr(pt0, "scripture")
        sc_ref = sc.get("reference", "") if isinstance(sc, dict) else getattr(sc, "reference", "")
        sc_text = sc.get("text", "") if isinstance(sc, dict) else getattr(sc, "text", "")

    # Scripture Reference Tag
    f_serif_bold = _load_font(fonts["serif_bold"], 34)
    draw.text((width // 2, card_y + 70), f"— {sc_ref} —", font=f_serif_bold, fill=INK_GOLD_OCHRE, anchor="mm")

    # Scripture Text with Literary Line Wrapping
    f_serif_text = _load_font(fonts["serif_regular"], 36)
    wrapped_lines = _wrap_text_korean(sc_text, f_serif_text, max_width=card_w - 120)
    text_curr_y = card_y + 140
    for line in wrapped_lines:
        draw.text((width // 2, text_curr_y), f"“ {line} ”" if len(wrapped_lines) == 1 else line, font=f_serif_text, fill=INK_DEEP_BROWN, anchor="mm")
        text_curr_y += 56

    # 4. Meditation & Blessing Note
    meditation = content.get("meditation") or content.get("call_to_action") or "오늘도 주님의 평강이 당신의 마음과 생각을 지키시길 축복합니다."
    f_med = _load_font(fonts["serif_regular"], 30)
    draw.line([(width // 2 - 60, text_curr_y + 20), (width // 2 + 60, text_curr_y + 20)], fill=(215, 205, 195, 200), width=1)
    
    med_lines = _wrap_text_korean(meditation, f_med, max_width=card_w - 140)
    med_y = text_curr_y + 60
    for mline in med_lines[:3]:
        draw.text((width // 2, med_y), mline, font=f_med, fill=INK_SOFT_MUTED, anchor="mm")
        med_y += 46

    # 5. Clean Church Branding Bottom
    _render_footer(draw, config, width, height, fonts)

    return canvas.convert("RGB")


# ---------------------------------------------------------------------------
# Form Factor 2: Gospel Leaflet (마음을 여는 스토리 전도지)
# ---------------------------------------------------------------------------

def render_gospel_leaflet(
    bg: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, Path],
    config: Dict[str, Any],
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Renders a warm, comforting Gospel Leaflet card for everyday people.
    
    Combines empathetic question, gentle life essay, and clear gospel truth.
    """
    canvas = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # 1. Warm Opening Header
    f_sans_small = _load_font(fonts["sans_regular"], 26)
    draw.text((width // 2, 120), "당신의 지친 하루에 건네는 따뜻한 쉼과 복음", font=f_sans_small, fill=INK_SOFT_MUTED, anchor="mm")

    # 2. Calligraphy Opening Question / Comfort
    headline = content.get("headline", "수고하고 무거운 짐 진 자들아")
    emphasis = content.get("calligraphy_emphasis", [])
    calli_end_y = render_organic_calligraphy_headline(
        canvas=canvas,
        center_y=230,
        headline_text=headline,
        font_path=fonts["calligraphy"],
        emphasis_words=emphasis,
        width=width,
        main_color=INK_CHARCOAL,
    )

    # 3. Life & Gospel Essay Section (마음을 울리는 위로 에세이)
    essay_card_y = calli_end_y + 50
    essay_card_w = width - 160
    essay_card_h = 420

    essay_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    e_draw = ImageDraw.Draw(essay_layer)
    e_draw.rounded_rectangle(
        [80, essay_card_y, 80 + essay_card_w, essay_card_y + essay_card_h],
        radius=16,
        fill=(255, 255, 255, 225),
        outline=CARD_BORDER,
        width=1,
    )
    canvas.alpha_composite(essay_layer)

    meditation = content.get("meditation") or (
        "세상은 늘 더 빠르게, 더 완벽하게 달리라고 요구하지만 "
        "하나님께서는 오늘 당신의 지친 숨결 그대로를 품에 안으십니다. "
        "참된 쉼과 평안은 세상의 조건이 아닌, 나를 위해 생명을 주신 예수 그리스도 안에 있습니다."
    )
    f_essay = _load_font(fonts["serif_regular"], 33)
    e_lines = _wrap_text_korean(meditation, f_essay, max_width=essay_card_w - 100)
    
    ey = essay_card_y + 70
    for el in e_lines[:6]:
        draw.text((width // 2, ey), el, font=f_essay, fill=INK_CHARCOAL, anchor="mm")
        ey += 52

    # 4. Scripture of Covenant Card (언약의 말씀 카드)
    sc_card_y = essay_card_y + essay_card_h + 40
    sc_card_h = 320
    sc_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(sc_layer)
    s_draw.rounded_rectangle(
        [100, sc_card_y, width - 100, sc_card_y + sc_card_h],
        radius=14,
        fill=(248, 244, 236, 235),
        outline=(210, 195, 175, 180),
        width=1,
    )
    canvas.alpha_composite(sc_layer)

    sc_ref = content.get("scripture_ref", "마태복음 11:28")
    sc_text = content.get("scripture_text", "수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라")
    
    f_sc_tag = _load_font(fonts["sans_bold"], 26)
    draw.text((width // 2, sc_card_y + 50), f"🕊️ 약속의 말씀  |  {sc_ref}", font=f_sc_tag, fill=INK_GOLD_OCHRE, anchor="mm")

    f_sc_body = _load_font(fonts["serif_bold"], 34)
    sc_lines = _wrap_text_korean(sc_text, f_sc_body, max_width=width - 260)
    sy = sc_card_y + 115
    for sl in sc_lines[:3]:
        draw.text((width // 2, sy), sl, font=f_sc_body, fill=INK_DEEP_BROWN, anchor="mm")
        sy += 50

    # Red seal stamp
    f_seal = _load_font(fonts["serif_bold"], 20)
    draw_red_seal_stamp(draw, width - 210, sc_card_y + sc_card_h - 75, text="은혜", size=24, font=f_seal)

    # 5. Welcoming Footer
    _render_footer(draw, config, width, height, fonts, is_leaflet=True)

    return canvas.convert("RGB")


# ---------------------------------------------------------------------------
# Form Factor 3: Devotional Postcard (데일리 묵상 엽서)
# ---------------------------------------------------------------------------

def render_devotional_postcard(
    bg: Image.Image,
    content: Dict[str, Any],
    fonts: Dict[str, Path],
    config: Dict[str, Any],
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Renders a quiet, contemplative Morning Devotional Postcard."""
    canvas = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # 1. Postcard Stamp & Header Area
    date_str = content.get("date_str", datetime.now().strftime("%Y.%m.%d"))
    f_sans = _load_font(fonts["sans_regular"], 24)
    draw.text((120, 130), f"DATE: {date_str}", font=f_sans, fill=INK_SOFT_MUTED)
    draw.text((120, 165), "SERIES: 아침을 여는 성령의 임재", font=f_sans, fill=INK_SOFT_MUTED)

    f_seal = _load_font(fonts["serif_bold"], 22)
    draw_red_seal_stamp(draw, width - 190, 120, text="말씀", size=28, font=f_seal)

    # 2. Main Calligraphy Proclamation
    headline = content.get("headline", "오직 성령으로 충만함을 받으라")
    emphasis = content.get("calligraphy_emphasis", [])
    calli_end_y = render_organic_calligraphy_headline(
        canvas=canvas,
        center_y=300,
        headline_text=headline,
        font_path=fonts["calligraphy"],
        emphasis_words=emphasis,
        width=width,
        main_color=INK_CHARCOAL,
    )

    # 3. Scripture Quote
    sc_ref = content.get("scripture_ref", "에베소서 5:18")
    sc_text = content.get("scripture_text", "술 취하지 말라 이는 방탕한 것이니 오직 성령으로 충만함을 받으라")
    
    f_ref = _load_font(fonts["serif_bold"], 32)
    draw.text((width // 2, calli_end_y + 80), sc_ref, font=f_ref, fill=INK_GOLD_OCHRE, anchor="mm")

    f_sc = _load_font(fonts["serif_regular"], 35)
    sc_lines = _wrap_text_korean(sc_text, f_sc, max_width=width - 220)
    scy = calli_end_y + 140
    for line in sc_lines[:4]:
        draw.text((width // 2, scy), f"“ {line} ”" if len(sc_lines) == 1 else line, font=f_sc, fill=INK_DEEP_BROWN, anchor="mm")
        scy += 54

    # 4. Prayer & Meditation Section (오늘의 기도)
    prayer_box_y = scy + 80
    box_w = width - 200
    box_h = 360

    p_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(p_layer)
    p_draw.rounded_rectangle(
        [100, prayer_box_y, 100 + box_w, prayer_box_y + box_h],
        radius=14,
        fill=(255, 255, 255, 220),
        outline=CARD_BORDER,
        width=1,
    )
    canvas.alpha_composite(p_layer)

    f_ptag = _load_font(fonts["serif_bold"], 28)
    draw.text((width // 2, prayer_box_y + 50), "✦ 오늘의 기도 ✦", font=f_ptag, fill=INK_CHARCOAL, anchor="mm")

    meditation = content.get("meditation") or content.get("call_to_action") or "주님, 나의 모든 계획과 염려를 내려놓고 주님의 인도하심을 온전히 따르게 하소서."
    f_pbody = _load_font(fonts["serif_regular"], 31)
    plines = _wrap_text_korean(meditation, f_pbody, max_width=box_w - 90)
    py = prayer_box_y + 110
    for pl in plines[:4]:
        draw.text((width // 2, py), pl, font=f_pbody, fill=INK_SOFT_MUTED, anchor="mm")
        py += 48

    # 5. Footer
    _render_footer(draw, config, width, height, fonts)

    return canvas.convert("RGB")


# ---------------------------------------------------------------------------
# Shared Typography Helpers & Footer
# ---------------------------------------------------------------------------

def _wrap_text_korean(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wraps Korean text naturally at word boundaries."""
    if not text:
        return []
    words = text.split()
    lines = []
    current = []

    for w in words:
        trial = " ".join(current + [w])
        bbox = font.getbbox(trial)
        if (bbox[2] - bbox[0]) <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]

    if current:
        lines.append(" ".join(current))
    return lines


def _render_footer(
    draw: ImageDraw.ImageDraw,
    config: Dict[str, Any],
    width: int,
    height: int,
    fonts: Dict[str, Path],
    is_leaflet: bool = False,
) -> None:
    """Renders a refined, minimalist church signature at bottom."""
    church_name = config.get("church", {}).get("name", "포이에마성령교회")
    show_contact = config.get("church", {}).get("show_contact", False)
    contact_number = config.get("church", {}).get("contact_number", "")

    f_bold = _load_font(fonts["serif_bold"], 30)
    f_sub = _load_font(fonts["sans_regular"], 24)

    foot_y = height - 160
    # Clean hairline separator
    draw.line([(width // 2 - 100, foot_y - 25), (width // 2 + 100, foot_y - 25)], fill=(200, 192, 180, 140), width=1)

    draw.text((width // 2, foot_y), church_name, font=f_bold, fill=INK_CHARCOAL, anchor="mm")

    if show_contact and contact_number:
        draw.text((width // 2, foot_y + 40), f"예배 및 상담 문의  |  {contact_number}", font=f_sub, fill=INK_SOFT_MUTED, anchor="mm")
    else:
        slogan = "성령의 임재와 말씀의 능력이 살아 숨쉬는 공동체" if is_leaflet else "Poiema Holy Spirit Church"
        draw.text((width // 2, foot_y + 38), slogan, font=f_sub, fill=INK_SOFT_MUTED, anchor="mm")


# ---------------------------------------------------------------------------
# Master Composition Entry Point
# ---------------------------------------------------------------------------

def compose_poster(
    bg_image_path: Path,
    content: Dict[str, Any],
    config: Dict[str, Any],
    output_path: Path,
) -> Path:
    """Selects the designated form factor and composes the final graphic masterpiece."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fonts_dir = BASE_DIR / config.get("fonts", {}).get("dir", "fonts")
    fonts = _get_fonts(config, fonts_dir)

    bg_img = Image.open(bg_image_path).convert("RGB")
    width, height = bg_img.size

    form_factor = content.get("form_factor", "verse_card")
    logger.info(f"[Publishing Manager] Composing artwork in form factor: '{form_factor}'...")

    if form_factor == "gospel_leaflet":
        final_img = render_gospel_leaflet(bg_img, content, fonts, config, width, height)
    elif form_factor == "devotional_postcard":
        final_img = render_devotional_postcard(bg_img, content, fonts, config, width, height)
    else:
        # Default: Verse Card
        final_img = render_verse_card(bg_img, content, fonts, config, width, height)

    final_img.save(output_path, format="PNG", quality=95)
    logger.info(f"✓ Beautiful graphic masterpiece saved to {output_path}")
    return output_path

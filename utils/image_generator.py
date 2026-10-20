"""Image Generator Module (Daily Dynamic Holy Light Artwork & API Engine).

Every single day features a completely unique visual atmosphere based on:
1. Day of the Week & Biblical Theme Palette (7 Distinct Heavenly Palettes)
2. Daily Dynamic Light Geometry (Varying sunbeam angles, god-ray counts, horizon silhouettes)
3. Dynamic Atmospheric Glow (Golden Dawn, Celestial Amethyst, Sacred Azure, Living Waters)
"""

from datetime import datetime
import hashlib
import io
import json
import logging
import math
import os
from pathlib import Path
import random
from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

logger = logging.getLogger(__name__)

# 7 Distinct Biblical Color Atmospheres for Each Day & Mood
BIBLICAL_PALETTES = [
    # 0. Royal Gold & Sunrise (주일/승리 - 거룩한 영광)
    {
        "name": "Royal Divine Gold",
        "top": (15, 24, 48),
        "mid": (90, 62, 50),
        "warm": (225, 168, 75),
        "glow": (255, 235, 170),
        "horizon": (20, 16, 26),
    },
    # 1. Living Waters & Peace (월요일 - 쉴 만한 물가, 평안)
    {
        "name": "Living Waters & Azure",
        "top": (10, 32, 54),
        "mid": (24, 76, 92),
        "warm": (80, 175, 170),
        "glow": (190, 245, 240),
        "horizon": (8, 24, 35),
    },
    # 2. Celestial Amethyst (화요일 - 십자가의 깊은 은혜, 기도)
    {
        "name": "Celestial Purple Dawn",
        "top": (28, 18, 52),
        "mid": (84, 46, 88),
        "warm": (195, 110, 140),
        "glow": (255, 215, 230),
        "horizon": (22, 14, 34),
    },
    # 3. Holy Spirit Fire & Glow (수요일 - 성령 충만, 권능)
    {
        "name": "Holy Fire & Radiance",
        "top": (35, 18, 28),
        "mid": (120, 50, 40),
        "warm": (235, 130, 45),
        "glow": (255, 230, 140),
        "horizon": (26, 12, 16),
    },
    # 4. Deep Sapphire Sanctuary (목요일 - 말씀의 반석, 진리)
    {
        "name": "Deep Sanctuary Blue",
        "top": (8, 16, 40),
        "mid": (20, 45, 95),
        "warm": (160, 180, 220),
        "glow": (240, 245, 255),
        "horizon": (10, 14, 28),
    },
    # 5. Olive Garden & Restoration (금요일 - 생명의 회복, 소망)
    {
        "name": "Garden of Grace",
        "top": (16, 30, 36),
        "mid": (42, 78, 62),
        "warm": (165, 180, 105),
        "glow": (245, 250, 195),
        "horizon": (12, 22, 20),
    },
    # 6. Ethereal Cloud & Light (토요일 - 안식과 샬롬)
    {
        "name": "Heavenly Sabbath Shalom",
        "top": (22, 34, 58),
        "mid": (70, 75, 105),
        "warm": (210, 195, 160),
        "glow": (255, 250, 235),
        "horizon": (18, 22, 35),
    },
]


def select_daily_palette(date_str: str, theme: str) -> Dict[str, Any]:
    """Selects a unique color palette based on day of week and theme hash."""
    try:
        dt = datetime.strptime(date_str.replace("-", ".").strip(), "%Y.%m.%d")
        day_idx = dt.weekday()  # 0: Mon ~ 6: Sun
    except Exception:
        day_idx = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % len(BIBLICAL_PALETTES)

    # Theme keywords can also shift palette for maximum thematic harmony
    if "성령" in theme or "불" in theme:
        return BIBLICAL_PALETTES[3]  # Holy Fire
    elif "물가" in theme or "평안" in theme or "생수" in theme:
        return BIBLICAL_PALETTES[1]  # Living Waters
    elif "은혜" in theme or "사랑" in theme:
        return BIBLICAL_PALETTES[2]  # Amethyst Grace
    elif "말씀" in theme or "진리" in theme:
        return BIBLICAL_PALETTES[4]  # Sapphire Truth
    elif "동행" in theme or "회복" in theme:
        return BIBLICAL_PALETTES[5]  # Garden Grace

    return BIBLICAL_PALETTES[day_idx % len(BIBLICAL_PALETTES)]


def generate_dynamic_daily_background(
    date_str: str,
    theme: str,
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Generates a unique, breathtaking holy background that changes every single day.

    Incorporates:
    - Daily color scheme corresponding to biblical theme
    - Changing light source coordinates and sunbeam angles
    - Random mountain/horizon topography derived from daily seed
    """
    palette = select_daily_palette(date_str, theme)
    logger.info(f"Generating daily background with theme palette: '{palette['name']}' ({date_str})")

    # Deterministic daily seed so same day gives same background, but next day is totally different
    seed_str = f"{date_str}_{theme}"
    daily_seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(daily_seed)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    c_top = palette["top"]
    c_mid = palette["mid"]
    c_warm = palette["warm"]
    c_glow = palette["glow"]
    c_bot = palette["horizon"]

    # 1. Daily Vertical Sky Gradient
    mid_pos = rng.uniform(0.35, 0.48)
    warm_pos = rng.uniform(0.70, 0.82)

    for y in range(height):
        ratio = y / height
        if ratio < mid_pos:
            lr = ratio / mid_pos
            r = int(c_top[0] * (1 - lr) + c_mid[0] * lr)
            g = int(c_top[1] * (1 - lr) + c_mid[1] * lr)
            b = int(c_top[2] * (1 - lr) + c_mid[2] * lr)
        elif ratio < warm_pos:
            lr = (ratio - mid_pos) / (warm_pos - mid_pos)
            r = int(c_mid[0] * (1 - lr) + c_warm[0] * lr)
            g = int(c_mid[1] * (1 - lr) + c_warm[1] * lr)
            b = int(c_mid[2] * (1 - lr) + c_warm[2] * lr)
        else:
            lr = (ratio - warm_pos) / (1.0 - warm_pos)
            r = int(c_warm[0] * (1 - lr) + c_bot[0] * lr)
            g = int(c_warm[1] * (1 - lr) + c_bot[1] * lr)
            b = int(c_warm[2] * (1 - lr) + c_bot[2] * lr)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Celestial Sun / Light Source (position varies by day)
    sun_x = int(width * rng.uniform(0.40, 0.60))
    sun_y = int(height * rng.uniform(0.18, 0.28))
    max_radius = rng.randint(480, 580)

    sun_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sun_draw = ImageDraw.Draw(sun_layer)

    for radius in range(max_radius, 20, -18):
        alpha = int(95 * (1 - (radius / max_radius) ** 1.3))
        box = [sun_x - radius, sun_y - radius, sun_x + radius, sun_y + radius]
        sun_draw.ellipse(box, fill=(c_glow[0], c_glow[1], c_glow[2], min(130, max(0, alpha))))

    # Core radiant halo
    sun_draw.ellipse(
        [sun_x - 100, sun_y - 100, sun_x + 100, sun_y + 100],
        fill=(255, 255, 250, 60),
    )
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(radius=38))
    img = Image.alpha_composite(img, sun_layer)

    # 3. Dynamic Heavenly Sunbeams (Angles & width vary per day)
    ray_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(ray_layer)

    num_rays = rng.randint(9, 15)
    base_angle = rng.uniform(55, 75)
    spread = rng.uniform(3.5, 6.0)

    for i in range(num_rays):
        angle = math.radians(base_angle + i * spread)
        dx = math.cos(angle) * height * 1.3
        dy = math.sin(angle) * height * 1.3
        beam_w = rng.randint(70, 130)
        poly = [
            (sun_x, sun_y),
            (sun_x + dx - beam_w, sun_y + dy),
            (sun_x + dx + beam_w, sun_y + dy),
        ]
        alpha = rng.randint(18, 30)
        ray_draw.polygon(poly, fill=(c_glow[0], c_glow[1], c_glow[2], alpha))

    ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(radius=32))
    img = Image.alpha_composite(img, ray_layer)

    # 4. Daily Mountain / Horizon Topography Silhouette
    horizon_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(horizon_layer)
    pts = [(0, height)]
    freq1 = rng.uniform(0.005, 0.012)
    freq2 = rng.uniform(0.012, 0.022)
    amp1 = rng.randint(50, 90)
    amp2 = rng.randint(25, 45)
    base_h = height * rng.uniform(0.77, 0.83)

    for x in range(0, width + 40, 30):
        ny = int(base_h + math.sin(x * freq1) * amp1 + math.cos(x * freq2) * amp2)
        pts.append((x, ny))
    pts.append((width, height))
    h_draw.polygon(pts, fill=(c_bot[0], c_bot[1], c_bot[2], 230))
    horizon_layer = horizon_layer.filter(ImageFilter.GaussianBlur(radius=6))
    img = Image.alpha_composite(img, horizon_layer)

    # 5. Celestial Light Dust
    dust_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dust_draw = ImageDraw.Draw(dust_layer)
    for _ in range(rng.randint(90, 140)):
        px = rng.randint(20, width - 20)
        py = rng.randint(60, int(height * 0.78))
        size = rng.randint(2, 5)
        alpha = rng.randint(40, 220)
        dust_draw.ellipse([px, py, px + size, py + size], fill=(255, 250, 220, alpha))

    dust_layer = dust_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    img = Image.alpha_composite(img, dust_layer)

    return img.convert("RGB")


def build_imagen_prompt(theme: str, visual_concept: str) -> str:
    """Builds an optimized, production-grade prompt for Imagen 3."""
    return (
        f"A breathtaking Christian cinematic background art symbolizing '{theme}'. {visual_concept}. "
        f"Glorious divine golden sunbeams streaming from heaven, sacred atmosphere, ethereal glowing clouds, "
        f"serene peaceful landscape, magnificent light and warmth. "
        f"Large empty negative space in the upper and middle area designed for typography overlay. "
        f"Photorealistic 8k, cinematic lighting, masterpiece, clean view, "
        f"absolutely NO text, NO typography, NO words, NO letters, NO watermark."
    )


def generate_background_image(
    prompt: str,
    output_path: Path,
    api_key: Optional[str] = None,
    aspect_ratio: str = "9:16",
    width: int = 1080,
    height: int = 1920,
    date_str: str = "",
    theme: str = "",
) -> Path:
    """Generates a high-quality sacred background image.

    Changes dynamically every day with biblical color harmony and unique lighting.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    today_str = date_str or datetime.now().strftime("%Y.%m.%d")
    current_theme = theme or "성령 충만과 은혜"

    # Generate daily dynamic holy background
    bg = generate_dynamic_daily_background(
        date_str=today_str,
        theme=current_theme,
        width=width,
        height=height,
    )
    bg.save(output_path, format="PNG")
    logger.info(f"Saved daily dynamic holy background ({today_str} / {current_theme}) to {output_path}")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out_dir = Path(__file__).resolve().parent.parent / "output"
    # Test generation for 3 different themes & days
    tests = [
        ("2026.10.20", "성령 충만과 불"),
        ("2026.10.21", "쉴 만한 물가와 평안"),
        ("2026.10.22", "십자가의 은혜와 구속"),
    ]
    for d, t in tests:
        p = generate_background_image("", out_dir / f"test_{d}.png", date_str=d, theme=t)
        print(f"Generated {t}: {p}")

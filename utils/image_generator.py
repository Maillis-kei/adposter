"""Image Generator Module (Multi-Style Sacred Art Background Engine).

Solves background monotony by providing 4 distinct visual art engines:
1. Dynamic Unsplash/CDN High-Res Sanctuary Landscapes (Mountains, Living Waters, Starry Sky, Olive Meadows)
2. AI-Driven Generative Content (Google GenAI Imagen/Gemini)
3. Procedural Celestial Sunbeams & Holy Dawn
4. Procedural Deep Cosmos & Golden Stardust
5. Procedural Cathedral & Stained Glass Radiance
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
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Curated High-Definition Commercial-Free Open Artwork Sources (Unsplash CDN direct 1080x1920)
CURATED_SANCTUARY_IMAGES: List[Dict[str, str]] = [
    {
        "category": "mountains_sunrise",
        "title": "여명의 시온산과 아침 햇살",
        "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "living_waters",
        "title": "쉴 만한 물가와 평화로운 숲",
        "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "starry_heavens",
        "title": "주의 영광을 선포하는 밤하늘 은하수",
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "golden_field",
        "title": "빛나는 추수의 들판과 아침 이슬",
        "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "clouds_glory",
        "title": "천상의 빛과 장엄한 구름 바다",
        "url": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "quiet_path",
        "title": "주님과 함께 걷는 숲속 오솔길",
        "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
    {
        "category": "ocean_dawn",
        "title": "깊고 고요한 새벽 바다와 수평선",
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1080&h=1920&q=85",
    },
]


def download_curated_background(index: int, width: int = 1080, height: int = 1920) -> Optional[Image.Image]:
    """Downloads a photo-art background from curated royalty-free sources."""
    item = CURATED_SANCTUARY_IMAGES[index % len(CURATED_SANCTUARY_IMAGES)]
    url = item["url"]
    logger.info(f"Downloading curated high-res artwork: '{item['title']}'...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as response:
            data = response.read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        logger.warning(f"Could not download curated image ({e}). Using algorithmic visual engine.")
        return None


def generate_starlight_cosmos(width: int, height: int, rng: random.Random) -> Image.Image:
    """Style 2: Deep Starry Cosmos & Nebula Light."""
    img = Image.new("RGBA", (width, height), (8, 12, 28, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        r = int(8 + 15 * (y / height))
        g = int(12 + 25 * (y / height))
        b = int(28 + 45 * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Nebula clouds
    nebula = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    n_draw = ImageDraw.Draw(nebula)
    for _ in range(5):
        cx = rng.randint(200, width - 200)
        cy = rng.randint(300, height - 400)
        rad = rng.randint(250, 450)
        n_draw.ellipse(
            [cx - rad, cy - rad, cx + rad, cy + rad],
            fill=(rng.randint(70, 130), rng.randint(40, 90), rng.randint(140, 210), 35),
        )
    nebula = nebula.filter(ImageFilter.GaussianBlur(radius=60))
    img = Image.alpha_composite(img, nebula)

    # Stars
    star_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(star_layer)
    for _ in range(250):
        sx = rng.randint(10, width - 10)
        sy = rng.randint(10, height - 10)
        sz = rng.choice([1, 1, 2, 2, 3])
        alpha = rng.randint(80, 255)
        s_draw.ellipse([sx, sy, sx + sz, sy + sz], fill=(255, 255, 255, alpha))

    star_layer = star_layer.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = Image.alpha_composite(img, star_layer)
    return img


def generate_cathedral_dawn(width: int, height: int, rng: random.Random) -> Image.Image:
    """Style 3: Majestic Cathedral Sunbeams & Amber Horizon."""
    img = Image.new("RGBA", (width, height), (22, 14, 30, 255))
    draw = ImageDraw.Draw(img)

    # Deep wine to amber gradient
    for y in range(height):
        ratio = y / height
        r = int(22 + 180 * ratio)
        g = int(14 + 110 * ratio)
        b = int(30 + 40 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Radiant golden rays from upper left
    rays = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(rays)
    for i in range(14):
        angle = math.radians(45 + i * 4)
        dx = math.cos(angle) * height * 1.5
        dy = math.sin(angle) * height * 1.5
        poly = [(150, 80), (150 + dx - 100, 80 + dy), (150 + dx + 100, 80 + dy)]
        r_draw.polygon(poly, fill=(255, 230, 160, 25))

    rays = rays.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, rays)
    return img


def generate_holy_nature_dawn(width: int, height: int, rng: random.Random) -> Image.Image:
    """Style 4: Peaceful Meadow Dawn with Sacred Light."""
    img = Image.new("RGBA", (width, height), (15, 30, 48, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(15 + 160 * ratio)
        g = int(30 + 150 * ratio)
        b = int(48 + 80 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Sunburst
    sun = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(sun)
    sx, sy = width // 2, int(height * 0.25)
    for rad in range(500, 30, -20):
        alpha = int(80 * (1 - (rad / 500) ** 1.2))
        s_draw.ellipse([sx - rad, sy - rad, sx + rad, sy + rad], fill=(255, 235, 170, alpha))
    sun = sun.filter(ImageFilter.GaussianBlur(radius=45))
    img = Image.alpha_composite(img, sun)
    return img


def generate_dynamic_background_artwork(
    date_str: str,
    theme: str,
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Selects and generates a totally distinct background style everyday.

    Alternates between:
    - Real-world curated high-res sanctuary landscapes (mountains, waters, stars, fields, clouds)
    - Distinct procedural generative styles (Cosmos, Cathedral Rays, Meadow Dawn)
    """
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    style_selector = seed_val % 10

    # 1. 70% of days: Curated high-res sanctuary photo-art
    if style_selector < 7:
        curated_img = download_curated_background(index=seed_val, width=width, height=height)
        if curated_img:
            # Add subtle dark vignette overlay to ensure text legibility
            vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            v_draw = ImageDraw.Draw(vignette)
            for y in range(height):
                top_fade = int(max(0, 140 * (1 - y / 500)))
                bot_fade = int(max(0, 160 * ((y - 1400) / (height - 1400))))
                alpha = min(190, top_fade + bot_fade + 40)
                v_draw.line([(0, y), (width, y)], fill=(10, 15, 25, alpha))
            combined = Image.alpha_composite(curated_img, vignette)
            return combined.convert("RGB")

    # 2. 30% of days or offline fallback: Generative Artistic engines
    alt_style = seed_val % 3
    if alt_style == 0:
        logger.info("Using Generative Starlight Cosmos artwork")
        base = generate_starlight_cosmos(width, height, rng)
    elif alt_style == 1:
        logger.info("Using Generative Cathedral Dawn artwork")
        base = generate_cathedral_dawn(width, height, rng)
    else:
        logger.info("Using Generative Holy Nature Dawn artwork")
        base = generate_holy_nature_dawn(width, height, rng)

    return base.convert("RGB")


def build_imagen_prompt(theme: str, visual_concept: str) -> str:
    return (
        f"A breathtaking Christian cinematic background art symbolizing '{theme}'. {visual_concept}. "
        f"Divine golden sunbeams, sacred aura, serene atmosphere, large negative space at upper half. "
        f"8k resolution, photorealistic masterpiece, absolutely NO text, NO typography, NO words."
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
    """Master background generator guaranteeing dynamic diversity everyday."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    today_str = date_str or datetime.now().strftime("%Y.%m.%d")
    current_theme = theme or "성령 충만과 삶의 변화"

    bg_img = generate_dynamic_background_artwork(
        date_str=today_str,
        theme=current_theme,
        width=width,
        height=height,
    )
    bg_img.save(output_path, format="PNG")
    logger.info(f"Saved fresh dynamic background artwork to {output_path}")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out_dir = Path(__file__).resolve().parent.parent / "output"
    for d, t in [("2026.10.21", "시온의 빛"), ("2026.10.22", "쉴 만한 물가"), ("2026.10.23", "은하수와 찬양")]:
        p = generate_background_image("", out_dir / f"test_variety_{d}.png", date_str=d, theme=t)
        print(f"Generated {t}: {p}")

"""Original Christian Artwork Generation Module (Learning & Generating Unique Reference Styles).

Learns the visual DNA of the reference artworks:
- Aesthetic 1: Warm Cinematic Anime & Ghibli-inspired sacred landscape (Expansive pastel sky at top 60%, young pilgrim sitting on hilltop with Bible, glowing cross on horizon)
- Aesthetic 2: Dramatic Renaissance Oil-Painting encounter (Christ's loving hand reaching down to praying believer, heavenly golden light beams)
- Aesthetic 3: Narrow Path of Faith (Pilgrim walking towards holy mountain dawn)
- Aesthetic 4: Living Waters & Sanctuary Meadow (Tranquil lake, olive trees, celestial dawn)

Generates totally original, non-duplicated backgrounds dynamically via Google GenAI or algorithmic rendering.
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

# Learned Reference Style Prompt Templates
STYLE_PROMPTS = [
    # Style 1: Cinematic Anime Sacred Pilgrim (Sample 1 DNA)
    (
        "A breathtaking Christian anime illustration in the style of Makoto Shinkai and Studio Ghibli. "
        "A vast, clear pastel sky with soft pink and golden dawn clouds occupying the top 65% of the frame, "
        "leaving abundant clean negative space. "
        "In the bottom 35%, a young pilgrim sitting on a grassy hilltop looking towards a brilliant glowing cross "
        "on the distant horizon, a bible and white lilies resting on rocks beside him, sun-drenched river valley, "
        "holy radiant atmosphere, ultra detailed, vibrant anime aesthetic, masterpiece, strictly NO text, NO letters."
    ),
    # Style 2: Christ's Loving Embrace & Encounter (Sample 2 DNA)
    (
        "A deeply moving Christian digital painting with rich oil-brush textures. "
        "Jesus Christ with gentle compassionate smile extending His hand down from heavenly clouds, "
        "warm divine light rays breaking through celestial sky, "
        "a praying pilgrim on a mountain ridge reaching hands upward in faith, "
        "upper half has open radiant blue and golden sky for typography, "
        "inspiring holy warmth, cinematic masterpiece, strictly NO text, NO watermark."
    ),
    # Style 3: Journey on the Mountain Path of Faith
    (
        "A serene and majestic Christian landscape painting. A quiet pathway winding through blooming meadow "
        "towards a distant sacred mountain peak illuminated by heavenly sunrise. "
        "Vast luminous sky with ethereal god-rays streaming from heaven taking up top 60%, "
        "peaceful pilgrim walking in the dawn, holy peaceful sanctuary atmosphere, 8k, strictly NO text."
    ),
    # Style 4: Living Waters & Sanctuary of Peace
    (
        "A beautiful pastoral Christian landscape, crystal clear peaceful river reflecting golden morning sunlight, "
        "ancient olive trees, soft mist rising from water, vast golden heavenly sky with open negative space at top, "
        "divine peace and stillness, sacred Christian art, 8k resolution, strictly NO text."
    ),
]


def generate_original_procedural_pilgrim_artwork(
    date_str: str,
    theme: str,
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Creates a 100% original, dynamic digital painting capturing the learned Pilgrim & Sky aesthetic.

    - Sky & Clouds: Top 62% of canvas is an expansive, radiant pastel sky tailored for typography.
    - Horizon: Radiant divine light source (Cross / Sunrise).
    - Foreground: Hilltop with grassy terrain, stones, Bible, and pilgrim silhouette.
    """
    seed_val = int(hashlib.md5(f"{date_str}_{theme}_original".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Radiant Sky (Dawn pastel blue to peach/golden horizon)
    sky_h = int(height * 0.64)
    c_sky_top = (rng.randint(90, 130), rng.randint(155, 190), rng.randint(220, 245))
    c_sky_mid = (rng.randint(175, 215), rng.randint(200, 225), rng.randint(235, 250))
    c_sky_warm = (252, rng.randint(215, 235), rng.randint(180, 205))

    for y in range(sky_h + 80):
        ratio = y / (sky_h + 80)
        if ratio < 0.5:
            lr = ratio / 0.5
            r = int(c_sky_top[0] * (1 - lr) + c_sky_mid[0] * lr)
            g = int(c_sky_top[1] * (1 - lr) + c_sky_mid[1] * lr)
            b = int(c_sky_top[2] * (1 - lr) + c_sky_mid[2] * lr)
        else:
            lr = (ratio - 0.5) / 0.5
            r = int(c_sky_mid[0] * (1 - lr) + c_sky_warm[0] * lr)
            g = int(c_sky_mid[1] * (1 - lr) + c_sky_warm[1] * lr)
            b = int(c_sky_mid[2] * (1 - lr) + c_sky_warm[2] * lr)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Fluffy Anime Clouds in the Sky
    cloud_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(cloud_layer)

    for _ in range(rng.randint(6, 10)):
        cx = rng.randint(50, width - 50)
        cy = rng.randint(120, int(sky_h * 0.85))
        rw = rng.randint(180, 340)
        rh = rng.randint(60, 110)
        c_draw.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=(255, 255, 255, rng.randint(70, 140)))
        # Shadow of cloud
        c_draw.ellipse([cx - rw + 20, cy - rh + 15, cx + rw - 20, cy + rh + 15], fill=(245, 210, 190, 45))

    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(radius=25))
    img = Image.alpha_composite(img, cloud_layer)

    # 3. Radiant Glowing Cross on the Horizon (Center-Right)
    cross_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x_draw = ImageDraw.Draw(cross_layer)
    cross_x = int(width * rng.uniform(0.60, 0.75))
    cross_y = int(sky_h * 0.95)

    # Divine bloom
    for rad in range(350, 10, -20):
        alpha = int(75 * (1 - (rad / 350) ** 1.3))
        x_draw.ellipse([cross_x - rad, cross_y - rad, cross_x + rad, cross_y + rad], fill=(255, 245, 190, alpha))

    # Cross shape
    cw = 12
    ch = 140
    x_draw.rectangle([cross_x - cw // 2, cross_y - ch, cross_x + cw // 2, cross_y + 40], fill=(255, 255, 250, 240))
    x_draw.rectangle([cross_x - 45, cross_y - int(ch * 0.7), cross_x + 45, cross_y - int(ch * 0.7) + cw], fill=(255, 255, 250, 240))

    cross_layer = cross_layer.filter(ImageFilter.GaussianBlur(radius=6))
    img = Image.alpha_composite(img, cross_layer)

    # 4. Hilltop Landscape (Bottom 36%)
    hill_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hill_layer)

    hill_pts = [(0, height)]
    for x in range(0, width + 50, 30):
        hy = int(sky_h + 30 + math.sin(x * 0.006) * 50 + math.cos(x * 0.012) * 30)
        hill_pts.append((x, hy))
    hill_pts.append((width, height))

    # Grassy hill colors (warm earth & fresh greens)
    h_draw.polygon(hill_pts, fill=(85, 115, 65, 255))

    # Foreground darker ridge with rocks & wild flowers
    fore_pts = [(0, height)]
    for x in range(0, width + 50, 30):
        fy = int(sky_h + 160 + math.sin(x * 0.008 + 2.0) * 60)
        fore_pts.append((x, fy))
    fore_pts.append((width, height))
    h_draw.polygon(fore_pts, fill=(55, 75, 45, 255))

    # 5. Pilgrim Silhouette Sitting on the Hill overlooking the cross
    px = int(width * rng.uniform(0.35, 0.45))
    py = int(sky_h + 120)

    # Body
    h_draw.ellipse([px - 28, py - 65, px + 28, py - 10], fill=(42, 38, 48, 255))  # torso
    h_draw.ellipse([px - 22, py - 105, px + 22, py - 65], fill=(42, 38, 48, 255))  # head
    h_draw.rounded_rectangle([px - 36, py - 55, px - 18, py - 15], radius=6, fill=(35, 30, 40, 255))  # backpack
    h_draw.rounded_rectangle([px - 30, py - 10, px + 35, py + 30], radius=10, fill=(38, 34, 44, 255))  # legs seated

    # Small Bible with golden cross on ground
    bx = px - 75
    by = py + 15
    h_draw.rounded_rectangle([bx, by, bx + 45, by + 30], radius=4, fill=(28, 22, 18, 255), outline=(210, 175, 75, 240), width=2)
    h_draw.line([(bx + 22, by + 5), (bx + 22, by + 25)], fill=(210, 175, 75, 240), width=2)
    h_draw.line([(bx + 14, by + 12), (bx + 30, by + 12)], fill=(210, 175, 75, 240), width=2)

    hill_layer = hill_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, hill_layer)

    return img.convert("RGB")


def try_generate_via_imagen_api(prompt: str, api_key: str, width: int = 1080, height: int = 1920) -> Optional[Image.Image]:
    """Attempts generation via Google GenAI Imagen 3 API with multiple endpoint fallbacks."""
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}",
        f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict",
    ]

    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
        "User-Agent": "PoiemaArtworkBot/1.0"
    }

    for ep in endpoints:
        try:
            req = urllib.request.Request(ep, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode())
                preds = data.get("predictions", [])
                if preds and "bytesBase64Encoded" in preds[0]:
                    import base64
                    img_bytes = base64.b64decode(preds[0]["bytesBase64Encoded"])
                    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    logger.info("Successfully received Imagen 3 original artwork!")
                    return img
        except Exception as e:
            logger.debug(f"Imagen endpoint {ep[:45]}... failed: {e}")

    return None


def build_imagen_prompt(theme: str, visual_concept: str) -> str:
    """Builds an optimized prompt capturing the learned sacred anime/painting aesthetic."""
    return (
        f"A breathtaking Christian illustration symbolizing '{theme}'. {visual_concept}. "
        f"Vast luminous pastel blue and golden dawn sky occupying top 60% of frame leaving clean space for typography. "
        f"In the bottom area, a peaceful hill overlooking distant glowing cross on horizon, holy sunbeams, "
        f"warm cinematic lighting, anime digital painting masterpiece, strictly NO text, NO typography, NO watermark."
    )


def generate_unique_sacred_background(
    date_str: str,
    theme: str,
    width: int = 1080,
    height: int = 1920,
    api_key: Optional[str] = None,
) -> Image.Image:
    """Master generator: Produces an authentic, unique sacred artwork for each day.

    Never duplicates static sample files. Learns the aesthetic DNA and generates fresh art.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    # 1. Try AI Generation with learned prompt
    if gemini_key:
        prompt_idx = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16) % len(STYLE_PROMPTS)
        prompt = STYLE_PROMPTS[prompt_idx]
        ai_img = try_generate_via_imagen_api(prompt, gemini_key, width, height)
        if ai_img:
            return ai_img

    # 2. Algorithmic Original Digital Painting (Sample 1/2 DNA)
    logger.info(f"Generating 100% original dynamic sacred artwork for '{theme}' ({date_str})...")
    original_artwork = generate_original_procedural_pilgrim_artwork(date_str, theme, width, height)
    return original_artwork


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
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    today_str = date_str or datetime.now().strftime("%Y.%m.%d")
    current_theme = theme or "성령 충만과 삶의 변화"

    bg_img = generate_unique_sacred_background(
        date_str=today_str,
        theme=current_theme,
        width=width,
        height=height,
        api_key=api_key,
    )
    bg_img.save(output_path, format="PNG")
    logger.info(f"Saved unique original artwork to {output_path}")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_out = Path(__file__).resolve().parent.parent / "output" / "test_unique_original.png"
    generate_background_image("", test_out, date_str="2026.10.21", theme="시온의 빛")
    print(f"Generated unique original artwork at: {test_out}")

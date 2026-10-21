"""Aesthetic Background Generation Module (Multi-Genre Christian Artwork Engine).

Supports 5 diverse visual genres tailored to user desires:
1. Cinematic & Editorial Photography (실사형 사진):
   - Natural 35mm sunlight, serene sanctuary, olive branches on wood, calm lake at sunrise.
2. Modern Christian Illustration (감성 일러스트):
   - Warm gouache & oil-pastel textures, peaceful pastoral landscapes, gentle brushstrokes.
3. Sacred Symbolic Art (상징 및 심벌 아트):
   - Radiant Holy Spirit Dove, Olive Branches of Peace, Living Waters, Glowing Cross, Golden Wheat.
4. Anime Sacred Aesthetic (감성 애니메이션):
   - Vast luminous pastel skies, Makoto Shinkai / Ghibli inspired celestial clouds, heavenly light.
5. Whimsical Storybook Art (따뜻한 동화 그림):
   - Children's storybook watercolor, gentle shepherd & flock, cozy peaceful biblical meadow.

Uses Google Imagen 3 official SDK (`client.models.generate_images`), and features a rich procedural
sacred illustration engine (Dove, Olive, Rays, Hills) so it is NEVER a plain monochrome background!
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


# ---------------------------------------------------------------------------
# 5 Rich Visual Genres for Imagen 3
# ---------------------------------------------------------------------------

VISUAL_GENRES = {
    "photography": (
        "Breathtaking editorial still-life photography. "
        "A peaceful sanctuary setting bathed in warm morning sunlight streaming in through tall arched windows, "
        "natural wooden texture, delicate fresh olive branches and white lilies casting gentle shadows, "
        "warm glowing ambiance, highly aesthetic, 35mm film photography, 8k resolution, "
        "ample negative space in upper area for Korean calligraphy, strictly NO text, NO letters, NO watermark."
    ),
    "illustration": (
        "A stunning, warm modern Christian editorial illustration with rich oil pastel and gouache textures. "
        "A peaceful sacred landscape under a majestic dawn, radiant divine light filtering softly through gentle trees, "
        "serene pathway of peace, comforting earthy pastel tones, artistic masterpiece, "
        "plenty of serene negative space, strictly NO text, NO letters, NO characters."
    ),
    "symbolic": (
        "An exquisite sacred Christian symbolic artwork. "
        "A radiant white dove of the Holy Spirit gracefully descending with an olive branch of peace, "
        "surrounded by subtle celestial golden light beams and soft glowing particles, "
        "majestic, deeply spiritual and reverent, artistic minimalism, beautiful negative space, "
        "masterpiece quality, strictly NO text, NO letters, NO watermark."
    ),
    "anime": (
        "A breathtaking anime sacred background in the style of Makoto Shinkai and Studio Ghibli. "
        "A vast luminous sky with breathtaking dawn clouds painted in gentle pastel blue, peach, and lavender, "
        "celestial god-rays breaking through heavenly clouds onto rolling tranquil hills below, "
        "holy peaceful atmosphere, vibrant and emotionally moving, top 60% clean for typography, "
        "strictly NO text, NO letters, NO watermark."
    ),
    "storybook": (
        "A heartwarming, cozy picture-book storybook watercolor illustration. "
        "Soft whimsical Christian scenery with a gentle shepherd guiding peaceful sheep across sun-drenched rolling green hills, "
        "wildflowers blooming, soft puffy clouds in a warm golden morning sky, comforting and gentle aesthetic, "
        "airy composition with negative space for Korean calligraphy, strictly NO text, NO letters."
    ),
}


def build_imagen_prompt(theme: str, visual_concept: str = "", form_factor: str = "verse_card") -> str:
    """Dynamically rotates and blends visual genres to produce rich, imaginative art."""
    # Seed by theme to ensure deterministic yet diverse choices
    seed_idx = int(hashlib.md5(f"{theme}_{datetime.now().strftime('%Y%m%d')}".encode()).hexdigest(), 16)
    genre_keys = list(VISUAL_GENRES.keys())
    chosen_genre = genre_keys[seed_idx % len(genre_keys)]
    base_genre_prompt = VISUAL_GENRES[chosen_genre]

    concept_str = f"Theme: '{theme}'. {visual_concept}." if visual_concept else f"Theme: '{theme}'."
    logger.info(f"[Visual Art Director] Selected Visual Genre: '{chosen_genre.upper()}' for '{theme}'")

    return f"{concept_str} {base_genre_prompt}"


# ---------------------------------------------------------------------------
# Rich Procedural Artwork Engine (NEVER PLAIN MONOCHROME!)
# ---------------------------------------------------------------------------

def _draw_sacred_dove_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    """Draws a graceful descending dove of the Holy Spirit with soft glowing wings."""
    # Wing Left
    w_left = [
        (cx, cy),
        (cx - int(70 * scale), cy - int(55 * scale)),
        (cx - int(120 * scale), cy - int(95 * scale)),
        (cx - int(150 * scale), cy - int(75 * scale)),
        (cx - int(90 * scale), cy - int(30 * scale)),
        (cx - int(30 * scale), cy - int(10 * scale)),
    ]
    # Wing Right
    w_right = [
        (cx, cy),
        (cx + int(70 * scale), cy - int(55 * scale)),
        (cx + int(120 * scale), cy - int(95 * scale)),
        (cx + int(150 * scale), cy - int(75 * scale)),
        (cx + int(90 * scale), cy - int(30 * scale)),
        (cx + int(30 * scale), cy - int(10 * scale)),
    ]
    # Body & Tail
    body = [
        (cx, cy - int(25 * scale)),    # head
        (cx + int(12 * scale), cy),
        (cx + int(15 * scale), cy + int(45 * scale)),
        (cx + int(28 * scale), cy + int(90 * scale)),  # tail right
        (cx, cy + int(75 * scale)),                    # tail center
        (cx - int(28 * scale), cy + int(90 * scale)),  # tail left
        (cx - int(15 * scale), cy + int(45 * scale)),
        (cx - int(12 * scale), cy),
    ]

    # Soft glowing dove color (warm white with soft golden rim)
    draw.polygon(w_left, fill=(255, 253, 245, 180))
    draw.polygon(w_right, fill=(255, 253, 245, 180))
    draw.polygon(body, fill=(255, 255, 250, 220))
    # Head
    draw.ellipse(
        [cx - int(10 * scale), cy - int(35 * scale), cx + int(10 * scale), cy - int(15 * scale)],
        fill=(255, 255, 250, 230),
    )


def _draw_olive_branch(draw: ImageDraw.ImageDraw, sx: int, sy: int, length: int = 220) -> None:
    """Draws a delicate, artistic watercolor olive sprig."""
    stem_pts = []
    for i in range(12):
        t = i / 11
        x = sx + int(t * length)
        y = sy + int(math.sin(t * 3.14) * 35)
        stem_pts.append((x, y))
        
        # Leaves along the stem
        if i % 2 == 1:
            lx = x
            ly = y - 18
            # Olive leaf
            draw.ellipse([lx - 16, ly - 8, lx + 16, ly + 8], fill=(135, 155, 120, 150))
            draw.ellipse([lx - 12, ly + 14, lx + 12, ly + 26], fill=(115, 138, 102, 140))

    if len(stem_pts) > 1:
        draw.line(stem_pts, fill=(110, 100, 85, 180), width=3)


def generate_rich_procedural_sacred_artwork(
    date_str: str,
    theme: str,
    form_factor: str = "verse_card",
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Generates an illustrative, richly detailed Christian artwork.
    
    Contains:
    - Celestial Dawn Atmosphere & Light Rays
    - Rolling watercolor hills and wildflower meadow
    - Ascending Holy Spirit Dove & Olive branch
    - Fine art watercolor & paper grain texture
    """
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    # 1. Scenic Color Palette
    palettes = [
        # Dawn Serenity (Sky blue to warm peach dawn)
        {"sky_top": (145, 185, 220), "sky_mid": (235, 215, 200), "sky_dawn": (255, 228, 195), "hill_back": (160, 180, 160), "hill_fore": (105, 135, 105)},
        # Golden Hour Sanctuary (Warm golden ochre to soft lilac)
        {"sky_top": (185, 175, 205), "sky_mid": (245, 210, 180), "sky_dawn": (255, 235, 190), "hill_back": (180, 160, 135), "hill_fore": (125, 105, 80)},
        # Fresh Living Waters (Misty sage to crystal morning)
        {"sky_top": (160, 200, 205), "sky_mid": (220, 235, 225), "sky_dawn": (250, 245, 220), "hill_back": (140, 175, 155), "hill_fore": (85, 120, 95)},
    ]
    pal = palettes[seed_val % len(palettes)]

    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 2. Painterly Sky Gradient (Top 65%)
    sky_h = int(height * 0.72)
    for y in range(sky_h):
        ratio = y / sky_h
        if ratio < 0.5:
            lr = ratio / 0.5
            r = int(pal["sky_top"][0] * (1 - lr) + pal["sky_mid"][0] * lr)
            g = int(pal["sky_top"][1] * (1 - lr) + pal["sky_mid"][1] * lr)
            b = int(pal["sky_top"][2] * (1 - lr) + pal["sky_mid"][2] * lr)
        else:
            lr = (ratio - 0.5) / 0.5
            r = int(pal["sky_mid"][0] * (1 - lr) + pal["sky_dawn"][0] * lr)
            g = int(pal["sky_mid"][1] * (1 - lr) + pal["sky_dawn"][1] * lr)
            b = int(pal["sky_mid"][2] * (1 - lr) + pal["sky_dawn"][2] * lr)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 3. Celestial God-Rays (Streaming down gently)
    ray_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(ray_layer)
    sun_x = int(width * rng.uniform(0.35, 0.65))
    sun_y = int(sky_h * 0.35)

    # Sun divine glow
    for rad in range(400, 20, -30):
        alpha = int(55 * (1 - (rad / 400) ** 1.2))
        r_draw.ellipse([sun_x - rad, sun_y - rad, sun_x + rad, sun_y + rad], fill=(255, 250, 225, alpha))

    # Beams of light
    for i in range(-5, 6):
        angle = i * 0.12
        ray_pts = [
            (sun_x, sun_y),
            (sun_x + int(math.sin(angle - 0.04) * height), sun_y + int(math.cos(angle - 0.04) * height)),
            (sun_x + int(math.sin(angle + 0.04) * height), sun_y + int(math.cos(angle + 0.04) * height)),
        ]
        r_draw.polygon(ray_pts, fill=(255, 252, 235, rng.randint(20, 45)))

    ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img, ray_layer)

    # 4. Sacred Dove of the Holy Spirit (Center top-right or center-left)
    dove_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dove_layer)
    dove_x = sun_x + int(rng.choice([-1, 1]) * rng.randint(80, 180))
    dove_y = sun_y - rng.randint(60, 120)
    _draw_sacred_dove_silhouette(d_draw, dove_x, dove_y, scale=rng.uniform(0.9, 1.25))
    dove_layer = dove_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, dove_layer)

    # 5. Distant Watercolor Mountain & Rolling Hills (Bottom 35%)
    hill_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hill_layer)

    # Distant hill
    back_pts = [(0, height)]
    for x in range(0, width + 50, 40):
        hy = int(sky_h - 40 + math.sin(x * 0.005 + 1.2) * 55)
        back_pts.append((x, hy))
    back_pts.append((width, height))
    h_draw.polygon(back_pts, fill=(*pal["hill_back"], 210))

    # Foreground hill with warmth
    fore_pts = [(0, height)]
    for x in range(0, width + 50, 30):
        fy = int(sky_h + 80 + math.sin(x * 0.007 + 3.0) * 65)
        fore_pts.append((x, fy))
    fore_pts.append((width, height))
    h_draw.polygon(fore_pts, fill=(*pal["hill_fore"], 240))

    # Delicate Wildflowers & Olive Sprigs at bottom
    for _ in range(35):
        fl_x = rng.randint(20, width - 20)
        fl_y = rng.randint(int(sky_h + 120), height - 40)
        fl_col = rng.choice([(255, 255, 255, 200), (255, 230, 160, 200), (240, 205, 220, 180)])
        h_draw.ellipse([fl_x - 4, fl_y - 4, fl_x + 4, fl_y + 4], fill=fl_col)

    # Olive branch silhouette across bottom corner
    _draw_olive_branch(h_draw, sx=60, sy=height - 180, length=280)

    hill_layer = hill_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, hill_layer)

    # 6. Fine Art Paper & Watercolor Bleed Grain
    grain_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grain_bytes = bytearray(width * height * 4)
    for idx in range(0, len(grain_bytes), 4):
        val = rng.randint(0, 22)
        grain_bytes[idx] = 200
        grain_bytes[idx + 1] = 195
        grain_bytes[idx + 2] = 185
        grain_bytes[idx + 3] = val
    grain_img = Image.frombytes("RGBA", (width, height), bytes(grain_bytes))
    grain_img = grain_img.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = Image.alpha_composite(img, grain_img)

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Google GenAI Official SDK Imagen 3 Generator
# ---------------------------------------------------------------------------

def try_generate_via_google_genai_sdk(
    prompt: str,
    api_key: str,
    width: int = 1080,
    height: int = 1920,
) -> Optional[Image.Image]:
    """Calls Google Imagen 3 using official `google-genai` SDK."""
    try:
        from google import genai
        from google.genai import types

        logger.info("[Imagen 3] Initializing Google GenAI Client for image generation...")
        client = genai.Client(api_key=api_key)

        # Standard Google GenAI SDK call for Imagen 3
        result = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16",
                output_mime_type="image/png",
            ),
        )

        if result and result.generated_images:
            img_bytes = result.generated_images[0].image.image_bytes
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            logger.info("✓ [Imagen 3] Successfully generated breathtaking artwork via Official SDK!")
            return img

    except Exception as e:
        logger.warning(f"[Imagen 3 SDK] SDK call failed ({e}). Trying REST fallback...")

    # Secondary REST fallback with detailed error tracking
    endpoints = [
        f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}",
        "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict",
    ]

    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "9:16"}
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
        "User-Agent": "PoiemaArtworkBot/3.0"
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
                    logger.info("✓ [Imagen 3 REST] Successfully generated artwork via REST endpoint!")
                    return img
        except Exception as e:
            logger.warning(f"[Imagen 3 REST] Endpoint failed: {e}")

    return None


def generate_unique_sacred_background(
    date_str: str,
    theme: str,
    form_factor: str = "verse_card",
    visual_concept: str = "",
    width: int = 1080,
    height: int = 1920,
    api_key: Optional[str] = None,
) -> Image.Image:
    """Master Artwork Dispatcher:
    
    1. Tries Google Imagen 3 (Photography, Illustration, Symbolic, Anime, Storybook).
    2. Falls back to bespoke procedural Christian painting (Dove, Olive, Light Rays, Rolling Hills).
       NEVER a plain monochrome canvas!
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    if gemini_key:
        prompt = build_imagen_prompt(theme, visual_concept=visual_concept, form_factor=form_factor)
        ai_img = try_generate_via_google_genai_sdk(prompt, gemini_key, width, height)
        if ai_img:
            return ai_img

    logger.info(f"[Visual Art Director] Creating rich procedural Christian painting for '{theme}'...")
    return generate_rich_procedural_sacred_artwork(
        date_str=date_str,
        theme=theme,
        form_factor=form_factor,
        width=width,
        height=height,
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
    form_factor: str = "verse_card",
    visual_concept: str = "",
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    today_str = date_str or datetime.now().strftime("%Y.%m.%d")
    current_theme = theme or "성령 충만과 삶의 변화"

    bg_img = generate_unique_sacred_background(
        date_str=today_str,
        theme=current_theme,
        form_factor=form_factor,
        visual_concept=visual_concept,
        width=width,
        height=height,
        api_key=api_key,
    )
    bg_img.save(output_path, format="PNG")
    logger.info(f"Saved rich background artwork to {output_path}")
    return output_path

"""Aesthetic Background Generation Module (Powered by Pollinations FLUX.1 AI & Fallback Art).

Official Engine: Pollinations.ai (https://pollinations.ai)
- Model: FLUX.1 (Black Forest Labs state-of-the-art text-to-image engine)
- 100% Free, Zero-API-Key, Zero-Config, Instant high-quality Christian artwork.
- Supports 5 diverse visual genres:
  1. Photography (실사 35mm 감성 사진)
  2. Illustration (감성 수채화/오일파스텔 일러스트)
  3. Symbolic (성령의 비둘기, 십자가, 올리브 심벌 아트)
  4. Anime (지브리/신카이 마코토 감성 맑은 하늘)
  5. Storybook (따뜻한 동화책 그림, 목자와 양 떼)
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
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageOps

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 5 Rich Visual Genres for FLUX.1
# ---------------------------------------------------------------------------

VISUAL_GENRES = {
    "photography": (
        "Breathtaking editorial still-life photography for Christian background. "
        "A peaceful sanctuary room bathed in warm morning sunlight streaming through arched windows, "
        "natural aged wood, fresh olive branches and white lilies casting soft gentle shadows, "
        "warm glowing ambiance, highly aesthetic, 35mm cinematic film photo, spacious negative space at top, "
        "masterpiece, strictly NO text, NO letters, NO words, NO watermark."
    ),
    "illustration": (
        "A stunning, warm modern Christian editorial illustration with rich gouache and oil pastel textures. "
        "A peaceful sacred landscape under a majestic dawn, radiant divine light filtering softly through gentle trees, "
        "serene pathway of peace, comforting earthy pastel tones, artistic masterpiece, "
        "clean negative space for typography, strictly NO text, NO letters, NO characters."
    ),
    "symbolic": (
        "An exquisite sacred Christian symbolic artwork. "
        "A glowing radiant white dove of the Holy Spirit gracefully descending with an olive branch of peace, "
        "surrounded by soft celestial golden light beams and subtle holy particles, "
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


def build_flux_prompt(theme: str, visual_concept: str = "", form_factor: str = "verse_card", forced_genre: Optional[str] = None) -> Tuple[str, str]:
    """Dynamically rotates and blends visual genres to produce rich FLUX.1 prompts."""
    genre_keys = list(VISUAL_GENRES.keys())
    if forced_genre and forced_genre.lower() in VISUAL_GENRES:
        chosen_genre = forced_genre.lower()
    else:
        seed_idx = int(hashlib.md5(f"{theme}_{datetime.now().strftime('%Y%m%d%H')}".encode()).hexdigest(), 16)
        chosen_genre = genre_keys[seed_idx % len(genre_keys)]
    
    base_genre_prompt = VISUAL_GENRES[chosen_genre]
    concept_str = f"Christian theme of '{theme}'. {visual_concept}." if visual_concept else f"Christian theme of '{theme}'."
    prompt = f"{concept_str} {base_genre_prompt}"
    return prompt, chosen_genre


def build_imagen_prompt(theme: str, visual_concept: str = "", form_factor: str = "verse_card") -> str:
    """Backward compatibility alias for crew_setup."""
    prompt, _ = build_flux_prompt(theme, visual_concept=visual_concept, form_factor=form_factor)
    return prompt


# ---------------------------------------------------------------------------
# Pollinations FLUX.1 Engine Invocation
# ---------------------------------------------------------------------------

def try_generate_via_pollinations_flux(
    prompt: str,
    seed: int,
    width: int = 1080,
    height: int = 1920,
    timeout: int = 45,
) -> Optional[Image.Image]:
    """Generates a high-resolution artwork via Pollinations.ai FLUX.1 engine."""
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        # Request high-definition aspect ratio
        req_w = 768
        req_h = 1344
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={req_w}&height={req_h}&model=flux&seed={seed}&nologo=true"
        )
        logger.info(f"[Pollinations FLUX.1] Requesting generation (seed: {seed})...")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 PoiemaStationeryBot/1.0"
            )
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            # Upscale/Resize to exact canvas target (1080x1920)
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            logger.info(f"✓ [Pollinations FLUX.1] Successfully generated authentic artwork ({img.size})!")
            return img

    except Exception as e:
        logger.warning(f"[Pollinations FLUX.1] Generation attempt failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Rich Procedural Artwork Fallback Engine
# ---------------------------------------------------------------------------

def _draw_sacred_dove_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    """Draws a graceful descending dove of the Holy Spirit with soft glowing wings."""
    w_left = [
        (cx, cy),
        (cx - int(70 * scale), cy - int(55 * scale)),
        (cx - int(120 * scale), cy - int(95 * scale)),
        (cx - int(150 * scale), cy - int(75 * scale)),
        (cx - int(90 * scale), cy - int(30 * scale)),
        (cx - int(30 * scale), cy - int(10 * scale)),
    ]
    w_right = [
        (cx, cy),
        (cx + int(70 * scale), cy - int(55 * scale)),
        (cx + int(120 * scale), cy - int(95 * scale)),
        (cx + int(150 * scale), cy - int(75 * scale)),
        (cx + int(90 * scale), cy - int(30 * scale)),
        (cx + int(30 * scale), cy - int(10 * scale)),
    ]
    body = [
        (cx, cy - int(25 * scale)),
        (cx + int(12 * scale), cy),
        (cx + int(15 * scale), cy + int(45 * scale)),
        (cx + int(28 * scale), cy + int(90 * scale)),
        (cx, cy + int(75 * scale)),
        (cx - int(28 * scale), cy + int(90 * scale)),
        (cx - int(15 * scale), cy + int(45 * scale)),
        (cx - int(12 * scale), cy),
    ]

    draw.polygon(w_left, fill=(255, 253, 245, 180))
    draw.polygon(w_right, fill=(255, 253, 245, 180))
    draw.polygon(body, fill=(255, 255, 250, 220))
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
        if i % 2 == 1:
            lx = x
            ly = y - 18
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
    """Fallback generator: Produces an illustrative, painterly Christian artwork."""
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    palettes = [
        {"sky_top": (145, 185, 220), "sky_mid": (235, 215, 200), "sky_dawn": (255, 228, 195), "hill_back": (160, 180, 160), "hill_fore": (105, 135, 105)},
        {"sky_top": (185, 175, 205), "sky_mid": (245, 210, 180), "sky_dawn": (255, 235, 190), "hill_back": (180, 160, 135), "hill_fore": (125, 105, 80)},
        {"sky_top": (160, 200, 205), "sky_mid": (220, 235, 225), "sky_dawn": (250, 245, 220), "hill_back": (140, 175, 155), "hill_fore": (85, 120, 95)},
    ]
    pal = palettes[seed_val % len(palettes)]

    img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

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

    ray_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(ray_layer)
    sun_x = int(width * rng.uniform(0.35, 0.65))
    sun_y = int(sky_h * 0.35)

    for rad in range(400, 20, -30):
        alpha = int(55 * (1 - (rad / 400) ** 1.2))
        r_draw.ellipse([sun_x - rad, sun_y - rad, sun_x + rad, sun_y + rad], fill=(255, 250, 225, alpha))

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

    dove_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dove_layer)
    dove_x = sun_x + int(rng.choice([-1, 1]) * rng.randint(80, 180))
    dove_y = sun_y - rng.randint(60, 120)
    _draw_sacred_dove_silhouette(d_draw, dove_x, dove_y, scale=rng.uniform(0.9, 1.25))
    dove_layer = dove_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, dove_layer)

    hill_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hill_layer)

    back_pts = [(0, height)]
    for x in range(0, width + 50, 40):
        hy = int(sky_h - 40 + math.sin(x * 0.005 + 1.2) * 55)
        back_pts.append((x, hy))
    back_pts.append((width, height))
    h_draw.polygon(back_pts, fill=(*pal["hill_back"], 210))

    fore_pts = [(0, height)]
    for x in range(0, width + 50, 30):
        fy = int(sky_h + 80 + math.sin(x * 0.007 + 3.0) * 65)
        fore_pts.append((x, fy))
    fore_pts.append((width, height))
    h_draw.polygon(fore_pts, fill=(*pal["hill_fore"], 240))

    for _ in range(35):
        fl_x = rng.randint(20, width - 20)
        fl_y = rng.randint(int(sky_h + 120), height - 40)
        fl_col = rng.choice([(255, 255, 255, 200), (255, 230, 160, 200), (240, 205, 220, 180)])
        h_draw.ellipse([fl_x - 4, fl_y - 4, fl_x + 4, fl_y + 4], fill=fl_col)

    _draw_olive_branch(h_draw, sx=60, sy=height - 180, length=280)

    hill_layer = hill_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
    img = Image.alpha_composite(img, hill_layer)

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


def _clean_watermark_area(img: Image.Image) -> Image.Image:
    """Safely cleans any watermark residue at bottom right corner if present."""
    w, h = img.size
    # Crop slightly and re-stretch or inpaint bottom edge
    # Seamless bottom edge fade
    bottom_strip = img.crop((w - 220, h - 50, w, h))
    blurred = bottom_strip.filter(ImageFilter.GaussianBlur(radius=8))
    img.paste(blurred, (w - 220, h - 50))
    return img


# ---------------------------------------------------------------------------
# Master Background Dispatcher
# ---------------------------------------------------------------------------

def generate_unique_sacred_background(
    date_str: str,
    theme: str,
    form_factor: str = "verse_card",
    visual_concept: str = "",
    forced_genre: Optional[str] = None,
    engine_choice: str = "auto",
    width: int = 1080,
    height: int = 1920,
    api_key: Optional[str] = None,
) -> Image.Image:
    """Master generator: Uses Local Apple Silicon M2 GPU or Pollinations FLUX.1 AI."""
    seed_val = int(hashlib.md5(f"{date_str}_{theme}".encode()).hexdigest(), 16) % 1000000
    prompt, genre = build_flux_prompt(theme, visual_concept=visual_concept, form_factor=form_factor, forced_genre=forced_genre)

    # 1. Local Apple Silicon M2 GPU Engine (100% Watermark Free)
    if engine_choice == "local":
        try:
            from utils.local_sdxl_engine import generate_local_artwork
            temp_local_out = Path(__file__).resolve().parent.parent / "output" / f"temp_local_{seed_val}.png"
            logger.info(f"[Visual Art Director] Generating 100% Native Artwork via Apple Silicon M2 GPU...")
            res_path = generate_local_artwork(prompt, temp_local_out, width=width, height=height)
            if res_path and res_path.exists():
                local_img = Image.open(res_path).convert("RGB")
                res_path.unlink(missing_ok=True)
                return local_img
        except Exception as e:
            logger.warning(f"Local M2 engine failed: {e}. Falling back...")

    # 2. Pollinations FLUX.1 Engine with Watermark Cleaning
    logger.info(f"[Visual Art Director] Requesting FLUX.1 AI with genre: '{genre.upper()}'...")
    ai_img = try_generate_via_pollinations_flux(
        prompt=prompt,
        seed=seed_val,
        width=width,
        height=height,
    )
    if ai_img is not None:
        return _clean_watermark_area(ai_img)

    # 3. Rich Procedural Painting Fallback
    logger.info(f"[Visual Art Director] Using rich procedural Christian painting for '{theme}'...")
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
    forced_genre: Optional[str] = None,
    engine_choice: str = "auto",
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
        forced_genre=forced_genre,
        engine_choice=engine_choice,
        width=width,
        height=height,
        api_key=api_key,
    )
    bg_img.save(output_path, format="PNG")
    logger.info(f"Saved artwork to {output_path}")
    return output_path

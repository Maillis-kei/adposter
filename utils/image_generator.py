"""Aesthetic Background Generation Module (Modern Christian Devotional & Verse Card Art).

Transfers the visual grammar from modern editorial Christian design, Korean devotional cards,
and minimalist sacred photography:
- Minimalist Still-Life & Editorial Photography (Natural sunlight, linen, olive branches, serene dawn)
- Textured Hanji & Fine-Art Watercolor Washes (Warm cream, oatmeal, muted sage, gentle sunset gradient)
- Cinematic 35mm Natural Film Aesthetics (Soft shadows, tranquil sanctuary light, peaceful atmosphere)

Generates 100% original, non-cliché backgrounds dynamically via Google Imagen 3 or high-art procedural paper wash.
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
# Dynamic Imagen 3 Prompt Engineering Engine
# ---------------------------------------------------------------------------

FORM_FACTOR_AESTHETICS = {
    "verse_card": (
        "Editorial minimalist Christian scripture card aesthetic. "
        "Still-life photography with soft, warm morning sunlight streaming in diagonally, "
        "a delicate olive sprig casting a gentle shadow upon textured cream linen fabric, "
        "subtle warm oatmeal and neutral muted beige palette, Kinfolk magazine style, "
        "peaceful, clean, ample serene negative space in the center and top for typography, "
        "shot on 35mm lens, f/2.8, shallow depth of field, strictly NO text, NO letters, NO watermark."
    ),
    "gospel_leaflet": (
        "Warm, comforting, authentic photographic atmosphere that feels like an invitation to rest. "
        "A quiet, sunlit sanctuary corner with natural wooden table, a cozy ceramic cup with rising gentle steam, "
        "warm golden hour sunlight illuminating the dust motes softly in the air, tranquil indoor plant leaves, "
        "welcoming, deeply comforting and serene ambiance, inviting peace, plenty of clean negative space, "
        "cinematic lighting, natural tones, strictly NO text, NO letters, NO words."
    ),
    "devotional_postcard": (
        "Fine-art minimalist watercolor and ink-wash background on rich textured handmade cotton paper. "
        "Soft ethereal dawn gradients in gentle misty sage green, warm ivory, and subtle peach morning glow, "
        "abstract soft celestial light filtering through a calm tranquil misty lake, contemplative holy stillness, "
        "delicate organic watercolor bleed textures, elegant and serene, ample negative space for Korean calligraphy, "
        "masterpiece quality, strictly NO typography, NO text, NO characters."
    ),
}


def build_imagen_prompt(theme: str, visual_concept: str, form_factor: str = "verse_card") -> str:
    """Builds a refined, trend-conscious visual prompt eliminating all clichés."""
    base_style = FORM_FACTOR_AESTHETICS.get(form_factor, FORM_FACTOR_AESTHETICS["verse_card"])
    
    # Custom contextual nuance from the spiritual theme
    context_note = f"The spiritual essence represents '{theme}'. {visual_concept}." if visual_concept else f"The spiritual essence represents '{theme}'."
    
    prompt = (
        f"{context_note} {base_style} "
        f"Atmospheric, poetic, extremely calm and sacred, spacious negative space, ultra-high resolution 8k, "
        f"strictly NO text, NO letters, NO characters, NO watermark."
    )
    return prompt


# ---------------------------------------------------------------------------
# High-Art Procedural Paper & Watercolor Background Engine
# ---------------------------------------------------------------------------

def generate_aesthetic_procedural_background(
    date_str: str,
    theme: str,
    form_factor: str = "verse_card",
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Generates an exquisite, textured fine-art Korean paper & watercolor background.
    
    Never looks like raw computer graphics. Replicates real organic handmade paper,
    gentle watercolor washes (Sage, Cream, Warm Ochre, Sunset Lavender), and soft ambient god-rays.
    """
    seed_val = int(hashlib.md5(f"{date_str}_{theme}_{form_factor}".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)

    # 1. Base Harmonious Palette Selection (Muted, warm, peaceful)
    palette_options = [
        # Palette 1: Warm Cream & Sage (Peace & Healing)
        {"bg": (248, 246, 240), "accent1": (225, 232, 222), "accent2": (245, 230, 215), "light": (255, 252, 245)},
        # Palette 2: Dawn Oatmeal & Peach (Grace & Morning Joy)
        {"bg": (247, 244, 238), "accent1": (245, 226, 216), "accent2": (230, 225, 215), "light": (255, 250, 240)},
        # Palette 3: Celestial Lavender & Mist (Holy Presence)
        {"bg": (245, 244, 246), "accent1": (232, 228, 238), "accent2": (224, 232, 235), "light": (255, 253, 250)},
        # Palette 4: Warm Sunlight Ochre (Comfort & Truth)
        {"bg": (250, 247, 240), "accent1": (242, 232, 210), "accent2": (235, 225, 215), "light": (255, 254, 245)},
    ]
    pal = palette_options[seed_val % len(palette_options)]

    # Create base canvas
    img = Image.new("RGBA", (width, height), (*pal["bg"], 255))
    draw = ImageDraw.Draw(img)

    # 2. Organic Gradient Base (Soft vertical and diagonal illumination)
    grad_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad_layer)
    for y in range(height):
        ratio = y / height
        # Subtle gradient from light at top-middle to cozy warmth at bottom
        r = int(pal["bg"][0] * (1 - ratio * 0.08) + pal["accent1"][0] * (ratio * 0.08))
        g = int(pal["bg"][1] * (1 - ratio * 0.08) + pal["accent1"][1] * (ratio * 0.08))
        b = int(pal["bg"][2] * (1 - ratio * 0.08) + pal["accent1"][2] * (ratio * 0.08))
        g_draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    img = Image.alpha_composite(img, grad_layer)

    # 3. Soft Watercolor Bleeds & Light Pools
    wash_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    w_draw = ImageDraw.Draw(wash_layer)

    # Top-right or top-left ethereal light pool
    light_x = rng.choice([int(width * 0.25), int(width * 0.75)])
    light_y = rng.randint(int(height * 0.15), int(height * 0.35))
    for rad in range(650, 50, -40):
        alpha = int(45 * (1 - (rad / 650) ** 1.5))
        w_draw.ellipse(
            [light_x - rad, light_y - rad, light_x + rad, light_y + rad],
            fill=(*pal["light"], alpha),
        )

    # Organic watercolor washes around bottom or edges
    for _ in range(4):
        wx = rng.randint(0, width)
        wy = rng.randint(int(height * 0.55), height + 100)
        rx = rng.randint(400, 800)
        ry = rng.randint(300, 600)
        color = rng.choice([pal["accent1"], pal["accent2"]])
        w_draw.ellipse(
            [wx - rx, wy - ry, wx + rx, wy + ry],
            fill=(*color, rng.randint(30, 65)),
        )

    wash_layer = wash_layer.filter(ImageFilter.GaussianBlur(radius=80))
    img = Image.alpha_composite(img, wash_layer)

    # 4. Realistic Paper Fiber Texture (Subtle Hanji / Cotton grain)
    grain_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grain_bytes = bytearray(width * height * 4)
    
    # Fast pseudo noise for paper grain
    for idx in range(0, len(grain_bytes), 4):
        val = rng.randint(0, 18)
        grain_bytes[idx] = 180      # R
        grain_bytes[idx + 1] = 175  # G
        grain_bytes[idx + 2] = 165  # B
        grain_bytes[idx + 3] = val  # Alpha grain
    grain_img = Image.frombytes("RGBA", (width, height), bytes(grain_bytes))
    grain_img = grain_img.filter(ImageFilter.GaussianBlur(radius=0.7))
    img = Image.alpha_composite(img, grain_img)

    # 5. Soft Inner Border / Frame (Giving an exquisite postcard feel)
    border_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(border_layer)
    margin = 55
    b_draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=(210, 202, 192, 90),
        width=1,
    )
    img = Image.alpha_composite(img, border_layer)

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Master Imagen 3 API & Fallback Handler
# ---------------------------------------------------------------------------

def try_generate_via_imagen_api(
    prompt: str,
    api_key: str,
    width: int = 1080,
    height: int = 1920,
) -> Optional[Image.Image]:
    """Attempts generation via Google GenAI Imagen 3 API."""
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
        "User-Agent": "PoiemaArtworkBot/2.0"
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
                    logger.info("✓ Successfully generated aesthetic background via Imagen 3 API!")
                    return img
        except Exception as e:
            logger.debug(f"Imagen endpoint failed: {e}")

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
    """Master generator: Produces an authentic, modern aesthetic background.
    
    1. Attempts Google Imagen 3 with creative editorial prompt.
    2. Gracefully falls back to high-art procedural paper wash.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    if gemini_key:
        prompt = build_imagen_prompt(theme, visual_concept, form_factor=form_factor)
        logger.info(f"[Visual Art Director] Requesting Imagen 3 with aesthetic prompt...")
        ai_img = try_generate_via_imagen_api(prompt, gemini_key, width, height)
        if ai_img:
            return ai_img

    logger.info(f"[Visual Art Director] Generating bespoke fine-art paper & watercolor background for '{theme}'...")
    return generate_aesthetic_procedural_background(
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
    logger.info(f"Saved background artwork to {output_path}")
    return output_path

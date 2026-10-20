"""Image Generator Module (Google Imagen 3 API & Enhanced Divine Artwork Fallback).

Generates high-definition 9:16 background artwork:
1. Google AI Studio Imagen 3 REST API (:predict endpoint with Developer API Key)
2. Enhanced procedural holy light artwork if API is unreachable
"""

import base64
import io
import json
import logging
import math
import os
from pathlib import Path
import random
from typing import Optional, Tuple
import urllib.request
from PIL import Image, ImageDraw, ImageFilter

logger = logging.getLogger(__name__)


def generate_fallback_background(
    width: int = 1080,
    height: int = 1920,
) -> Image.Image:
    """Generates an inspiring, vibrant holy light sanctuary artwork for 9:16 vertical poster.

    Creates a rich atmosphere with radiant golden sunbeams, heavenly dawn sky,
    and soft ethereal mist so the poster feels warm and alive.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Warm sunrise sky gradient (Dawn gold to twilight indigo)
    c_top = (18, 28, 54)        # Deep dawn navy
    c_mid = (75, 52, 68)        # Warm celestial mauve
    c_warm = (196, 138, 70)     # Radiant sunrise gold
    c_bot = (32, 28, 38)        # Ground shadow

    for y in range(height):
        ratio = y / height
        if ratio < 0.4:
            local_r = ratio / 0.4
            r = int(c_top[0] * (1 - local_r) + c_mid[0] * local_r)
            g = int(c_top[1] * (1 - local_r) + c_mid[1] * local_r)
            b = int(c_top[2] * (1 - local_r) + c_mid[2] * local_r)
        elif ratio < 0.75:
            local_r = (ratio - 0.4) / 0.35
            r = int(c_mid[0] * (1 - local_r) + c_warm[0] * local_r)
            g = int(c_mid[1] * (1 - local_r) + c_warm[1] * local_r)
            b = int(c_mid[2] * (1 - local_r) + c_warm[2] * local_r)
        else:
            local_r = (ratio - 0.75) / 0.25
            r = int(c_warm[0] * (1 - local_r) + c_bot[0] * local_r)
            g = int(c_warm[1] * (1 - local_r) + c_bot[1] * local_r)
            b = int(c_warm[2] * (1 - local_r) + c_bot[2] * local_r)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Golden Sun & Divine Bloom (Top-center light source)
    sun_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sun_draw = ImageDraw.Draw(sun_layer)
    sun_x = width // 2
    sun_y = int(height * 0.22)

    # Multi-layered radial glow
    for radius in range(500, 20, -15):
        alpha = int(90 * (1 - (radius / 500) ** 1.3))
        box = [sun_x - radius, sun_y - radius, sun_x + radius, sun_y + radius]
        sun_draw.ellipse(box, fill=(255, 230, 150, min(120, max(0, alpha))))

    # Core brilliant light
    for radius in range(120, 0, -10):
        sun_draw.ellipse(
            [sun_x - radius, sun_y - radius, sun_x + radius, sun_y + radius],
            fill=(255, 255, 240, 45)
        )

    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, sun_layer)

    # 3. God Rays / Heavenly Beams streaming downward
    ray_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(ray_layer)

    num_rays = 12
    for i in range(num_rays):
        angle = math.radians(65 + i * 5)
        dx = math.cos(angle) * height * 1.2
        dy = math.sin(angle) * height * 1.2
        poly = [
            (sun_x, sun_y),
            (sun_x + dx - 90, sun_y + dy),
            (sun_x + dx + 90, sun_y + dy)
        ]
        ray_draw.polygon(poly, fill=(255, 235, 175, 24))

    ray_layer = ray_layer.filter(ImageFilter.GaussianBlur(radius=35))
    img = Image.alpha_composite(img, ray_layer)

    # 4. Sacred Mountains Silhouette at Bottom Horizon
    horizon_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(horizon_layer)
    pts = [(0, height)]
    for x in range(0, width + 40, 40):
        ny = int(height * 0.78 + math.sin(x * 0.008) * 80 + math.cos(x * 0.015) * 40)
        pts.append((x, ny))
    pts.append((width, height))
    h_draw.polygon(pts, fill=(18, 14, 28, 220))
    horizon_layer = horizon_layer.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, horizon_layer)

    # 5. Golden dust particles
    dust_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dust_draw = ImageDraw.Draw(dust_layer)
    random.seed(153)
    for _ in range(120):
        px = random.randint(30, width - 30)
        py = random.randint(80, int(height * 0.75))
        size = random.randint(2, 5)
        alpha = random.randint(40, 200)
        dust_draw.ellipse([px, py, px + size, py + size], fill=(255, 245, 210, alpha))

    dust_layer = dust_layer.filter(ImageFilter.GaussianBlur(radius=1.5))
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
        f"absolutely NO text, NO typography, NO words, NO letters, NO watermark, NO cross graphic."
    )


def generate_background_via_imagen3_rest(
    prompt: str,
    api_key: str,
    aspect_ratio: str = "9:16",
) -> Optional[Image.Image]:
    """Generates an image using Google AI Studio Developer API (:predict endpoint)."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"
    
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "personGeneration": "DONT_ALLOW"
        }
    }

    req_data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
        "User-Agent": "PoiemaPosterBot/1.0"
    }

    req = urllib.request.Request(endpoint, data=req_data, headers=headers)
    logger.info("Calling Google AI Studio Imagen 3 REST API (:predict)...")

    with urllib.request.urlopen(req, timeout=45) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))

    predictions = res_json.get("predictions", [])
    if not predictions:
        logger.warning(f"No predictions returned from Imagen 3: {res_json}")
        return None

    first_pred = predictions[0]
    b64_bytes = first_pred.get("bytesBase64Encoded")
    if not b64_bytes:
        logger.warning("No bytesBase64Encoded in prediction response")
        return None

    img_data = base64.b64decode(b64_bytes)
    img = Image.open(io.BytesIO(img_data)).convert("RGB")
    logger.info(f"Successfully received Imagen 3 image: {img.size}")
    return img


def generate_background_image(
    prompt: str,
    output_path: Path,
    api_key: Optional[str] = None,
    aspect_ratio: str = "9:16",
    width: int = 1080,
    height: int = 1920,
) -> Path:
    """Generates background image using Google Imagen 3 API.

    Falls back to high-quality procedural divine artwork if API is unreachable.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")

    if gemini_key and gemini_key.strip():
        try:
            img = generate_background_via_imagen3_rest(
                prompt=prompt,
                api_key=gemini_key.strip(),
                aspect_ratio=aspect_ratio,
            )
            if img:
                if img.size != (width, height):
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                img.save(output_path, format="PNG")
                logger.info(f"Successfully saved Imagen 3 artwork: {output_path}")
                return output_path
        except Exception as e:
            logger.error(f"Google Imagen 3 REST API call failed: {e}. Falling back to rich procedural background...")

    # Fallback to enhanced divine artwork
    bg = generate_fallback_background(width=width, height=height)
    bg.save(output_path, format="PNG")
    logger.info(f"Saved enhanced procedural divine background to {output_path}")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_out = Path(__file__).resolve().parent.parent / "output" / "test_rich_bg.png"
    p = generate_background_image("Test prompt", test_out)
    print(f"Generated enhanced background at: {p}")

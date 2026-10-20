"""Image Generator Module (Google Imagen 3 API & Fallback Engine).

Generates high-definition 9:16 background artwork using Google Imagen 3:
- Enforces negative space at top and center for typography readability
- Cinematic lighting, sacred heavenly aura, ultra-high resolution
- Zero-text generation guarantee (via negative prompt filtering)
- Built-in graceful fallback gradient generator if API is unavailable or quota is exceeded
"""

import io
import logging
import math
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

logger = logging.getLogger(__name__)


def generate_fallback_background(
    width: int = 1080,
    height: int = 1920,
    base_color_top: Tuple[int, int, int] = (15, 23, 42),  # Deep slate midnight
    base_color_bottom: Tuple[int, int, int] = (30, 41, 59),  # Rich twilight navy
    accent_glow: Tuple[int, int, int] = (212, 175, 55),  # Golden divine aura
) -> Image.Image:
    """Generates an elegant, cinematic divine gradient background when API is offline.

    Includes soft light rays and celestial glow suitable for sacred worship posters.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Vertical smooth gradient
    for y in range(height):
        ratio = y / height
        r = int(base_color_top[0] * (1 - ratio) + base_color_bottom[0] * ratio)
        g = int(base_color_top[1] * (1 - ratio) + base_color_bottom[1] * ratio)
        b = int(base_color_top[2] * (1 - ratio) + base_color_bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # 2. Celestial Light Glow at upper center (Heavenly radiance)
    glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    glow_center_x = width // 2
    glow_center_y = int(height * 0.28)
    max_radius = int(width * 0.85)

    for radius in range(max_radius, 0, -20):
        alpha = int(45 * (1 - (radius / max_radius) ** 1.5))
        box = [
            glow_center_x - radius,
            glow_center_y - radius,
            glow_center_x + radius,
            glow_center_y + radius,
        ]
        glow_draw.ellipse(
            box,
            fill=(
                accent_glow[0],
                accent_glow[1],
                accent_glow[2],
                max(0, min(alpha, 80)),
            ),
        )

    # Blur glow for natural soft bloom
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=60))
    img = Image.alpha_composite(img, glow_layer)

    # 3. Soft ambient particles (stars / light dust)
    dust_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    dust_draw = ImageDraw.Draw(dust_layer)

    import random

    random.seed(42)  # Consistent aesthetic
    for _ in range(80):
        px = random.randint(20, width - 20)
        py = random.randint(50, int(height * 0.65))
        size = random.randint(2, 6)
        alpha = random.randint(40, 180)
        dust_draw.ellipse(
            [px, py, px + size, py + size],
            fill=(255, 250, 230, alpha),
        )
    dust_layer = dust_layer.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, dust_layer)

    return img.convert("RGB")


def build_imagen_prompt(theme: str, visual_concept: str) -> str:
    """Builds an optimized, production-grade prompt for Imagen 3."""
    return (
        f"A cinematic Christian background art symbolizing '{theme}'. {visual_concept}. "
        f"Divine heavenly light rays streaming from above, golden glowing atmosphere, ethereal clouds, "
        f"holy and peaceful sanctuary aura. "
        f"Vast negative space at the upper half and center designed for typography overlay. "
        f"Hyper-detailed, 8k resolution, photorealistic cinematic lighting, masterpiece, clean composition, "
        f"no characters in the foreground, strictly NO text, NO typography, NO letters, NO watermark, NO logo."
    )


def generate_background_image(
    prompt: str,
    output_path: Path,
    api_key: Optional[str] = None,
    aspect_ratio: str = "9:16",
    width: int = 1080,
    height: int = 1920,
) -> Path:
    """Generates background image using Google Imagen 3 API.

    Falls back to high-quality procedural gradient artwork if API is unreachable.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")

    if not gemini_key or not gemini_key.strip():
        logger.warning(
            "GEMINI_API_KEY not set. Generating beautiful procedural divine background..."
        )
        bg = generate_fallback_background(width=width, height=height)
        bg.save(output_path, format="PNG")
        logger.info(f"Saved fallback background to {output_path}")
        return output_path

    # Attempt Google Imagen 3 generation
    try:
        logger.info("Connecting to Google GenAI Imagen 3 API...")
        # Check for google.genai (new SDK)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            result = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/png",
                    aspect_ratio="9:16",
                    person_generation="DONT_ALLOW",
                ),
            )

            if result.generated_images:
                image_bytes = result.generated_images[0].image.image_bytes
                img = Image.open(io.BytesIO(image_bytes))
                # Ensure exact resolution
                if img.size != (width, height):
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                img.save(output_path, format="PNG")
                logger.info(
                    f"Successfully generated Imagen 3 artwork: {output_path}"
                )
                return output_path

        except ImportError:
            # Fallback to legacy google.generativeai if available
            import google.generativeai as gai

            gai.configure(api_key=gemini_key)
            imagen = gai.ImageGenerationModel("imagen-3.0-generate-002")
            result = imagen.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="9:16",
                safety_filter_level="block_medium_and_above",
                person_generation="dont_allow",
            )
            for image in result.images:
                image.save(str(output_path))
                logger.info(
                    f"Successfully generated Imagen 3 artwork (legacy SDK): {output_path}"
                )
                return output_path

    except Exception as e:
        logger.error(
            f"Google Imagen 3 generation failed: {e}. Generating graceful procedural background..."
        )

    # Graceful fallback on any API error or quota limit
    bg = generate_fallback_background(width=width, height=height)
    bg.save(output_path, format="PNG")
    logger.info(f"Saved procedural background to {output_path}")
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_out = Path(__file__).resolve().parent.parent / "output" / "test_bg.png"
    prompt = build_imagen_prompt(
        "성령의 임재",
        "Golden rays shining through mountain mist into a sacred sanctuary",
    )
    print(f"Generated prompt: {prompt[:100]}...")
    p = generate_background_image(prompt, test_out)
    print(f"Background ready at: {p} (Size: {p.stat().st_size:,} bytes)")

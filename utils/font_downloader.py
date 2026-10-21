"""Font Auto-Downloader Module (Zero-Dependency Font Setup).

Downloads and verifies required commercial-free open source fonts (OFL):
- Headline: PyeongChangPeace-Bold.otf
- Body Bold: Pretendard-Bold.otf
- Body Regular: Pretendard-Regular.otf
"""

import logging
from pathlib import Path
import urllib.request
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Verified public raw URLs for OFL open-source fonts
FONT_SOURCES: Dict[str, str] = {
    "PyeongChangPeace-Bold.otf": (
        "https://github.com/fonts-archive/PyeongChangPeace/raw/main/PyeongChangPeace-Bold.otf"
    ),
    "Pretendard-Bold.otf": (
        "https://github.com/orioncactus/pretendard/raw/main/packages/pretendard/dist/public/static/Pretendard-Bold.otf"
    ),
    "Pretendard-Regular.otf": (
        "https://github.com/orioncactus/pretendard/raw/main/packages/pretendard/dist/public/static/Pretendard-Regular.otf"
    ),
    "MaruBuri-Regular.ttf": (
        "https://github.com/fonts-archive/MaruBuri/raw/main/MaruBuri-Regular.ttf"
    ),
    "MaruBuri-Bold.ttf": (
        "https://github.com/fonts-archive/MaruBuri/raw/main/MaruBuri-Bold.ttf"
    ),
}

# Fallback mirrors in case primary raw GitHub is rate-limited or blocked
FONT_FALLBACK_SOURCES: Dict[str, str] = {
    "PyeongChangPeace-Bold.otf": (
        "https://cdn.jsdelivr.net/gh/fonts-archive/PyeongChangPeace@main/PyeongChangPeace-Bold.otf"
    ),
    "Pretendard-Bold.otf": (
        "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/packages/pretendard/dist/public/static/Pretendard-Bold.otf"
    ),
    "Pretendard-Regular.otf": (
        "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/packages/pretendard/dist/public/static/Pretendard-Regular.otf"
    ),
    "MaruBuri-Regular.ttf": (
        "https://cdn.jsdelivr.net/gh/fonts-archive/MaruBuri/MaruBuri-Regular.ttf"
    ),
    "MaruBuri-Bold.ttf": (
        "https://cdn.jsdelivr.net/gh/fonts-archive/MaruBuri/MaruBuri-Bold.ttf"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 PoiemaPosterBot/1.0"
    )
}


def _download_file(url: str, target_path: Path, min_size: int = 50000) -> bool:
    """Download a single font file with validation."""
    logger.info(f"Downloading font from {url} to {target_path.name}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()

        if len(content) < min_size:
            logger.warning(
                f"Downloaded content from {url} is too small ({len(content)} bytes), likely an error page."
            )
            return False

        # Write safely
        temp_path = target_path.with_suffix(".tmp")
        temp_path.write_bytes(content)
        if target_path.exists():
            target_path.unlink()
        temp_path.rename(target_path)
        logger.info(
            f"Successfully downloaded {target_path.name} ({len(content):,} bytes)."
        )
        return True

    except Exception as e:
        logger.error(f"Failed to download from {url}: {e}")
        return False


def ensure_fonts_exist(
    target_dir: Optional[Path] = None,
) -> Dict[str, Optional[Path]]:
    """Ensures all required fonts are present in fonts/ directory.

    If any font is missing, automatically downloads it from verified GitHub/CDN sources.

    Returns:
        Dict mapping font filename to Path on disk (or None if failed).
    """
    if target_dir is None:
        base_dir = Path(__file__).resolve().parent.parent
        fonts_dir = base_dir / "fonts"
    else:
        fonts_dir = Path(target_dir)

    fonts_dir.mkdir(parents=True, exist_ok=True)
    font_paths: Dict[str, Optional[Path]] = {}

    for font_name, primary_url in FONT_SOURCES.items():
        file_path = fonts_dir / font_name

        # If font exists and has valid size (> 50KB), consider it ready
        if file_path.exists() and file_path.stat().st_size > 50000:
            font_paths[font_name] = file_path
            continue

        # Try primary URL
        success = _download_file(primary_url, file_path)

        # Fallback if primary fails
        if not success and font_name in FONT_FALLBACK_SOURCES:
            fallback_url = FONT_FALLBACK_SOURCES[font_name]
            logger.info(f"Retrying with fallback mirror for {font_name}...")
            success = _download_file(fallback_url, file_path)

        if success and file_path.exists():
            font_paths[font_name] = file_path
        else:
            logger.error(
                f"Could not secure font: {font_name}. Graphic composer will use system fallback."
            )
            font_paths[font_name] = None

    return font_paths


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Checking and downloading fonts...")
    results = ensure_fonts_exist()
    for k, v in results.items():
        print(f"[{'OK' if v else 'FAIL'}] {k} -> {v}")

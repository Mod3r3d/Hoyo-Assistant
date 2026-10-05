"""Các tiện ích vẽ và xử lý ảnh Pillow cho Card Renderer."""

import io
import os
from pathlib import Path
from typing import Optional, Tuple
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from loguru import logger
from app.integrations.cache import global_cache


def get_font(size: int = 18, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Tải font chữ hệ thống trên Windows hoặc fallback."""
    font_names = (
        ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    )
    # Tìm kiếm trong C:\Windows\Fonts
    win_fonts = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    for fn in font_names:
        font_path = win_fonts / fn
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                pass

    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


async def download_image(url: str, size: Optional[Tuple[int, int]] = None) -> Optional[Image.Image]:
    """Tải ảnh từ URL với cache in-memory."""
    if not url:
        return None

    cache_key = f"img:{url}"
    cached_bytes = await global_cache.get(cache_key)

    if not cached_bytes:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        cached_bytes = await resp.read()
                        await global_cache.set(cache_key, cached_bytes, ttl=7200)
                    else:
                        return None
        except Exception as e:
            logger.debug(f"Không thể tải ảnh {url}: {e}")
            return None

    try:
        image = Image.open(io.BytesIO(cached_bytes)).convert("RGBA")
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        logger.debug(f"Lỗi đọc ảnh Pillow từ {url}: {e}")
        return None


def create_gradient_bg(width: int, height: int, start_color: Tuple[int, int, int], end_color: Tuple[int, int, int]) -> Image.Image:
    """Tạo nền gradient chuyển màu sang trọng."""
    base = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base)

    for y in range(height):
        ratio = y / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    return base


def draw_rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width: int = 1):
    """Vẽ hình chữ nhật bo góc mềm mại."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

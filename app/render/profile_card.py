"""Renderer tạo ảnh Profile Card đẹp mắt cho Genshin Impact và Honkai: Star Rail."""

import asyncio
import io
from typing import Any, List, Optional
from PIL import Image, ImageDraw
from app.games.enums import GameType
from app.render.card_utils import (
    create_gradient_bg,
    draw_rounded_rect,
    download_image,
    get_font,
)
from app.utils.validators import mask_uid


async def render_profile_card(profile: Any, game: GameType, show_uid: bool = False) -> io.BytesIO:
    """Tạo ảnh Profile Card tổng quan hồ sơ người chơi với avatar đầy đủ."""
    # Tải avatar người chơi nếu có
    user_avatar: Optional[Image.Image] = None
    if getattr(profile, "avatar_url", ""):
        user_avatar = await download_image(profile.avatar_url, size=(75, 75))

    # Tải đồng thời hình ảnh avatar của các nhân vật trong tủ trưng bày
    characters = profile.showcase_characters[:8]
    tasks = [
        download_image(c.icon_url, size=(82, 82)) if getattr(c, "icon_url", "") else asyncio.sleep(0)
        for c in characters
    ]
    raw_images = await asyncio.gather(*tasks, return_exceptions=True)
    char_images: List[Optional[Image.Image]] = [
        img if isinstance(img, Image.Image) else None for img in raw_images
    ]

    return await asyncio.to_thread(
        _sync_render_profile_card, profile, game, show_uid, user_avatar, char_images
    )


def _sync_render_profile_card(
    profile: Any,
    game: GameType,
    show_uid: bool,
    user_avatar: Optional[Image.Image] = None,
    char_images: Optional[List[Optional[Image.Image]]] = None,
) -> io.BytesIO:
    if char_images is None:
        char_images = []

    width, height = 900, 480

    # Màu gradient chủ đạo theo game
    if game == GameType.GENSHIN:
        start_col = (18, 32, 48)
        end_col = (10, 18, 28)
        accent_col = (91, 192, 190)
        game_title = "GENSHIN IMPACT"
        rank_label = f"Hạng Mạo Hiểm (AR): {profile.level}"
        world_label = f"Cấp Thế Giới: {profile.world_level}"
        badge_prefix = "C"
    else:
        start_col = (30, 20, 52)
        end_col = (15, 12, 28)
        accent_col = (186, 104, 200)
        game_title = "HONKAI: STAR RAIL"
        rank_label = f"Cấp Khai Phá: {profile.level}"
        world_label = f"Cấp Cân Bằng: {profile.world_level}"
        badge_prefix = "E"

    base_img = create_gradient_bg(width, height, start_col, end_col)

    # Lớp overlay hỗ trợ hiệu ứng kính mờ (Glassmorphism) chuẩn xác
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)

    # Viền bao ngoài thẻ
    draw_rounded_rect(d_overlay, [12, 12, width - 12, height - 12], radius=18, fill=None, outline=(60, 70, 90, 160), width=2)

    # Thẻ Header Profile kính mờ
    draw_rounded_rect(d_overlay, [30, 30, width - 30, 150], radius=14, fill=(255, 255, 255, 20), outline=(255, 255, 255, 40))

    # Vẽ khung nhân vật trưng bày vào overlay
    characters = profile.showcase_characters[:8]
    card_w, card_h = 95, 185
    start_x = 35
    start_y = 205
    spacing = 10

    if characters:
        for idx, char in enumerate(characters):
            cx = start_x + idx * (card_w + spacing)
            cy = start_y
            char_bg_fill = (45, 55, 75, 180) if char.rarity == 5 else (35, 45, 60, 180)
            char_border = (235, 175, 75, 220) if char.rarity == 5 else (150, 110, 200, 220)
            draw_rounded_rect(d_overlay, [cx, cy, cx + card_w, cy + card_h], radius=10, fill=char_bg_fill, outline=char_border, width=2)
            # Khung badge góc trên phải
            draw_rounded_rect(d_overlay, [cx + card_w - 32, cy + 6, cx + card_w - 6, cy + 24], radius=4, fill=(0, 0, 0, 180))

            # Khung placeholder nếu không có ảnh
            char_img = char_images[idx] if idx < len(char_images) else None
            if not char_img:
                draw_rounded_rect(d_overlay, [cx + 10, cy + 26, cx + card_w - 10, cy + 104], radius=8, fill=(255, 255, 255, 12))

    # Ghép lớp nền và lớp kính mờ
    base_img = Image.alpha_composite(base_img, overlay)

    # Vẽ avatar người chơi lên base_img
    text_x = 50
    if user_avatar:
        av_x, av_y = 50, 52
        av_size = 72
        mask = Image.new("L", (av_size, av_size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, av_size, av_size], fill=255)
        user_av_resized = user_avatar.resize((av_size, av_size), Image.Resampling.LANCZOS)
        base_img.paste(user_av_resized, (av_x, av_y), mask=mask)

        # Viền avatar người chơi
        draw_temp = ImageDraw.Draw(base_img)
        draw_temp.ellipse([av_x, av_y, av_x + av_size, av_y + av_size], outline=accent_col, width=2)
        text_x = 142

    # Vẽ các avatar nhân vật lên base_img
    if characters:
        for idx, char in enumerate(characters):
            char_img = char_images[idx] if idx < len(char_images) else None
            if char_img:
                cx = start_x + idx * (card_w + spacing)
                cy = start_y
                av_w, av_h = 82, 82
                ix = cx + (card_w - av_w) // 2
                iy = cy + 26
                # Dùng kênh alpha của ảnh để render độ trong suốt hoàn hảo
                if char_img.mode == "RGBA":
                    base_img.paste(char_img, (ix, iy), mask=char_img.split()[3])
                else:
                    base_img.paste(char_img, (ix, iy))

    # Lớp chữ và chi tiết sắc nét cuối cùng
    draw = ImageDraw.Draw(base_img)

    # Tên người chơi
    font_title = get_font(26, bold=True)
    draw.text((text_x, 46), profile.nickname, fill=(255, 255, 255), font=font_title)

    # Game Title Tag
    font_sub = get_font(13, bold=True)
    draw.text((text_x, 83), f"{game_title}  •  UID: {mask_uid(profile.uid, show=show_uid)}", fill=accent_col, font=font_sub)

    # Cấp độ & Thành tích
    font_info = get_font(15, bold=False)
    draw.text((text_x, 110), f"{rank_label}   |   {world_label}   |   Thành Tựu: {profile.achievement_count}", fill=(200, 205, 215), font=font_info)

    # Chữ ký (Signature) nếu có
    if profile.signature:
        font_sig = get_font(13, bold=False)
        sig_text = profile.signature[:60] + ("..." if len(profile.signature) > 60 else "")
        draw.text((width - 430, 48), f'"{sig_text}"', fill=(160, 170, 185), font=font_sig)

    # Tiêu đề khu vực tủ nhân vật
    font_sec = get_font(18, bold=True)
    draw.text((32, 170), "TỦ TRƯNG BÀY NHÂN VẬT", fill=(255, 255, 255), font=font_sec)

    # Vẽ thông tin chữ cho từng nhân vật
    if characters:
        font_cname = get_font(12, bold=True)
        font_clevel = get_font(12, bold=False)
        font_badge = get_font(11, bold=True)
        font_elem = get_font(11, bold=True)

        for idx, char in enumerate(characters):
            cx = start_x + idx * (card_w + spacing)
            cy = start_y

            # Cung Mệnh / Tinh Hồn Badge
            const_val = getattr(char, "constellation", getattr(char, "eidolon", 0))
            const_text = f"{badge_prefix}{const_val}"
            draw.text((cx + card_w - 28, cy + 8), const_text, fill=accent_col, font=font_badge)

            # Nếu không có ảnh avatar, hiển thị text ký hiệu ở giữa
            char_img = char_images[idx] if idx < len(char_images) else None
            if not char_img:
                elem_tag = char.element[:4] if char.element != "None" else "N/A"
                draw.text((cx + 28, cy + 58), elem_tag, fill=(160, 175, 195), font=font_badge)

            # Tên nhân vật (rút gọn nếu quá dài)
            char_name = char.name.split(" ")[-1] if len(char.name) > 8 else char.name
            draw.text((cx + 8, cy + 112), char_name[:11], fill=(255, 255, 255), font=font_cname)

            # Cấp độ
            draw.text((cx + 8, cy + 132), f"Lv.{char.level}", fill=(200, 210, 225), font=font_clevel)

            # Nguyên tố
            elem_display = f"• {char.element}" if char.element != "None" else f"{char.rarity}★"
            draw.text((cx + 8, cy + 154), elem_display, fill=accent_col, font=font_elem)
    else:
        # Trường hợp tủ trưng bày trống hoặc bị ẩn
        draw_rounded_rect(draw, [30, 205, width - 30, 390], radius=12, fill=(255, 255, 255, 10))
        font_empty = get_font(18, bold=True)
        draw.text((width // 2 - 160, 280), "Tủ trưng bày nhân vật đang trống hoặc bị ẩn", fill=(170, 180, 195), font=font_empty)

    # Footer
    font_footer = get_font(12, bold=False)
    draw.text((32, height - 32), "HoyoBot • Trợ thủ Genshin Impact & Honkai: Star Rail", fill=(120, 130, 150), font=font_footer)

    buffer = io.BytesIO()
    base_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

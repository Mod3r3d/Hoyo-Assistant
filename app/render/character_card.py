"""Renderer tạo ảnh Thẻ Chi Tiết Nhân Vật (Character Card) cho Genshin & HSR."""

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


def format_substat_display(sub_str: str) -> str:
    """Rút gọn tên chỉ số dòng phụ để hiển thị lưới 2x2 cân đối, rõ nét."""
    s = sub_str.strip()
    replacements = [
        ("Hiệu Quả Nạp NT:", "Nạp NT:"),
        ("Tỷ Lệ Bạo Kích:", "TL Bạo:"),
        ("Sát Thương Bạo Kích:", "ST Bạo:"),
        ("ST Bạo Kích:", "ST Bạo:"),
        ("Tinh Thông NT:", "Tinh Thông:"),
        ("Tấn Công Kích Phá:", "Kích Phá:"),
        ("Tăng Sát Thương Lôi:", "Tăng ST Lôi:"),
        ("Kháng Hiệu Ứng:", "Kháng H.Ứng:"),
        ("Chính Xác Hiệu Ứng:", "Chính Xác:"),
        ("Tấn Công %:", "Tấn Công%:"),
        ("Phòng Ngự %:", "Phòng Ngự%:"),
        ("Phòng Thủ %:", "Phòng Thủ%:"),
        ("HP %:", "HP%:"),
    ]
    for old, new in replacements:
        if s.startswith(old):
            s = s.replace(old, new, 1)
            break
    if any(k in s for k in ["Nạp NT", "TL Bạo", "ST Bạo", "Tấn Công%", "Phòng Ngự%", "Phòng Thủ%", "HP%", "Kích Phá", "Tăng ST", "Kháng H.Ứng", "Chính Xác"]) and not s.endswith("%"):
        s += "%"
    return s


async def render_character_card(character: Any, game: GameType) -> io.BytesIO:
    """Tạo ảnh chi tiết trang bị và chỉ số của một nhân vật."""
    # Tải đồng thời avatar nhân vật, vũ khí và các món di vật
    char_img_task = (
        download_image(character.icon_url, size=(80, 80))
        if getattr(character, "icon_url", "")
        else asyncio.sleep(0)
    )
    weapon = getattr(character, "weapon", getattr(character, "light_cone", None))
    weapon_img_task = (
        download_image(weapon.icon_url, size=(60, 60))
        if weapon and getattr(weapon, "icon_url", "")
        else asyncio.sleep(0)
    )

    max_relics = 6 if game == GameType.HSR else 5
    relics = getattr(character, "artifacts", getattr(character, "relics", []))[:max_relics]
    relic_size = 50 if game == GameType.HSR else 54
    relic_tasks = [
        download_image(r.icon_url, size=(relic_size, relic_size)) if getattr(r, "icon_url", "") else asyncio.sleep(0)
        for r in relics
    ]

    all_tasks = [char_img_task, weapon_img_task] + relic_tasks
    results = await asyncio.gather(*all_tasks, return_exceptions=True)

    char_img = results[0] if isinstance(results[0], Image.Image) else None
    weapon_img = results[1] if isinstance(results[1], Image.Image) else None
    relic_imgs: List[Optional[Image.Image]] = [
        r if isinstance(r, Image.Image) else None for r in results[2 : 2 + len(relics)]
    ]

    return await asyncio.to_thread(
        _sync_render_character_card, character, game, char_img, weapon_img, relic_imgs
    )


def _sync_render_character_card(
    character: Any,
    game: GameType,
    char_img: Optional[Image.Image] = None,
    weapon_img: Optional[Image.Image] = None,
    relic_imgs: Optional[List[Optional[Image.Image]]] = None,
) -> io.BytesIO:
    if relic_imgs is None:
        relic_imgs = []

    is_hsr = (game == GameType.HSR)
    width = 960
    height = 560
    slot_h = 66 if is_hsr else 76
    spacing = 8 if is_hsr else 10
    ry_start = 68 if is_hsr else 78
    max_relics = 6 if is_hsr else 5

    if not is_hsr:
        start_col = (20, 35, 50)
        end_col = (12, 20, 30)
        accent_col = (91, 192, 190)
        equip_label = "VŨ KHÍ"
        badge_prefix = "C"
        badge_val = getattr(character, "constellation", 0)
    else:
        start_col = (32, 22, 54)
        end_col = (18, 14, 32)
        accent_col = (186, 104, 200)
        equip_label = "NÓN ÁNH SÁNG"
        badge_prefix = "E"
        badge_val = getattr(character, "eidolon", 0)

    base_img = create_gradient_bg(width, height, start_col, end_col)

    # Lớp overlay kính mờ
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)

    # Viền bao ngoài thẻ
    draw_rounded_rect(d_overlay, [12, 12, width - 12, height - 12], radius=18, fill=None, outline=(65, 75, 95, 160), width=2)

    # Cột trái: Thông tin nhân vật & Vũ khí
    draw_rounded_rect(d_overlay, [28, 24, 370, height - 24], radius=14, fill=(255, 255, 255, 18), outline=(255, 255, 255, 35))

    # Khung Vũ Khí / Nón Ánh Sáng
    draw_rounded_rect(d_overlay, [42, 120, 356, 216], radius=10, fill=(0, 0, 0, 100), outline=(255, 255, 255, 25))

    # Khung Chỉ Số Chiến Đấu
    draw_rounded_rect(d_overlay, [42, 228, 356, height - 36], radius=10, fill=(0, 0, 0, 100), outline=(255, 255, 255, 25))

    # Cột phải: Thánh Di Vật / Di Vật
    draw_rounded_rect(d_overlay, [386, 24, width - 24, height - 24], radius=14, fill=(255, 255, 255, 18), outline=(255, 255, 255, 35))

    relics = getattr(character, "artifacts", getattr(character, "relics", []))
    if relics:
        for idx in range(min(len(relics), max_relics)):
            ry = ry_start + idx * (slot_h + spacing)
            draw_rounded_rect(d_overlay, [400, ry, width - 38, ry + slot_h], radius=8, fill=(0, 0, 0, 100), outline=(255, 255, 255, 25))

    base_img = Image.alpha_composite(base_img, overlay)

    # Dán ảnh avatar nhân vật
    if char_img:
        av_x, av_y = 278, 34
        av_size = 76
        mask = Image.new("L", (av_size, av_size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, av_size, av_size], radius=10, fill=255)
        char_resized = char_img.resize((av_size, av_size), Image.Resampling.LANCZOS)
        if char_resized.mode == "RGBA":
            base_img.paste(char_resized, (av_x, av_y), mask=char_resized.split()[3])
        else:
            base_img.paste(char_resized, (av_x, av_y), mask=mask)

        d_temp = ImageDraw.Draw(base_img)
        d_temp.rounded_rectangle([av_x, av_y, av_x + av_size, av_y + av_size], radius=10, outline=accent_col, width=2)

    # Dán ảnh vũ khí
    if weapon_img:
        w_x, w_y = 286, 134
        w_size = 58
        w_resized = weapon_img.resize((w_size, w_size), Image.Resampling.LANCZOS)
        if w_resized.mode == "RGBA":
            base_img.paste(w_resized, (w_x, w_y), mask=w_resized.split()[3])
        else:
            base_img.paste(w_resized, (w_x, w_y))

    # Dán ảnh từng Thánh Di Vật / Di Vật
    if relics:
        r_size = 48 if is_hsr else 54
        for idx in range(min(len(relics), max_relics)):
            r_img = relic_imgs[idx] if idx < len(relic_imgs) else None
            if r_img:
                ry = ry_start + idx * (slot_h + spacing)
                rx = 408
                r_resized = r_img.resize((r_size, r_size), Image.Resampling.LANCZOS)
                ry_offset = (slot_h - r_size) // 2
                if r_resized.mode == "RGBA":
                    base_img.paste(r_resized, (rx, ry + ry_offset), mask=r_resized.split()[3])
                else:
                    base_img.paste(r_resized, (rx, ry + ry_offset))

    draw = ImageDraw.Draw(base_img)

    # Tên nhân vật
    font_name = get_font(24, bold=True)
    draw.text((46, 42), character.name[:14], fill=(255, 255, 255), font=font_name)

    # Cấp độ & Cung mệnh / Tinh hồn
    font_meta = get_font(14, bold=True)
    elem_str = getattr(character, "element", "")
    draw.text((46, 79), f"Lv.{character.level}  •  {badge_prefix}{badge_val}  •  {elem_str}", fill=accent_col, font=font_meta)

    # Khung Vũ Khí tiêu đề
    font_wtitle = get_font(12, bold=True)
    draw.text((52, 130), equip_label, fill=(180, 190, 205), font=font_wtitle)

    weapon = getattr(character, "weapon", getattr(character, "light_cone", None))
    if weapon:
        w_name = getattr(weapon, "name", "Chưa trang bị")
        w_level = getattr(weapon, "level", 1)
        w_refine = getattr(weapon, "refinement", getattr(weapon, "superimposition", 1))
        font_wname = get_font(13 if len(w_name) > 22 else 14, bold=True)
        draw.text((52, 154), w_name[:26], fill=(255, 255, 255), font=font_wname)
        font_winfo = get_font(12, bold=False)
        draw.text((52, 182), f"Cấp: {w_level}  •  {('R' if not is_hsr else 'S')}{w_refine}", fill=(200, 215, 230), font=font_winfo)
    else:
        font_wname = get_font(14, bold=False)
        draw.text((52, 158), "Chưa trang bị", fill=(150, 160, 175), font=font_wname)

    # Chỉ số chiến đấu
    font_stitle = get_font(12, bold=True)
    draw.text((52, 236), "CHỈ SỐ CHIẾN ĐẤU", fill=(180, 190, 205), font=font_stitle)

    stats = getattr(character, "stats", {})
    stat_items = list(stats.items())[:13]
    if len(stat_items) >= 12:
        start_stat_y = 254
        spacing_stat = 21
        font_sitem = get_font(11, bold=False)
        font_sval = get_font(11, bold=True)
    elif len(stat_items) >= 10:
        start_stat_y = 256
        spacing_stat = 23
        font_sitem = get_font(12, bold=False)
        font_sval = get_font(12, bold=True)
    elif len(stat_items) >= 8:
        start_stat_y = 258
        spacing_stat = 25
        font_sitem = get_font(12, bold=False)
        font_sval = get_font(12, bold=True)
    else:
        start_stat_y = 260
        spacing_stat = 28
        font_sitem = get_font(13, bold=False)
        font_sval = get_font(13, bold=True)

    for i, (k, v) in enumerate(stat_items):
        cur_y = start_stat_y + i * spacing_stat
        draw.text((52, cur_y), str(k), fill=(190, 200, 215), font=font_sitem)
        val_str = str(v)
        val_w = int(draw.textlength(val_str, font=font_sval))
        draw.text((346 - val_w, cur_y), val_str, fill=(255, 255, 255), font=font_sval)

    # Cột phải: Thánh Di Vật / Di Vật
    font_rtitle = get_font(16, bold=True)
    relic_box_label = "THÁNH DI VẬT TRANG BỊ" if not is_hsr else "DI VẬT & PHỤ KIỆN VỊ DIỆN"
    draw.text((406, 40 if is_hsr else 44), relic_box_label, fill=(255, 255, 255), font=font_rtitle)

    if relics:
        font_rslot = get_font(12, bold=True)
        font_rset = get_font(11, bold=False)
        font_rmain = get_font(13 if not is_hsr else 12, bold=True)
        font_rsub = get_font(11 if not is_hsr else 10, bold=False)

        for idx in range(min(len(relics), max_relics)):
            relic = relics[idx]
            ry = ry_start + idx * (slot_h + spacing)
            tx = 468  # Khoảng cách bắt đầu sau icon di vật

            # Tên vị trí và cấp độ
            slot_text = f"{relic.slot} (+{relic.level})"
            slot_w = int(draw.textlength(slot_text, font=font_rslot))
            draw.text((tx, ry + (5 if is_hsr else 7)), slot_text, fill=accent_col, font=font_rslot)

            # Tên bộ di vật (tự căn sau vị trí)
            if relic.set_name and relic.set_name not in ["Bộ Thánh Di Vật", "Di Vật"]:
                draw.text((tx + slot_w + 10, ry + (6 if is_hsr else 8)), f"•  {relic.set_name[:40]}", fill=(190, 200, 215), font=font_rset)

            # Chỉ số chính (Cột trái)
            draw.text((tx, ry + (25 if is_hsr else 30)), f"{relic.main_stat}:", fill=(200, 210, 225), font=get_font(10, bold=False))
            draw.text((tx, ry + (41 if is_hsr else 48)), str(relic.main_value), fill=(255, 255, 255), font=font_rmain)

            # Lưới hiển thị toàn bộ 4 dòng phụ (2 cột x 2 hàng)
            col1_x = tx + 130
            col2_x = tx + 270

            sub_items = relic.sub_stats[:4] if relic.sub_stats else []
            for s_idx, sub_raw in enumerate(sub_items):
                formatted_sub = format_substat_display(sub_raw)
                s_x = col1_x if s_idx % 2 == 0 else col2_x
                s_y = (ry + 25 if s_idx < 2 else ry + 43) if is_hsr else (ry + 29 if s_idx < 2 else ry + 49)
                draw.text((s_x, s_y), f"• {formatted_sub}", fill=(210, 220, 235), font=font_rsub)
    else:
        font_norelic = get_font(14, bold=False)
        draw.text((415, 100), "Chưa có thông tin di vật hoặc di vật bị ẩn", fill=(160, 170, 185), font=font_norelic)

    buffer = io.BytesIO()
    base_img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

"""Dữ liệu hướng dẫn xây dựng (Build Guides) tiếng Việt cho nhân vật Genshin Impact."""

from typing import Dict, Optional
from app.games.genshin.models import GenshinBuild

GENSHIN_BUILDS: Dict[str, GenshinBuild] = {
    "furina": GenshinBuild(
        character_name="Furina",
        element="Hydro",
        rarity=5,
        role="Sub DPS / Buffer sát thương toàn đội",
        weapons=[
            "Huy Hoàng Của Lặng Lẽ (Trấn)",
            "Thanh Kiếm Rỉ Sét R5 / Kiếm Tây Phong R5",
            "Ống Dẫn Khí Fleuve Cendre R5",
            "Ánh Trăng Xiphos",
        ],
        artifact_sets=[
            "4x Đoàn Kịch Hoàng Kim (Khuyên dùng nhất)",
            "2x Thiên Nham Cổ Vững + 2x Thợ Săn Marechaussee (Tạm thời)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "HP% hoặc Hiệu Quả Nạp (nếu thiếu ER)",
            "Ly (Goblet)": "HP% hoặc Sát Thương Thủy",
            "Nón (Circlet)": "Tỷ Lệ Bạo Kích / Sát Thương Bạo Kích",
        },
        substats=[
            "Hiệu Quả Nạp NT (đạt 160% - 200% tùy đội hình)",
            "Tỷ Lệ Bạo Kích",
            "Sát Thương Bạo Kích",
            "HP%",
        ],
        talent_priority="Kỹ Năng Nguyên Tố (E) = Kỹ Năng Nộ (Q) > Đánh Thường",
        team_synergy=[
            "Neuvillette + Furina + Kazuha + Baizhu",
            "Hu Tao + Xingqiu + Furina + Xianyun",
            "Arlecchino + Furina + Yelan + Bennett",
            "Raiden Shogun + Furina + Yelan + Jean",
        ],
        notes="Furina cần đủ Nạp để nộ liên tục mỗi chu kỳ. Đi cùng healer hồi máu toàn đội (Jean, Baizhu, Xianyun, Charlotte) để tích tầng Fanfare nhanh nhất.",
    ),
    "neuvillette": GenshinBuild(
        character_name="Neuvillette",
        element="Hydro",
        rarity=5,
        role="Main DPS Trọng Kích",
        weapons=[
            "Nghi Lễ Dòng Chảy Bất Tận (Trấn)",
            "Ngọc Tế Lễ R5 (Nhật Ký Hành Trình)",
            "Mẫu Kim Phách R5 (Rèn F2P)",
            "Vòng Xoáy Tinh Khiết / Điển Tích Tây Phong",
        ],
        artifact_sets=[
            "4x Thợ Săn Marechaussee (Mạnh nhất)",
            "4x Trầm Luân Giữa Tâm Tưởng",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "HP%",
            "Ly (Goblet)": "Sát Thương Thủy hoặc HP%",
            "Nón (Circlet)": "Sát Thương Bạo Kích / HP% (Hạn chế thừa CR vì set 4 cho 36%)",
        },
        substats=[
            "Sát Thương Bạo Kích",
            "HP%",
            "Tỷ Lệ Bạo Kích (giữ ở 50-64%)",
            "Hiệu Quả Nạp (110 - 130%)",
        ],
        talent_priority="Tấn Công Thường (Trọng Kích) >>> Kỹ Năng Nộ (Q) > Kỹ Năng Nguyên Tố (E)",
        team_synergy=[
            "Neuvillette + Furina + Kazuha + Baizhu/Zhongli",
            "Neuvillette + Fischl + Beidou + Kazuha (Taser)",
            "Neuvillette + Nahida + Raiden (EM) + Zhongli (Hyperbloom)",
        ],
        notes="Sức mạnh chính nằm ở Trọng Kích bắn tia Hydro. Phản ứng với 3 nguyên tố khác nhau để kích đủ 3 tầng nội tại Thiên Phú.",
    ),
    "arlecchino": GenshinBuild(
        character_name="Arlecchino",
        element="Pyro",
        rarity=5,
        role="Main DPS Đánh Thường Khế Ước Sinh Mệnh",
        weapons=[
            "Hình Bóng Vầng Trăng Đỏ (Trấn)",
            "Hòa Phác Diệp (Xương Cá)",
            "Trượng Hộ Ma / Quyết Đấu R5",
            "Thương Hắc Nham / Mũi Giáo Sấm Sét",
        ],
        artifact_sets=[
            "4x Dư Âm Ảo Tưởng Hài Hòa (Tối ưu nhất)",
            "4x Giác Đấu Sĩ Triệu Tập",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "Tấn Công% hoặc Tinh Thông NT (nếu chơi Bốc Hơi)",
            "Ly (Goblet)": "Sát Thương Hỏa",
            "Nón (Circlet)": "Tỷ Lệ Bạo Kích / Sát Thương Bạo Kích",
        },
        substats=[
            "Tỷ Lệ Bạo Kích",
            "Sát Thương Bạo Kích",
            "Tấn Công%",
            "Tinh Thông Nguyên Tố",
        ],
        talent_priority="Tấn Công Thường >>> Kỹ Năng Nguyên Tố (E) > Kỹ Năng Nộ (Q)",
        team_synergy=[
            "Arlecchino + Yelan/Xingqiu + Bennett + Kazuha/Zhongli (Bốc Hơi)",
            "Arlecchino + Chevreuse + Fischl + Bennett (Quá Tải)",
            "Arlecchino + Emilie + Xiangling + Bennett (Thiêu Đốt)",
        ],
        notes="Trong chiến đấu chỉ có thể hồi máu qua Kỹ Năng Nộ của bản thân. Đi cùng khiên chắn như Zhongli giúp combo an toàn tối đa.",
    ),
    "raiden shogun": GenshinBuild(
        character_name="Raiden Shogun",
        element="Electro",
        rarity=5,
        role="Main DPS / Ắc Quy Nạp Năng Lượng Toàn Đội",
        weapons=[
            "Đoạn Thảo Trảm Quang (Trấn)",
            "Lao Câu Cá R5 (Vũ khí câu cá F2P cực mạnh)",
            "Xương Sống Thiên Không",
            "Thương Tây Phong",
        ],
        artifact_sets=[
            "4x Dấu Ấn Ngăn Cách (Bộ trang bị trấn phái)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "Hiệu Quả Nạp NT",
            "Ly (Goblet)": "Sát Thương Lôi hoặc Tấn Công%",
            "Nón (Circlet)": "Tỷ Lệ Bạo Kích / Sát Thương Bạo Kích",
        },
        substats=[
            "Hiệu Quả Nạp NT (mục tiêu 250% - 270%)",
            "Tỷ Lệ Bạo Kích",
            "Sát Thương Bạo Kích",
            "Tấn Công%",
        ],
        talent_priority="Kỹ Năng Nộ (Q) >>> Kỹ Năng Nguyên Tố (E) > Tấn Công Thường",
        team_synergy=[
            "Raiden + Xiangling + Xingqiu/Yelan + Bennett (Lôi Thần Quốc Dân)",
            "Raiden + Sara C6 + Kazuha + Bennett (Hypercarry)",
            "Raiden + Furina + Yelan + Jean (Taser cao cấp)",
        ],
        notes="Càng nhiều Hiệu Quả Nạp, sát thương Lôi và khả năng sạc năng lượng cho đồng đội càng tăng mạnh nhờ Thiên Phú nội tại.",
    ),
    "zhonli": GenshinBuild(
        character_name="Zhongli",
        element="Geo",
        rarity=5,
        role="Hỗ trợ Tạo Khiên Tuyệt Đối / Giảm Kháng Quái",
        weapons=[
            "Hắc Anh Thương (F2P tối đa HP)",
            "Thương Tây Phong (Hỗ trợ nạp team)",
            "Trượng Hộ Ma (Build Sub-DPS Nộ)",
        ],
        artifact_sets=[
            "4x Thiên Nham Cổ Vững (Tăng HP & buff ATK toàn đội)",
            "4x Tông Thất Cổ Nhân (Buff ATK khi Nộ)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "HP%",
            "Ly (Goblet)": "HP%",
            "Nón (Circlet)": "HP% (hoặc Tỷ Lệ Bạo Kích nếu cầm Tây Phong)",
        },
        substats=[
            "HP%",
            "HP phẳng",
            "Hiệu Quả Nạp NT",
            "Tỷ Lệ Bạo Kích (nếu cầm Tây Phong)",
        ],
        talent_priority="Kỹ Năng Nguyên Tố (E) >>> Kỹ Năng Nộ (Q) > Tấn Công Thường",
        team_synergy=[
            "Phù hợp với hầu hết mọi đội hình cần sự an toàn tuyệt đối (Hu Tao, Ganyu, Yoimiya, Arlecchino, Navia).",
        ],
        notes="Giữ E để tạo khiên dày nhất game và giảm 20% toàn bộ kháng nguyên tố của địch xung quanh.",
    ),
    "nahida": GenshinBuild(
        character_name="Nahida",
        element="Dendro",
        rarity=5,
        role="Sub DPS Thảo / Hỗ trợ Phản Ứng Nguyên Tố Thảo",
        weapons=[
            "Cõi Mộng Ngàn Đêm (Trấn)",
            "Chương Nhạc Lang Thang",
            "Mảnh Chương Tế Lễ R5",
            "Hạt Muội Ma Thuật (3 sao F2P)",
        ],
        artifact_sets=[
            "4x Ký Ức Rừng Sâu (Giảm 30% kháng Thảo)",
            "4x Giấc Mộng Hoàng Kim (Nếu trong đội đã có người mang Ký Ức Rừng Sâu)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "Tinh Thông Nguyên Tố",
            "Ly (Goblet)": "Tinh Thông Nguyên Tố hoặc Sát Thương Thảo",
            "Nón (Circlet)": "Tinh Thông Nguyên Tố hoặc Tỷ Lệ / ST Bạo Kích",
        },
        substats=[
            "Tinh Thông Nguyên Tố (đạt mốc 800 - 1000 EM)",
            "Tỷ Lệ Bạo Kích",
            "Sát Thương Bạo Kích",
            "Hiệu Quả Nạp NT (120 - 140%)",
        ],
        talent_priority="Kỹ Năng Nguyên Tố (E) > Kỹ Năng Nộ (Q) > Tấn Công Thường",
        team_synergy=[
            "Alhaitham + Nahida + Xingqiu + Kuki Shinobu (Hyperbloom)",
            "Nilou + Nahida + Kokomi + Baizhu (Nở Rộ Siêu Cấp)",
            "Cyno + Nahida + Furina + Baizhu (Quickbloom)",
        ],
        notes="Nahida chuyển đổi Tinh Thông Nguyên Tố thành Tỷ Lệ Bạo Kích và Sát Thương cho Kỹ Năng Nguyên Tố thông qua thiên phú.",
    ),
    "kaedehara kazuha": GenshinBuild(
        character_name="Kaedehara Kazuha",
        element="Anemo",
        rarity=5,
        role="Hỗ Trợ Gom Quái / Khuếch Tán Tăng Sát Thương Nguyên Tố",
        weapons=[
            "Lời Thề Tự Do Cổ Xưa (Trấn)",
            "Ánh Trăng Xiphos",
            "Kiếm Tây Phong R5",
            "Thiết Phong Kích (Rèn F2P)",
        ],
        artifact_sets=[
            "4x Bóng Hình Màu Xanh (Bắt buộc để giảm 40% kháng nguyên tố)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "Tinh Thông Nguyên Tố (hoặc Nạp nếu dùng Thiết Phong Kích)",
            "Ly (Goblet)": "Tinh Thông Nguyên Tố",
            "Nón (Circlet)": "Tinh Thông Nguyên Tố",
        },
        substats=[
            "Tinh Thông Nguyên Tố (càng nhiều càng tốt, mục tiêu 900+)",
            "Hiệu Quả Nạp NT (160% - 180%)",
            "Tỷ Lệ Bạo Kích (nếu dùng Kiếm Tây Phong)",
        ],
        talent_priority="Kỹ Năng Nộ (Q) = Kỹ Năng Nguyên Tố (E) > Tấn Công Thường",
        team_synergy=[
            "Mọi đội hình nguyên tố Hỏa/Thủy/Lôi/Băng (Childe International, Raiden Hypercarry, Ayaka Freeze, Neuvillette Furina).",
        ],
        notes="Khuếch tán nguyên tố nào sẽ buff sát thương nguyên tố đó cho toàn đội dựa trên lượng Tinh Thông của Kazuha.",
    ),
    "xilonen": GenshinBuild(
        character_name="Xilonen",
        element="Geo",
        rarity=5,
        role="Hỗ trợ Giảm Kháng Toàn Năng / Hồi Máu",
        weapons=[
            "Bài Ca Đỉnh Núi (Trấn)",
            "Thanh Kiếm Tây Phong R5",
            "Kiếm Sáo / Kiếm Rèn Natlan",
        ],
        artifact_sets=[
            "4x Bí Cảnh Dũng Sĩ Tro Tàn (Cực mạnh ở Natlan)",
            "4x Giáp Trụ Tinh Xảo (Def)",
        ],
        main_stats={
            "Đồng Hồ (Sands)": "Phòng Ngự% hoặc Nạp",
            "Ly (Goblet)": "Phòng Ngự%",
            "Nón (Circlet)": "Tăng Trị Liệu hoặc Phòng Ngự% / Tỷ Lệ Bạo Kích",
        },
        substats=[
            "Phòng Ngự%",
            "Hiệu Quả Nạp NT",
            "Tỷ Lệ Bạo Kích (nếu dùng Tây Phong)",
        ],
        talent_priority="Kỹ Năng Nguyên Tố (E) > Kỹ Năng Nộ (Q) > Tấn Công Thường",
        team_synergy=[
            "Mavuika / Arlecchino + Furina + Xilonen + Kazuha",
            "Navia + Xilonen + Furina + Bennett",
            "Neuvillette + Furina + Xilonen + Kazuha",
        ],
        notes="Giảm tới 36% kháng các nguyên tố của đồng đội mang theo dạng Sampler. Rất linh hoạt và buff sát thương cực lớn.",
    ),
}


def get_genshin_build(character_name: str) -> Optional[GenshinBuild]:
    """Tìm build cho nhân vật Genshin theo tên (không phân biệt hoa thường)."""
    key = character_name.strip().lower()
    if key in GENSHIN_BUILDS:
        return GENSHIN_BUILDS[key]

    # Tìm kiếm tương đối
    for name, build in GENSHIN_BUILDS.items():
        if key in name or name in key:
            return build

    return None

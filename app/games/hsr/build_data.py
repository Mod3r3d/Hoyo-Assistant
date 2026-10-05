"""Dữ liệu hướng dẫn xây dựng (Build Guides) tiếng Việt cho nhân vật Honkai: Star Rail."""

from typing import Dict, Optional
from app.games.hsr.models import HSRBuild

HSR_BUILDS: Dict[str, HSRBuild] = {
    "acheron": HSRBuild(
        character_name="Acheron",
        path="Hư Vô",
        element="Lôi",
        rarity=5,
        role="Main DPS Sát Thương Tuyệt Kỹ",
        light_cones=[
            "Dọc Theo Bờ Mộng (Trấn S1)",
            "Cơn Mưa Tầm Tã (Nón Sói Bạc)",
            "Chúc Ngủ Ngon (S5)",
            "Chuyến Tàu Đêm Vô Tận",
        ],
        relic_sets=[
            "4x Tiên Phong Trong Nước Chết (Tốt nhất)",
            "4x Ban Nhạc Sấm Sét",
        ],
        planar_sets=[
            "2x Izumo Gensei & Vương Quốc Thần Thoại Takama",
            "2x Trạm Phong Ấn Không Gian",
        ],
        main_stats={
            "Áo (Body)": "Sát Thương Bạo Kích / Tỷ Lệ Bạo Kích",
            "Giày (Feet)": "Tấn Công% hoặc Tốc Độ",
            "Cầu Vị Diện (Sphere)": "Tăng ST Lôi hoặc Tấn Công%",
            "Dây Liên Kết (Rope)": "Tấn Công% (Acheron không dùng dây Nạp)",
        },
        substats=[
            "Sát Thương Bạo Kích",
            "Tỷ Lệ Bạo Kích",
            "Tấn Công%",
            "Tốc Độ",
        ],
        trace_priority="Tuyệt Kỹ >>> Chiến Kỹ > Thiên Phú > Tấn Công Thường",
        team_synergy=[
            "Acheron + Jiaoqiu + Pela/Silver Wolf + Aventurine (Đội hình tối ưu nhất)",
            "Acheron + Black Swan + Kafka + Huohuo",
            "Acheron + Sparkle + Pela + Aventurine (Nếu có E2)",
        ],
        notes="Acheron không tích nộ bằng năng lượng mà bằng điểm 'Mộng Tàn' khi kẻ địch nhận debuff. Jiaoqiu và Aventurine (với Xu Hướng Vũ Trụ) là các đối tác sạc điểm tuyệt vời.",
    ),
    "firefly": HSRBuild(
        character_name="Firefly (Đom Đóm)",
        path="Hủy Diệt",
        element="Hỏa",
        rarity=5,
        role="Main DPS Siêu Kích Phá (Super Break)",
        light_cones=[
            "Nơi Ước Mơ Nghỉ Lại (Trấn S1)",
            "Lời Hứa Không Quên (S5)",
            "Sự Sụp Đổ Của Aeon (S5 shop Herta F2P)",
            "Bí Mật Của Kẻ Bội Nguyện",
        ],
        relic_sets=[
            "4x Thiết Kỵ Kỵ Binh Lửa (Bắt buộc để bỏ qua phòng ngự Siêu Kích Phá)",
            "2x Thiết Kỵ + 2x Kẻ Trộm Vết Tích",
        ],
        planar_sets=[
            "2x Lò Rèn Kalpagni (Tăng Tốc độ & 40% Tấn Công Kích Phá)",
            "2x Talia - Vương Quốc Trộm Cắp",
        ],
        main_stats={
            "Áo (Body)": "Tấn Công%",
            "Giày (Feet)": "Tốc Độ (mục tiêu 150+ ngoài giao tranh)",
            "Cầu Vị Diện (Sphere)": "Tấn Công%",
            "Dây Liên Kết (Rope)": "Tấn Công Kích Phá",
        },
        substats=[
            "Tấn Công Kích Phá (càng cao càng tốt, 250%+)",
            "Tốc Độ (đạt mốc hành động thêm trong trạng thái Đốt Cháy Hoàn Toàn)",
            "Tấn Công% (chuyển đổi thành Tấn Công Kích Phá)",
        ],
        trace_priority="Thiên Phú = Tuyệt Kỹ = Chiến Kỹ > Tấn Công Thường",
        team_synergy=[
            "Firefly + Nhà Khai Phá (Hòa Hợp) + Ruan Mei + Gallagher/Lingsha (Đội hình Kích Phá chuẩn mực)",
        ],
        notes="Firefly không cần chỉ số Bạo Kích. Toàn bộ sát thương đến từ phản ứng Siêu Kích Phá kết hợp cùng Nhà Khai Phá Hòa Hợp.",
    ),
    "feixiao": HSRBuild(
        character_name="Feixiao",
        path="Săn Bắn",
        element="Phong",
        rarity=5,
        role="Main DPS Đòn Đánh Theo Sau Siêu Cấp (FUA)",
        light_cones=[
            "Săn Đuổi Đến Tận Cùng (Trấn S1)",
            "Chuyến Du Ngoạn Trên Biển Sao (S5 shop Herta)",
            "Luận Kiếm (S5)",
            "Chỉ Trầm Mặc Là Tốt",
        ],
        relic_sets=[
            "4x Dũng Khí Gió Lộng (Bộ mới chuyên buff Tuyệt Kỹ & Đòn Đánh Theo Sau)",
            "2x Đại Công Tước + 2x Gió Lộng",
        ],
        planar_sets=[
            "2x Duran - Vương Triều Sói Hoang",
            "2x Salsotto Dừng Xoay",
        ],
        main_stats={
            "Áo (Body)": "Tỷ Lệ Bạo Kích / Sát Thương Bạo Kích",
            "Giày (Feet)": "Tốc Độ",
            "Cầu Vị Diện (Sphere)": "Tăng ST Phong",
            "Dây Liên Kết (Rope)": "Tấn Công%",
        },
        substats=[
            "Tỷ Lệ Bạo Kích (càng gần 100% càng tốt)",
            "Sát Thương Bạo Kích",
            "Tốc Độ",
            "Tấn Công%",
        ],
        trace_priority="Tuyệt Kỹ >>> Thiên Phú > Chiến Kỹ > Tấn Công Thường",
        team_synergy=[
            "Feixiao + Robin + Topaz / Moze / March 7th Săn Bắn + Aventurine (Đội hình FUA Thần Tốc)",
        ],
        notes="Feixiao tích điểm Tuyệt Kỹ dựa trên số lần tấn công của toàn đội (cứ 2 đòn đánh của đồng minh = 1 tầng Phi Vũ). Đi cùng các tướng FUA liên tục như Topaz, Moze, March 7th.",
    ),
    "robin": HSRBuild(
        character_name="Robin",
        path="Hòa Hợp",
        element="Vật Lý",
        rarity=5,
        role="Buffer Tiến Lượt Toàn Đội & Đòn Đánh Kèm",
        light_cones=[
            "Ánh Sáng Rực Rỡ Bay Xa (Trấn S1)",
            "Hành Trình Ngày Mai (S5 Event F2P)",
            "Khắc Khắc Khắc Khắc Khắc",
            "Bánh Xe Quá Khứ (S5)",
        ],
        relic_sets=[
            "2x Xạ Thủ Thiện Xạ + 2x Tù Nhân Giam Giữ Sâu (Max ATK%)",
            "4x Thiết Kỵ Băng Giá",
        ],
        planar_sets=[
            "2x Lushaka - Dải Đất Ngập Nước (Tăng hồi năng lượng & buff ATK chủ lực)",
            "2x Hạm Đội Vô Tận / Vonwacq Sống Động",
        ],
        main_stats={
            "Áo (Body)": "Tấn Công%",
            "Giày (Feet)": "Tấn Công%",
            "Cầu Vị Diện (Sphere)": "Tấn Công%",
            "Dây Liên Kết (Rope)": "Hiệu Suất Hồi Năng Lượng (Bắt buộc)",
        },
        substats=[
            "Tấn Công%",
            "Tốc Độ (khoảng 120-125)",
            "Kháng Hiệu Ứng / HP%",
        ],
        trace_priority="Tuyệt Kỹ = Chiến Kỹ > Thiên Phú > Tấn Công Thường",
        team_synergy=[
            "Robin phù hợp với hầu hết mọi đội hình, đặc biệt là Đòn Đánh Theo Sau (Feixiao, Dr. Ratio, Topaz, Yunli) và Siêu Cấp Năng Động.",
        ],
        notes="Khi Tuyệt Kỹ kích hoạt, Robin lập tức hành động toàn đội và gây sát thương Vật Lý kèm theo mỗi khi đồng minh đánh trúng địch.",
    ),
    "sunday": HSRBuild(
        character_name="Sunday",
        path="Hòa Hợp",
        element="Số Ảo",
        rarity=5,
        role="Buffer Kéo Lượt & Bạo Kích Độc Quyền Triệu Hồi Vật",
        light_cones=[
            "Mặt Trời Mọc Đầy Hy Vọng (Trấn S1)",
            "Khắc Lên Ký Ức",
            "Cuộc Chiến Chưa Nguôi (Nón Bronya)",
            "Điệu Nhảy Đồng Điệu (S5)",
        ],
        relic_sets=[
            "4x Du Khách Rong Ruổi Biển Sao",
            "2x Tín Sứ + 2x Thợ Rèn",
        ],
        planar_sets=[
            "2x Lushaka - Dải Đất Ngập Nước",
            "2x Keel Gãy",
        ],
        main_stats={
            "Áo (Body)": "Sát Thương Bạo Kích",
            "Giày (Feet)": "Tốc Độ",
            "Cầu Vị Diện (Sphere)": "HP% hoặc Phòng Ngự%",
            "Dây Liên Kết (Rope)": "Hiệu Suất Hồi Năng Lượng",
        },
        substats=[
            "Sát Thương Bạo Kích",
            "Tốc Độ",
            "Kháng Hiệu Ứng",
            "HP% / DEF%",
        ],
        trace_priority="Chiến Kỹ = Tuyệt Kỹ > Thiên Phú > Tấn Công Thường",
        team_synergy=[
            "Sunday + Jing Yuan / Feixiao / Dan Heng IL + Robin + Aventurine / Huohuo",
        ],
        notes="Sunday cung cấp khả năng hồi Điểm Chiến Kỹ, kéo lượt cả nhân vật lẫn vật triệu hồi, và buff lượng lớn Sát Thương Bạo Kích.",
    ),
    "ruan mei": HSRBuild(
        character_name="Ruan Mei",
        path="Hòa Hợp",
        element="Băng",
        rarity=5,
        role="Buffer Toàn Đội Đa Năng / Tăng Hiệu Suất Kích Phá & Tốc Độ",
        light_cones=[
            "Chiếc Gương Trong Quá Khứ (Trấn S1)",
            "Ký Ức Thời Gian (S5 F2P)",
            "Điệu Nhảy Đồng Điệu",
            "Hình Ảnh Trong Ký Ức (S5)",
        ],
        relic_sets=[
            "4x Tín Sứ Du Ngoạn Không Gian Hacker (Buff Tốc độ toàn đội)",
            "4x Kẻ Trộm Vết Tích Bị Bắn Lén",
        ],
        planar_sets=[
            "2x Talia - Vương Quốc Trộm Cắp (Nếu thiếu Kích Phá)",
            "2x Keel Gãy / Hạm Đội Vô Tận / Vonwacq",
        ],
        main_stats={
            "Áo (Body)": "HP% hoặc Phòng Ngự%",
            "Giày (Feet)": "Tốc Độ",
            "Cầu Vị Diện (Sphere)": "HP% hoặc Phòng Ngự%",
            "Dây Liên Kết (Rope)": "Hiệu Suất Hồi Năng Lượng (Bắt buộc)",
        },
        substats=[
            "Tấn Công Kích Phá (đạt mốc 160% ngoài trận -> vào trận nhận 20% thiên phú là đủ 180%)",
            "Tốc Độ (145+)",
            "HP% / DEF%",
        ],
        trace_priority="Chiến Kỹ = Tuyệt Kỹ > Thiên Phú > Tấn Công Thường",
        team_synergy=[
            "Là buffer đa năng bậc nhất trong game, xuất hiện ở đội hình Siêu Kích Phá (Firefly, Boothill), DoT (Kafka, Black Swan) và DPS Đôi (Jingliu, Blade).",
        ],
        notes="Giữ buff Chiến Kỹ liên tục để nhận 50% Hiệu Suất Kích Phá, tăng 68% Sát Thương toàn đội và tăng Tốc Độ.",
    ),
    "aventurine": HSRBuild(
        character_name="Aventurine",
        path="Bảo Hộ",
        element="Số Ảo",
        rarity=5,
        role="Tạo Khiên Tự Động Toàn Đội / Sub DPS Đòn Đánh Theo Sau",
        light_cones=[
            "Mệnh Vận Chưa Công Bằng (Trấn S1)",
            "Chiến Thắng Trong Nháy Mắt",
            "Xu Hướng Vũ Trụ Thị Trường (Cực tốt khi đi với Acheron)",
            "Ngày Mai Tươi Sáng / Dệt Nên Sợi Chỉ Vận Mệnh",
        ],
        relic_sets=[
            "4x Thánh Kỵ Sĩ Giáo Hội Tịnh Hóa (Khiên dày nhất)",
            "2x Thánh Kỵ Sĩ + 2x Đại Công Tước (Build lai sát thương)",
        ],
        planar_sets=[
            "2x Salsotto Dừng Xoay",
            "2x Keel Gãy",
        ],
        main_stats={
            "Áo (Body)": "Phòng Ngự% (hoặc ST Bạo Kích nếu đã đủ 4000 DEF)",
            "Giày (Feet)": "Tốc Độ hoặc Phòng Ngự%",
            "Cầu Vị Diện (Sphere)": "Phòng Ngự% hoặc ST Số Ảo",
            "Dây Liên Kết (Rope)": "Phòng Ngự% hoặc Hiệu Suất Hồi Năng Lượng",
        },
        substats=[
            "Phòng Ngự% (ưu tiên đạt tối thiểu 4000 DEF để nhận tối đa 48% Tỷ Lệ Bạo Kích)",
            "Tốc Độ",
            "Sát Thương Bạo Kích",
            "Kháng Hiệu Ứng",
        ],
        trace_priority="Chiến Kỹ = Thiên Phú > Tuyệt Kỹ > Tấn Công Thường",
        team_synergy=[
            "Mọi đội hình cần sự an toàn, đặc biệt là đội FUA (Feixiao, Robin, Topaz, Dr. Ratio) và Acheron.",
        ],
        notes="Khiên Xu Cược Đỏ Đen tự động làm mới khi Aventurine tích đủ 7 tầng Mù Quáng và thực hiện Đòn Đánh Theo Sau.",
    ),
}


def get_hsr_build(character_name: str) -> Optional[HSRBuild]:
    """Tìm build cho nhân vật HSR theo tên."""
    key = character_name.strip().lower()
    if key in HSR_BUILDS:
        return HSR_BUILDS[key]

    for name, build in HSR_BUILDS.items():
        if key in name or name in key:
            return build

    return None

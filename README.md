# HoyoBot — Discord Bot cho Genshin Impact & Honkai: Star Rail 🌟
*(Tích hợp Lớp Tự Động Hóa Chạy Nền)*

**HoyoBot** là một Discord Bot bằng Python chuyên biệt dành cho hai tựa game nổi tiếng của HoYoverse: **Genshin Impact** và **Honkai: Star Rail**. Bot được xây dựng với kiến trúc phân tầng hiện đại, giao diện hoàn toàn bằng **Tiếng Việt**, ưu tiên tốc độ phản hồi, đồ họa thẻ ảnh (Card) sang trọng và **lớp tự động hóa chạy nền (Automation Layer)** bảo mật cao.

---

## 🎯 Phạm Vi & Triết Lý Thiết Kế

- **Chỉ 2 Tựa Game**: Tập trung sâu vào **Genshin Impact** và **Honkai: Star Rail**. Hoàn toàn không chứa mã nguồn thừa của ZZZ, Honkai Impact 3rd hay Tears of Themis.
- **Tiếng Việt 100%**: Tất cả các lệnh Slash, mô tả, thông báo lỗi, hướng dẫn build, nhật ký và giao diện UI đều được bản địa hóa tiếng Việt trực quan, thân thiện.
- **Lớp Tự Động Hóa Chạy Nền (Automation)**: Tự động điểm danh hàng ngày, phát hiện giftcode mới, tự động đổi mã, hoàn thành nhiệm vụ Mimo/Đồng hành, quét sự kiện web và thông báo Discord không làm nghẽn bot.
- **Bảo Mật Tuyệt Đối**: Cookie / Session HoYoLAB được **mã hóa đối xứng (Fernet/AES)** tại cơ sở dữ liệu. Không bao giờ hiển thị cookie thô ra log hoặc màn hình Discord. Người dùng có toàn quyền bật/tắt (opt-in/opt-out) và thu hồi phiên.
- **Không Gacha History**: Tối giản lưu trữ, loại bỏ toàn bộ tính năng và bảng dữ liệu lịch sử gacha.
- **Không Challenge & End-Game Leaderboard**: Không tạo card hay thống kê Spiral Abyss, La Hoàn, MoC, Pure Fiction, Apocalyptic Shadow.
- **Không Resource Tracking & Reminder**: Không theo dõi Nhựa (Resin), Điểm Khai Phá, không spam nhắc nhở tài nguyên.

---

## ⚡ Các Nhóm Lệnh Chính

### 1. 🤖 Tự Động Hóa Chạy Nền (`/auto`)
- `/auto status`: Mở bảng điều khiển tương tác hiển thị trạng thái tất cả các tính năng tự động (Điểm danh, Giftcode, Mimo, Đồng Hành, Sự kiện) kèm nút bấm thao tác nhanh.
- `/auto toggle <tính_năng> <trạng_thái>`: Bật hoặc tắt từng tính năng tự động cho tài khoản của bạn.
- `/auto session_add`: Mở cửa sổ Modal nhập Cookie HoYoLAB an toàn để kích hoạt tự động hóa.
- `/auto session_remove`: Xóa bỏ phiên đăng nhập Cookie khỏi hệ thống.
- `/auto run <tác_vụ>`: Kích hoạt thủ công chạy ngay một tác vụ tự động (Checkin, Giftcode, Mimo, v.v.).

### 2. 📅 Điểm Danh HoYoLAB (`/checkin`)
- `/checkin now`: Điểm danh ngay lập tức cho các tài khoản game của bạn mà không cần đợi lịch nửa đêm.
- `/checkin status`: Kiểm tra trạng thái điểm danh hôm nay của bạn (Đã nhận hoặc đang chờ).

### 3. 🎁 Mã Quà Tặng Giftcode (`/giftcode`)
- `/giftcode list [game]`: Xem danh sách toàn bộ giftcode đang hoạt động phát hiện bởi bot.
- `/giftcode redeem <code> [game]`: Đổi thủ công một mã quà tặng cho tài khoản của bạn.

### 4. 🔔 Thông Báo Tự Động (`/notify`)
- `/notify status`: Xem cấu hình kênh và mức độ nhận thông báo hiện tại.
- `/notify set <chế_độ>`: Chọn mức độ thông báo (*Chỉ báo lỗi*, *Báo tất cả*, hoặc *Tắt*).
- `/notify channel [kênh]`: Thiết lập gửi thông báo vào một kênh máy chủ cụ thể hoặc gửi qua tin nhắn riêng (DM).

### 5. 👤 Quản Lý Tài Khoản (`/account`)
- `/account add <game> <uid> [nickname]`: Liên kết UID Genshin hoặc Star Rail vào tài khoản Discord của bạn. Tự động nhận diện Server (*Asia, America, Europe, TW/HK/MO*).
- `/account list`: Xem danh sách tất cả các UID bạn đã liên kết kèm nhãn mặc định.
- `/account default`: Mở menu tương tác chọn tài khoản mặc định cho từng game.
- `/account remove`: Mở menu chọn và xác nhận xóa tài khoản đã lưu.

### 6. 📊 Hồ Sơ Người Chơi (`/profile`)
- `/profile genshin [uid] [user]`: Xem thẻ hồ sơ người chơi Genshin (Hạng Mạo Hiểm AR, Cấp Thế Giới, Thành Tựu, Tủ trưng bày nhân vật kèm Cung Mệnh).
- `/profile hsr [uid] [user]`: Xem thẻ hồ sơ người chơi Star Rail (Cấp Khai Phá, Cấp Cân Bằng, Tinh Hồn nhân vật).
- **Tương tác động**: Chọn trực tiếp nhân vật trong tủ từ Menu thả xuống để xem thẻ trang bị chi tiết ngay lập tức!

### 7. ⚔️ Tủ Trưng Bày Nhân Vật (`/characters`)
- `/characters genshin [uid] [user]`: Xem toàn bộ danh sách nhân vật trong tủ trưng bày với giao diện phân trang (Paginator).
- `/characters hsr [uid] [user]`: Xem danh sách nhân vật showcase trong Honkai: Star Rail.

### 8. 📖 Hướng Dẫn Xây Dựng Nhân Vật (`/build`)
- `/build genshin <nhân vật>` (Hỗ trợ **Autocomplete** tự gợi ý tên): Hướng dẫn vũ khí (Trấn, F2P), Bộ Thánh Di Vật, Chỉ số chính từng mảnh, Thứ tự dòng phụ, Ưu tiên nâng Thiên phú, Đội hình tiêu biểu và lưu ý chiến đấu.
- `/build hsr <nhân vật>` (Hỗ trợ **Autocomplete**): Hướng dẫn Nón Ánh Sáng, Bộ Di Vật & Phụ Kiện Vị Diện, Chỉ số chính, Vết Tích, Đội hình chiến thuật.

### 9. 🔍 Bách Khoa Tra Cứu (`/search`)
- `/search genshin <từ khóa>`: Tra cứu nhanh thông tin nhân vật, nguyên tố, độ hiếm trong Genshin Impact.
- `/search hsr <từ khóa>`: Tra cứu thông tin nhân vật, vận mệnh, thuộc tính trong Honkai: Star Rail.

### 10. 📅 Sự Kiện Game (`/events`)
- `/events genshin`: Theo dõi các sự kiện phiên bản và banner cầu nguyện đang mở trong Genshin Impact.
- `/events hsr`: Theo dõi sự kiện Khai Phá và banner bước nhảy trong Honkai: Star Rail.

### 11. ⚙️ Cài Đặt Cá Nhân (`/settings`)
- `/settings`: Mở bảng cài đặt cá nhân tương tác (Bật/tắt ẩn UID bảo mật `812***678`, Bật/tắt ưu tiên ảnh Card đồ họa Pillow, Bật/tắt chế độ phản hồi riêng tư Ephemeral).

### 12. 🛠️ Quản Trị Hệ Thống (`/admin`)
- `/admin auto_status`: Xem trạng thái lập lịch nền (Scheduler), danh sách Job, thời gian chạy kế tiếp và nhật ký lỗi.
- `/admin auto_run <tác_vụ>`: Kích hoạt cưỡng bức một tác vụ nền bất kỳ.

---

## 🏗️ Cấu Trúc Thư Mục

```text
hoyoBot/
├── app/
│   ├── main.py                  # Điểm khởi chạy chính
│   ├── config.py                # Cấu hình Pydantic Settings & Automation
│   ├── bot/                     # Client discord.py, error handler, lifecycle
│   ├── automation/              # Lớp tự động hóa chạy nền (v2)
│   │   ├── manager.py           # APScheduler async manager
│   │   ├── notifications.py     # Notification dispatcher (DM/Channel)
│   │   ├── tasks/               # Checkin, Giftcode, Mimo, Accompany, WebEvent tasks
│   │   └── providers/           # HoYoLAB API, Giftcode feeds, Mimo/Accompany
│   ├── security/                # Mã hóa đối xứng Fernet & Session helpers
│   ├── db/                      # SQLite bất đồng bộ (aiosqlite)
│   │   ├── database.py
│   │   ├── models/              # User, Account, Settings, Automation models
│   │   └── repositories/        # Repository pattern CRUD
│   ├── games/                   # Game Abstraction Layer
│   │   ├── enums.py
│   │   ├── base.py              # GameProvider Protocol
│   │   ├── factory.py           # Provider Factory
│   │   ├── genshin/             # Genshin Impact Provider, Models, Builds, Data
│   │   └── hsr/                 # Star Rail Provider, Models, Builds, Data
│   ├── integrations/            # Client Enka.Network, TTL Cache
│   ├── services/                # Application Services
│   ├── render/                  # Đồ họa ảnh Pillow (Profile Card & Character Card)
│   ├── ui/                      # Discord Views, Modals, Buttons, Select Menus
│   ├── commands/                # Discord Slash Commands Groups
│   └── utils/                   # Validators, Tiếng Việt Localization, Rate Limit
├── tests/                       # Bộ kiểm thử tự động unittest (Core & Automation)
├── docs/                        # Tài liệu kiến trúc tự động hóa
├── data/
│   └── migrations/              # SQL migrations
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Yêu Cầu Môi Trường
- Python 3.12 trở lên.
- Đã tạo Bot trên [Discord Developer Portal](https://discord.com/developers/applications) và lấy Token.

### 2. Cài Đặt Thư Viện

```bash
# Tạo môi trường ảo (khuyến nghị)
python -m venv .venv
source .venv/bin/activate  # Trên Linux/macOS
# hoặc trên Windows:
.venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu Hình Biến Môi Trường

Sao chép `.env.example` thành `.env` và điền Token của bạn:

```bash
cp .env.example .env
```

Mở file `.env` và cập nhật:
```env
DISCORD_TOKEN=your_bot_token_here
DATABASE_PATH=data/hoyobot.db
DEBUG=False
DEFAULT_THEME=dark

# Cấu hình Automation v2
AUTOMATION_ENABLED=True
AUTOMATION_MODE=live
TIMEZONE=Asia/Ho_Chi_Minh
```

### 4. Khởi Chạy Bot

```bash
python -m app.main
```

### 5. Chạy Kiểm Thử (Unit Tests)

```bash
python -m unittest discover tests
```

### 6. Triển Khai Với Docker (Tùy Chọn)

```bash
docker compose up -d --build
```

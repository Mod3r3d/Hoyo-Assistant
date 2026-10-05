# Kiến Trúc Tự Động Hóa (Automation v2) — HoyoBot

## 1. Kết Quả Audit Hệ Thống Hiện Tại
- **Ngôn ngữ & Framework**: Python 3.12, `discord.py` v2.7, `pydantic` v2, `aiosqlite`.
- **Cơ sở dữ liệu**: SQLite async (`data/hoyobot.db`) với các bảng: `users`, `accounts`, `settings`.
- **Tựa game**: Hỗ trợ độc quyền 2 game **Genshin Impact** và **Honkai: Star Rail**.
- **Public Data**: Enka.Network API client đã có sẵn caching, timeout và error translation tiếng Việt.
- **Tiêu chí v2**:
  - Tích hợp lớp chạy nền (Background Scheduler) bằng `APScheduler` bất đồng bộ.
  - Tách bạch rõ: Scheduler (Khi nào chạy) -> Task (Cần làm gì) -> Provider (Làm bằng cách nào) -> Repository (Lưu ở đâu) -> Notifier (Báo cho ai).
  - Bảo mật tuyệt đối: Mã hóa đối xứng token/cookie (AES/Fernet), không log bí mật, người dùng kiểm soát bật/tắt (opt-in).

## 2. Sơ Đồ Khối Tự Động Hóa
```text
Discord Client (discord.py)
   │
   ├── Background Scheduler (APScheduler AsyncIOScheduler)
   │     ├─ Daily Check-in (00:05 hàng ngày + jitter)
   │     ├─ Giftcode Discovery & Auto-Redeem (mỗi 30-60 phút)
   │     ├─ Mimo / Accompany Task Sync (mỗi 30-60 phút)
   │     └─ Web Event Monitor (mỗi 2-4 giờ)
   │
   ├── Task Execution Engine
   │     ├─ Concurrency Semaphore (Giới hạn tải)
   │     ├─ Retry Policy & Rate Limit Backoff
   │     └─ Execution Logger (Ghi nhận trạng thái)
   │
   ├── Providers Layer
   │     ├─ HoYoLAB Check-in Provider (Genshin & HSR)
   │     ├─ Giftcode Provider & Auto-Redeem Provider
   │     ├─ Mimo & Accompany Providers
   │     └─ Web Events Source Provider
   │
   ├── Security Layer
   │     ├─ Fernet Cookie/Token Encryption
   │     └─ Session Validator
   │
   └── Notification Dispatcher
         ├─ DM thông báo riêng
         └─ Guild Channel thông báo chung
```

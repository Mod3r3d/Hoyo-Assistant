"""Cơ chế mã hóa đối xứng an toàn cho Cookies và Thông tin xác thực (Fernet)."""

import os
from pathlib import Path
from cryptography.fernet import Fernet
from loguru import logger
from app.config import settings


class SecretCipher:
    def __init__(self):
        self._fernet: Fernet | None = None

    def _get_or_create_key(self) -> bytes:
        if settings.ENCRYPTION_KEY:
            return settings.ENCRYPTION_KEY.encode("utf-8")

        key_file = settings.DATA_DIR / ".secret.key"
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

        if key_file.exists():
            return key_file.read_bytes().strip()

        new_key = Fernet.generate_key()
        try:
            key_file.write_bytes(new_key)
            logger.info("Đã tạo mới khóa mã hóa bảo mật tại data/.secret.key")
        except Exception as e:
            logger.warning(f"Không thể lưu key file: {e}")
        return new_key

    @property
    def cipher(self) -> Fernet:
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt(self, plain_text: str) -> str:
        """Mã hóa chuỗi văn bản bí mật."""
        if not plain_text:
            return ""
        encrypted_bytes = self.cipher.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        """Giải mã văn bản đã mã hóa."""
        if not cipher_text:
            return ""
        decrypted_bytes = self.cipher.decrypt(cipher_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")


def mask_cookie(cookie: str) -> str:
    """Che giấu một phần cookie nhạy cảm để hiển thị an toàn trên giao diện."""
    if not cookie:
        return "Chưa cấu hình"
    if len(cookie) <= 12:
        return "***"
    return f"{cookie[:4]}...{cookie[-4:]}"


cipher = SecretCipher()

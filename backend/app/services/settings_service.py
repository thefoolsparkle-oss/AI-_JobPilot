import base64
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SETTINGS_FILE = Path(os.getenv("JOBPILOT_SETTINGS_FILE", BASE_DIR / "settings.json"))
KEY_FILE = Path(os.getenv("JOBPILOT_SECRET_KEY_FILE", BASE_DIR / ".secret_key"))


def _get_fernet() -> Fernet:
    if KEY_FILE.exists():
        key = KEY_FILE.read_bytes()
        return Fernet(key)
    key = Fernet.generate_key()
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(key)
    return Fernet(key)


class SettingsStore:
    def load(self) -> dict:
        if SETTINGS_FILE.exists():
            try:
                return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save(self, data: dict):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_key(self) -> str:
        data = self.load()
        encrypted = data.get("DEEPSEEK_API_KEY", "")
        if not encrypted:
            return ""
        try:
            return _get_fernet().decrypt(encrypted.encode()).decode()
        except Exception:
            try:
                key = base64.b64decode(encrypted.encode()).decode()
                self.set_key(key)
                return key
            except Exception:
                return ""

    def set_key(self, api_key: str):
        data = self.load()
        data["DEEPSEEK_API_KEY"] = _get_fernet().encrypt(api_key.encode()).decode()
        self.save(data)

    def set_model_config(self, base_url: str = "", fast_model: str = "", reasoning_model: str = ""):
        data = self.load()
        if base_url:
            data["DEEPSEEK_BASE_URL"] = base_url
        if fast_model:
            data["DEEPSEEK_FAST_MODEL"] = fast_model
        if reasoning_model:
            data["DEEPSEEK_REASONING_MODEL"] = reasoning_model
        self.save(data)

    def get_masked_key(self) -> str:
        key = self.get_key()
        if len(key) < 8:
            return "未设置" if not key else key[:4] + "****"
        return key[:4] + "*" * (len(key) - 8) + key[-4:]

    def get_models(self) -> dict:
        data = self.load()
        from app.core.config import settings
        return {
            "fast_model": data.get("DEEPSEEK_FAST_MODEL") or settings.DEEPSEEK_FAST_MODEL,
            "reasoning_model": data.get("DEEPSEEK_REASONING_MODEL") or settings.DEEPSEEK_REASONING_MODEL,
            "base_url": data.get("DEEPSEEK_BASE_URL") or settings.DEEPSEEK_BASE_URL,
        }

    def has_key(self) -> bool:
        return bool(self.get_key())


_store = SettingsStore()


def get_settings_store() -> SettingsStore:
    return _store

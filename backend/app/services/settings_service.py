import json
import os
import base64
from pathlib import Path

SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "settings.json"


def _encode(data: str) -> str:
    return base64.b64encode(data.encode()).decode()


def _decode(data: str) -> str:
    try:
        return base64.b64decode(data.encode()).decode()
    except Exception:
        return ""


class SettingsStore:
    def load(self) -> dict:
        if SETTINGS_FILE.exists():
            try:
                return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def save(self, data: dict):
        SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_key(self) -> str:
        data = self.load()
        encrypted = data.get("DEEPSEEK_API_KEY", "")
        return _decode(encrypted)

    def set_key(self, api_key: str):
        data = self.load()
        data["DEEPSEEK_API_KEY"] = _encode(api_key)
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

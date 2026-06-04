import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
        except ImportError:
            return None
    return _reader


class OCRService:
    def extract_text(self, image_path: str) -> str:
        reader = _get_reader()
        if reader is None:
            return "EasyOCR 未安装。请运行: pip install easyocr"

        if not os.path.isfile(image_path):
            return f"文件不存在: {image_path}"

        try:
            results = reader.readtext(image_path, detail=0)
            return "\n".join(results) if results else "未识别到文字"
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return f"OCR 识别失败: {e}"

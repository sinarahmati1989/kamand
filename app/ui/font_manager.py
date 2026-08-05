"""
Font Manager — مدیریت فونت‌های پروژه کمند
فونت اصلی: Vazirmatn
"""
import logging
from pathlib import Path
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

from app.config.settings import BASE_DIR

logger = logging.getLogger(__name__)


class FontManager:
    """مدیریت فونت پیش‌فرض برنامه"""

    PRIMARY_FONT = "Vazirmatn"
    FALLBACK_FONTS = ["Segoe UI", "Tahoma", "B Nazanin", "Arial"]

    FONTS_DIR = BASE_DIR / "app" / "resources" / "fonts"

    _loaded = False
    _available_font = None

    @classmethod
    def setup(cls, app: QApplication) -> str:
        """
        بارگذاری فایل‌های TTF از پوشه fonts و انتخاب بهترین گزینه.
        """
        if cls._loaded:
            return cls._available_font

        # ── بارگذاری فایل‌های TTF از پوشه ──────────────────────────
        cls._load_font_files()

        installed_fonts = QFontDatabase.families()

        # بررسی Vazirmatn
        chosen_font = None
        for candidate in [cls.PRIMARY_FONT] + cls.FALLBACK_FONTS:
            if candidate in installed_fonts:
                chosen_font = candidate
                logger.info(f"✅ فونت انتخاب شد: {chosen_font}")
                break

        if not chosen_font:
            chosen_font = "Tahoma"
            logger.warning("⚠️ فونت پیش‌فرض یافت نشد، استفاده از Tahoma")

        # اعمال روی کل برنامه
        default_font = QFont(chosen_font, 10)
        default_font.setHintingPreference(
            QFont.HintingPreference.PreferFullHinting
        )
        default_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        app.setFont(default_font)

        cls._available_font = chosen_font
        cls._loaded = True
        return chosen_font

    @classmethod
    def _load_font_files(cls):
        """بارگذاری همه فایل‌های TTF/OTF از پوشه fonts"""
        if not cls.FONTS_DIR.exists():
            logger.warning(f"پوشه فونت وجود ندارد: {cls.FONTS_DIR}")
            return

        loaded_count = 0
        for font_file in cls.FONTS_DIR.iterdir():
            if font_file.suffix.lower() in (".ttf", ".otf"):
                font_id = QFontDatabase.addApplicationFont(str(font_file))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    logger.info(
                        f"✅ فونت بارگذاری شد: {font_file.name} → {families}"
                    )
                    loaded_count += 1
                else:
                    logger.error(f"❌ خطا در بارگذاری: {font_file.name}")

        if loaded_count == 0:
            logger.warning("هیچ فایل فونتی در پوشه fonts پیدا نشد")

    @classmethod
    def get_font(
        cls, size: int = 10, weight: int = QFont.Weight.Normal
    ) -> QFont:
        """گرفتن یک QFont با اندازه و وزن دلخواه"""
        font_name = cls._available_font or "Tahoma"
        font = QFont(font_name, size)
        font.setWeight(weight)
        return font

    @classmethod
    def font_family(cls) -> str:
        """نام فونت انتخاب شده (برای QSS)"""
        return cls._available_font or "Tahoma"
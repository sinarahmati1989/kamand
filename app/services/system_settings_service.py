"""
Kamand - SystemSettings Service
مدیریت تنظیمات سیستم (key/value)
"""
import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.system_settings import SystemSetting

logger = logging.getLogger(__name__)

# ─── کلیدهای استاندارد ───
KEY_OVERHEAD_PERCENT       = "overhead_percent"
KEY_DEFAULT_MARKUP_PERCENT = "default_markup_percent"

# ─── مقادیر پیش‌فرض ───
DEFAULTS: dict[str, str] = {
    KEY_OVERHEAD_PERCENT:       "10.00",
    KEY_DEFAULT_MARKUP_PERCENT: "20.00",
}


class SystemSettingsService:

    def __init__(self, session: Session):
        self._session = session

    # ─── پایه ───

    def get(self, key: str) -> Optional[str]:
        row = (
            self._session.query(SystemSetting)
            .filter(SystemSetting.key == key)
            .first()
        )
        if row:
            return row.value
        return DEFAULTS.get(key)

    def set(self, key: str, value: str, description: str = "") -> SystemSetting:
        row = (
            self._session.query(SystemSetting)
            .filter(SystemSetting.key == key)
            .first()
        )
        if row:
            row.value = value
            if description:
                row.description = description
        else:
            row = SystemSetting(key=key, value=value, description=description)
            self._session.add(row)
        self._session.flush()
        return row

    def get_all(self) -> list[SystemSetting]:
        rows = self._session.query(SystemSetting).order_by(SystemSetting.key).all()
        # اضافه کردن مقادیر پیش‌فرض اگر در DB نباشند
        existing_keys = {r.key for r in rows}
        result = list(rows)
        for key, value in DEFAULTS.items():
            if key not in existing_keys:
                result.append(SystemSetting(key=key, value=value))
        return result

    # ─── Typed Getters ───

    def get_decimal(self, key: str, default: Decimal = Decimal("0")) -> Decimal:
        val = self.get(key)
        try:
            return Decimal(str(val)) if val else default
        except Exception:
            logger.warning(f"مقدار نامعتبر برای کلید {key}: {val}")
            return default

    def get_overhead_percent(self) -> Decimal:
        return self.get_decimal(KEY_OVERHEAD_PERCENT, Decimal("10.00"))

    def get_markup_percent(self) -> Decimal:
        return self.get_decimal(KEY_DEFAULT_MARKUP_PERCENT, Decimal("20.00"))

    # ─── Seed ───

    def ensure_defaults(self) -> None:
        """اطمینان از وجود مقادیر پیش‌فرض در DB"""
        for key, value in DEFAULTS.items():
            existing = (
                self._session.query(SystemSetting)
                .filter(SystemSetting.key == key)
                .first()
            )
            if not existing:
                descriptions = {
                    KEY_OVERHEAD_PERCENT:       "درصد سربار عمومی کارخانه",
                    KEY_DEFAULT_MARKUP_PERCENT: "درصد markup پیش‌فرض (سود روی هزینه)",
                }
                self._session.add(SystemSetting(
                    key=key,
                    value=value,
                    description=descriptions.get(key, ""),
                ))
        self._session.flush()
        logger.info("✅ SystemSettings defaults ensured")
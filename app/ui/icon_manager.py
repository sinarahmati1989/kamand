"""
Icon Manager — مدیریت متمرکز آیکون‌ها با qtawesome
همه آیکون‌های پروژه از اینجا فراخوانی می‌شن
"""
import logging
import qtawesome as qta
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)


class IconManager:
    """مدیریت آیکون‌های پروژه با Material Design Icons"""

    # ═══ رنگ‌های استاندارد پروژه ═══
    COLOR_PRIMARY   = "#6366F1"
    COLOR_SECONDARY = "#64748B"
    COLOR_MUTED     = "#94A3B8"
    COLOR_ACTIVE    = "#FFFFFF"
    COLOR_DANGER    = "#EF4444"
    COLOR_SUCCESS   = "#10B981"
    COLOR_WARNING   = "#F59E0B"

    # ═══ نگاشت آیکون‌های سایدبار ═══
    ICONS = {
        # داشبورد
        "dashboard":        "mdi.view-dashboard-outline",

        # داده‌های پایه
        "base_data":        "mdi.database-outline",
        "customers":        "mdi.account-group-outline",
        "suppliers":        "mdi.truck-outline",
        "costs":            "mdi.cash-multiple",
        "operations":       "mdi.hammer-wrench",
        "departments":      "mdi.office-building-outline",
        "work_centers":     "mdi.factory",
        "machines":         "mdi.robot-industrial",          # ✅ رفع باگ

        # مهندسی دستگاه
        "engineering":      "mdi.cog-outline",
        "device_templates": "mdi.file-cog-outline",
        "items":            "mdi.package-variant-closed",
        "bom":              "mdi.file-tree-outline",
        "routing":          "mdi.source-branch",

        # عملیات
        "operations_group": "mdi.chart-timeline-variant",
        "projects":         "mdi.clipboard-list-outline",
        "purchases":        "mdi.cart-outline",

        # گزارش‌ها
        "reports":          "mdi.chart-line",
        "profit":           "mdi.chart-bar",
        "prj_report":       "mdi.chart-donut",

        # سیستم
        "system":           "mdi.shield-account-outline",
        "users":            "mdi.account-multiple-outline",
        "lookups":          "mdi.tune-variant",
        "settings":         "mdi.cog",

        # عمومی
        "logout":           "mdi.logout",
        "user":             "mdi.account-circle-outline",
        "home":             "mdi.home-outline",
        "search":           "mdi.magnify",
        "add":              "mdi.plus",
        "edit":             "mdi.pencil",
        "delete":           "mdi.delete-outline",
        "save":             "mdi.content-save-outline",
        "cancel":           "mdi.close",
        "check":            "mdi.check",
        "info":             "mdi.information-outline",
        "warning":          "mdi.alert-outline",
        "error":            "mdi.alert-circle-outline",
        "success":          "mdi.check-circle-outline",
        "arrow_down":       "mdi.chevron-down",
        "arrow_left":       "mdi.chevron-left",
        "arrow_right":      "mdi.chevron-right",
        "arrow_up":         "mdi.chevron-up",
        "menu":             "mdi.menu",
        "close":            "mdi.close",
        "refresh":          "mdi.refresh",
        "filter":           "mdi.filter-variant",
        "download":         "mdi.download",
        "upload":           "mdi.upload",
        "bell":             "mdi.bell-outline",
        "eye":              "mdi.eye-outline",
        "eye_off":          "mdi.eye-off-outline",
        "lock":             "mdi.lock-outline",

        # پروژه — آیکون‌های جدید
        "project":          "mdi.clipboard-list-outline",
        "project_device":   "mdi.devices",
        "calendar":         "mdi.calendar-outline",
        "contract":         "mdi.file-sign",
        "money":            "mdi.cash",
        "status":           "mdi.list-status",
        "copy":             "mdi.content-copy",
        "expand":           "mdi.arrow-expand",
    }

    @classmethod
    def get(
        cls,
        name: str,
        color: str = None,
        size: int = None,
    ) -> QIcon:
        """
        دریافت آیکون با نام کوتاه

        مثال:
            IconManager.get("home", color="#6366F1")
            IconManager.get("save", color=IconManager.COLOR_PRIMARY)
        """
        mdi_name = cls.ICONS.get(name)
        if not mdi_name:
            logger.warning(f"⚠ آیکون '{name}' یافت نشد")
            mdi_name = "mdi.help-circle-outline"

        try:
            options = {}
            if color:
                options["color"] = color
            else:
                options["color"] = cls.COLOR_PRIMARY

            return qta.icon(mdi_name, **options)
        except Exception as e:
            logger.error(f"خطا در بارگذاری آیکون '{name}': {e}")
            # fallback به آیکون ساده
            try:
                return qta.icon("mdi.help-circle-outline", color=color or cls.COLOR_PRIMARY)
            except Exception:
                return QIcon()

    @classmethod
    def get_by_mdi(cls, mdi_name: str, color: str = None) -> QIcon:
        """دریافت آیکون با نام مستقیم mdi (بدون نگاشت)"""
        try:
            options = {"color": color or cls.COLOR_PRIMARY}
            return qta.icon(mdi_name, **options)
        except Exception as e:
            logger.error(f"خطا در بارگذاری mdi '{mdi_name}': {e}")
            return QIcon()
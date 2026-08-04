"""
Display Config — مدیریت رزولوشن و مقیاس صفحه
"""
from PySide6.QtWidgets import QApplication


class Display:
    """اطلاعات صفحه فعال"""

    @staticmethod
    def screen_size() -> tuple[int, int]:
        """اندازه صفحه اصلی"""
        screen = QApplication.primaryScreen()
        if not screen:
            return 1920, 1080
        geo = screen.availableGeometry()
        return geo.width(), geo.height()

    @staticmethod
    def scale_factor() -> float:
        """ضریب مقیاس (DPI)"""
        screen = QApplication.primaryScreen()
        if not screen:
            return 1.0
        return screen.devicePixelRatio()

    @staticmethod
    def category() -> str:
        """دسته‌بندی صفحه: small / medium / large / xlarge"""
        w, _ = Display.screen_size()
        if w < 1400:
            return "small"      # 1366×768
        elif w < 1920:
            return "medium"     # 1600×900, 1680×1050
        elif w < 2560:
            return "large"      # 1920×1080, 2K
        else:
            return "xlarge"     # 2560×1440, 4K

    # ─── سایزهای پیشنهادی برای هر بخش ───

    @staticmethod
    def login_size() -> tuple[int, int]:
        """سایز پنجره لاگین"""
        w, h = Display.screen_size()
        # حدود 50% عرض، حداکثر 1000
        width = min(int(w * 0.5), 1000)
        width = max(width, 720)  # حداقل
        height = int(width * 0.61)  # نسبت طلایی
        return width, height

    @staticmethod
    def main_window_min() -> tuple[int, int]:
        """حداقل سایز پنجره اصلی"""
        cat = Display.category()
        if cat == "small":
            return 1100, 650
        elif cat == "medium":
            return 1200, 700
        else:
            return 1300, 780

    @staticmethod
    def sidebar_width() -> int:
        """عرض Sidebar"""
        cat = Display.category()
        return {
            "small":  210,
            "medium": 230,
            "large":  250,
            "xlarge": 280,
        }[cat]
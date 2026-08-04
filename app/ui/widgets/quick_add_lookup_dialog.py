"""
QuickAddLookupDialog — دیالوگ کوچک افزودن سریع Lookup
────────────────────────────────────────────────────────────
با تبدیل خودکار فارسی به لاتین (Transliteration)
"""
import re
import time
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
import logging

from app.database.session import get_session
from app.services.lookup_service import LookupService
from app.schemas.lookup_schema import LookupCreate
from app.enums.lookup_categories import LookupCategory
from app.core.exceptions import DuplicateError
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# متن راهنمای placeholder برای هر دسته
# ────────────────────────────────────────────────────────────

CATEGORY_HINTS = {
    # تأمین‌کنندگان
    "supplier_type":           "مثال: بازرگانی",
    "supplier_subcategory":    "مثال: قطعات پنوماتیک",
    "supplier_specialization": "مثال: آلومینیوم 6061",
    "supplier_tier":           "مثال: D - آزمایشی",
    "payment_terms":           "مثال: پیش‌پرداخت",

    # مالی
    "currency":                "مثال: درهم",

    # هزینه‌ها
    "cost_category":           "مثال: هزینه سربار",
    "cost_behavior":           "مثال: پله‌ای",
    "cost_unit":               "مثال: کیلوگرم",
    "allocation_method":       "مثال: بر اساس متراژ",

    # مشتری
    "customer_type":           "مثال: نمایندگی",

    # عملیات ساخت
    "operation_type":          "مثال: لیزر برش",
    "skill_level":             "مثال: سطح ۶ - نخبه",
    "time_unit":               "مثال: روز",
}


def get_placeholder_for(category: str) -> str:
    """برگرداندن متن راهنمای مناسب برای یک category"""
    return CATEGORY_HINTS.get(category, "نام گزینه جدید را وارد کنید")


# ────────────────────────────────────────────────────────────
# جدول تبدیل فارسی به لاتین (Transliteration)
# ────────────────────────────────────────────────────────────

FA_TO_LATIN = {
    # حروف
    "ا": "a",  "آ": "a",  "أ": "a",  "إ": "e",
    "ب": "b",  "پ": "p",  "ت": "t",  "ث": "s",
    "ج": "j",  "چ": "ch", "ح": "h",  "خ": "kh",
    "د": "d",  "ذ": "z",  "ر": "r",  "ز": "z",
    "ژ": "zh", "س": "s",  "ش": "sh", "ص": "s",
    "ض": "z",  "ط": "t",  "ظ": "z",  "ع": "a",
    "غ": "gh", "ف": "f",  "ق": "gh", "ک": "k",
    "ك": "k",  "گ": "g",  "ل": "l",  "م": "m",
    "ن": "n",  "و": "v",  "ه": "h",  "ة": "h",
    "ی": "y",  "ي": "y",  "ئ": "y",  "ؤ": "v",
    "ء": "",   "ّ": "",

    # اعداد فارسی/عربی
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",

    # فاصله و علائم
    " ": "_",
    "‌": "_",    # نیم‌فاصله (ZWNJ)
    "\u200c": "_",
    "\u200f": "",  # RTL mark
    "\u200e": "",  # LTR mark

    # علائم که حذف بشن
    "،": "",  ",": "",  "؛": "",  "?": "",
    "!": "",  ".": "",  "(": "",  ")": "",
    "[": "",  "]": "",  "{": "",  "}": "",
    ":": "",  "؟": "",  ";": "",  '"': "",
    "'": "",  "«": "",  "»": "",  "/": "_",
    "\\": "_", "|": "_",  "-": "_",
}


def transliterate_fa_to_en(text: str) -> str:
    """
    تبدیل فارسی به لاتین

    Examples:
        "استیل 304" → "steel_304"  (سعی می‌کنه)
        "آهن ST37" → "ahan_st37"
        "مس خالص" → "mes_khales"
    """
    if not text:
        return ""

    # تبدیل حرف به حرف
    result = ""
    for char in text:
        if char in FA_TO_LATIN:
            result += FA_TO_LATIN[char]
        elif char.isascii():
            # حروف انگلیسی، عدد، _ رو نگه دار
            result += char.lower()
        else:
            # هر چیز دیگه (emoji، ...) رو حذف کن
            continue

    # پاکسازی: چند تا _ پشت هم → یکی
    result = re.sub(r"_+", "_", result)

    # حذف _ از ابتدا و انتها
    result = result.strip("_")

    return result


def generate_safe_code(text: str, prefix: str = "item") -> str:
    """
    تولید کد امن از متن فارسی
    اگه transliteration نتوانست چیز مفیدی تولید کند، از timestamp استفاده می‌کنیم
    """
    code = transliterate_fa_to_en(text)

    # اگه کد خالی یا خیلی کوتاه بود، از timestamp استفاده کن
    if not code or len(code) < 2:
        timestamp = int(time.time() * 1000) % 10000000
        code = f"{prefix}_{timestamp}"

    return code[:50]  # محدود به ۵۰ کاراکتر


# ────────────────────────────────────────────────────────────
# Dialog
# ────────────────────────────────────────────────────────────

class QuickAddLookupDialog(QDialog):
    """
    دیالوگ سریع افزودن Lookup

    Args:
        category: نام دسته (مثل "supplier_type")
        parent_id: اگه زیرشاخه‌ست، ID والد
        parent_label: نام والد برای نمایش
    """

    lookup_added = Signal(str, str)  # (code, label_fa)

    def __init__(
        self,
        category: str,
        parent_id: Optional[int] = None,
        parent_label: Optional[str] = None,
        parent=None
    ):
        super().__init__(parent)
        self.category = category
        self.parent_id = parent_id
        self.parent_label = parent_label

        # کش parent code برای prefix کد
        self._parent_code_prefix = ""
        self._load_parent_code()

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setModal(True)
        self.setFixedSize(480, 400)

        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._apply_style()

    def _load_parent_code(self):
        """بارگذاری کد والد برای استفاده به عنوان prefix"""
        if self.parent_id is None:
            return

        try:
            with get_session() as session:
                svc = LookupService(session)
                parent = svc.get_by_id(self.parent_id)
                if parent:
                    self._parent_code_prefix = parent.code
        except Exception:
            pass

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = QWidget()
        self._card.setObjectName("quickAddCard")
        outer.addWidget(self._card)

        root = QVBoxLayout(self._card)
        root.setContentsMargins(28, 24, 28, 22)
        root.setSpacing(14)

        # ─── عنوان ───
        cat_persian = LookupCategory.to_persian(self.category)
        if self.parent_label:
            title_text = f"➕  افزودن به «{self.parent_label}»"
        else:
            title_text = f"➕  افزودن به «{cat_persian}»"

        title = QLabel(title_text)
        title.setObjectName("quickAddTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(title)

        # ─── جداکننده ───
        sep = QFrame()
        sep.setObjectName("quickAddSep")
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # ─── نام فارسی ───
        lbl_fa = QLabel("نام فارسی *")
        lbl_fa.setObjectName("quickAddLabel")
        lbl_fa.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(lbl_fa)

        self.label_fa_input = QLineEdit()
        self.label_fa_input.setObjectName("quickAddInput")
        self.label_fa_input.setPlaceholderText(get_placeholder_for(self.category))
        self.label_fa_input.setMinimumHeight(40)
        self.label_fa_input.textChanged.connect(self._auto_generate_code)
        root.addWidget(self.label_fa_input)

        # ─── کد یکتا ───
        lbl_code = QLabel("کد یکتا (انگلیسی - خودکار)")
        lbl_code.setObjectName("quickAddLabel")
        lbl_code.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(lbl_code)

        self.code_input = QLineEdit()
        self.code_input.setObjectName("quickAddInput")
        self.code_input.setPlaceholderText("خودکار از نام فارسی تولید می‌شود...")
        self.code_input.setMinimumHeight(40)
        root.addWidget(self.code_input)

        # ─── راهنما ───
        hint = QLabel(
            "💡 نام فارسی را تایپ کنید، کد لاتین خودکار ساخته می‌شود\n"
            "    (می‌توانید دستی هم تغییرش بدهید اگه خواستید)"
        )
        hint.setStyleSheet(
            "color: #64748B; font-size: 11px; padding: 4px 0; line-height: 1.5;"
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignRight)
        hint.setWordWrap(True)
        root.addWidget(hint)

        root.addStretch(1)

        # ─── دکمه‌ها ───
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("quickAddCancelBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("💾  ذخیره و افزودن")
        save_btn.setObjectName("quickAddSaveBtn")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

        self.label_fa_input.setFocus()

    def _auto_generate_code(self, text: str):
        """تولید خودکار کد از نام فارسی (با transliteration)"""
        if not text.strip():
            self.code_input.clear()
            return

        # ابتدا transliterate کن
        code = transliterate_fa_to_en(text)

        # اگه چیز مفیدی نبود، از timestamp استفاده کن
        if not code or len(code) < 2:
            code = generate_safe_code(text, prefix=self.category)

        # اگه parent داره، prefix parent رو اضافه کن
        if self._parent_code_prefix:
            code = f"{self._parent_code_prefix}_{code}"

        code = code[:50]
        self.code_input.setText(code)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#quickAddCard {
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(99, 102, 241, 0.3);
                border-radius: 20px;
            }

            QLabel#quickAddTitle {
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 15px;
                font-weight: bold;
                color: #6366F1;
                background: transparent;
                padding: 0;
            }

            QFrame#quickAddSep {
                background-color: rgba(99, 102, 241, 0.15);
                min-height: 1px;
                max-height: 1px;
                border: none;
            }

            QLabel#quickAddLabel {
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: #374151;
                background: transparent;
                padding: 4px 0 2px 0;
            }

            QLineEdit#quickAddInput {
                background: white;
                color: #1E293B;
                border: 1.5px solid rgba(99, 102, 241, 0.25);
                border-radius: 10px;
                padding: 8px 14px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 14px;
                selection-background-color: #C7D2FE;
            }

            QLineEdit#quickAddInput:focus {
                border: 1.5px solid #6366F1;
            }

            QPushButton#quickAddSaveBtn {
                background-color: #6366F1;
                color: white;
                border: none;
                border-radius: 10px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: bold;
                min-width: 150px;
                min-height: 40px;
                padding: 0 16px;
            }
            QPushButton#quickAddSaveBtn:hover {
                background-color: #4F46E5;
            }

            QPushButton#quickAddCancelBtn {
                background-color: rgba(241, 245, 249, 0.9);
                color: #64748B;
                border: 1px solid rgba(148, 163, 184, 0.4);
                border-radius: 10px;
                font-family: "Segoe UI", "B Nazanin", sans-serif;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
                min-height: 40px;
                padding: 0 16px;
            }
            QPushButton#quickAddCancelBtn:hover {
                background-color: rgba(226, 232, 240, 1);
                color: #1E293B;
            }
        """)

    def _validate(self, label_fa: str, code: str) -> Optional[str]:
        if not label_fa:
            return "نام فارسی الزامی است"
        if not code:
            return "کد خالی است. لطفاً یک نام معتبر وارد کنید"
        if not re.match(r"^[a-z0-9_\-]+$", code):
            return (
                "کد فقط می‌تواند شامل حروف انگلیسی کوچک، عدد، _ و - باشد.\n"
                "کد را دستی اصلاح کنید یا نام فارسی دیگری امتحان کنید."
            )
        return None

    def _on_save(self):
        label_fa = self.label_fa_input.text().strip()
        code = self.code_input.text().strip().lower()

        # اگه کد خالیه، دوباره تولید کن
        if not code and label_fa:
            self._auto_generate_code(label_fa)
            code = self.code_input.text().strip().lower()

        # اگه هنوز چیز معتبری نیست، از timestamp استفاده کن
        if not code or not re.match(r"^[a-z0-9_\-]+$", code):
            code = generate_safe_code(label_fa, prefix=self.category)
            if self._parent_code_prefix:
                code = f"{self._parent_code_prefix}_{code}"
            code = code[:50].lower()
            self.code_input.setText(code)

        error = self._validate(label_fa, code)
        if error:
            Toast.warning(self, error)
            return

        try:
            with get_session() as session:
                svc = LookupService(session)

                # پیدا کردن بزرگ‌ترین sort_order
                existing = svc.get_by_category(
                    self.category,
                    active_only=False,
                    parent_id=self.parent_id
                )
                max_sort = max((item.sort_order for item in existing), default=0)

                data = LookupCreate(
                    category=self.category,
                    code=code,
                    label_fa=label_fa,
                    parent_id=self.parent_id,
                    sort_order=max_sort + 10,
                    is_active=True,
                )
                svc.create(data, is_system=False)

            self.lookup_added.emit(code, label_fa)
            logger.info(f"✅ QuickAdd: {self.category}/{code} - {label_fa}")
            self.accept()

        except DuplicateError as e:
            Toast.warning(self, str(e))
        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در QuickAdd: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # درگ کردن
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
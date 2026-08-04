"""
دیالوگ افزودن/ویرایش Lookup
"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit,
    QPushButton, QWidget, QGroupBox, QSpinBox,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt
import logging

from app.database.session import get_session
from app.services.lookup_service import LookupService
from app.schemas.lookup_schema import LookupCreate, LookupUpdate
from app.enums.lookup_categories import LookupCategory
from app.core.exceptions import DuplicateError, NotFoundError
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class LookupFormDialog(QDialog):
    """فرم افزودن/ویرایش Lookup"""

    def __init__(
        self,
        category: str,
        lookup_id: Optional[int] = None,
        parent=None
    ):
        super().__init__(parent)
        self.category = category
        self.lookup_id = lookup_id
        self.is_edit = lookup_id is not None
        self._current_lookup = None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش گزینه" if self.is_edit else "افزودن گزینه جدید"
        )
        self.setMinimumSize(560, 580)
        self.resize(600, 620)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    # ══════════════════════════════════════════════════════════════════
    # Setup
    # ══════════════════════════════════════════════════════════════════

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        cat_label = LookupCategory.to_persian(self.category)
        title_text = (
            f"✏️  ویرایش «{cat_label}»" if self.is_edit
            else f"➕  افزودن به «{cat_label}»"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # محتوا
        layout.addWidget(self._build_form(), 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("💾  ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedSize(140, 42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedSize(110, 42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ══════════════════════════════════════════════════════════════════
    # Helper: ساخت فیلد
    # ══════════════════════════════════════════════════════════════════

    def _make_field(self, label_text: str, widget: QWidget, required: bool = False) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if required:
            lbl.setStyleSheet("QLabel#fieldLabel { color: #6366F1; font-weight: 600; }")

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    # ══════════════════════════════════════════════════════════════════
    # فرم اصلی
    # ══════════════════════════════════════════════════════════════════

    def _build_form(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ═══ اطلاعات اصلی ═══
        main_group = QGroupBox("📝  اطلاعات اصلی")
        main_group.setObjectName("formGroup")
        mv = QVBoxLayout(main_group)
        mv.setContentsMargins(14, 20, 14, 14)
        mv.setSpacing(12)

        # کد + ترتیب (یک ردیف)
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("مثال: my_option")
        self.code_input.setMinimumHeight(36)
        if self.is_edit:
            self.code_input.setEnabled(False)  # کد قابل تغییر نیست
        row1.addWidget(self._make_field("کد یکتا (انگلیسی)", self.code_input, required=True), 2)

        self.sort_input = QSpinBox()
        self.sort_input.setRange(0, 9999)
        self.sort_input.setValue(0)
        self.sort_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("ترتیب", self.sort_input), 1)

        mv.addLayout(row1)

        # لیبل فارسی
        self.label_fa_input = QLineEdit()
        self.label_fa_input.setPlaceholderText("متن نمایشی فارسی")
        self.label_fa_input.setMinimumHeight(36)
        mv.addWidget(self._make_field("لیبل فارسی", self.label_fa_input, required=True))

        # لیبل انگلیسی
        self.label_en_input = QLineEdit()
        self.label_en_input.setPlaceholderText("متن نمایشی انگلیسی (اختیاری)")
        self.label_en_input.setMinimumHeight(36)
        mv.addWidget(self._make_field("لیبل انگلیسی", self.label_en_input))

        layout.addWidget(main_group)

        # ═══ ساختار و وضعیت ═══
        struct_group = QGroupBox("📊  ساختار و وضعیت")
        struct_group.setObjectName("formGroup")
        sv = QVBoxLayout(struct_group)
        sv.setContentsMargins(14, 20, 14, 14)
        sv.setSpacing(12)

        # والد (اختیاری)
        self.parent_combo = QComboBox()
        self.parent_combo.setMinimumHeight(36)
        self._load_parent_options()
        sv.addWidget(self._make_field("والد (اختیاری)", self.parent_combo))

        # وضعیت
        self.active_cb = QCheckBox("گزینه فعال است")
        self.active_cb.setChecked(True)
        self.active_cb.setMinimumHeight(28)
        sv.addWidget(self.active_cb)

        layout.addWidget(struct_group)

        # ═══ توضیحات ═══
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات اضافی (اختیاری)")
        self.description_input.setMinimumHeight(70)
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self._make_field("توضیحات", self.description_input))

        layout.addStretch(1)

        # ScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    # ══════════════════════════════════════════════════════════════════
    # بارگذاری والدها
    # ══════════════════════════════════════════════════════════════════

    def _load_parent_options(self):
        """
        اگه دسته supplier_subcategory هست، والدها از supplier_type میان
        اگه نه، از همون دسته میان (ساختار درختی داخل خود دسته)
        """
        self.parent_combo.clear()
        self.parent_combo.addItem("— بدون والد —", None)

        # تعیین دسته والد
        parent_category = self.category
        if self.category == "supplier_subcategory":
            parent_category = "supplier_type"

        try:
            with get_session() as session:
                svc = LookupService(session)
                items = svc.get_by_category(
                    parent_category,
                    active_only=False,
                    include_children=False
                )

                for item in items:
                    # از خودش به عنوان والد جلوگیری
                    if self.is_edit and item.id == self.lookup_id:
                        continue
                    self.parent_combo.addItem(
                        f"{item.label_fa}  ({item.code})",
                        item.id
                    )
        except Exception as e:
            logger.error(f"خطا در بارگذاری والدها: {e}")

    # ══════════════════════════════════════════════════════════════════
    # بارگذاری داده (ویرایش)
    # ══════════════════════════════════════════════════════════════════

    def _load_data(self):
        try:
            with get_session() as session:
                svc = LookupService(session)
                item = svc.get_by_id(self.lookup_id)
                self._current_lookup = item

                self.code_input.setText(item.code)
                self.label_fa_input.setText(item.label_fa)
                self.label_en_input.setText(item.label_en or "")
                self.sort_input.setValue(item.sort_order)
                self.active_cb.setChecked(item.is_active)
                self.description_input.setPlainText(item.description or "")

                if item.parent_id:
                    idx = self.parent_combo.findData(item.parent_id)
                    if idx >= 0:
                        self.parent_combo.setCurrentIndex(idx)

                # اگه سیستمیه، پیام هشدار
                if item.is_system:
                    warning = QLabel(
                        "⚠️  این یک گزینه سیستمی است. "
                        "می‌توانید ویرایش کنید ولی حذف امکان‌پذیر نیست."
                    )
                    warning.setStyleSheet(
                        "background: #FEF3C7; color: #92400E; "
                        "padding: 10px; border-radius: 8px; "
                        "font-weight: 600; font-size: 12px;"
                    )
                    self.layout().insertWidget(1, warning)

        except Exception as e:
            logger.error(f"خطا در بارگذاری Lookup: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # ══════════════════════════════════════════════════════════════════
    # ذخیره
    # ══════════════════════════════════════════════════════════════════

    def _collect_data(self) -> dict:
        return {
            "category":    self.category,
            "code":        self.code_input.text().strip().lower(),
            "label_fa":    self.label_fa_input.text().strip(),
            "label_en":    self.label_en_input.text().strip() or None,
            "parent_id":   self.parent_combo.currentData(),
            "sort_order":  self.sort_input.value(),
            "is_active":   self.active_cb.isChecked(),
            "description": self.description_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> Optional[str]:
        if not data.get("code"):
            return "کد یکتا الزامی است"
        if not data.get("label_fa"):
            return "لیبل فارسی الزامی است"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()

            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = LookupService(session)

                if self.is_edit:
                    # فقط فیلدهای قابل ویرایش
                    update_data = {
                        "label_fa":    data["label_fa"],
                        "label_en":    data["label_en"],
                        "parent_id":   data["parent_id"],
                        "sort_order":  data["sort_order"],
                        "is_active":   data["is_active"],
                        "description": data["description"],
                    }
                    schema = LookupUpdate(**update_data)
                    svc.update(self.lookup_id, schema)
                else:
                    schema = LookupCreate(**data)
                    svc.create(schema, is_system=False)

            self.accept()

        except DuplicateError as e:
            Toast.warning(self, str(e))
        except (ValueError, NotFoundError) as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره Lookup: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
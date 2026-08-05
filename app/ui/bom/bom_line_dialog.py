"""
Kamand - BOM Line Dialog
دیالوگ افزودن/ویرایش خط BOM
"""
import logging
from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QCheckBox,
    QDoubleSpinBox, QTextEdit, QFrame, QComboBox,
)
from PySide6.QtCore import Qt

from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.toast import Toast
from app.services.bom_service import BOMService
from app.services.item_service import ItemService
from app.services.lookup_service import LookupService
from app.enums.lookup_categories import LookupCategory
from app.database.session import get_session

logger = logging.getLogger(__name__)

# واحدهایی که اعشار نمی‌گیرند (شمارشی)
DISCRETE_UOMS = {"pcs", "عدد", "each", "unit", "set", "دستگاه", "ست"}


class BOMLineDialog(QDialog):
    """دیالوگ افزودن/ویرایش خط BOM"""

    def __init__(
        self,
        bom_header_id: int,
        line_id: int | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.bom_header_id = bom_header_id
        self.line_id = line_id
        self._is_edit = line_id is not None
        self._all_items = []
        self._type_map = {}
        self._uom_map = {}

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش خط BOM" if self._is_edit else "افزودن قلم به BOM"
        )
        self.setMinimumWidth(600)
        self.setModal(True)

        self._setup_ui()
        self._load_items()

        if self._is_edit:
            self._load_line_data()

    # ── UI ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # عنوان
        title = QLabel(
            "ویرایش خط BOM" if self._is_edit else "افزودن قلم به BOM"
        )
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #1E293B;
        """)
        layout.addWidget(title)

        # خط جداکننده
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(99, 102, 241, 0.15);")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # فرم
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        # ── جستجو + انتخاب قلم ─────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("جستجو در کد یا نام قلم...")
        self._search_edit.setFixedHeight(36)
        self._search_edit.textChanged.connect(self._on_search)

        self._item_combo = QComboBox()
        self._item_combo.setFixedHeight(36)
        self._item_combo.setMinimumWidth(290)
        self._item_combo.currentIndexChanged.connect(self._on_item_selected)

        search_row.addWidget(self._search_edit, stretch=1)
        search_row.addWidget(self._item_combo, stretch=2)
        form.addRow("قلم *:", search_row)

        # اطلاعات قلم
        self._item_info_lbl = QLabel("—")
        self._item_info_lbl.setStyleSheet("""
            color: #6366F1;
            font-style: italic;
            font-size: 12px;
        """)
        form.addRow("اطلاعات:", self._item_info_lbl)

        # مقدار
        self._qty = QDoubleSpinBox()
        self._qty.setFixedHeight(36)
        self._qty.setMinimum(0.001)
        self._qty.setMaximum(9999999)
        self._qty.setDecimals(3)  # پیش‌فرض ۳ رقم — بعد پویا میشه
        self._qty.setValue(1.0)
        self._qty.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow("مقدار *:", self._qty)

        # واحد
        self._uom_combo = LookupComboBox(
            LookupCategory.UOM.value,
            allow_empty=False,
        )
        self._uom_combo.setFixedHeight(36)
        self._uom_combo.currentIndexChanged.connect(self._on_uom_changed)
        form.addRow("واحد:", self._uom_combo)

        # درصد ضایعات
        self._scrap = QDoubleSpinBox()
        self._scrap.setFixedHeight(36)
        self._scrap.setMinimum(0)
        self._scrap.setMaximum(100)
        self._scrap.setDecimals(1)
        self._scrap.setValue(0)
        self._scrap.setSuffix("  %")
        self._scrap.setSingleStep(0.5)
        self._scrap.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        form.addRow("درصد ضایعات:", self._scrap)

        # اختیاری
        self._optional = QCheckBox("این قلم در BOM اختیاری است")
        form.addRow("", self._optional)

        # یادداشت
        self._notes = QTextEdit()
        self._notes.setFixedHeight(64)
        self._notes.setPlaceholderText("یادداشت...")
        form.addRow("یادداشت:", self._notes)

        layout.addLayout(form)

        # دکمه‌ها
        btn_row = QHBoxLayout()

        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setFixedWidth(110)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton(
            "ذخیره تغییرات" if self._is_edit else "افزودن به BOM"
        )
        save_btn.setObjectName("primaryButton")
        save_btn.setFixedHeight(40)
        save_btn.setMinimumWidth(150)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    # ── Data ───────────────────────────────────────────────────────

    def _load_items(self):
        try:
            with get_session() as session:
                svc = ItemService(session)
                lookup_svc = LookupService(session)
                self._all_items = svc.search("", None, "active")
                self._type_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.ITEM_TYPE.value
                )
                self._uom_map = lookup_svc.get_code_to_label_map(
                    LookupCategory.UOM.value
                )
            self._fill_item_combo(self._all_items)
        except Exception as e:
            logger.error(f"خطا در بارگذاری اقلام: {e}")

    def _fill_item_combo(self, items):
        self._item_combo.blockSignals(True)
        self._item_combo.clear()
        self._item_combo.addItem("— قلم انتخاب کنید —", None)
        for item in items:
            self._item_combo.addItem(
                f"{item.code}  —  {item.name}", item.id
            )
        self._item_combo.blockSignals(False)

    def _load_line_data(self):
        try:
            with get_session() as session:
                svc = BOMService(session)
                line = svc.get_line_by_id(self.line_id)
            if not line:
                return

            for i in range(self._item_combo.count()):
                if self._item_combo.itemData(i) == line.item_id:
                    self._item_combo.setCurrentIndex(i)
                    break

            if line.uom:
                self._uom_combo.set_current_code(line.uom)
                # بر اساس واحد، اعشار تنظیم بشه
                self._adjust_qty_decimals(line.uom)

            self._qty.setValue(float(line.quantity))
            self._scrap.setValue(float(line.scrap_percent or 0))
            self._optional.setChecked(line.is_optional)
            self._notes.setPlainText(line.notes or "")

        except Exception as e:
            logger.error(f"خطا در بارگذاری خط BOM: {e}")

    # ── Helpers ────────────────────────────────────────────────────

    def _adjust_qty_decimals(self, uom_code: str | None):
        """
        بر اساس نوع واحد، تعداد اعشار QDoubleSpinBox را تنظیم می‌کند.
        - واحدهای شمارشی (عدد، دستگاه، ست): بدون اعشار
        - واحدهای پیوسته (kg، m، L): سه رقم اعشار
        """
        if not uom_code:
            self._qty.setDecimals(3)
            self._qty.setSingleStep(0.1)
            return

        uom_lower = uom_code.lower().strip()
        uom_label = self._uom_map.get(uom_code, "").lower().strip()

        # چک شمارشی بودن
        is_discrete = (
            uom_lower in DISCRETE_UOMS
            or uom_label in DISCRETE_UOMS
        )

        # حفظ مقدار فعلی
        current_val = self._qty.value()

        if is_discrete:
            self._qty.setDecimals(0)
            self._qty.setSingleStep(1)
            self._qty.setMinimum(1)
            # گرد کردن به نزدیک‌ترین عدد صحیح
            self._qty.setValue(max(1, round(current_val)))
        else:
            self._qty.setDecimals(3)
            self._qty.setSingleStep(0.1)
            self._qty.setMinimum(0.001)
            self._qty.setValue(current_val if current_val > 0 else 1.0)

    # ── Events ─────────────────────────────────────────────────────

    def _on_search(self, text: str):
        text_low = text.strip().lower()
        if not text_low:
            filtered = self._all_items
        else:
            filtered = [
                it for it in self._all_items
                if text_low in it.code.lower()
                or text_low in it.name.lower()
            ]
        cur_id = self._item_combo.currentData()
        self._fill_item_combo(filtered)
        if cur_id:
            for i in range(self._item_combo.count()):
                if self._item_combo.itemData(i) == cur_id:
                    self._item_combo.setCurrentIndex(i)
                    break

    def _on_item_selected(self, _idx: int):
        item_id = self._item_combo.currentData()
        if not item_id:
            self._item_info_lbl.setText("—")
            return

        for item in self._all_items:
            if item.id == item_id:
                type_label = self._type_map.get(
                    item.item_type, item.item_type or "—"
                )
                uom_label = self._uom_map.get(item.uom, item.uom or "—")
                cost_str = ""
                if item.standard_cost:
                    cost_str = f"  |  هزینه: {item.standard_cost:,.0f}"
                self._item_info_lbl.setText(
                    f"نوع: {type_label}  |  واحد: {uom_label}{cost_str}"
                )
                # واحد پیش‌فرض از قلم
                if item.uom:
                    self._uom_combo.set_current_code(item.uom)
                    # اعشار را تنظیم کن
                    self._adjust_qty_decimals(item.uom)
                break

    def _on_uom_changed(self, _idx: int):
        """وقتی کاربر خود واحد را عوض کرد"""
        uom = self._uom_combo.get_current_code()
        self._adjust_qty_decimals(uom)

    def _on_save(self):
        item_id = self._item_combo.currentData()
        if not item_id:
            Toast.warning(self, "یک قلم انتخاب کنید")
            return

        qty = Decimal(str(self._qty.value()))
        if qty <= 0:
            Toast.warning(self, "مقدار باید بزرگتر از صفر باشد")
            return

        scrap = Decimal(str(self._scrap.value()))
        uom = self._uom_combo.get_current_code()
        is_optional = self._optional.isChecked()
        notes = self._notes.toPlainText().strip()

        try:
            with get_session() as session:
                svc = BOMService(session)
                if self._is_edit:
                    svc.update_line(
                        line_id=self.line_id,
                        quantity=qty,
                        uom=uom,
                        scrap_percent=scrap,
                        is_optional=is_optional,
                        notes=notes,
                    )
                else:
                    svc.add_line(
                        bom_header_id=self.bom_header_id,
                        item_id=item_id,
                        quantity=qty,
                        uom=uom,
                        scrap_percent=scrap,
                        is_optional=is_optional,
                        notes=notes,
                    )
            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره خط BOM: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
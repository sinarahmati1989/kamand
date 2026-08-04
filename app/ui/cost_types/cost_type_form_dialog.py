"""
دیالوگ افزودن/ویرایش نوع هزینه
"""

from decimal import Decimal
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTextEdit,
    QPushButton, QWidget, QGroupBox, QDoubleSpinBox,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt

from app.services.cost_type_service import CostTypeService
from app.schemas.cost_type_schema import CostTypeCreate, CostTypeUpdate
from app.database.session import get_session
from app.enums.cost_enums import CostStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class CostTypeFormDialog(QDialog):
    """فرم افزودن/ویرایش نوع هزینه"""

    def __init__(self, cost_type_id: int | None = None, parent=None):
        super().__init__(parent)
        self.cost_type_id = cost_type_id
        self.is_edit = cost_type_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("ویرایش نوع هزینه" if self.is_edit else "افزودن نوع هزینه جدید")
        self.setMinimumSize(680, 640)
        self.resize(720, 680)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    # ---------- Setup ----------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title_text = "ویرایش نوع هزینه" if self.is_edit else "افزودن نوع هزینه جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(self._build_form(), 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("ذخیره")
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

    def _make_field(self, label_text: str, widget: QWidget, required: bool = False) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _build_form(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        if self.is_edit:
            top_row = QHBoxLayout()
            top_row.setSpacing(12)

            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("مثال: مواد اولیه فلزی")
            self.name_input.setMinimumHeight(36)
            top_row.addWidget(self._make_field("نام نوع هزینه", self.name_input, required=True), 2)

            code_wrapper = QWidget()
            ch = QVBoxLayout(code_wrapper)
            ch.setContentsMargins(0, 0, 0, 0)
            ch.setSpacing(6)

            code_lbl = QLabel("کد نوع هزینه")
            code_lbl.setObjectName("fieldLabel")
            code_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px; "
                "padding: 8px 12px; background: rgba(255,255,255,0.85); "
                "border: 1.5px solid rgba(99,102,241,0.25); border-radius: 10px; "
                "min-height: 20px;"
            )

            ch.addWidget(code_lbl)
            ch.addWidget(self.code_label)
            top_row.addWidget(code_wrapper, 1)

            layout.addLayout(top_row)
        else:
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("مثال: مواد اولیه فلزی")
            self.name_input.setMinimumHeight(36)
            layout.addWidget(self._make_field("نام نوع هزینه", self.name_input, required=True))

        category_group = QGroupBox("دسته‌بندی و رفتار هزینه")
        category_group.setObjectName("formGroup")
        cv = QVBoxLayout(category_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        cat_row = QHBoxLayout()
        cat_row.setSpacing(12)

        self.category_combo = LookupComboBoxWithAdd(LookupCategory.COST_CATEGORY.value)
        self.category_combo.setMinimumHeight(36)
        cat_row.addWidget(self._make_field("دسته‌بندی", self.category_combo, required=True), 1)

        self.behavior_combo = LookupComboBoxWithAdd(LookupCategory.COST_BEHAVIOR.value)
        self.behavior_combo.setMinimumHeight(36)
        cat_row.addWidget(self._make_field("رفتار هزینه", self.behavior_combo, required=True), 1)

        cv.addLayout(cat_row)

        alloc_row = QHBoxLayout()
        alloc_row.setSpacing(12)

        self.unit_combo = LookupComboBoxWithAdd(LookupCategory.COST_UNIT.value)
        self.unit_combo.setMinimumHeight(36)
        alloc_row.addWidget(self._make_field("واحد", self.unit_combo, required=True), 1)

        self.allocation_combo = LookupComboBoxWithAdd(LookupCategory.ALLOCATION_METHOD.value)
        self.allocation_combo.setMinimumHeight(36)
        alloc_row.addWidget(self._make_field("روش تخصیص", self.allocation_combo, required=True), 1)

        cv.addLayout(alloc_row)
        layout.addWidget(category_group)

        financial_group = QGroupBox("مبلغ و اطلاعات حسابداری")
        financial_group.setObjectName("formGroup")
        fv = QVBoxLayout(financial_group)
        fv.setContentsMargins(14, 20, 14, 14)
        fv.setSpacing(12)

        fin_row = QHBoxLayout()
        fin_row.setSpacing(12)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999_999_999_999)
        self.amount_input.setDecimals(0)
        self.amount_input.setGroupSeparatorShown(True)
        self.amount_input.setSpecialValueText("—")
        self.amount_input.setMinimumHeight(36)
        fin_row.addWidget(self._make_field("مبلغ پیش‌فرض", self.amount_input), 1)

        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("مثال: 5101-01")
        self.account_input.setMinimumHeight(36)
        fin_row.addWidget(self._make_field("کد حسابداری", self.account_input), 1)

        fv.addLayout(fin_row)

        self.taxable_cb = QCheckBox("مشمول مالیات است")
        self.taxable_cb.setMinimumHeight(28)
        fv.addWidget(self.taxable_cb)

        layout.addWidget(financial_group)

        structure_group = QGroupBox("ساختار و وضعیت")
        structure_group.setObjectName("formGroup")
        sv = QVBoxLayout(structure_group)
        sv.setContentsMargins(14, 20, 14, 14)
        sv.setSpacing(12)

        self.parent_combo = QComboBox()
        self.parent_combo.setMinimumHeight(36)
        self._load_parents()
        sv.addWidget(self._make_field("نوع هزینه والد", self.parent_combo))

        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in CostStatus:
            self.status_combo.addItem(st.label, st.value)

        if not self.is_edit:
            self.status_combo.setCurrentIndex(0)
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip("وضعیت رکورد جدید به‌صورت پیش‌فرض «فعال» ثبت می‌شود.")

        sv.addWidget(self._make_field("وضعیت", self.status_combo))
        layout.addWidget(structure_group)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("توضیحات اضافی")
        self.description_input.setMinimumHeight(70)
        self.description_input.setMaximumHeight(90)
        layout.addWidget(self._make_field("توضیحات", self.description_input))

        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll

    # ---------- Load Data ----------

    def _load_parents(self):
        self.parent_combo.clear()
        self.parent_combo.addItem("— بدون والد —", None)

        try:
            with get_session() as session:
                svc = CostTypeService(session)
                items = svc.get_all()

                for item in items:
                    if self.is_edit and item.id == self.cost_type_id:
                        continue
                    self.parent_combo.addItem(f"{item.code} - {item.name}", item.id)

        except Exception as e:
            logger.warning(f"خطا در بارگذاری والدها: {e}")

    def _load_data(self):
        try:
            with get_session() as session:
                svc = CostTypeService(session)
                ct = svc.get_by_id(self.cost_type_id)

                if not ct:
                    raise ValueError("نوع هزینه یافت نشد")

                self.code_label.setText(ct.code)
                self.name_input.setText(ct.name or "")

                self.category_combo.set_current_code(ct.category)
                self.behavior_combo.set_current_code(ct.cost_behavior)
                self.unit_combo.set_current_code(ct.unit)
                self.allocation_combo.set_current_code(ct.allocation_method)

                if ct.default_amount is not None:
                    self.amount_input.setValue(float(ct.default_amount))

                if ct.account_code:
                    self.account_input.setText(ct.account_code)

                self.taxable_cb.setChecked(bool(ct.taxable))

                if ct.parent_id:
                    idx = self.parent_combo.findData(ct.parent_id)
                    if idx >= 0:
                        self.parent_combo.setCurrentIndex(idx)

                if ct.status:
                    idx = self.status_combo.findData(ct.status)
                    if idx >= 0:
                        self.status_combo.setCurrentIndex(idx)

                if ct.description:
                    self.description_input.setPlainText(ct.description)

        except Exception as e:
            logger.error(f"خطا در بارگذاری نوع هزینه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    # ---------- Save ----------

    def _collect_data(self) -> dict:
        amount_val = self.amount_input.value()

        return {
            "name": self.name_input.text().strip(),
            "category": self.category_combo.get_current_code(),
            "cost_behavior": self.behavior_combo.get_current_code(),
            "unit": self.unit_combo.get_current_code(),
            "default_amount": Decimal(str(amount_val)) if amount_val > 0 else None,
            "allocation_method": self.allocation_combo.get_current_code(),
            "account_code": self.account_input.text().strip() or None,
            "taxable": self.taxable_cb.isChecked(),
            "parent_id": self.parent_combo.currentData(),
            "description": self.description_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام نوع هزینه الزامی است"

        if len(data["name"]) < 2:
            return "نام نوع هزینه باید حداقل ۲ کاراکتر باشد"

        if not data.get("category"):
            return "انتخاب دسته‌بندی الزامی است"

        if not data.get("cost_behavior"):
            return "انتخاب رفتار هزینه الزامی است"

        if not data.get("unit"):
            return "انتخاب واحد الزامی است"

        if not data.get("allocation_method"):
            return "انتخاب روش تخصیص الزامی است"

        return None

    def _on_save(self):
        try:
            data = self._collect_data()

            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = CostTypeService(session)

                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    schema = CostTypeUpdate(**data)
                    svc.update(self.cost_type_id, schema)
                else:
                    schema = CostTypeCreate(**data)
                    svc.create(schema)

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره نوع هزینه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
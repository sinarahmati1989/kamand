"""
Kamand - Item Form Dialog
افزودن/ویرایش قلم
با WeightWidget و MoneyWidget
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt

from app.services.item_service import ItemService
from app.schemas.item_schema import ItemCreate, ItemUpdate
from app.database.session import get_session
from app.enums.engineering_enums import ItemStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.lookup_combo import LookupComboBox
from app.ui.widgets.weight_widget import WeightWidget
from app.ui.widgets.money_widget import MoneyWidget
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class ItemFormDialog(QDialog):
    """فرم افزودن/ویرایش قلم"""

    def __init__(self, item_id: int | None = None, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.is_edit = item_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش قلم" if self.is_edit else "قلم جدید"
        )
        self.setMinimumSize(680, 720)
        self.resize(720, 760)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = "ویرایش قلم" if self.is_edit else "قلم جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد
        code_row = QHBoxLayout()
        code_lbl = QLabel("کد قلم:")
        code_lbl.setObjectName("fieldLabel")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(
            "خودکار: ITM-0001 (یا خودتان وارد کنید)"
        )
        self.code_input.setMinimumHeight(36)
        self.code_input.setMaximumWidth(280)
        if self.is_edit:
            self.code_input.setReadOnly(True)
            self.code_input.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
                "padding: 6px 12px; background: rgba(255,255,255,0.85);"
                "border: 1.5px solid rgba(99,102,241,0.25);"
                "border-radius: 8px;"
            )
        code_row.addWidget(code_lbl)
        code_row.addWidget(self.code_input)
        code_row.addStretch()
        layout.addLayout(code_row)

        # اسکرول
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # اطلاعات پایه
        basic = QGroupBox("اطلاعات پایه")
        basic.setObjectName("formGroup")
        bv = QVBoxLayout(basic)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        # نام
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "مثال: پیچ M12×50، بلبرینگ 6205، ورق فولادی 3mm"
        )
        self.name_input.setMinimumHeight(36)
        bv.addWidget(
            self._make_field("نام قلم", self.name_input, required=True)
        )

        # نوع + واحد
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.ITEM_TYPE.value,
            allow_empty=True,
        )
        self.type_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("نوع قلم", self.type_combo), 2)

        self.uom_combo = LookupComboBox(
            LookupCategory.UOM.value,
            allow_empty=True,
        )
        self.uom_combo.setMinimumHeight(36)
        row1.addWidget(self._make_field("واحد", self.uom_combo), 1)
        bv.addLayout(row1)

        # وضعیت — فقط در ویرایش
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in ItemStatus:
            self.status_combo.addItem(st.label, st.value)

        if self.is_edit:
            status_row = QHBoxLayout()
            status_row.addWidget(
                self._make_field("وضعیت", self.status_combo)
            )
            status_row.addStretch()
            bv.addLayout(status_row)
        else:
            self.status_combo.hide()
            idx = self.status_combo.findData(ItemStatus.ACTIVE.value)
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)

        content_layout.addWidget(basic)

        # شناسه‌ها و سازنده
        ids_grp = QGroupBox("شناسه‌ها و سازنده")
        ids_grp.setObjectName("formGroup")
        iv = QVBoxLayout(ids_grp)
        iv.setContentsMargins(14, 20, 14, 14)
        iv.setSpacing(12)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.part_no_input = QLineEdit()
        self.part_no_input.setPlaceholderText("شماره قطعه داخلی")
        self.part_no_input.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("شماره قطعه", self.part_no_input), 1
        )

        self.drawing_no_input = QLineEdit()
        self.drawing_no_input.setPlaceholderText("شماره نقشه")
        self.drawing_no_input.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("شماره نقشه", self.drawing_no_input), 1
        )
        iv.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.manufacturer_combo = LookupComboBoxWithAdd(
            LookupCategory.ITEM_MANUFACTURER.value,
            allow_empty=True,
        )
        self.manufacturer_combo.setMinimumHeight(36)
        row3.addWidget(
            self._make_field("سازنده", self.manufacturer_combo), 2
        )

        self.mfr_part_no_input = QLineEdit()
        self.mfr_part_no_input.setPlaceholderText("Part No سازنده")
        self.mfr_part_no_input.setMinimumHeight(36)
        row3.addWidget(
            self._make_field("Part No سازنده", self.mfr_part_no_input), 2
        )
        iv.addLayout(row3)

        content_layout.addWidget(ids_grp)

        # مشخصات فنی
        tech_grp = QGroupBox("مشخصات فنی")
        tech_grp.setObjectName("formGroup")
        tv = QVBoxLayout(tech_grp)
        tv.setContentsMargins(14, 20, 14, 14)
        tv.setSpacing(12)

        row4 = QHBoxLayout()
        row4.setSpacing(12)

        self.weight_widget = WeightWidget()
        row4.addWidget(self._make_field("وزن", self.weight_widget), 1)

        self.material_grade_combo = LookupComboBoxWithAdd(
            LookupCategory.MATERIAL_GRADE.value,
            allow_empty=True,
        )
        self.material_grade_combo.setMinimumHeight(36)
        row4.addWidget(
            self._make_field("گرید متریال", self.material_grade_combo), 2
        )
        tv.addLayout(row4)

        self.surface_combo = LookupComboBoxWithAdd(
            LookupCategory.SURFACE_TREATMENT.value,
            allow_empty=True,
        )
        self.surface_combo.setMinimumHeight(36)
        tv.addWidget(
            self._make_field("پوشش/آبکاری", self.surface_combo)
        )

        content_layout.addWidget(tech_grp)

        # هزینه استاندارد
        cost_grp = QGroupBox("هزینه استاندارد")
        cost_grp.setObjectName("formGroup")
        cv = QVBoxLayout(cost_grp)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        self.money_widget = MoneyWidget()
        cv.addWidget(self._make_field("هزینه واحد", self.money_widget))

        content_layout.addWidget(cost_grp)

        # مشخصات فنی متن
        self.spec_input = QTextEdit()
        self.spec_input.setPlaceholderText(
            "مشخصات فنی کامل...\n"
            "مثال: ابعاد، تلرانس، استاندارد..."
        )
        self.spec_input.setMinimumHeight(80)
        self.spec_input.setMaximumHeight(110)
        content_layout.addWidget(
            self._make_field("مشخصات فنی", self.spec_input)
        )

        # یادداشت‌ها
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت‌ها...")
        self.notes_input.setMinimumHeight(60)
        self.notes_input.setMaximumHeight(90)
        content_layout.addWidget(
            self._make_field("یادداشت‌ها", self.notes_input)
        )

        content_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # دکمه‌ها
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        save_btn = QPushButton("ذخیره")
        save_btn.setObjectName("neonButton")
        save_btn.setFixedSize(130, 42)
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

    def _make_field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        lbl = QLabel(f"{label_text} *" if required else label_text)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _load_data(self):
        try:
            with get_session() as session:
                svc = ItemService(session)
                it = svc.get_by_id(self.item_id)
                if not it:
                    raise ValueError("قلم یافت نشد")

                self.code_input.setText(it.code)
                self.name_input.setText(it.name or "")

                if it.item_type:
                    self.type_combo.set_current_code(it.item_type)
                if it.uom:
                    self.uom_combo.set_current_code(it.uom)

                idx = self.status_combo.findData(it.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

                self.part_no_input.setText(it.part_no or "")
                self.drawing_no_input.setText(it.drawing_no or "")

                if it.manufacturer:
                    self.manufacturer_combo.set_current_code(it.manufacturer)
                self.mfr_part_no_input.setText(
                    it.manufacturer_part_no or ""
                )

                if it.weight:
                    self.weight_widget.set_value_kg(float(it.weight))

                if it.material_grade:
                    self.material_grade_combo.set_current_code(
                        it.material_grade
                    )
                if it.surface_treatment:
                    self.surface_combo.set_current_code(
                        it.surface_treatment
                    )

                if it.standard_cost is not None:
                    self.money_widget.set_amount_and_currency(
                        float(it.standard_cost),
                        it.currency or "irr",
                    )

                if it.specification:
                    self.spec_input.setPlainText(it.specification)
                if it.notes:
                    self.notes_input.setPlainText(it.notes)

        except Exception as e:
            logger.error(f"خطا در بارگذاری قلم: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect_data(self) -> dict:
        weight_kg = self.weight_widget.get_value_kg()
        cost_amount, cost_currency = (
            self.money_widget.get_amount_and_currency()
        )

        return {
            "code": self.code_input.text().strip() or None,
            "name": self.name_input.text().strip(),
            "item_type": (
                self.type_combo.get_current_code() or "purchased_part"
            ),
            "uom": self.uom_combo.get_current_code() or "pcs",
            "part_no": self.part_no_input.text().strip() or None,
            "drawing_no": self.drawing_no_input.text().strip() or None,
            "manufacturer": (
                self.manufacturer_combo.get_current_code() or None
            ),
            "manufacturer_part_no": (
                self.mfr_part_no_input.text().strip() or None
            ),
            "weight": weight_kg,
            "material_grade": (
                self.material_grade_combo.get_current_code() or None
            ),
            "surface_treatment": (
                self.surface_combo.get_current_code() or None
            ),
            "standard_cost": cost_amount,
            "currency": cost_currency,
            "specification": (
                self.spec_input.toPlainText().strip() or None
            ),
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام قلم الزامی است"
        if len(data["name"]) < 2:
            return "نام قلم باید حداقل ۲ کاراکتر باشد"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()
            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = ItemService(session)
                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    data.pop("code", None)
                    svc.update(self.item_id, ItemUpdate(**data))
                else:
                    svc.create(ItemCreate(**data))

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
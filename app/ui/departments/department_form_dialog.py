"""
دیالوگ افزودن/ویرایش دپارتمان
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QWidget, QGroupBox,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt

from app.services.department_service import DepartmentService
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.database.session import get_session
from app.enums.department_enums import DepartmentStatus
from app.enums.lookup_categories import LookupCategory
from app.ui.widgets.lookup_combo_with_add import LookupComboBoxWithAdd
from app.ui.widgets.toast import Toast

logger = logging.getLogger(__name__)


class DepartmentFormDialog(QDialog):
    """فرم افزودن/ویرایش دپارتمان"""

    def __init__(self, department_id: int | None = None, parent=None):
        super().__init__(parent)
        self.department_id = department_id
        self.is_edit = department_id is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش دپارتمان" if self.is_edit else "افزودن دپارتمان جدید"
        )
        self.setMinimumSize(560, 580)
        self.resize(600, 620)

        self._setup_ui()

        if self.is_edit:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = "ویرایش دپارتمان" if self.is_edit else "افزودن دپارتمان جدید"
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # کد در ویرایش
        if self.is_edit:
            code_row = QHBoxLayout()
            code_lbl = QLabel("کد دپارتمان:")
            code_lbl.setObjectName("fieldLabel")
            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
                "padding: 6px 12px; background: rgba(255,255,255,0.85);"
                "border: 1.5px solid rgba(99,102,241,0.25); border-radius: 8px;"
            )
            code_row.addWidget(code_lbl)
            code_row.addWidget(self.code_label)
            code_row.addStretch()
            layout.addLayout(code_row)

        # Scroll content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # ── گروه اطلاعات پایه ──
        basic_group = QGroupBox("اطلاعات پایه")
        basic_group.setObjectName("formGroup")
        bv = QVBoxLayout(basic_group)
        bv.setContentsMargins(14, 20, 14, 14)
        bv.setSpacing(12)

        # نام
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: واحد تولید، بخش کنترل کیفیت")
        self.name_input.setMinimumHeight(36)
        bv.addWidget(self._make_field("نام دپارتمان", self.name_input, required=True))

        # نوع
        self.type_combo = LookupComboBoxWithAdd(
            LookupCategory.DEPARTMENT_TYPE.value,
            allow_empty=True
        )
        self.type_combo.setMinimumHeight(36)
        bv.addWidget(self._make_field("نوع دپارتمان", self.type_combo))

        content_layout.addWidget(basic_group)

        # ── گروه اطلاعات تماس ──
        contact_group = QGroupBox("مشخصات مدیر و موقعیت")
        contact_group.setObjectName("formGroup")
        cv = QVBoxLayout(contact_group)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.manager_input = QLineEdit()
        self.manager_input.setPlaceholderText("نام مسئول دپارتمان")
        self.manager_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("مسئول/مدیر", self.manager_input), 2)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("داخلی: ۱۲۳")
        self.phone_input.setMinimumHeight(36)
        row1.addWidget(self._make_field("تلفن داخلی", self.phone_input), 1)

        cv.addLayout(row1)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("مثال: سالن A، طبقه اول")
        self.location_input.setMinimumHeight(36)
        cv.addWidget(self._make_field("موقعیت در کارگاه", self.location_input))

        content_layout.addWidget(contact_group)

        # ── یادداشت ──
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت‌های اضافی...")
        self.notes_input.setMinimumHeight(80)
        self.notes_input.setMaximumHeight(110)
        content_layout.addWidget(
            self._make_field("یادداشت‌ها", self.notes_input)
        )

        # ── وضعیت ──
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        for st in DepartmentStatus:
            self.status_combo.addItem(st.label, st.value)

        if not self.is_edit:
            self.status_combo.setEnabled(False)
            self.status_combo.setToolTip("وضعیت رکورد جدید به‌صورت پیش‌فرض «فعال» ثبت می‌شود.")

        status_row = QHBoxLayout()
        status_row.addWidget(self._make_field("وضعیت", self.status_combo))
        status_row.addStretch()
        content_layout.addLayout(status_row)

        content_layout.addStretch(1)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

    def _load_data(self):
        try:
            with get_session() as session:
                svc = DepartmentService(session)
                dept = svc.get_by_id(self.department_id)
                if not dept:
                    raise ValueError("دپارتمان یافت نشد")

                self.code_label.setText(dept.code)
                self.name_input.setText(dept.name or "")
                if dept.department_type:
                    self.type_combo.set_current_code(dept.department_type)
                self.manager_input.setText(dept.manager_name or "")
                self.phone_input.setText(dept.phone or "")
                self.location_input.setText(dept.location or "")
                if dept.notes:
                    self.notes_input.setPlainText(dept.notes)

                idx = self.status_combo.findData(dept.status)
                if idx >= 0:
                    self.status_combo.setCurrentIndex(idx)

        except Exception as e:
            logger.error(f"خطا در بارگذاری دپارتمان: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")

    def _collect_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "department_type": self.type_combo.get_current_code() or None,
            "manager_name": self.manager_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "location": self.location_input.text().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def _validate(self, data: dict) -> str | None:
        if not data.get("name"):
            return "نام دپارتمان الزامی است"
        if len(data["name"]) < 2:
            return "نام دپارتمان باید حداقل ۲ کاراکتر باشد"
        return None

    def _on_save(self):
        try:
            data = self._collect_data()
            error = self._validate(data)
            if error:
                Toast.warning(self, error)
                return

            with get_session() as session:
                svc = DepartmentService(session)
                if self.is_edit:
                    data["status"] = self.status_combo.currentData()
                    svc.update(self.department_id, DepartmentUpdate(**data))
                else:
                    svc.create(DepartmentCreate(**data))

            self.accept()

        except ValueError as e:
            Toast.warning(self, str(e))
        except Exception as e:
            logger.error(f"خطا در ذخیره دپارتمان: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
"""
Kamand - Project Form Dialog
افزودن/ویرایش پروژه با ۳ Tab مدرن
"""
import logging

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit,
    QPushButton, QTabWidget, QWidget, QGroupBox,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.services.project_service import ProjectService
from app.database.session import get_session
from app.ui.widgets.toast import Toast
from app.ui.widgets.persian_date_edit import PersianDateEdit
from app.ui.widgets.money_widget import MoneyWidget
from app.ui.widgets.searchable_customer_combo import SearchableCustomerCombo

logger = logging.getLogger(__name__)


class ProjectFormDialog(QDialog):
    """فرم افزودن/ویرایش پروژه با ۳ Tab"""

    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_id = project.id if project else None
        self.is_edit = project is not None

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(
            "ویرایش پروژه" if self.is_edit else "افزودن پروژه جدید"
        )
        self.setMinimumSize(860, 700)
        self.resize(900, 740)

        self._setup_ui()

        if self.is_edit:
            self._load_data()
        else:
            self._load_next_project_no()

    # ═══════════════ Setup ═══════════════

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # عنوان
        title_text = (
            "ویرایش پروژه" if self.is_edit
            else "افزودن پروژه جدید"
        )
        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # شماره پروژه (فقط در ویرایش)
        if self.is_edit:
            code_wrapper = QWidget()
            ch = QHBoxLayout(code_wrapper)
            ch.setContentsMargins(0, 0, 0, 0)
            ch.setSpacing(8)

            code_lbl = QLabel("شماره پروژه:")
            code_lbl.setObjectName("fieldLabel")

            self.code_label = QLabel("—")
            self.code_label.setStyleSheet(
                "color: #6366F1; font-weight: bold; font-size: 14px;"
            )

            ch.addWidget(code_lbl)
            ch.addWidget(self.code_label)
            ch.addStretch()
            layout.addWidget(code_wrapper)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("customerTabs")
        self.tabs.addTab(self._build_basic_tab(),    "📋  اطلاعات پایه")
        self.tabs.addTab(self._build_schedule_tab(), "📅  تاریخ‌ها و برنامه")
        self.tabs.addTab(self._build_finance_tab(),  "💰  اطلاعات مالی")
        layout.addWidget(self.tabs, 1)

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

    # ═══════════════ Helpers ═══════════════

    def _make_field(
        self, label_text: str, widget: QWidget, required: bool = False
    ) -> QWidget:
        wrapper = QWidget()
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)

        label_full = f"{label_text} *" if required else label_text
        lbl = QLabel(label_full)
        lbl.setObjectName("fieldLabel")
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        if required:
            lbl.setStyleSheet(
                "QLabel#fieldLabel { color: #6366F1; font-weight: 600; }"
            )

        v.addWidget(lbl)
        v.addWidget(widget)
        return wrapper

    def _wrap_scroll(self, content: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setWidget(content)
        return scroll

    def _apply_persian_font(self, text_edit: QTextEdit):
        font = QFont("Vazirmatn", 10)
        text_edit.setFont(font)
        text_edit.document().setDefaultFont(font)

    # ═══════════════ Tab 1: اطلاعات پایه ═══════════════

    def _build_basic_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── گروه شناسه ───
        identity = QGroupBox("📁  شناسه پروژه")
        identity.setObjectName("formGroup")
        iv = QVBoxLayout(identity)
        iv.setContentsMargins(14, 20, 14, 14)
        iv.setSpacing(12)

        # شماره پروژه (فقط در حالت افزودن)
        if not self.is_edit:
            self.project_no_input = QLineEdit()
            self.project_no_input.setPlaceholderText(
                "خودکار: PRJ-0001 (یا خودتان وارد کنید)"
            )
            self.project_no_input.setMinimumHeight(36)
            self.project_no_input.setMaximumWidth(280)

            no_row = QHBoxLayout()
            no_row.addWidget(
                self._make_field("شماره پروژه", self.project_no_input)
            )
            no_row.addStretch()
            iv.addLayout(no_row)
        else:
            self.project_no_input = None

        # نام پروژه + شماره قرارداد
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("نام پروژه را وارد کنید")
        self.name_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("نام پروژه", self.name_input, required=True), 1
        )

        self.contract_no_input = QLineEdit()
        self.contract_no_input.setPlaceholderText("شماره قرارداد (اختیاری)")
        self.contract_no_input.setMinimumHeight(36)
        row1.addWidget(
            self._make_field("شماره قرارداد", self.contract_no_input), 1
        )

        iv.addLayout(row1)

        # مشتری + اولویت
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.customer_combo = SearchableCustomerCombo()
        self.customer_combo.setMinimumHeight(36)
        row2.addWidget(
            self._make_field("مشتری", self.customer_combo, required=True), 2
        )

        self.priority_combo = QComboBox()
        self.priority_combo.setMinimumHeight(36)
        self.priority_combo.addItem("پایین", "low")
        self.priority_combo.addItem("عادی", "normal")
        self.priority_combo.addItem("بالا", "high")
        self.priority_combo.addItem("فوری", "urgent")
        self.priority_combo.setCurrentIndex(1)
        row2.addWidget(self._make_field("اولویت", self.priority_combo), 1)

        iv.addLayout(row2)

        layout.addWidget(identity)

        # ─── توضیحات ───
        desc = QGroupBox("📝  توضیحات پروژه")
        desc.setObjectName("formGroup")
        dv = QVBoxLayout(desc)
        dv.setContentsMargins(14, 20, 14, 14)
        dv.setSpacing(12)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "شرح کوتاه پروژه، محدوده کار، اهداف..."
        )
        self.description_input.setMinimumHeight(100)
        self.description_input.setMaximumHeight(140)
        self._apply_persian_font(self.description_input)
        dv.addWidget(self._make_field("شرح پروژه", self.description_input))

        layout.addWidget(desc)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Tab 2: تاریخ‌ها ═══════════════

    def _build_schedule_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ─── تاریخ‌ها ───
        dates = QGroupBox("📆  زمان‌بندی پروژه")
        dates.setObjectName("formGroup")
        dv = QVBoxLayout(dates)
        dv.setContentsMargins(14, 20, 14, 14)
        dv.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.start_date_input = PersianDateEdit(allow_empty=True)
        row1.addWidget(
            self._make_field("📅  تاریخ شروع", self.start_date_input), 1
        )

        self.delivery_date_input = PersianDateEdit(allow_empty=True)
        row1.addWidget(
            self._make_field(
                "🎯  تاریخ تحویل برنامه‌ریزی‌شده",
                self.delivery_date_input,
            ), 1
        )

        dv.addLayout(row1)

        if self.is_edit:
            self.actual_delivery_input = PersianDateEdit(allow_empty=True)
            actual_row = QHBoxLayout()
            actual_row.addWidget(
                self._make_field(
                    "✅  تاریخ تحویل واقعی",
                    self.actual_delivery_input,
                )
            )
            actual_row.addStretch()
            dv.addLayout(actual_row)
        else:
            self.actual_delivery_input = None

        layout.addWidget(dates)

        # ─── یادداشت داخلی ───
        notes = QGroupBox("📌  یادداشت داخلی")
        notes.setObjectName("formGroup")
        nv = QVBoxLayout(notes)
        nv.setContentsMargins(14, 20, 14, 14)
        nv.setSpacing(12)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText(
            "یادداشت‌های داخلی تیم، نکات مهم..."
        )
        self.notes_input.setMinimumHeight(100)
        self.notes_input.setMaximumHeight(140)
        self._apply_persian_font(self.notes_input)
        nv.addWidget(self._make_field("یادداشت‌ها", self.notes_input))

        layout.addWidget(notes)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Tab 3: مالی ═══════════════

    def _build_finance_tab(self) -> QScrollArea:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        contract = QGroupBox("💵  ارزش قرارداد")
        contract.setObjectName("formGroup")
        cv = QVBoxLayout(contract)
        cv.setContentsMargins(14, 20, 14, 14)
        cv.setSpacing(12)

        self.contract_value_widget = MoneyWidget()
        cv.addWidget(
            self._make_field("مبلغ کل قرارداد", self.contract_value_widget)
        )

        hint = QLabel(
            "💡 مبلغ را وارد کنید و واحد آن را انتخاب کنید "
            "(ریال / هزار / میلیون / میلیارد / دلار / یورو)"
        )
        hint.setStyleSheet(
            "color: #64748B; font-size: 11px; padding: 4px 0;"
        )
        hint.setWordWrap(True)
        cv.addWidget(hint)

        layout.addWidget(contract)
        layout.addStretch(1)

        return self._wrap_scroll(content)

    # ═══════════════ Load ═══════════════

    def _load_next_project_no(self):
        try:
            with get_session() as session:
                service = ProjectService(session)
                no = service.get_next_project_no()
                if self.project_no_input:
                    self.project_no_input.setPlaceholderText(
                        f"خودکار: {no} (یا خودتان وارد کنید)"
                    )
        except Exception as e:
            logger.error(f"خطا در دریافت شماره پروژه: {e}")

    def _load_data(self):
        try:
            with get_session() as session:
                p = ProjectService(session).get_by_id(self.project_id)

            if not p:
                Toast.error(self, "پروژه یافت نشد")
                self.reject()
                return

            self.code_label.setText(p.project_no or "—")
            self.name_input.setText(p.name or "")
            self.contract_no_input.setText(p.contract_no or "")

            if p.customer_id:
                self.customer_combo.set_customer_id(p.customer_id)

            if p.priority:
                idx = self.priority_combo.findData(p.priority)
                if idx >= 0:
                    self.priority_combo.setCurrentIndex(idx)

            self.description_input.setPlainText(p.description or "")

            self.start_date_input.set_date(p.start_date)
            self.delivery_date_input.set_date(p.delivery_date)
            if self.actual_delivery_input:
                self.actual_delivery_input.set_date(p.actual_delivery_date)

            self.notes_input.setPlainText(p.notes or "")

            if p.contract_value is not None:
                self.contract_value_widget.set_amount_and_currency(
                    float(p.contract_value),
                    p.currency or "irr",
                )

        except Exception as e:
            logger.error(f"خطا در بارگذاری پروژه: {e}", exc_info=True)
            Toast.error(self, f"خطا در بارگذاری: {e}")
            self.reject()

    # ═══════════════ Save ═══════════════

    def _validate(self) -> bool:
        if not self.name_input.text().strip():
            Toast.warning(self, "نام پروژه الزامی است")
            self.tabs.setCurrentIndex(0)
            self.name_input.setFocus()
            return False

        if not self.customer_combo.get_customer_id():
            Toast.warning(self, "انتخاب مشتری الزامی است")
            self.tabs.setCurrentIndex(0)
            self.customer_combo.setFocus()
            return False

        return True

    def _collect(self) -> dict:
        amount, currency = self.contract_value_widget.get_amount_and_currency()

        data = {
            "name":         self.name_input.text().strip(),
            "contract_no":  self.contract_no_input.text().strip() or None,
            "customer_id":  self.customer_combo.get_customer_id(),
            "priority":     self.priority_combo.currentData(),
            "description":  self.description_input.toPlainText().strip() or None,
            "notes":        self.notes_input.toPlainText().strip() or None,
            "start_date":   self.start_date_input.get_date(),
            "delivery_date": self.delivery_date_input.get_date(),
            "contract_value": amount,
            "currency":     currency,
        }

        if self.actual_delivery_input:
            data["actual_delivery_date"] = self.actual_delivery_input.get_date()

        if not self.is_edit and self.project_no_input:
            no = self.project_no_input.text().strip()
            if no:
                data["project_no"] = no

        return data

    def _on_save(self):
        if not self._validate():
            return

        try:
            data = self._collect()

            with get_session() as session:
                svc = ProjectService(session)
                if self.is_edit:
                    fresh = svc.get_by_id(self.project_id)
                    svc.update(fresh, data)
                else:
                    svc.create(data)

            self.accept()

        except Exception as e:
            logger.error(f"خطا در ذخیره پروژه: {e}", exc_info=True)
            Toast.error(self, f"خطا: {e}")
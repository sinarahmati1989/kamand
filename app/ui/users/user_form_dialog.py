"""
UserFormDialog — فرم افزودن / ویرایش کاربر
"""
from PySide6.QtWidgets import (
    QComboBox, QCheckBox, QLabel,
    QWidget, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from app.ui.base.base_form import BaseForm
from app.ui.widgets.modern_input import ModernInput
from app.enums.roles import UserRole
from app.schemas.user_schema import UserReadDTO
import logging

logger = logging.getLogger(__name__)


class UserFormDialog(BaseForm):

    def __init__(
        self,
        user: UserReadDTO | None = None,
        parent=None,
    ):
        self._user = user
        self._is_edit = user is not None

        super().__init__(
            title="ویرایش کاربر" if self._is_edit else "افزودن کاربر جدید",
            subtitle="اطلاعات کاربر را وارد کنید",
            save_text="ذخیره تغییرات" if self._is_edit else "ایجاد کاربر",
            parent=parent,
        )

        self._build_fields()

        if self._is_edit:
            self.populate(self._user_to_dict(user))

    # ─────────────────────────── Fields ──────────────────────────────

    def _build_fields(self):
        # نام کاربری
        self.username_input = ModernInput(
            "نام کاربری *",
            placeholder="مثال: ali_karimi",
        )
        if self._is_edit:
            self.username_input.set_enabled(False)
        self.add_field(self.username_input)

        # نام کامل
        self.fullname_input = ModernInput(
            "نام کامل *",
            placeholder="مثال: علی کریمی",
        )
        self.add_field(self.fullname_input)

        # ایمیل
        self.email_input = ModernInput(
            "ایمیل",
            placeholder="مثال: ali@example.com",
        )
        self.add_field(self.email_input)

        # پسورد — فقط در افزودن
        if not self._is_edit:
            self.password_input = ModernInput(
                "رمز عبور *",
                placeholder="حداقل ۶ کاراکتر",
                is_password=True,
            )
            self.add_field(self.password_input)

        # نقش
        self.add_field(self._build_role_field())

        # وضعیت فعال — فقط در ویرایش
        if self._is_edit:
            self.active_check = QCheckBox("کاربر فعال است")
            self.active_check.setChecked(True)
            self.add_field(self.active_check)

    def _build_role_field(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel("نقش کاربر *")
        lbl.setObjectName("inputLabel")
        layout.addWidget(lbl)

        self.role_combo = QComboBox()
        self.role_combo.setObjectName("modernCombo")
        self.role_combo.setFixedHeight(42)
        self.role_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        role_items = [
            (UserRole.ADMIN,    "مدیر سیستم"),
            (UserRole.OPERATOR, "اپراتور"),
            (UserRole.VIEWER,   "بازدیدکننده"),
        ]
        for role, label in role_items:
            self.role_combo.addItem(label, role)

        layout.addWidget(self.role_combo)
        return container

    # ─────────────────────────── Data ────────────────────────────────

    def collect_data(self) -> dict | None:
        full_name = self.fullname_input.get_text()
        email = self.email_input.get_text() or None
        role = self.role_combo.currentData()

        errors = []

        if not self._is_edit:
            username = self.username_input.get_text()
            password = self.password_input.get_text()
            if not username:
                errors.append("نام کاربری الزامی است")
            if not password:
                errors.append("رمز عبور الزامی است")
            elif len(password) < 6:
                errors.append("رمز عبور باید حداقل ۶ کاراکتر باشد")

        if not full_name:
            errors.append("نام کامل الزامی است")

        if errors:
            QMessageBox.warning(
                self,
                "خطای اعتبارسنجی",
                "\n".join(f"• {e}" for e in errors),
            )
            return None

        data: dict = {
            "full_name": full_name,
            "email":     email,
            "role":      role,
        }

        if not self._is_edit:
            data["username"] = self.username_input.get_text()
            data["password"] = self.password_input.get_text()
        else:
            data["is_active"] = self.active_check.isChecked()

        return data

    def populate(self, data: dict):
        self.fullname_input.set_text(data.get("full_name", ""))
        self.email_input.set_text(data.get("email") or "")

        role = data.get("role")
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == role:
                self.role_combo.setCurrentIndex(i)
                break

        if self._is_edit and hasattr(self, "active_check"):
            self.active_check.setChecked(data.get("is_active", True))

    @staticmethod
    def _user_to_dict(user: UserReadDTO) -> dict:
        return {
            "username":  user.username,
            "full_name": user.full_name,
            "email":     user.email,
            "role":      user.role,
            "is_active": user.is_active,
        }
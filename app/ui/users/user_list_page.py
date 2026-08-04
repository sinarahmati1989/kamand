"""
UserListPage — لیست کاربران با جستجو و CRUD
"""
from PySide6.QtWidgets import QMessageBox
import logging

from app.ui.base.base_page import BasePage
from app.ui.base.base_table import AuroraTable
from app.database.session import get_session
from app.services.user_service import UserService
from app.schemas.user_schema import UserReadDTO

logger = logging.getLogger(__name__)


ROLE_LABELS = {
    "admin":    "مدیر سیستم",
    "operator": "اپراتور",
    "viewer":   "بازدیدکننده",
}


class UserListPage(BasePage):

    COLUMNS = [
        {"key": "row_num",   "label": "#",           "width": 50},
        {"key": "username",  "label": "نام کاربری",  "width": 140},
        {"key": "full_name", "label": "نام کامل",    "width": 180},
        {"key": "email",     "label": "ایمیل",       "width": 200},
        {"key": "role",      "label": "نقش",         "width": 110},
        {"key": "is_active", "label": "وضعیت",       "width": 100},
    ]

    def __init__(self, parent=None):
        super().__init__(
            title="مدیریت کاربران",
            subtitle="افزودن، ویرایش و مدیریت دسترسی کاربران",
            add_button_text="کاربر جدید",
            parent=parent,
        )
        self._users: list[UserReadDTO] = []
        self._filtered: list[UserReadDTO] = []

        self._connect_page_signals()
        self.load_users()

    def _build_content(self) -> AuroraTable:
        self.table = AuroraTable(self.COLUMNS)
        self.table.edit_requested.connect(self._on_edit)
        self.table.delete_requested.connect(self._on_delete)
        return self.table

    def _connect_page_signals(self):
        self.add_requested.connect(self._on_add)
        self.refresh_requested.connect(self.load_users)
        self.search_changed.connect(self._on_search)

    def load_users(self):
        try:
            with get_session() as session:
                self._users = UserService(session).get_all_users()
            self._filtered = list(self._users)
            self._render_table(self._filtered)
            self.set_info(f"مجموع: {len(self._users)} کاربر")
        except Exception as e:
            logger.error(f"خطا در بارگذاری کاربران: {e}")
            self.set_info("خطا در بارگذاری اطلاعات")

    def _render_table(self, users: list[UserReadDTO]):
        rows = []
        for i, u in enumerate(users, 1):
            role_str = u.role.value if hasattr(u.role, "value") else str(u.role)
            role_label = ROLE_LABELS.get(role_str, role_str)
            rows.append({
                "id":        u.id,
                "row_num":   str(i),
                "username":  u.username,
                "full_name": u.full_name,
                "email":     u.email or "—",
                "role":      role_label,
                "is_active": "✅ فعال" if u.is_active else "❌ غیرفعال",
            })
        self.table.load_data(rows)

    def _on_search(self, text: str):
        if not text:
            self._filtered = list(self._users)
        else:
            low = text.lower()
            self._filtered = [
                u for u in self._users
                if low in u.username.lower()
                or low in u.full_name.lower()
                or (u.email and low in u.email.lower())
            ]
        self._render_table(self._filtered)
        self.set_info(
            f"نمایش: {len(self._filtered)} از {len(self._users)} کاربر"
        )

    def _on_add(self):
        from app.ui.users.user_form_dialog import UserFormDialog
        dlg = UserFormDialog(parent=self)
        dlg.submitted.connect(self._save_new_user)
        dlg.exec()

    def _on_edit(self, user_id: int):
        user = self._find_user(user_id)
        if not user:
            return
        from app.ui.users.user_form_dialog import UserFormDialog
        dlg = UserFormDialog(user=user, parent=self)
        dlg.submitted.connect(
            lambda data: self._save_edit_user(user_id, data)
        )
        dlg.exec()

    def _on_delete(self, user_id: int):
        user = self._find_user(user_id)
        if not user:
            return

        reply = QMessageBox.question(
            self,
            "تأیید غیرفعال‌سازی",
            f"آیا از غیرفعال کردن کاربر «{user.full_name}» اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._deactivate_user(user_id)

    def _save_new_user(self, data: dict):
        try:
            from app.schemas.user_schema import UserCreateDTO
            # role رو به str تبدیل کن اگه enum بود
            if "role" in data and hasattr(data["role"], "value"):
                data["role"] = data["role"].value
            with get_session() as session:
                UserService(session).create_user(UserCreateDTO(**data))
            self.load_users()
        except Exception as e:
            logger.error(f"خطا در ساخت کاربر: {e}")
            QMessageBox.critical(self, "خطا", str(e))

    def _save_edit_user(self, user_id: int, data: dict):
        try:
            from app.schemas.user_schema import UserUpdateDTO
            if "role" in data and data["role"] is not None and hasattr(data["role"], "value"):
                data["role"] = data["role"].value
            with get_session() as session:
                UserService(session).update_user(
                    user_id, UserUpdateDTO(**data)
                )
            self.load_users()
        except Exception as e:
            logger.error(f"خطا در ویرایش کاربر: {e}")
            QMessageBox.critical(self, "خطا", str(e))

    def _deactivate_user(self, user_id: int):
        try:
            with get_session() as session:
                UserService(session).deactivate_user(user_id)
            self.load_users()
        except Exception as e:
            logger.error(f"خطا در غیرفعال‌سازی: {e}")
            QMessageBox.critical(self, "خطا", str(e))

    def _find_user(self, user_id: int) -> UserReadDTO | None:
        return next((u for u in self._users if u.id == user_id), None)
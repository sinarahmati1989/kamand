"""
Kamand Login Window
پنجره لاگین اصلی — کارت ثابت گرد
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QApplication, QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QKeyEvent

from app.ui.widgets.modern_input import ModernInput
from app.ui.widgets.neon_button import NeonButton
from app.ui.widgets.toast import Toast
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserLoginDTO, UserReadDTO
from app.core.exceptions import AuthenticationError, ValidationError
from app.constants import (
    LOGIN_WIDTH, LOGIN_HEIGHT,
    BRAND_NAME, BRAND_TAGLINE, APP_VERSION,
)

logger = logging.getLogger(__name__)


class LoginWindow(QDialog):
    """پنجره لاگین با تم Aurora Glass — ثابت و گرد"""

    login_success = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ورود به سیستم")
        from app.config.display import Display
        w, h = Display.login_size()
        self.setFixedSize(w, h)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setObjectName("loginWindow")

        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._center_on_screen()
        self.username_input.set_focus()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # ─────────────────────────── UI ──────────────────────────────────

    def _build_ui(self):
        card = QWidget(self)
        card.setObjectName("loginCard")
        card.setGeometry(0, 0, self.width(), self.height())
        card.setStyleSheet("""
            #loginCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0    #E0E7FF,
                    stop:0.33 #EDE9FE,
                    stop:0.66 #FCE7F3,
                    stop:1    #DBEAFE
                );
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(99, 102, 241, 80))
        shadow.setOffset(0, 12)
        card.setGraphicsEffect(shadow)

        main_layout = QHBoxLayout(card)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_left_panel(), 1)
        main_layout.addWidget(self._build_right_panel(), 1)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 50, 40, 50)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🏭")
        icon.setStyleSheet("font-size: 84px; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(BRAND_NAME)
        title.setStyleSheet("""
            font-size: 48px;
            font-weight: 900;
            color: #6366F1;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line = QLabel()
        line.setFixedHeight(4)
        line.setFixedWidth(70)
        line.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899
            );
            border-radius: 2px;
        """)
        line_wrap = QHBoxLayout()
        line_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_wrap.addWidget(line)

        subtitle = QLabel(BRAND_TAGLINE)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #475569;
            background: transparent;
            font-weight: 600;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        version = QLabel(f"نسخه {APP_VERSION}")
        version.setStyleSheet(
            "color: #94A3B8; font-size: 12px; background: transparent;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addLayout(line_wrap)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(version)

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        wrapper = QVBoxLayout(panel)
        wrapper.setContentsMargins(20, 40, 40, 40)
        wrapper.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_card = QWidget()
        form_card.setObjectName("formCard")
        form_card.setStyleSheet("""
            #formCard {
                background-color: rgba(255, 255, 255, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.7);
                border-radius: 18px;
            }
        """)
        form_card.setFixedWidth(340)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(28, 28, 28, 28)
        form_layout.setSpacing(16)

        title = QLabel("ورود به سیستم")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 800;
            color: #1E293B;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("لطفاً اطلاعات کاربری خود را وارد کنید")
        subtitle.setStyleSheet("""
            color: #64748B;
            font-size: 12px;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = ModernInput(
            label="نام کاربری",
            placeholder="نام کاربری خود را وارد کنید",
        )
        self.password_input = ModernInput(
            label="رمز عبور",
            placeholder="••••••••",
            is_password=True,
        )

        self.login_btn = NeonButton("ورود  ←")
        self.login_btn.clicked.connect(self._handle_login)

        exit_lbl = QLabel("خروج از برنامه")
        exit_lbl.setStyleSheet("""
            color: #94A3B8;
            font-size: 12px;
            background: transparent;
            padding: 5px;
        """)
        exit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exit_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_lbl.mousePressEvent = lambda e: QApplication.quit()

        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(8)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(4)
        form_layout.addWidget(self.login_btn)
        form_layout.addSpacing(8)
        form_layout.addWidget(exit_lbl)

        wrapper.addWidget(form_card, alignment=Qt.AlignmentFlag.AlignCenter)
        return panel

    # ─────────────────────────── Events ──────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._handle_login()
        elif event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and hasattr(self, "_drag_pos")
        ):
            self.move(
                event.globalPosition().toPoint() - self._drag_pos
            )
            event.accept()

    # ─────────────────────────── Login Logic ─────────────────────────

    def _handle_login(self):
        username = self.username_input.get_text()
        password = self.password_input.get_text()

        if not username or not password:
            Toast.warning(self, "نام کاربری و رمز عبور را وارد کنید")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("در حال ورود...")
        QApplication.processEvents()

        try:
            dto = UserLoginDTO(username=username, password=password)
            user = AuthService().login(dto)

            Toast.success(self, f"خوش آمدید {user.full_name} 🎉")
            logger.info(f"ورود موفق: {user.username}")
            QTimer.singleShot(800, lambda: self._on_success(user))

        except ValidationError as e:
            Toast.warning(self, str(e))
            self._reset_button()

        except AuthenticationError as e:
            Toast.error(self, str(e))
            self.password_input.clear()
            self.password_input.set_focus()
            self._reset_button()

        except Exception as e:
            logger.exception("خطای غیرمنتظره در لاگین")
            Toast.error(self, f"خطای غیرمنتظره: {e}")
            self._reset_button()

    def _reset_button(self):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("ورود  ←")

    def _on_success(self, user: UserReadDTO):
        self.login_success.emit(user)
        self.accept()

    # ─────────────────────────── Helpers ─────────────────────────────

    def reset_form(self):
        """ری‌ست کامل فرم برای ورود کاربر جدید"""
        self.username_input.clear()
        self.password_input.clear()
        self._reset_button()
        self.username_input.set_focus()

    # سازگاری با کد قدیمی
    def clear_fields(self):
        self.reset_form()
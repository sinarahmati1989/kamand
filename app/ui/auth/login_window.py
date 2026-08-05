"""
Kamand Login Window — Professional Edition v3
پنجره لاگین حرفه‌ای — با فونت Vazirmatn (سایز متعادل)
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QApplication, QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QFont
from PySide6.QtSvg import QSvgRenderer

from app.ui.widgets.modern_input import ModernInput
from app.ui.widgets.neon_button import PrimaryButton
from app.ui.widgets.toast import Toast
from app.ui.font_manager import FontManager
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserLoginDTO, UserReadDTO
from app.core.exceptions import AuthenticationError, ValidationError
from app.constants import (
    BRAND_NAME, BRAND_TAGLINE, APP_VERSION,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# لوگو SVG — Hexagon مینیمال با گرادیان
# ═══════════════════════════════════════════════════════════════

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#6366F1;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#8B5CF6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#EC4899;stop-opacity:1" />
        </linearGradient>
    </defs>
    <polygon points="50,8 87,29 87,71 50,92 13,71 13,29" 
             fill="none" 
             stroke="url(#grad)" 
             stroke-width="4"
             stroke-linejoin="round"/>
    <polygon points="50,28 70,39 70,61 50,72 30,61 30,39" 
             fill="url(#grad)"
             opacity="0.9"/>
    <circle cx="50" cy="50" r="6" fill="#FFFFFF"/>
</svg>
"""


class LogoWidget(QWidget):
    """ویجت لوگو SVG با اندازه ثابت"""

    def __init__(self, size: int = 72, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._renderer = QSvgRenderer(LOGO_SVG.encode('utf-8'))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._renderer.render(painter)


# ═══════════════════════════════════════════════════════════════
# LoginWindow — پنجره اصلی
# ═══════════════════════════════════════════════════════════════

class LoginWindow(QDialog):
    """پنجره لاگین حرفه‌ای — تک‌ستونه با Card وسط"""

    login_success = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ورود به سامانه کمند")

        # 🎯 اندازه متعادل و حرفه‌ای (نه خیلی بزرگ، نه خیلی کوچیک)
        self.setFixedSize(390, 550)

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setObjectName("loginWindow")

        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # فونت اصلی برنامه
        self._font_family = FontManager.font_family()

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
        """ساخت UI اصلی — Card تک‌ستونه"""

        # Card اصلی
        card = QWidget(self)
        card.setObjectName("loginCard")
        card.setGeometry(0, 0, self.width(), self.height())
        card.setStyleSheet("""
            #loginCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #E2E8F0;
            }
        """)

        # سایه نرم
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(99, 102, 241, 65))
        shadow.setOffset(0, 15)
        card.setGraphicsEffect(shadow)

        # Layout اصلی
        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 34, 42, 22)
        layout.setSpacing(0)

        # ─── 1. لوگو ───
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo = LogoWidget(size=68)
        logo_container.addWidget(self.logo)
        layout.addLayout(logo_container)

        layout.addSpacing(14)

        # ─── 2. عنوان اصلی ───
        title = QLabel(f"سامانه {BRAND_NAME}")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            #loginTitle {{
                font-family: "{self._font_family}";
                font-size: 24px;
                font-weight: 800;
                color: #1E293B;
                background: transparent;
                letter-spacing: 0.3px;
            }}
        """)
        layout.addWidget(title)

        layout.addSpacing(6)

        # ─── 3. زیرعنوان ───
        subtitle = QLabel(BRAND_TAGLINE)
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            #loginSubtitle {{
                font-family: "{self._font_family}";
                font-size: 12px;
                color: #64748B;
                background: transparent;
                font-weight: 500;
            }}
        """)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(28)

        # ─── 4. فیلد نام کاربری ───
        self.username_input = ModernInput(
            label="نام کاربری",
            placeholder="نام کاربری خود را وارد کنید",
            height=30,
        )
        layout.addWidget(self.username_input)

        layout.addSpacing(14)

        # ─── 5. فیلد رمز عبور ───
        self.password_input = ModernInput(
            label="رمز عبور",
            placeholder="رمز عبور خود را وارد کنید",
            is_password=True,
            height=30,
        )
        layout.addWidget(self.password_input)

        layout.addSpacing(22)

        # ─── 6. دکمه ورود ───
        self.login_btn = PrimaryButton("ورود به سامانه")
        self.login_btn.clicked.connect(self._handle_login)
        layout.addWidget(self.login_btn)

        layout.addSpacing(10)

        # ─── 7. لینک خروج (بلافاصله بعد از دکمه ورود) ───
        exit_lbl = QLabel("خروج از برنامه")
        exit_lbl.setObjectName("exitLink")
        exit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exit_lbl.setStyleSheet(f"""
            QLabel#exitLink {{
                font-family: "{self._font_family}";
                color: #64748B;
                font-size: 12px;
                background: transparent;
                padding: 4px;
                font-weight: 500;
            }}
            QLabel#exitLink:hover {{
                color: #6366F1;
            }}
        """)
        exit_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_lbl.mousePressEvent = lambda e: QApplication.quit()
        layout.addWidget(exit_lbl)

        # فضای انعطاف‌پذیر
        layout.addStretch()

        # ─── 8. نسخه (کوچیک، پایین صفحه) ───
        version = QLabel(f"v{APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"""
            QLabel {{
                font-family: "{self._font_family}";
                color: #CBD5E1;
                font-size: 9px;
                background: transparent;
                font-weight: 400;
                letter-spacing: 0.8px;
            }}
        """)
        layout.addWidget(version)

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
        self.login_btn.setText("ورود به سامانه")

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

    def clear_fields(self):
        """سازگاری با کد قدیمی"""
        self.reset_form()
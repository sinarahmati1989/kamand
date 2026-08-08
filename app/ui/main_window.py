"""
MainWindow — پنجره اصلی برنامه
"""
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPainter
from PySide6.QtSvg import QSvgRenderer

from app.core.access_control import AccessControl
from app.enums.roles import UserRole
from app.constants import BRAND_NAME, APP_VERSION
from app.config.display import Display
from app.ui.icon_manager import IconManager

logger = logging.getLogger(__name__)


SIDEBAR_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#6366F1;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#8B5CF6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#EC4899;stop-opacity:1" />
        </linearGradient>
    </defs>
    <polygon points="50,8 87,29 87,71 50,92 13,71 13,29"
             fill="none" stroke="url(#grad)" stroke-width="5"
             stroke-linejoin="round"/>
    <polygon points="50,28 70,39 70,61 50,72 30,61 30,39"
             fill="url(#grad)" opacity="0.9"/>
    <circle cx="50" cy="50" r="6" fill="#FFFFFF"/>
</svg>
"""


class SidebarLogo(QWidget):
    def __init__(self, size=56, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._renderer = QSvgRenderer(SIDEBAR_LOGO_SVG.encode("utf-8"))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._renderer.render(painter)


class SidebarItem(QPushButton):
    def __init__(self, icon_key, label, page_key, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.icon_key = icon_key
        self.label_text = label
        self.setText(f"   {label}")
        self.setObjectName("sidebarItem")
        self.setCheckable(True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(IconManager.get(icon_key, color=IconManager.COLOR_SECONDARY))
        from PySide6.QtCore import QSize
        self.setIconSize(QSize(20, 20))

    def set_active(self, active):
        self.setChecked(active)
        self.setObjectName("sidebarItemActive" if active else "sidebarItem")
        color = IconManager.COLOR_ACTIVE if active else IconManager.COLOR_SECONDARY
        self.setIcon(IconManager.get(self.icon_key, color=color))
        self.style().unpolish(self)
        self.style().polish(self)


class SidebarSection(QWidget):
    section_clicked = Signal(object)

    def __init__(self, icon_key, title, section_key, parent=None):
        super().__init__(parent)
        self.section_key = section_key
        self.icon_key = icon_key
        self.title_text = title
        self._items = []
        self._is_expanded = False
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.header_btn = QPushButton()
        self.header_btn.setObjectName("sidebarSectionHeader")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._update_header()
        self.header_btn.clicked.connect(lambda: self.section_clicked.emit(self))
        layout.addWidget(self.header_btn)

        self.items_container = QWidget()
        self.items_container.setObjectName("sidebarSectionItems")
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 4, 0, 6)
        self.items_layout.setSpacing(2)
        layout.addWidget(self.items_container)
        self.items_container.setVisible(False)

    def _update_header(self):
        from PySide6.QtCore import QSize
        arrow = "▼" if self._is_expanded else "◀"
        self.header_btn.setText(f"   {self.title_text}      {arrow}")
        color = IconManager.COLOR_PRIMARY if self._is_expanded else IconManager.COLOR_SECONDARY
        self.header_btn.setIcon(IconManager.get(self.icon_key, color=color))
        self.header_btn.setIconSize(QSize(20, 20))

    def add_item(self, item):
        self._items.append(item)
        self.items_layout.addWidget(item)

    def get_items(self):
        return self._items

    def has_page(self, page_key):
        return any(item.page_key == page_key for item in self._items)

    def set_expanded(self, expanded):
        self._is_expanded = expanded
        self.items_container.setVisible(expanded)
        obj_name = "sidebarSectionHeaderActive" if expanded else "sidebarSectionHeader"
        self.header_btn.setObjectName(obj_name)
        self.header_btn.style().unpolish(self.header_btn)
        self.header_btn.style().polish(self.header_btn)
        self._update_header()

    def is_expanded(self):
        return self._is_expanded


class Sidebar(QFrame):
    page_changed = Signal(str)
    logout_clicked = Signal()

    STRUCTURE = [
        ("item", "dashboard", "داشبورد اصلی", "dashboard", False),
        ("section", "base_data", "base_data", "داده‌های پایه", False, [
            ("customers",   "مشتریان",         "customers"),
            ("suppliers",   "تأمین‌کنندگان",   "suppliers"),
            ("costs",       "انواع هزینه",     "costs"),
            ("operations",  "عملیات ساخت",     "operations"),
            ("departments", "دپارتمان‌ها",     "departments"),
            ("work_centers", "مراکز کار",      "work_centers"),
            ("machines",    "ماشین‌آلات",      "machines"),
        ]),
        ("section", "engineering_group", "engineering", "مهندسی دستگاه", False, [
            ("device_templates", "تعریف دستگاه", "device_templates"),
            ("items",            "مدیریت اقلام", "items"),
            ("bom",              "BOM",          "bom"),
            ("routing",          "مسیر ساخت",    "routing"),
        ]),
        ("section", "operations_group", "operations_group", "عملیات", False, [
            ("projects",  "مدیریت پروژه",  "projects"),
            ("purchases", "تأمین و خرید",  "purchases"),
        ]),
        ("section", "reports_group", "reports", "گزارش‌ها", False, [
            ("profit",     "گزارش سود",      "profit"),
            ("prj_report", "گزارش پروژه‌ها", "prj_report"),
        ]),
        ("section", "system_group", "system", "سیستم", True, [
            ("users",    "کاربران",             "users"),
            ("lookups",  "داده‌های پایه سیستم", "lookups"),
            ("settings", "تنظیمات",             "settings"),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(280)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._all_items = []
        self._sections = []
        self._admin_sections = []
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_brand())
        outer.addWidget(self._build_scroll_menu(), stretch=1)
        outer.addWidget(self._build_user_card())
        outer.addWidget(self._build_logout())
        outer.addWidget(self._build_version())

    def _build_brand(self):
        brand = QFrame()
        brand.setObjectName("sidebarBrand")
        brand.setFixedHeight(140)
        layout = QVBoxLayout(brand)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_wrap = QHBoxLayout()
        logo_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_widget = SidebarLogo(size=52)
        logo_wrap.addWidget(self.logo_widget)
        layout.addLayout(logo_wrap)
        title = QLabel(BRAND_NAME)
        title.setObjectName("sidebarLogoTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(18); f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)
        sub = QLabel("سامانه مدیریت")
        sub.setObjectName("sidebarLogoSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f2 = QFont(); f2.setPointSize(9)
        sub.setFont(f2)
        layout.addWidget(sub)
        return brand

    def _build_scroll_menu(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("sidebarScroll")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        menu = QWidget()
        menu.setObjectName("sidebarMenu")
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(12, 16, 12, 16)
        menu_layout.setSpacing(4)
        section_label = QLabel("منوی اصلی")
        section_label.setObjectName("sidebarSectionLabel")
        menu_layout.addWidget(section_label)
        menu_layout.addSpacing(4)
        from PySide6.QtCore import QSize
        for entry in self.STRUCTURE:
            if entry[0] == "item":
                _, icon_key, label, key, admin_only = entry
                item = SidebarItem(icon_key, label, key)
                item.setMinimumHeight(42)
                item.setIconSize(QSize(22, 22))
                item.clicked.connect(lambda checked=False, k=key: self._on_item_clicked(k))
                self._all_items.append(item)
                menu_layout.addWidget(item)
                menu_layout.addSpacing(6)
            elif entry[0] == "section":
                _, sec_key, icon_key, title, admin_only, sub_items = entry
                section = SidebarSection(icon_key, title, sec_key)
                section.header_btn.setMinimumHeight(42)
                section.section_clicked.connect(self._on_section_toggle)
                for si_icon, si_label, si_key in sub_items:
                    item = SidebarItem(si_icon, si_label, si_key)
                    item.setMinimumHeight(36)
                    item.setIconSize(QSize(18, 18))
                    item.clicked.connect(lambda checked=False, k=si_key: self._on_item_clicked(k))
                    section.add_item(item)
                    self._all_items.append(item)
                self._sections.append(section)
                if admin_only:
                    self._admin_sections.append(section)
                menu_layout.addWidget(section)
        menu_layout.addStretch()
        scroll.setWidget(menu)
        return scroll

    def _build_user_card(self):
        from PySide6.QtCore import QSize
        wrap = QFrame()
        wrap.setObjectName("sidebarUserCardWrap")
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(12, 8, 12, 4)
        card = QFrame()
        card.setObjectName("sidebarUserCard")
        card.setFixedHeight(58)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        avatar_btn = QPushButton()
        avatar_btn.setFixedSize(38, 38)
        avatar_btn.setIcon(IconManager.get("user", color=IconManager.COLOR_PRIMARY))
        avatar_btn.setIconSize(QSize(30, 30))
        avatar_btn.setStyleSheet("QPushButton { background-color: #EEF2FF; border: none; border-radius: 19px; }")
        avatar_btn.setEnabled(False)
        layout.addWidget(avatar_btn)
        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(0)
        self.user_name_label = QLabel("—")
        self.user_name_label.setObjectName("sidebarUserName")
        info.addWidget(self.user_name_label)
        self.user_role_label = QLabel("—")
        self.user_role_label.setObjectName("sidebarUserRole")
        info.addWidget(self.user_role_label)
        layout.addLayout(info)
        layout.addStretch()
        wrap_layout.addWidget(card)
        return wrap

    def _build_logout(self):
        from PySide6.QtCore import QSize
        wrap = QFrame()
        wrap.setObjectName("sidebarLogoutWrap")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(12, 6, 12, 8)
        self.logout_btn = QPushButton("   خروج از سیستم")
        self.logout_btn.setObjectName("sidebarLogout")
        self.logout_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setIcon(IconManager.get("logout", color=IconManager.COLOR_DANGER))
        self.logout_btn.setIconSize(QSize(18, 18))
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(self.logout_btn)
        return wrap

    def _build_version(self):
        wrap = QFrame()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 10)
        ver = QLabel(f"نسخه  {APP_VERSION}")
        ver.setObjectName("sidebarVersion")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)
        return wrap

    def set_user_info(self, name, role):
        self.user_name_label.setText(name)
        self.user_role_label.setText(role)

    def _on_section_toggle(self, section):
        was_expanded = section.is_expanded()
        for sec in self._sections:
            sec.set_expanded(False)
        if not was_expanded:
            section.set_expanded(True)

    def _on_item_clicked(self, key):
        self.navigate_to(key)
        self.page_changed.emit(key)

    def navigate_to(self, key):
        for item in self._all_items:
            item.set_active(item.page_key == key)
        for sec in self._sections:
            sec.set_expanded(sec.has_page(key))

    def filter_by_role(self, role):
        for sec in self._admin_sections:
            sec.setVisible(role == UserRole.ADMIN)


class TopHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topHeader")
        self.setFixedHeight(58)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        self.page_title = QLabel("داشبورد")
        self.page_title.setObjectName("headerPageTitle")
        font = QFont(); font.setPointSize(15); font.setBold(True)
        self.page_title.setFont(font)
        layout.addWidget(self.page_title)
        layout.addStretch()
        self.user_label = QLabel()
        self.user_label.setObjectName("headerUserLabel")
        layout.addWidget(self.user_label)

    def set_page_title(self, title):
        self.page_title.setText(title)

    def set_user(self, full_name, role):
        self.user_label.setText(f"👤  {full_name}   |   {role}")


class MainWindow(QMainWindow):
    logout_requested = Signal()

    PAGE_TITLES = {
        "dashboard":        "داشبورد اصلی",
        "customers":        "مشتریان",
        "suppliers":        "تأمین‌کنندگان",
        "costs":            "انواع هزینه",
        "operations":       "عملیات ساخت",
        "departments":      "دپارتمان‌ها",
        "work_centers":     "مراکز کار",
        "machines":         "ماشین‌آلات",
        "device_templates": "تعریف دستگاه",
        "items":            "مدیریت اقلام",
        "bom":              "BOM — ساختار قطعات",
        "routing":          "مسیر ساخت",
        "projects":         "مدیریت پروژه",
        "purchases":        "تأمین و خرید",
        "profit":           "گزارش سود",
        "prj_report":       "گزارش وضعیت پروژه‌ها",
        "users":            "مدیریت کاربران",
        "lookups":          "مدیریت داده‌های پایه سیستم",
        "settings":         "تنظیمات",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{BRAND_NAME} — سیستم مدیریت ساخت دستگاه")
        mw, mh = Display.main_window_min()
        self.setMinimumSize(mw, mh)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setObjectName("mainWindow")
        self._pages = {}
        self._setup_ui()
        self._connect_signals()
        self._init_session()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.header = TopHeader()
        root.addWidget(self.header)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        self.sidebar = Sidebar()
        body.addWidget(self.sidebar)
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        body.addWidget(self.stack, stretch=1)
        root.addLayout(body, stretch=1)

    def _connect_signals(self):
        self.sidebar.page_changed.connect(self._navigate_to)
        self.sidebar.logout_clicked.connect(self._on_logout)

    def _init_session(self):
        user = AccessControl.get_current_user()
        if user:
            role_text = user.role.value if hasattr(user.role, "value") else str(user.role)
            self.header.set_user(user.full_name, role_text)
            self.sidebar.set_user_info(user.full_name, role_text)
            self.sidebar.filter_by_role(user.role)
        self._load_pages()
        self._navigate_to("dashboard")

    def _load_pages(self):
        from app.ui.dashboard.dashboard_page import DashboardPage
        from app.ui.users.user_list_page import UserListPage
        from app.ui.customers.customer_list_page import CustomerListPage
        from app.ui.suppliers.supplier_list_page import SupplierListPage
        from app.ui.cost_types.cost_type_list_page import CostTypeListPage
        from app.ui.lookups.lookup_management_page import LookupManagementPage
        from app.ui.operations.operation_list_page import OperationListPage
        from app.ui.departments.department_list_page import DepartmentListPage
        from app.ui.work_centers.work_center_list_page import WorkCenterListPage
        from app.ui.machines.machine_list_page import MachineListPage
        from app.ui.device_templates.device_template_list_page import DeviceTemplateListPage
        from app.ui.items.item_list_page import ItemListPage
        from app.ui.bom.bom_page import BOMPage
        from app.ui.routing.routing_page import RoutingPage
        from app.ui.projects.project_list_page import ProjectListPage

        self.register_page("dashboard",        DashboardPage())
        self.register_page("users",            UserListPage())
        self.register_page("customers",        CustomerListPage())
        self.register_page("suppliers",        SupplierListPage())
        self.register_page("costs",            CostTypeListPage())
        self.register_page("lookups",          LookupManagementPage())
        self.register_page("operations",       OperationListPage())
        self.register_page("departments",      DepartmentListPage())
        self.register_page("work_centers",     WorkCenterListPage())
        self.register_page("machines",         MachineListPage())
        self.register_page("device_templates", DeviceTemplateListPage())
        self.register_page("items",            ItemListPage())
        self.register_page("bom",              BOMPage())
        self.register_page("routing",          RoutingPage())
        self.register_page("projects",         ProjectListPage())

        for key, title in self.PAGE_TITLES.items():
            if key in self._pages:
                continue
            self.register_page(key, self._make_placeholder(key, title))

    def _make_placeholder(self, key, title):
        w = QWidget()
        w.setObjectName("placeholderPage")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("🚧")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(64)
        icon.setFont(f)
        layout.addWidget(icon)
        lbl = QLabel(f"صفحه «{title}»")
        lbl.setObjectName("placeholderTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f2 = QFont(); f2.setPointSize(22); f2.setBold(True)
        lbl.setFont(f2)
        layout.addWidget(lbl)
        sub = QLabel("این صفحه هنوز پیاده‌سازی نشده است")
        sub.setObjectName("placeholderSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)
        return w

    def register_page(self, key, widget):
        self._pages[key] = widget
        self.stack.addWidget(widget)

    def _navigate_to(self, key):
        if key not in self._pages:
            logger.warning(f"صفحه '{key}' یافت نشد")
            return
        page = self._pages[key]
        self.stack.setCurrentWidget(page)
        self.sidebar.navigate_to(key)
        self.header.set_page_title(self.PAGE_TITLES.get(key, key))
        if hasattr(page, "refresh") and callable(getattr(page, "refresh")):
            try:
                page.refresh()
            except Exception as e:
                logger.error(f"خطا در refresh صفحه '{key}': {e}", exc_info=True)
        logger.info(f"ناوبری به: {key}")

    def _on_logout(self):
        from app.services.auth_service import AuthService
        try:
            AuthService().logout()
            logger.info("خروج موفق از سیستم")
        except Exception as e:
            logger.error(f"خطا در خروج: {e}", exc_info=True)
        finally:
            self.logout_requested.emit()
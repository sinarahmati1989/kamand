"""
MainWindow — پنجره اصلی کمند
Sidebar با اکاردئون هوشمند + Header + Content Stack
"""
import logging
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QFrame, QLabel,
    QPushButton, QStackedWidget, QScrollArea,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.core.access_control import AccessControl
from app.enums.roles import UserRole
from app.constants import BRAND_NAME, APP_VERSION
from app.config.display import Display

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# اجزای Sidebar
# ══════════════════════════════════════════════════════════════

class SidebarItem(QPushButton):
    """آیتم داخل یک بخش (فرزند)"""

    def __init__(self, icon: str, label: str, page_key: str, parent=None):
        super().__init__(parent)
        self.page_key = page_key
        self.setText(f"    {icon}   {label}")
        self.setObjectName("sidebarItem")
        self.setFixedHeight(40)
        self.setCheckable(True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

    def set_active(self, active: bool):
        self.setChecked(active)
        self.setObjectName("sidebarItemActive" if active else "sidebarItem")
        self.style().unpolish(self)
        self.style().polish(self)


class SidebarSection(QWidget):
    """بخش اکاردئون — عنوان قابل کلیک + آیتم‌های داخلی"""

    section_clicked = Signal(object)

    def __init__(self, icon: str, title: str, section_key: str, parent=None):
        super().__init__(parent)
        self.section_key = section_key
        self._items: list[SidebarItem] = []
        self._is_expanded = False

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui(icon, title)

    def _setup_ui(self, icon: str, title: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.header_btn = QPushButton()
        self.header_btn.setObjectName("sidebarSectionHeader")
        self.header_btn.setFixedHeight(44)
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._update_header_text(icon, title)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.header_btn.setFont(font)

        self.header_btn.clicked.connect(lambda: self.section_clicked.emit(self))
        layout.addWidget(self.header_btn)

        self.items_container = QWidget()
        self.items_container.setObjectName("sidebarSectionItems")
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 2, 0, 6)
        self.items_layout.setSpacing(2)
        layout.addWidget(self.items_container)

        self._icon = icon
        self._title = title
        self.items_container.setVisible(False)

    def _update_header_text(self, icon: str, title: str):
        arrow = "▼" if self._is_expanded else "◀"
        self.header_btn.setText(f"  {icon}   {title}      {arrow}")

    def add_item(self, item: SidebarItem):
        self._items.append(item)
        self.items_layout.addWidget(item)

    def get_items(self) -> list[SidebarItem]:
        return self._items

    def has_page(self, page_key: str) -> bool:
        return any(item.page_key == page_key for item in self._items)

    def set_expanded(self, expanded: bool):
        self._is_expanded = expanded
        self.items_container.setVisible(expanded)
        self._update_header_text(self._icon, self._title)

        obj_name = "sidebarSectionHeaderActive" if expanded else "sidebarSectionHeader"
        self.header_btn.setObjectName(obj_name)
        self.header_btn.style().unpolish(self.header_btn)
        self.header_btn.style().polish(self.header_btn)

    def is_expanded(self) -> bool:
        return self._is_expanded


# ══════════════════════════════════════════════════════════════
# Sidebar اصلی
# ══════════════════════════════════════════════════════════════

class Sidebar(QFrame):
    """سایدبار اصلی با اکاردئون"""

    page_changed = Signal(str)

    STRUCTURE = [
        ("item", "📊", "داشبورد اصلی", "dashboard", False),

        ("section", "base_data", "📦", "داده‌های پایه", False, [
            ("👥", "مشتریان",        "customers"),
            ("🏭", "تأمین‌کنندگان",  "suppliers"),
            ("💰", "انواع هزینه",    "costs"),
            ("🔨", "عملیات ساخت",    "operations"),
            ("🏢", "دپارتمان‌ها",    "departments"),
            ("🔧", "مراکز کار",      "work_centers"),
            ("🤖", "ماشین‌آلات",     "machines"),
        ]),

        ("section", "engineering_group", "🔩", "مهندسی دستگاه", False, [
            ("📐", "قالب‌های دستگاه",  "device_templates"),
            ("📦", "کتابخانه اقلام",   "items"),
            ("📋", "BOM",              "bom"),
            ("🔀", "مسیر ساخت",       "routing"),
        ]),

        ("section", "operations_group", "⚙️", "عملیات", False, [
            ("📋", "مدیریت پروژه",  "projects"),
            ("🛒", "تأمین و خرید",  "purchases"),
        ]),

        ("section", "reports_group", "📈", "گزارش‌ها", False, [
            ("📈", "گزارش سود",       "profit"),
            ("📊", "گزارش پروژه‌ها",  "prj_report"),
        ]),

        ("section", "system_group", "🔒", "سیستم", True, [
            ("👥", "کاربران",              "users"),
            ("🗂️", "داده‌های پایه سیستم", "lookups"),
            ("⚙️", "تنظیمات",              "settings"),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(Display.sidebar_width())
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self._all_items: list[SidebarItem] = []
        self._sections: list[SidebarSection] = []
        self._admin_sections: list[SidebarSection] = []

        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_brand())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("sidebarScroll")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        menu = QWidget()
        menu.setObjectName("sidebarMenu")
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(8, 8, 8, 8)
        menu_layout.setSpacing(4)

        for entry in self.STRUCTURE:
            if entry[0] == "item":
                _, icon, label, key, admin_only = entry
                item = SidebarItem(icon, label, key)
                item.clicked.connect(
                    lambda checked=False, k=key: self._on_item_clicked(k)
                )
                self._all_items.append(item)
                menu_layout.addWidget(item)

            elif entry[0] == "section":
                _, sec_key, icon, title, admin_only, sub_items = entry
                section = SidebarSection(icon, title, sec_key)
                section.section_clicked.connect(self._on_section_toggle)

                for si_icon, si_label, si_key in sub_items:
                    item = SidebarItem(si_icon, si_label, si_key)
                    item.clicked.connect(
                        lambda checked=False, k=si_key: self._on_item_clicked(k)
                    )
                    section.add_item(item)
                    self._all_items.append(item)

                self._sections.append(section)
                if admin_only:
                    self._admin_sections.append(section)

                menu_layout.addWidget(section)

        menu_layout.addStretch()
        scroll.setWidget(menu)
        outer.addWidget(scroll, stretch=1)
        outer.addWidget(self._build_logout())

    def _build_brand(self) -> QFrame:
        brand = QFrame()
        brand.setObjectName("sidebarBrand")
        brand.setFixedHeight(90)

        layout = QVBoxLayout(brand)
        layout.setContentsMargins(10, 14, 10, 10)
        layout.setSpacing(0)

        logo = QLabel(f"🏭  {BRAND_NAME}")
        logo.setObjectName("sidebarLogo")
        font = QFont()
        font.setPointSize(17)
        font.setBold(True)
        logo.setFont(font)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        ver = QLabel(f"نسخه  {APP_VERSION}")
        ver.setObjectName("sidebarVersion")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

        return brand

    def _build_logout(self) -> QFrame:
        wrap = QFrame()
        wrap.setObjectName("sidebarLogoutWrap")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(10, 8, 10, 12)

        self.logout_btn = QPushButton("  🚪   خروج از سیستم")
        self.logout_btn.setObjectName("sidebarLogout")
        self.logout_btn.setFixedHeight(42)
        self.logout_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.logout_btn)

        return wrap

    def _on_section_toggle(self, section: SidebarSection):
        was_expanded = section.is_expanded()
        for sec in self._sections:
            sec.set_expanded(False)
        if not was_expanded:
            section.set_expanded(True)

    def _on_item_clicked(self, key: str):
        self.navigate_to(key)
        self.page_changed.emit(key)

    def navigate_to(self, key: str):
        for item in self._all_items:
            item.set_active(item.page_key == key)
        for sec in self._sections:
            if sec.has_page(key):
                sec.set_expanded(True)
            else:
                sec.set_expanded(False)

    def filter_by_role(self, role):
        for sec in self._admin_sections:
            sec.setVisible(role == UserRole.ADMIN)


# ══════════════════════════════════════════════════════════════
# Top Header
# ══════════════════════════════════════════════════════════════

class TopHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topHeader")
        self.setFixedHeight(58)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        self.page_title = QLabel("داشبورد")
        self.page_title.setObjectName("headerPageTitle")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.page_title.setFont(font)
        layout.addWidget(self.page_title)

        layout.addStretch()

        self.user_label = QLabel()
        self.user_label.setObjectName("headerUserLabel")
        layout.addWidget(self.user_label)

    def set_page_title(self, title: str):
        self.page_title.setText(title)

    def set_user(self, full_name: str, role: str):
        self.user_label.setText(f"👤  {full_name}   |   {role}")


# ══════════════════════════════════════════════════════════════
# MainWindow اصلی
# ══════════════════════════════════════════════════════════════

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
        # مهندسی دستگاه
        "device_templates": "قالب‌های دستگاه",
        "items":            "کتابخانه اقلام",
        "bom":              "BOM — ساختار قطعات",
        "routing":          "مسیر ساخت",
        # عملیات
        "projects":         "مدیریت پروژه",
        "purchases":        "تأمین و خرید",
        # گزارش
        "profit":           "گزارش سود",
        "prj_report":       "گزارش وضعیت پروژه‌ها",
        # سیستم
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

        self._pages: dict[str, QWidget] = {}

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
        self.sidebar.logout_btn.clicked.connect(self._on_logout)

    def _init_session(self):
        user = AccessControl.get_current_user()
        if user:
            role_text = (
                user.role.value if hasattr(user.role, "value") else str(user.role)
            )
            self.header.set_user(user.full_name, role_text)
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

        for key, title in self.PAGE_TITLES.items():
            if key in self._pages:
                continue
            self.register_page(key, self._make_placeholder(key, title))

    def _make_placeholder(self, key: str, title: str) -> QWidget:
        w = QWidget()
        w.setObjectName("placeholderPage")

        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🚧")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(64)
        icon.setFont(f)
        layout.addWidget(icon)

        lbl = QLabel(f"صفحه «{title}»")
        lbl.setObjectName("placeholderTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f2 = QFont()
        f2.setPointSize(22)
        f2.setBold(True)
        lbl.setFont(f2)
        layout.addWidget(lbl)

        sub = QLabel("این صفحه به زودی پیاده‌سازی خواهد شد")
        sub.setObjectName("placeholderSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        return w

    def register_page(self, key: str, widget: QWidget):
        self._pages[key] = widget
        self.stack.addWidget(widget)

    def _navigate_to(self, key: str):
        if key not in self._pages:
            logger.warning(f"صفحه '{key}' یافت نشد")
            return
        self.stack.setCurrentWidget(self._pages[key])
        self.sidebar.navigate_to(key)
        self.header.set_page_title(self.PAGE_TITLES.get(key, key))
        logger.info(f"ناوبری به: {key}")

    def _on_logout(self):
        from app.services.auth_service import AuthService
        try:
            AuthService().logout()
            logger.info("خروج موفق از سیستم")
        except Exception as e:
            logger.error(f"خطا در خروج: {e}")
        finally:
            self.logout_requested.emit()
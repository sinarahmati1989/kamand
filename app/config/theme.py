"""
Aurora Glass Light Theme
رنگ‌ها، فونت‌ها، سایز‌ها
"""


class Colors:
    """پالت رنگی Aurora"""
    
    # ══════════ Primary ══════════
    INDIGO = "#6366F1"
    VIOLET = "#8B5CF6"
    PINK = "#EC4899"
    BLUE = "#3B82F6"
    
    # ══════════ Gradient Backgrounds ══════════
    BG_1 = "#E0E7FF"   # Indigo روشن
    BG_2 = "#EDE9FE"   # Violet روشن
    BG_3 = "#FCE7F3"   # Pink روشن
    BG_4 = "#DBEAFE"   # Blue روشن
    
    # ══════════ Glass ══════════
    GLASS_WHITE = "rgba(255, 255, 255, 0.7)"
    GLASS_LIGHT = "rgba(255, 255, 255, 0.5)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.4)"
    
    # ══════════ Text ══════════
    TEXT_PRIMARY = "#1E293B"      # اصلی
    TEXT_SECONDARY = "#64748B"    # ثانویه
    TEXT_MUTED = "#94A3B8"        # کم‌رنگ
    TEXT_ON_PRIMARY = "#FFFFFF"   # روی رنگ اصلی
    
    # ══════════ Status ══════════
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"
    INFO = "#3B82F6"
    
    # ══════════ Border ══════════
    BORDER_LIGHT = "#E2E8F0"
    BORDER_FOCUS = "#6366F1"
    
    # ══════════ Shadow ══════════
    SHADOW_INDIGO = "rgba(99, 102, 241, 0.3)"
    SHADOW_VIOLET = "rgba(139, 92, 246, 0.3)"
    SHADOW_PINK = "rgba(236, 72, 153, 0.3)"


class Fonts:
    """فونت‌ها"""
    
    FA_BODY = "B Nazanin"
    FA_TITLE = "B Titr"
    EN_BODY = "Segoe UI"
    EN_TITLE = "Poppins"
    
    SIZE_XS = 10
    SIZE_SM = 12
    SIZE_BASE = 14
    SIZE_LG = 16
    SIZE_XL = 20
    SIZE_2XL = 24
    SIZE_3XL = 32


class Sizes:
    """سایز‌های استاندارد"""
    
    # Radius
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 16
    RADIUS_XL = 20
    
    # Padding
    PAD_SM = 8
    PAD_MD = 16
    PAD_LG = 24
    
    # Heights
    INPUT_HEIGHT = 44
    BUTTON_HEIGHT = 44
    HEADER_HEIGHT = 64
    SIDEBAR_WIDTH = 240
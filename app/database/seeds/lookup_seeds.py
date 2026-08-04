"""
Seed کردن داده‌های اولیه Lookup — با کدهای انگلیسی استاندارد
"""
import logging
from app.database.session import get_session
from app.services.lookup_service import LookupService

logger = logging.getLogger(__name__)


LOOKUP_SEEDS = {

    "supplier_type": [
        {"code": "raw_material", "label": "مواد اولیه",       "sort": 10},
        {"code": "parts",        "label": "قطعات",            "sort": 20},
        {"code": "services",     "label": "خدمات",            "sort": 30},
        {"code": "contractor",   "label": "پیمانکار",         "sort": 40},
        {"code": "packaging",    "label": "بسته‌بندی",        "sort": 50},
        {"code": "tools",        "label": "ابزار و تجهیزات",  "sort": 60},
    ],

    "supplier_tier": [
        {"code": "a", "label": "A - استراتژیک", "sort": 10},
        {"code": "b", "label": "B - معمولی",    "sort": 20},
        {"code": "c", "label": "C - جایگزین",   "sort": 30},
    ],

    "payment_terms": [
        {"code": "cash",        "label": "نقدی",     "sort": 10},
        {"code": "check",       "label": "چک",       "sort": 20},
        {"code": "credit",      "label": "اعتباری",  "sort": 30},
        {"code": "installment", "label": "مدت‌دار",  "sort": 40},
    ],

    "currency": [
        {"code": "irr", "label": "ریال", "sort": 10, "en": "IRR"},
        {"code": "usd", "label": "دلار", "sort": 20, "en": "USD"},
        {"code": "eur", "label": "یورو", "sort": 30, "en": "EUR"},
    ],

    "cost_category": [
        {"code": "direct",   "label": "مستقیم",     "sort": 10},
        {"code": "indirect", "label": "غیرمستقیم",  "sort": 20},
        {"code": "fixed",    "label": "ثابت",       "sort": 30},
        {"code": "variable", "label": "متغیر",      "sort": 40},
    ],

    "cost_behavior": [
        {"code": "fixed",         "label": "ثابت",        "sort": 10},
        {"code": "variable",      "label": "متغیر",       "sort": 20},
        {"code": "semi_variable", "label": "نیمه‌متغیر",  "sort": 30},
        {"code": "step",          "label": "پلکانی",      "sort": 40},
    ],

    "cost_unit": [
        {"code": "rial",    "label": "ریال",  "sort": 10},
        {"code": "dollar",  "label": "دلار",  "sort": 20},
        {"code": "euro",    "label": "یورو",  "sort": 30},
        {"code": "percent", "label": "درصد",  "sort": 40},
        {"code": "hour",    "label": "ساعت",  "sort": 50},
        {"code": "unit",    "label": "عدد",   "sort": 60},
    ],

    "allocation_method": [
        {"code": "direct",         "label": "مستقیم",         "sort": 10},
        {"code": "machine_hour",   "label": "ساعت ماشین",     "sort": 20},
        {"code": "labor_hour",     "label": "ساعت نیروی کار", "sort": 30},
        {"code": "production_qty", "label": "تعداد تولید",    "sort": 40},
        {"code": "area",           "label": "متراژ",          "sort": 50},
        {"code": "manual",         "label": "دستی",           "sort": 60},
    ],

    "customer_type": [
        {"code": "real",  "label": "حقیقی",  "sort": 10},
        {"code": "legal", "label": "حقوقی",  "sort": 20},
    ],

    "operation_type": [
        {"code": "machining",         "label": "ماشین‌کاری",          "sort": 10},
        {"code": "turning",           "label": "تراشکاری",            "sort": 20},
        {"code": "milling",           "label": "فرزکاری",             "sort": 30},
        {"code": "drilling",          "label": "سوراخکاری",           "sort": 40},
        {"code": "grinding",          "label": "سنگ‌زنی",             "sort": 50},
        {"code": "cnc",               "label": "CNC",                 "sort": 60},
        {"code": "cutting",           "label": "برش",                 "sort": 70},
        {"code": "welding",           "label": "جوشکاری",             "sort": 80},
        {"code": "assembly",          "label": "مونتاژ",              "sort": 90},
        {"code": "painting",          "label": "رنگ‌کاری",            "sort": 100},
        {"code": "surface_treatment", "label": "آبکاری/عملیات سطحی",  "sort": 110},
        {"code": "heat_treatment",    "label": "عملیات حرارتی",       "sort": 120},
        {"code": "testing",           "label": "تست و کنترل کیفیت",   "sort": 130},
        {"code": "packaging",         "label": "بسته‌بندی",           "sort": 140},
        {"code": "other",             "label": "سایر",                "sort": 999},
    ],

    "skill_level": [
        {"code": "level_1", "label": "سطح ۱ - مبتدی",     "sort": 10},
        {"code": "level_2", "label": "سطح ۲ - نیمه‌ماهر", "sort": 20},
        {"code": "level_3", "label": "سطح ۳ - ماهر",      "sort": 30},
        {"code": "level_4", "label": "سطح ۴ - پیشرفته",   "sort": 40},
        {"code": "level_5", "label": "سطح ۵ - متخصص",     "sort": 50},
    ],

    "time_unit": [
        {"code": "second", "label": "ثانیه", "sort": 10},
        {"code": "minute", "label": "دقیقه", "sort": 20},
        {"code": "hour",   "label": "ساعت",  "sort": 30},
    ],

    "department_type": [
        {"code": "production",  "label": "تولید",             "sort": 10},
        {"code": "quality",     "label": "کنترل کیفیت",       "sort": 20},
        {"code": "maintenance", "label": "تعمیر و نگهداری",   "sort": 30},
        {"code": "warehouse",   "label": "انبار",             "sort": 40},
        {"code": "engineering", "label": "مهندسی و طراحی",    "sort": 50},
        {"code": "procurement", "label": "خرید و تأمین",      "sort": 60},
        {"code": "admin",       "label": "اداری و پشتیبانی",  "sort": 70},
        {"code": "it",          "label": "فناوری اطلاعات",    "sort": 80},
        {"code": "other",       "label": "سایر",              "sort": 999},
    ],

    "work_center_type": [
        {"code": "machining",  "label": "ماشین‌کاری",   "sort": 10},
        {"code": "assembly",   "label": "مونتاژ",        "sort": 20},
        {"code": "welding",    "label": "جوشکاری",       "sort": 30},
        {"code": "painting",   "label": "رنگ‌کاری",      "sort": 40},
        {"code": "testing",    "label": "تست و بازرسی",  "sort": 50},
        {"code": "packaging",  "label": "بسته‌بندی",     "sort": 60},
        {"code": "warehouse",  "label": "انبار",         "sort": 70},
        {"code": "other",      "label": "سایر",          "sort": 999},
    ],

    "machine_type": [
        {"code": "cnc_lathe",    "label": "تراش CNC",        "sort": 10},
        {"code": "cnc_mill",     "label": "فرز CNC",         "sort": 20},
        {"code": "cnc_drill",    "label": "دریل CNC",        "sort": 30},
        {"code": "manual_lathe", "label": "تراش دستی",       "sort": 40},
        {"code": "manual_mill",  "label": "فرز دستی",        "sort": 50},
        {"code": "grinder",      "label": "سنگ‌زنی",         "sort": 60},
        {"code": "press",        "label": "پرس",             "sort": 70},
        {"code": "welder",       "label": "دستگاه جوش",      "sort": 80},
        {"code": "laser",        "label": "لیزر برش",        "sort": 90},
        {"code": "plasma",       "label": "پلاسما برش",      "sort": 100},
        {"code": "3d_printer",   "label": "پرینتر سه‌بعدی",  "sort": 110},
        {"code": "conveyor",     "label": "نقاله",           "sort": 120},
        {"code": "compressor",   "label": "کمپرسور",         "sort": 130},
        {"code": "other",        "label": "سایر",            "sort": 999},
    ],

    # ─── مهندسی دستگاه ─── 🆕
    "device_template_type": [
        {"code": "hydraulic",    "label": "هیدرولیک",           "sort": 10},
        {"code": "pneumatic",    "label": "پنوماتیک",           "sort": 20},
        {"code": "mechanical",   "label": "مکانیکی",            "sort": 30},
        {"code": "electrical",   "label": "الکتریکی",           "sort": 40},
        {"code": "electromech",  "label": "الکترومکانیکی",      "sort": 50},
        {"code": "valve",        "label": "شیرآلات",            "sort": 60},
        {"code": "gearbox",      "label": "گیربکس",             "sort": 70},
        {"code": "actuator",     "label": "اکچویتور",           "sort": 80},
        {"code": "pump",         "label": "پمپ",                "sort": 90},
        {"code": "custom",       "label": "سفارشی",             "sort": 100},
        {"code": "other",        "label": "سایر",               "sort": 999},
    ],

    "item_type": [
        {"code": "raw_material",     "label": "ماده اولیه",          "sort": 10},
        {"code": "purchased_part",   "label": "قطعه خریدنی",         "sort": 20},
        {"code": "manufactured_part","label": "قطعه ساختنی",         "sort": 30},
        {"code": "assembly",         "label": "مجموعه/اسمبلی",       "sort": 40},
        {"code": "consumable",       "label": "مصرفی",               "sort": 50},
        {"code": "semi_finished",    "label": "نیمه‌ساخته",          "sort": 60},
        {"code": "finished_good",    "label": "محصول نهایی",         "sort": 70},
        {"code": "tool",             "label": "ابزار",               "sort": 80},
        {"code": "other",            "label": "سایر",                "sort": 999},
    ],

    "uom": [
        {"code": "pcs",  "label": "عدد",        "sort": 10,  "en": "PCS"},
        {"code": "set",  "label": "ست",         "sort": 20,  "en": "SET"},
        {"code": "kg",   "label": "کیلوگرم",    "sort": 30,  "en": "KG"},
        {"code": "gr",   "label": "گرم",        "sort": 40,  "en": "GR"},
        {"code": "ton",  "label": "تن",         "sort": 50,  "en": "TON"},
        {"code": "m",    "label": "متر",        "sort": 60,  "en": "M"},
        {"code": "cm",   "label": "سانتی‌متر",  "sort": 70,  "en": "CM"},
        {"code": "mm",   "label": "میلی‌متر",   "sort": 80,  "en": "MM"},
        {"code": "m2",   "label": "متر مربع",   "sort": 90,  "en": "M2"},
        {"code": "m3",   "label": "متر مکعب",   "sort": 100, "en": "M3"},
        {"code": "liter","label": "لیتر",       "sort": 110, "en": "LTR"},
        {"code": "hour", "label": "ساعت",       "sort": 120, "en": "HR"},
        {"code": "day",  "label": "روز",        "sort": 130, "en": "DAY"},
        {"code": "lot",  "label": "لات",        "sort": 140, "en": "LOT"},
    ],

    # ─── پروژه ─── 🆕
    "project_type": [
        {"code": "new_device",    "label": "ساخت دستگاه جدید",     "sort": 10},
        {"code": "repeat",        "label": "تکرار تولید",           "sort": 20},
        {"code": "overhaul",      "label": "تعمیرات اساسی",         "sort": 30},
        {"code": "customization", "label": "سفارشی‌سازی محصول",     "sort": 40},
        {"code": "prototype",     "label": "نمونه‌سازی",            "sort": 50},
        {"code": "other",         "label": "سایر",                  "sort": 999},
    ],
        # ─── مشخصات فنی اقلام ─── 🆕
    "material_grade": [
        {"code": "st37",   "label": "ST37 (فولاد ساختمانی)",    "sort": 10},
        {"code": "st52",   "label": "ST52 (فولاد ساختمانی)",    "sort": 20},
        {"code": "ck45",   "label": "CK45 (فولاد کربنی)",       "sort": 30},
        {"code": "mo40",   "label": "MO40 (فولاد آلیاژی)",      "sort": 40},
        {"code": "ss304",  "label": "SS304 (استیل ضدزنگ)",      "sort": 50},
        {"code": "ss316",  "label": "SS316 (استیل ضدزنگ)",      "sort": 60},
        {"code": "al6061", "label": "Al6061 (آلومینیوم)",        "sort": 70},
        {"code": "al7075", "label": "Al7075 (آلومینیوم)",        "sort": 80},
        {"code": "brass",  "label": "برنج",                      "sort": 90},
        {"code": "copper", "label": "مس",                        "sort": 100},
        {"code": "cast_iron","label": "چدن",                     "sort": 110},
        {"code": "nylon",  "label": "نایلون",                    "sort": 120},
        {"code": "teflon", "label": "تفلون (PTFE)",              "sort": 130},
        {"code": "rubber", "label": "لاستیک/الاستومر",           "sort": 140},
        {"code": "other",  "label": "سایر",                      "sort": 999},
    ],

    "surface_treatment": [
        {"code": "galvanize",      "label": "گالوانیزه",                "sort": 10},
        {"code": "zinc_plating",   "label": "آبکاری روی",               "sort": 20},
        {"code": "nickel_plating", "label": "آبکاری نیکل",              "sort": 30},
        {"code": "chrome_plating", "label": "آبکاری کروم",              "sort": 40},
        {"code": "anodize",        "label": "آنودایز",                  "sort": 50},
        {"code": "phosphate",      "label": "فسفاته",                   "sort": 60},
        {"code": "powder_coat",    "label": "رنگ پودری (الکترواستاتیک)", "sort": 70},
        {"code": "epoxy_paint",    "label": "رنگ اپوکسی",               "sort": 80},
        {"code": "black_oxide",    "label": "اکسید سیاه",               "sort": 90},
        {"code": "passivation",    "label": "پسیواسیون",                "sort": 100},
        {"code": "heat_treat",     "label": "عملیات حرارتی",            "sort": 110},
        {"code": "sandblast",      "label": "سندبلاست",                 "sort": 120},
        {"code": "none",           "label": "بدون پوشش",                "sort": 130},
        {"code": "other",          "label": "سایر",                     "sort": 999},
    ],

    "item_manufacturer": [
        {"code": "skf",        "label": "SKF",                "sort": 10},
        {"code": "fag",        "label": "FAG",                "sort": 20},
        {"code": "nsk",        "label": "NSK",                "sort": 30},
        {"code": "bosch",      "label": "Bosch",              "sort": 40},
        {"code": "siemens",    "label": "Siemens",            "sort": 50},
        {"code": "schneider",  "label": "Schneider Electric", "sort": 60},
        {"code": "abb",        "label": "ABB",                "sort": 70},
        {"code": "festo",      "label": "Festo",              "sort": 80},
        {"code": "smc",        "label": "SMC",                "sort": 90},
        {"code": "parker",     "label": "Parker",             "sort": 100},
        {"code": "rexroth",    "label": "Bosch Rexroth",      "sort": 110},
        {"code": "danfoss",    "label": "Danfoss",            "sort": 120},
        {"code": "omron",      "label": "Omron",              "sort": 130},
        {"code": "mitsubishi", "label": "Mitsubishi",         "sort": 140},
        {"code": "domestic",   "label": "تولید داخلی",         "sort": 150},
        {"code": "other",      "label": "سایر",               "sort": 999},
    ],
}


# ══════════════════════════════════════════════════════════════════
# زیرشاخه‌های تأمین‌کننده
# ══════════════════════════════════════════════════════════════════

SUPPLIER_SUBCATEGORIES = {

    "raw_material": [
        ("metals",        "فلزات (فولاد، آلومینیوم، مس)"),
        ("plastic",       "پلاستیک و پلیمر"),
        ("wood",          "چوب"),
        ("glass",         "شیشه"),
        ("ceramic",       "سرامیک"),
        ("rubber",        "لاستیک"),
        ("paint_coating", "رنگ و پوشش"),
        ("adhesive",      "چسب و مواد شیمیایی"),
        ("paper",         "کاغذ و مقوا"),
        ("textile",       "منسوجات"),
    ],

    "parts": [
        ("electronic",    "الکترونیکی"),
        ("mechanical",    "مکانیکی"),
        ("hydraulic",     "هیدرولیک و پنوماتیک"),
        ("fasteners",     "اتصالات (پیچ، مهره، واشر)"),
        ("bearings",      "یاتاقان و بلبرینگ"),
        ("motor_gearbox", "موتور و گیربکس"),
        ("valves",        "شیرآلات"),
        ("sensors",       "سنسور و اندازه‌گیری"),
        ("cables",        "کابل و سیم"),
        ("plastic_parts", "قطعات پلاستیکی"),
    ],

    "services": [
        ("cutting_srv",     "برشکاری (لیزر، پلاسما، آب)"),
        ("welding_srv",     "جوشکاری"),
        ("machining_srv",   "ماشین‌کاری (تراش، فرز، CNC)"),
        ("painting_srv",    "رنگ‌آمیزی"),
        ("plating_srv",     "آبکاری و گالوانیزه"),
        ("heat_srv",        "کوره و عملیات حرارتی"),
        ("transport_srv",   "حمل و نقل"),
        ("engineering_srv", "خدمات مهندسی و طراحی"),
        ("qc_srv",          "بازرسی فنی و کنترل کیفی"),
        ("it_srv",          "خدمات IT و شبکه"),
    ],

    "contractor": [
        ("installation",  "نصب و راه‌اندازی"),
        ("maintenance",   "تعمیر و نگهداری"),
        ("mold_making",   "ساخت قالب و ابزار"),
        ("design",        "طراحی مهندسی"),
        ("construction",  "ساخت و ساز"),
        ("electrical",    "برق صنعتی"),
        ("mechanical_ct", "تأسیسات مکانیکی"),
        ("automation",    "اتوماسیون صنعتی"),
    ],

    "packaging": [
        ("carton",        "کارتن و جعبه"),
        ("nylon_plastic", "نایلون و پلاستیک"),
        ("wooden_pack",   "چوبی (پالت، جعبه)"),
        ("metal_pack",    "فلزی"),
        ("shrink",        "شیرینک و استرچ"),
        ("label",         "برچسب و لیبل"),
        ("foam",          "فوم و ضربه‌گیر"),
    ],

    "tools": [
        ("hand_tools",  "ابزار دستی"),
        ("power_tools", "ابزار برقی"),
        ("machinery",   "ماشین‌آلات صنعتی"),
        ("measurement", "تجهیزات اندازه‌گیری"),
        ("safety",      "لوازم ایمنی"),
        ("lab",         "تجهیزات آزمایشگاهی"),
        ("consumables", "لوازم مصرفی کارگاه"),
    ],
}


# ══════════════════════════════════════════════════════════════════
# Seed Function
# ══════════════════════════════════════════════════════════════════

def seed_lookups(force: bool = False):
    """Seed داده‌های اولیه Lookup"""
    logger.info("🌱 شروع Seed کردن Lookup ها...")

    added_count = 0
    skipped_count = 0

    with get_session() as session:
        svc = LookupService(session)

        # ═══ 1. سطح اول ═══
        for category, items in LOOKUP_SEEDS.items():
            for item in items:
                try:
                    existing = svc.repo.get_by_category_code(
                        category, item["code"]
                    )
                    if existing and not force:
                        skipped_count += 1
                        continue

                    svc.seed_if_not_exists(
                        category=category,
                        code=item["code"],
                        label_fa=item["label"],
                        label_en=item.get("en"),
                        sort_order=item.get("sort", 0),
                    )
                    added_count += 1
                except Exception as e:
                    logger.error(
                        f"خطا در seed {category}/{item['code']}: {e}"
                    )

        # ═══ 2. زیرشاخه‌های تأمین‌کننده ═══
        for parent_code, subcategories in SUPPLIER_SUBCATEGORIES.items():
            parent = svc.repo.get_by_category_code(
                "supplier_type", parent_code
            )
            if not parent:
                logger.warning(f"والد '{parent_code}' یافت نشد!")
                continue

            for idx, (sub_code, sub_label) in enumerate(subcategories):
                try:
                    existing = svc.repo.get_by_category_code(
                        "supplier_subcategory", sub_code
                    )
                    if existing and not force:
                        skipped_count += 1
                        continue

                    svc.seed_if_not_exists(
                        category="supplier_subcategory",
                        code=sub_code,
                        label_fa=sub_label,
                        parent_id=parent.id,
                        sort_order=(idx + 1) * 10,
                    )
                    added_count += 1
                except Exception as e:
                    logger.error(
                        f"خطا در seed subcategory '{sub_label}': {e}"
                    )

    logger.info(
        f"✅ Seed تمام شد. اضافه: {added_count}, رد شده: {skipped_count}"
    )
    return added_count, skipped_count


if __name__ == "__main__":
    from app.config.logging_config import setup_logging
    setup_logging()
    added, skipped = seed_lookups()
    print(f"\n✅ اضافه شده: {added}")
    print(f"⏭️  رد شده: {skipped}")
"""
Seed کردن جزئیات تخصصی (Level 3) — با کدهای انگلیسی صحیح
"""
import logging
from app.database.session import get_session
from app.services.lookup_service import LookupService

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# جزئیات تخصصی — به تفکیک زیرشاخه (کد Level 2)
# ساختار: parent_code → [(code, label), ...]
# ══════════════════════════════════════════════════════════════════

SPECIALIZATIONS = {

    # ══ مواد اولیه → فلزات ══
    "metals": [
        ("steel_304",    "استیل 304"),
        ("steel_316",    "استیل 316"),
        ("steel_321",    "استیل 321"),
        ("steel_430",    "استیل 430"),
        ("iron_st37",    "آهن ST37"),
        ("iron_st52",    "آهن ST52"),
        ("alu_6061",     "آلومینیوم 6061"),
        ("alu_7075",     "آلومینیوم 7075"),
        ("alu_5052",     "آلومینیوم 5052"),
        ("copper_pure",  "مس خالص"),
        ("brass",        "برنج"),
        ("bronze",       "برنز"),
    ],

    # ══ مواد اولیه → پلاستیک و پلیمر ══
    "plastic": [
        ("pvc",          "PVC"),
        ("abs",          "ABS"),
        ("pp",           "PP (پلی پروپیلن)"),
        ("pe",           "PE (پلی اتیلن)"),
        ("pet",          "PET"),
        ("pmma",         "PMMA (پلکسی گلاس)"),
        ("polycarb",     "پلی کربنات"),
        ("nylon",        "نایلون"),
        ("teflon",       "تفلون"),
    ],

    # ══ مواد اولیه → لاستیک ══
    "rubber": [
        ("natural_rub",  "لاستیک طبیعی"),
        ("silicone_rub", "لاستیک سیلیکون"),
        ("epdm",         "EPDM"),
        ("neoprene",     "نئوپرن"),
        ("nitrile",      "نیتریل"),
        ("butyl",        "بوتیل"),
    ],

    # ══ مواد اولیه → چوب ══
    "wood": [
        ("beech",    "چوب راش"),
        ("oak",      "چوب بلوط"),
        ("pine",     "چوب کاج"),
        ("mdf",      "MDF"),
        ("neopan",   "نئوپان"),
        ("plywood",  "پلی وود"),
    ],

    # ══ قطعات → الکترونیکی ══
    "electronic": [
        ("ic_mcu",       "IC و میکروکنترلر"),
        ("temp_sensor",  "سنسور دما"),
        ("pres_sensor",  "سنسور فشار"),
        ("hum_sensor",   "سنسور رطوبت"),
        ("led",          "LED"),
        ("relay_em",     "رله الکترومکانیکی"),
        ("transistor",   "ترانزیستور"),
        ("capacitor",    "خازن"),
        ("resistor",     "مقاومت"),
        ("diode",        "دیود"),
        ("pcb",          "برد مدار چاپی (PCB)"),
    ],

    # ══ قطعات → یاتاقان و بلبرینگ ══
    "bearings": [
        ("deep_groove",   "بلبرینگ شیاردار (Deep Groove)"),
        ("angular",       "بلبرینگ زاویه‌ای"),
        ("cyl_roller",    "رولبرینگ استوانه‌ای"),
        ("needle_roller", "رولبرینگ سوزنی"),
        ("sph_roller",    "رولبرینگ کروی"),
        ("slide_bearing", "یاتاقان لغزشی"),
        ("linear_bearing","یاتاقان خطی"),
    ],

    # ══ قطعات → موتور و گیربکس ══
    "motor_gearbox": [
        ("dc_motor",       "موتور DC"),
        ("ac_single",      "موتور AC تک‌فاز"),
        ("ac_three",       "موتور AC سه‌فاز"),
        ("servo",          "سرو موتور"),
        ("stepper",        "استپر موتور"),
        ("worm_gear",      "گیربکس حلزونی"),
        ("planetary_gear", "گیربکس سیاره‌ای"),
        ("parallel_gear",  "گیربکس شافت موازی"),
    ],

    # ══ قطعات → هیدرولیک و پنوماتیک ══
    "hydraulic": [
        ("hyd_cylinder",  "سیلندر هیدرولیک"),
        ("pneu_cylinder", "سیلندر پنوماتیک"),
        ("hyd_pump",      "پمپ هیدرولیک"),
        ("hyd_valve",     "شیر هیدرولیک"),
        ("pneu_valve",    "شیر پنوماتیک"),
        ("hyd_hose",      "شلنگ هیدرولیک"),
        ("pneu_fitting",  "اتصالات پنوماتیک"),
    ],

    # ══ قطعات → اتصالات ══
    "fasteners": [
        ("allen_screw",   "پیچ آلن"),
        ("hex_screw",     "پیچ شش‌گوش"),
        ("self_tap",      "پیچ خودکار"),
        ("hex_nut",       "مهره شش‌گوش"),
        ("lock_nut",      "مهره قفلی"),
        ("flat_washer",   "واشر تخت"),
        ("spring_washer", "واشر فنری"),
        ("key",           "خار"),
    ],

    # ══ خدمات → برشکاری ══
    "cutting_srv": [
        ("fiber_laser",   "برش لیزر فایبر"),
        ("co2_laser",     "برش لیزر CO2"),
        ("plasma_cut",    "برش پلاسما"),
        ("water_jet",     "برش واترجت"),
        ("guillotine",    "برش گیوتین"),
    ],

    # ══ خدمات → جوشکاری ══
    "welding_srv": [
        ("tig",       "جوش TIG (آرگون)"),
        ("mig_mag",   "جوش MIG/MAG (CO2)"),
        ("electrode", "جوش الکترود"),
        ("submerged", "جوش زیرپودری"),
        ("spot_weld", "جوش نقطه‌ای"),
        ("brass_weld","جوش برنج (زرد)"),
    ],

    # ══ خدمات → ماشین‌کاری ══
    "machining_srv": [
        ("cnc_turn",      "تراشکاری CNC"),
        ("cnc_mill_3",    "فرزکاری CNC 3 محور"),
        ("cnc_mill_5",    "فرزکاری CNC 5 محور"),
        ("manual_turn",   "تراش سنتی"),
        ("manual_mill",   "فرز سنتی"),
        ("grinding_ms",   "سنگ‌زنی"),
        ("gear_cutting",  "دنده‌زنی"),
        ("drilling_ms",   "سوراخکاری"),
    ],
}


# ══════════════════════════════════════════════════════════════════
# Seed Function
# ══════════════════════════════════════════════════════════════════

def seed_specializations():
    """Seed جزئیات تخصصی"""
    logger.info("🌱 شروع Seed کردن جزئیات تخصصی...")

    added_count = 0
    skipped_count = 0
    not_found_parents = 0

    with get_session() as session:
        svc = LookupService(session)

        for parent_code, specializations in SPECIALIZATIONS.items():
            parent = svc.repo.get_by_category_code(
                "supplier_subcategory", parent_code
            )

            if not parent:
                logger.warning(f"⚠️  زیرشاخه '{parent_code}' یافت نشد!")
                not_found_parents += 1
                continue

            for idx, (spec_code, spec_label) in enumerate(specializations):
                try:
                    existing = svc.repo.get_by_category_code(
                        "supplier_specialization", spec_code
                    )
                    if existing:
                        skipped_count += 1
                        continue

                    svc.seed_if_not_exists(
                        category="supplier_specialization",
                        code=spec_code,
                        label_fa=spec_label,
                        parent_id=parent.id,
                        sort_order=(idx + 1) * 10,
                    )
                    added_count += 1
                except Exception as e:
                    logger.error(
                        f"خطا در seed specialization '{spec_label}': {e}"
                    )

    logger.info(
        f"✅ Seed تمام شد. "
        f"اضافه: {added_count}, رد شده: {skipped_count}, "
        f"والد پیدا نشد: {not_found_parents}"
    )
    return added_count, skipped_count


if __name__ == "__main__":
    from app.config.logging_config import setup_logging
    setup_logging()
    added, skipped = seed_specializations()
    print(f"\n✅ اضافه شده: {added}")
    print(f"⏭️  رد شده: {skipped}")
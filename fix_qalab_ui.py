"""
جایگزینی هوشمند 'قالب' با 'تعریف' فقط در UI
Comment های مدل، Migration و Seed دست‌نخورده می‌مونن
"""
from pathlib import Path


# فایل‌هایی که باید تغییر کنن
TARGET_FILES = [
    "app/ui/device_templates/device_template_list_page.py",
    "app/ui/widgets/workflow_bar.py",
    "app/services/device_template_service.py",
    "app/services/bom_service.py",
]

# جایگزینی‌ها (به ترتیب — طولانی‌ها اول)
REPLACEMENTS = [
    ("قالب‌های دستگاه", "تعریف‌های دستگاه"),
    ("قالب دستگاه",     "تعریف دستگاه"),
    ("+ قالب جدید",     "+ دستگاه جدید"),
    ("یک قالب را",       "یک تعریف را"),
    ("قالب یافت نشد",    "تعریف یافت نشد"),
    ("قالب «",           "تعریف «"),
    ("قالب‌ها بارگذاری", "تعریف‌ها بارگذاری"),
    ("قالب‌ها: {e}",     "تعریف‌ها: {e}"),
    ("قالب حذف شد",      "تعریف حذف شد"),
]


def main():
    total_changes = 0

    for file_path in TARGET_FILES:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠  فایل نیست: {file_path}")
            continue

        original = path.read_text(encoding="utf-8")
        modified = original

        file_changes = 0
        for old, new in REPLACEMENTS:
            count = modified.count(old)
            if count > 0:
                modified = modified.replace(old, new)
                file_changes += count
                print(f"  ✅ {old:20s} → {new:20s} ({count} بار)")

        if file_changes > 0:
            path.write_text(modified, encoding="utf-8")
            print(f"📝 {file_path}: {file_changes} تغییر\n")
            total_changes += file_changes

    print(f"\n🎉 مجموع تغییرات: {total_changes}")


if __name__ == "__main__":
    main()
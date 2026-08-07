"""پیدا کردن 'قالب' در همه فایل‌های .py"""
import os
from pathlib import Path


def main():
    root = Path("app")
    keyword = "قالب"
    total = 0

    for py_file in root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for i, line in enumerate(content.split("\n"), 1):
            if keyword in line:
                print(f"{py_file}:{i}: {line.strip()}")
                total += 1

    print(f"\n📊 مجموع: {total} خط")


if __name__ == "__main__":
    main()
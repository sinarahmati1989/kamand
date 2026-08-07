"""رفع مغایرت currency: تبدیل irt_* -> irr_*"""
from app.database.session import get_session
from sqlalchemy import text


def main():
    with get_session() as s:
        # 1) پاک کردن ردیف‌های قدیمی که labelش ریاله ولی codeش تومنه
        old_codes = ['irt_k', 'irt_m', 'irt_b', 'irt']
        for code in old_codes:
            s.execute(
                text(
                    "DELETE FROM lookups "
                    "WHERE category = 'currency' AND code = :c"
                ),
                {"c": code},
            )
            print(f"  🗑  حذف: {code}")

        s.commit()
        print("✅ ردیف‌های قدیمی پاک شدند")

        # 2) نمایش نهایی
        print("\n=== Currency پس از پاکسازی ===")
        result = s.execute(text(
            "SELECT code, label_fa FROM lookups "
            "WHERE category = 'currency' ORDER BY sort_order"
        ))
        for row in result:
            print(f"  {row[0]:10s} -> {row[1]}")


if __name__ == "__main__":
    main()
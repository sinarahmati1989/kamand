"""بررسی سریع lookup ها"""
from app.database.session import get_session
from sqlalchemy import text


def main():
    with get_session() as s:
        print("=== Currency ===")
        result = s.execute(text(
            "SELECT code, label_fa FROM lookups "
            "WHERE category = 'currency' ORDER BY sort_order"
        ))
        for row in result:
            print(f"  {row[0]:10s} -> {row[1]}")

        print("\n=== Weight Unit ===")
        result = s.execute(text(
            "SELECT code, label_fa FROM lookups "
            "WHERE category = 'weight_unit' ORDER BY sort_order"
        ))
        for row in result:
            print(f"  {row[0]:10s} -> {row[1]}")


if __name__ == "__main__":
    main()
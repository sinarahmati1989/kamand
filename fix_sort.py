"""مرتب‌سازی sort_order برای currency"""
from app.database.session import get_session
from sqlalchemy import text


def main():
    order = [
        ("irr",   10),
        ("irr_k", 20),
        ("irr_m", 30),
        ("irr_b", 40),
        ("usd",   50),
        ("eur",   60),
    ]
    with get_session() as s:
        for code, sort in order:
            s.execute(
                text(
                    "UPDATE lookups SET sort_order = :so "
                    "WHERE category = 'currency' AND code = :c"
                ),
                {"so": sort, "c": code},
            )
        s.commit()
        print("✅ sort_order مرتب شد")


if __name__ == "__main__":
    main()
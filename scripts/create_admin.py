"""
Create Admin User Script
اجرا: python scripts/create_admin.py
"""

import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from sqlalchemy import select

from app.config.logging_config import setup_logging
from app.database.session import get_session
from app.models.user import User
from app.enums.roles import UserRole
from app.core.security import hash_password


setup_logging()
logger = logging.getLogger(__name__)


# ══════════════════════
# تنظیمات ادمین پیش‌فرض
# ══════════════════════
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "مدیر سیستم"
ADMIN_EMAIL = "admin@localhost"


def create_admin():
    """ساخت کاربر ادمین اگه نباشه"""
    
    print("=" * 50)
    print("  Creating Admin User")
    print("=" * 50)
    
    with get_session() as session:
        # چک کن اگه از قبل هست
        existing = session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        ).scalar_one_or_none()
        
        if existing:
            print(f"\n  ⚠️  کاربر '{ADMIN_USERNAME}' از قبل موجوده!")
            print(f"     ID:       {existing.id}")
            print(f"     Name:     {existing.full_name}")
            print(f"     Role:     {existing.role}")
            print(f"     Active:   {existing.is_active}")
            print(f"     Created:  {existing.created_at}")
            return
        
        # ساخت ادمین جدید
        admin = User(
            username=ADMIN_USERNAME,
            full_name=ADMIN_FULL_NAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        
        session.add(admin)
        session.flush()   # برای گرفتن id قبل از commit
        
        print(f"\n  ✅ کاربر ادمین ساخته شد!")
        print(f"     ID:        {admin.id}")
        print(f"     Username:  {ADMIN_USERNAME}")
        print(f"     Password:  {ADMIN_PASSWORD}")
        print(f"     Full Name: {ADMIN_FULL_NAME}")
        print(f"     Role:      {UserRole.ADMIN.value}")
        print(f"\n  ⚠️  حتماً بعد از اولین ورود پسورد رو عوض کن!")


if __name__ == "__main__":
    try:
        create_admin()
        print("\n" + "=" * 50)
        print("  ✅ Done!")
        print("=" * 50)
    except Exception as e:
        logger.exception("Error creating admin")
        print(f"\n  ❌ خطا: {e}")
        sys.exit(1)
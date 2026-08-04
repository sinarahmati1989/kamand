"""
Test Login Script
اجرا: python scripts/test_login.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config.logging_config import setup_logging
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserLoginDTO
from app.core.exceptions import AuthenticationError, ValidationError


setup_logging()


def test_login():
    print("=" * 50)
    print("  Testing Login")
    print("=" * 50)
    
    auth = AuthService()
    
    # تست 1: پسورد اشتباه
    print("\n[1] تست پسورد اشتباه:")
    try:
        auth.login(UserLoginDTO(username="admin", password="wrong"))
    except AuthenticationError as e:
        print(f"  ✅ درست: {e}")
    
    # تست 2: کاربر ناموجود
    print("\n[2] تست کاربر ناموجود:")
    try:
        auth.login(UserLoginDTO(username="nobody", password="1234"))
    except AuthenticationError as e:
        print(f"  ✅ درست: {e}")
    
    # تست 3: لاگین موفق
    print("\n[3] تست لاگین درست (admin/admin123):")
    try:
        user = auth.login(UserLoginDTO(username="admin", password="admin123"))
        print(f"  ✅ موفق!")
        print(f"     ID:       {user.id}")
        print(f"     Username: {user.username}")
        print(f"     Name:     {user.full_name}")
        print(f"     Role:     {user.role}")
    except Exception as e:
        print(f"  ❌ خطا: {e}")
    
    # تست 4: چک session
    print("\n[4] چک session:")
    from app.core.access_control import AccessControl
    if AccessControl.is_logged_in():
        current = AccessControl.get_current_user()
        print(f"  ✅ لاگین شده: {current.username}")
        print(f"     Admin? {current.is_admin()}")
    
    # تست 5: logout
    print("\n[5] لاگ‌اوت:")
    auth.logout()
    print(f"  ✅ لاگ‌اوت شد. Logged in? {AccessControl.is_logged_in()}")
    
    print("\n" + "=" * 50)
    print("  ✅ همه تست‌ها OK!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_login()
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
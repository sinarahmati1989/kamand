"""
Security Utilities
Password Hashing با bcrypt
"""

import bcrypt
import logging


logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    هش کردن پسورد با bcrypt
    
    Args:
        password: پسورد متنی
    
    Returns:
        هش پسورد (str)
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    # bcrypt نیاز به bytes داره
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)   # 12 = امنیت خوب، سرعت مناسب
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    چک کردن پسورد با هش
    
    Args:
        password: پسورد ورودی
        hashed: هش ذخیره شده
    
    Returns:
        True اگه درست، False اگه غلط
    """
    if not password or not hashed:
        return False
    
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False
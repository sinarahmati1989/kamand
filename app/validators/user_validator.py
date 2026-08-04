"""
User Validators
اعتبارسنجی ورودی‌های کاربر
"""

import re
from app.core.exceptions import ValidationError


class UserValidator:
    """اعتبارسنجی داده‌های کاربر"""
    
    USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.]{3,50}$")
    
    @staticmethod
    def validate_username(username: str) -> None:
        """چک username"""
        if not username or not username.strip():
            raise ValidationError("نام کاربری نمی‌تواند خالی باشد")
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValidationError("نام کاربری حداقل ۳ کاراکتر باشد")
        
        if len(username) > 50:
            raise ValidationError("نام کاربری حداکثر ۵۰ کاراکتر")
        
        if not UserValidator.USERNAME_PATTERN.match(username):
            raise ValidationError(
                "نام کاربری فقط حروف انگلیسی، عدد، _ و . می‌تواند داشته باشد"
            )
    
    @staticmethod
    def validate_password(password: str) -> None:
        """چک پسورد"""
        if not password:
            raise ValidationError("پسورد نمی‌تواند خالی باشد")
        
        if len(password) < 4:
            raise ValidationError("پسورد حداقل ۴ کاراکتر باشد")
        
        if len(password) > 100:
            raise ValidationError("پسورد حداکثر ۱۰۰ کاراکتر")
    
    @staticmethod
    def validate_full_name(name: str) -> None:
        """چک نام کامل"""
        if not name or not name.strip():
            raise ValidationError("نام کامل نمی‌تواند خالی باشد")
        
        if len(name.strip()) < 2:
            raise ValidationError("نام کامل حداقل ۲ کاراکتر باشد")
        
        if len(name) > 100:
            raise ValidationError("نام کامل حداکثر ۱۰۰ کاراکتر")
    
    @staticmethod
    def validate_email(email: str | None) -> None:
        """چک ایمیل (اختیاری)"""
        if not email:
            return
        
        pattern = re.compile(r"^[\w\.\-]+@[\w\.\-]+\.\w+$")
        if not pattern.match(email):
            raise ValidationError("فرمت ایمیل نامعتبر است")
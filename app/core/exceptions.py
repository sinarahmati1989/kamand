"""
Custom Exceptions — خطاهای سفارشی کمند
"""


class AppError(Exception):
    """پایه همه خطاهای اپلیکیشن"""
    def __init__(self, message: str = "خطای سیستمی"):
        self.message = message
        super().__init__(message)


# ─────────────────────────── Common ──────────────────────────────────

class ValidationError(AppError):
    """خطای اعتبارسنجی"""
    def __init__(self, message: str = "داده‌های وارد شده معتبر نیست"):
        super().__init__(message)


class NotFoundError(AppError):
    """رکورد یافت نشد"""
    def __init__(self, message: str = "رکورد یافت نشد"):
        super().__init__(message)


class DuplicateError(AppError):
    """رکورد تکراری است"""
    def __init__(self, message: str = "رکورد تکراری است"):
        super().__init__(message)


# ─────────────────────────── Auth ────────────────────────────────────

class AuthenticationError(AppError):
    """نام کاربری یا رمز عبور اشتباه"""
    pass


class PermissionDeniedError(AppError):
    """دسترسی غیرمجاز"""
    pass


class SessionExpiredError(AppError):
    """نشست منقضی شده"""
    pass


# ─────────────────────────── User ────────────────────────────────────

class UserNotFoundError(NotFoundError):
    """کاربر یافت نشد"""
    def __init__(self, message: str = "کاربر یافت نشد"):
        super().__init__(message)


class DuplicateUsernameError(DuplicateError):
    """نام کاربری تکراری"""
    def __init__(self, message: str = "نام کاربری قبلاً ثبت شده است"):
        super().__init__(message)


# ─────────────────────────── Database ────────────────────────────────

class DatabaseError(AppError):
    """خطای پایگاه داده"""
    pass
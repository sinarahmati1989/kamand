"""
Logging Configuration
سه فایل لاگ جدا: app / error / audit
"""

import logging
import logging.handlers
from pathlib import Path

from app.config.settings import settings


def setup_logging() -> None:
    """راه‌اندازی سیستم لاگ"""
    
    log_dir = settings.LOG_PATH
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # فرمت پیش‌فرض
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
    
    # ══════════ Root Logger ══════════
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    
    # Console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(log_level)
    root.addHandler(console)
    
    # ══════════ app.log ══════════
    app_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)
    root.addHandler(app_handler)
    
    # ══════════ error.log ══════════
    err_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    err_handler.setFormatter(formatter)
    err_handler.setLevel(logging.ERROR)
    root.addHandler(err_handler)
    
    # ══════════ audit.log (جدا) ══════════
    audit = logging.getLogger("audit")
    audit.setLevel(logging.INFO)
    audit.propagate = False  # نره تو root
    
    audit_handler = logging.handlers.RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    audit_handler.setFormatter(formatter)
    audit.addHandler(audit_handler)
    
    logging.getLogger(__name__).info("Logging initialized")
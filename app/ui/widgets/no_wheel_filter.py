"""
No-Wheel Global Filter
جلوگیری از تغییر مقدار Combo/SpinBox با scroll wheel
"""
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import (
    QComboBox, QSpinBox, QDoubleSpinBox, QAbstractSpinBox
)


class NoWheelFilter(QObject):

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            if isinstance(
                obj,
                (QComboBox, QSpinBox, QDoubleSpinBox, QAbstractSpinBox)
            ):
                # همیشه wheel را block کن - حتی اگر focus داشته باشد
                event.ignore()
                return True
        return super().eventFilter(obj, event)


_filter_instance = None


def install_no_wheel_filter(app):
    global _filter_instance
    _filter_instance = NoWheelFilter()
    app.installEventFilter(_filter_instance)
    print("[DEBUG] NoWheelFilter installed OK")
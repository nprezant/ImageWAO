from PySide2.QtGui import QColor


class TwoColorGradient:
    def __init__(self, start: QColor, end: QColor):
        self.start: QColor = start
        self.end: QColor = end

    def getColor(self, percentage: float) -> QColor:
        """Percentage must be between 0 and 1"""
        if percentage < 0 or percentage > 1:
            raise ValueError(f"Percentage must be in [0,1] domain, not: {percentage}")
        return interpolate(self.start, self.end, percentage)


def interpolate(start: QColor, end: QColor, ratio: float) -> QColor:
    """Interpolate between two colors"""
    r = int(ratio * start.red() + (1 - ratio) * end.red())
    g = int(ratio * start.green() + (1 - ratio) * end.green())
    b = int(ratio * start.blue() + (1 - ratio) * end.blue())
    return QColor.fromRgb(r, g, b)

import sys

from PyQt6 import QtGui
from PyQt6.QtCore import QSize, Qt, QRect
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication


def create_gradient_px_map() -> QPixmap:
    px_map = QtGui.QPixmap(QSize(800, 800))
    px_map.fill(Qt.GlobalColor.white)
    painter = QtGui.QPainter(px_map)
    gradient = QtGui.QLinearGradient(0, 0, 800, 0)
    gradient.setColorAt(0, Qt.GlobalColor.black)
    gradient.setColorAt(1, Qt.GlobalColor.white)
    painter.fillRect(QRect(0, 0, 800, 800), gradient)
    painter.end()
    return px_map


if __name__ == '__main__':
    app = QApplication(sys.argv)
    px_map = create_gradient_px_map()
    px_map.save('gradient.png')
    sys.exit(app.exec())

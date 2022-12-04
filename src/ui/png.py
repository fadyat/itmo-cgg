from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
)

from src.errors.png import PngError
from src.files.png import PngIO
from src.typedef import logs
from src.ui.errors import FileErrorMessage


class PngViewWidget(QMainWindow):
    file_name: str = '../../docs/sad1.png'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PNG Viewer")
        self.resize(800, 600)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.png_label = QLabel("PNG Preview")
        self.png_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.png_label)

        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_self_implement)
        self.main_layout.addWidget(self.preview_button)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def preview_png(self):
        self.png_label.setPixmap(
            QPixmap(self.file_name)
        )

    def preview_self_implement(self):
        try:
            with PngIO(self.file_name) as r:
                png = r.read_for_ui()
        except PngError as e:
            FileErrorMessage(str(e), self, logs).show()
            return

        print(png)
        self.png_label.setPixmap(png.to_qpixmap())


if __name__ == '__main__':
    app = QApplication([])
    w = PngViewWidget()
    w.show()
    app.exec()

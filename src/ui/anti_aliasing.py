from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFrame,
    QLabel,
    QGridLayout,
    QFileDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from src.files.pnm import PnmIO
from src.typedef import logs
from src.ui.errors import PnmFileErrorMessage


class AntiAliasingWidget(QWidget):
    selected_file: str = r"C:\Users\sergo\PycharmProjects\cg22-project-NeedForGirl3\docs\shrek.pnm"  # todo: remove this

    def __init__(
            self,
            preview_widget: 'PicturePreviewWidget',
    ):
        super().__init__()
        self.preview_widget = preview_widget
        self.gamma_input = QLineEdit()
        self.gamma_input.setText("1.0")

        self.select_file_layout = QHBoxLayout()
        self.select_file_button = QPushButton("Select file")
        self.select_file_button.clicked.connect(self.select_file)
        self.selected_file_label = QLabel(self.selected_file)
        self.select_file_layout.addWidget(self.select_file_button)
        self.select_file_layout.addWidget(self.selected_file_label)

        self.form_layout = QVBoxLayout()
        self.form_layout.addLayout(self.select_file_layout)

        self.setLayout(self.form_layout)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def select_file(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Select file", "", "")[0]
        self.selected_file_label.setText(self.selected_file.split("/")[-1])
        self.preview_widget.render_picture(self.selected_file)


class PicturePreviewWidget(QWidget):

    def __init__(
            self,
    ):
        super().__init__()
        self.pnm_data = None
        self.preview_layout = QHBoxLayout()
        self.preview_frame = QFrame()
        self.preview_layout.addWidget(self.preview_frame)
        self.preview_label = QLabel("Preview")
        self.preview_layout.addWidget(self.preview_label)
        self.setLayout(self.preview_layout)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def Bresenham(self, px_map, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self.draw_point(x1, y1, px_map)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def draw_point(
            self,
            x: int,
            y: int,
            px_map,
    ) -> None:
        painter = QtGui.QPainter(px_map)
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawPoint(x, y)
        painter.end()
        self.preview_label.setPixmap(px_map)

    def render_picture(
            self,
            selected_file: str,
    ) -> None:
        try:
            with PnmIO(selected_file) as pnm:
                self.pnm_data = pnm.read_for_ui()
        except Exception as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        px_map = QtGui.QPixmap(QSize(self.pnm_data.width, self.pnm_data.height))
        painter = QtGui.QPainter(px_map)
        for i in range(
                0,
                self.pnm_data.width * self.pnm_data.height * self.pnm_data.bytes_per_pixel,
                self.pnm_data.bytes_per_pixel,
        ):

            painter.setPen(QtGui.QColor(255, 255, 255))
            painter.drawPoint(
                i // self.pnm_data.bytes_per_pixel % self.pnm_data.width,
                i // self.pnm_data.bytes_per_pixel // self.pnm_data.width
            )
        painter.end()
        self.preview_label.setPixmap(px_map)
        self.Bresenham(px_map, 0, 0, 33, 100)


class AssignGammaWidget(QWidget):

    def __init__(
            self,
    ):
        super().__init__()
        self.global_hori_layout = QGridLayout()
        self.picture_preview_widget = PicturePreviewWidget()
        self.global_hori_layout.addWidget(self.picture_preview_widget, 1, 0)

        self.form_gamma_widget = AntiAliasingWidget(self.picture_preview_widget)
        self.global_hori_layout.addWidget(self.form_gamma_widget, 0, 0)

        self.setLayout(self.global_hori_layout)
        self.global_hori_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setGeometry(0, 0, 800, 600)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = AssignGammaWidget()
    w.show()
    sys.exit(app.exec())

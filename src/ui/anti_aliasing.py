from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage
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
        self.draw_pixels = []
        self.pnm_data = None
        self.preview_layout = QHBoxLayout()
        self.preview_frame = QFrame()
        self.preview_layout.addWidget(self.preview_frame)
        self.preview_label = QLabel("Preview")
        self.preview_layout.addWidget(self.preview_label)
        self.setLayout(self.preview_layout)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _fpart(self, x):
        return x - int(x)

    def _rfpart(self, x):
        return 1 - self._fpart(x)

    def putpixel(self, img: QImage, px, color, alpha=1):
        """
        Paints color over the background at the point xy in img.
        Use alpha for blending. alpha=1 means a completely opaque foreground.
        """
        compose_color = lambda bg, fg: int(round(alpha * fg + (1 - alpha) * bg))
        x, y = px
        if 0 <= x < img.width() and 0 <= y < img.height():
            r, g, b, _ = img.pixelColor(x, y).getRgb()
            img.setPixelColor(x, y, QtGui.QColor(compose_color(r, color[0]),
                                                 compose_color(g, color[1]),
                                                 compose_color(b, color[2])))

    def draw_line(self, img, p1, p2, color, thickness):
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        steep = abs(dx) < abs(dy)
        p = lambda px, py: ((px, py), (py, px))[steep]

        if steep:
            x1, y1, x2, y2, dx, dy = y1, x1, y2, x2, dy, dx
        if x2 < x1:
            x1, x2, y1, y2 = x2, x1, y2, y1

        grad = dy / dx
        intery = y1 + self._rfpart(x1) * grad

        def draw_endpoint(pt):
            x, y = pt
            xend = round(x)
            yend = y + grad * (xend - x)
            xgap = self._rfpart(x + 0.5)
            px, py = int(xend), int(yend)
            self.putpixel(img, p(px, py), color, self._rfpart(yend) * xgap)
            self.putpixel(img, p(px, py + 1), color, self._fpart(yend) * xgap)
            return px

        xstart = draw_endpoint(p(*p1)) + 1
        xend = draw_endpoint(p(*p2))

        for x in range(xstart, xend + 1):
            for dx in range(thickness + 1):
                for dy in range(thickness + 1):
                    if 0 <= x - dx < img.width() and 0 <= intery - dy < img.height():
                        self.putpixel(img, p(x - dx, int(intery) - dy), color, self._rfpart(intery))
                        self.putpixel(img, p(x - dx, int(intery) - dy + 1), color, self._fpart(intery))
            intery += grad

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
                self.pnm_data.width * self.pnm_data.height * self.pnm_data.bytes_per_px,
                self.pnm_data.bytes_per_px,
        ):
            painter.setPen(QtGui.QColor(255, 255, 255))
            painter.drawPoint(
                i // self.pnm_data.bytes_per_px % self.pnm_data.width,
                i // self.pnm_data.bytes_per_px // self.pnm_data.width
            )
        painter.end()
        self.preview_label.setPixmap(px_map)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.draw_pixels.append((a0.pos().x(), a0.pos().y()))
        img = self.preview_label.pixmap().toImage()
        if len(self.draw_pixels) == 2:
            self.draw_line(
                img,
                self.draw_pixels[0],
                self.draw_pixels[1],
                (0, 0, 0),
                7,
            )
            self.draw_pixels = []
            self.preview_label.setPixmap(QtGui.QPixmap.fromImage(img))


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

import sys

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QFrame, QLabel, QWidget

from src.utils.dithering.ordered import ordered_dithering_bytes


class DitheringWidget(QWidget):
    # selected_file: str = "/Users/artyomfadeyev/GitHub/dem.pnm"

    # selected_file: str = "/Users/artyomfadeyev/GitHub/cg22-project-NeedForGirl/docs/lena.pnm"

    def __init__(
        self,
    ):
        super().__init__()
        self.preview_layout = QHBoxLayout()
        self.preview_frame = QFrame()
        self.preview_layout.addWidget(self.preview_frame)
        self.preview_label = QLabel("Preview")
        self.preview_layout.addWidget(self.preview_label)
        self.setLayout(self.preview_layout)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_frame.setFrameShape(QFrame.Shape.Box)
        # save pixmap to file
        self.preview_label.setPixmap(
            # QtGui.QPixmap(self.selected_file)
            create_gradient_px_map(800, 800)
        )
        # file = QFile("/Users/artyomfadeyev/GitHub/cg22-project-NeedForGirl/docs/gradient.png")
        # file.open(QFile.OpenModeFlag.WriteOnly)
        # self.preview_label.pixmap().save(file, "PNG")
        self.setFixedSize(QSize(800, 800))
        self.preview_layout.unsetContentsMargins()
        self.preview_layout.setSpacing(0)

        self.preview_label.setPixmap(
            create_px_map(
                # floyd_steinberg_dithering_bytes(
                # atkinson_dithering_bytes(
                ordered_dithering_bytes(
                    # random_dithering_bytes(
                    get_pixel_map_pxls(self.preview_label.pixmap()),
                    # bayer_matrix=bayer_matrix_8x8(),
                    # 1,
                    # ),
                    width=self.preview_label.pixmap().width(),
                ),
                self.preview_label.pixmap().width(),
                self.preview_label.pixmap().height(),
                3,
            )
        )


def create_gradient_px_map(w, h):
    px_map = QtGui.QPixmap(QSize(w, h))
    px_map.fill(Qt.GlobalColor.white)
    painter = QtGui.QPainter(px_map)
    gradient = QtGui.QLinearGradient(0, 0, w, 0)
    gradient.setColorAt(0, Qt.GlobalColor.black)
    gradient.setColorAt(1, Qt.GlobalColor.white)
    rect = QRect(0, 0, w, h)
    painter.fillRect(rect, gradient)
    painter.end()
    return px_map


def create_px_map(
    content: list[float],
    w: int,
    h: int,
    bytes_per_px: int = 3,
):
    px_map = QtGui.QPixmap(QSize(w, h))
    painter = QtGui.QPainter()
    painter.begin(px_map)

    for i in range(0, w * h * bytes_per_px, bytes_per_px):
        rgb = content[i: i + bytes_per_px]
        if bytes_per_px == 1:
            rgb *= 3

        painter.setPen(QtGui.QColor(*rgb))
        painter.drawPoint(i // bytes_per_px % w, i // bytes_per_px // w)

    painter.end()
    return px_map


def get_pixel_map_pxls(px_map):
    img = px_map.toImage()
    return [
        i for y in range(img.height())
        for x in range(img.width())
        for i in img.pixelColor(x, y).getRgb()[:3]
    ]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DitheringWidget()
    w.show()
    sys.exit(app.exec())

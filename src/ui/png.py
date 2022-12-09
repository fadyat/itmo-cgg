from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QWidget, QFileDialog, QApplication
)

from src.entities.png import PngFileUI
from src.errors.png import PngError
from src.files.png import PngIO
from src.typedef import logs
from src.ui.errors import FileErrorMessage


class PngViewWidget(QMainWindow):
    file_name: str = None
    previous_png: PngFileUI = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PNG Viewer")
        self.resize(800, 600)
        self.toolbar = self.addToolBar("Toolbar")

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.png_label = QLabel("PNG Preview")
        self.png_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.png_label)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.toolbar.addAction("Preview", self.preview_self_implement)
        self.toolbar.addAction("Save", self.save_png)

    def preview_self_implement(self):
        selected_file = QFileDialog.getOpenFileName(
            self, "Select PNG file", "", "PNG (*.png)"
        )

        if not selected_file[0]:
            return

        self.file_name = selected_file[0]
        try:
            with PngIO(self.file_name) as r:
                png = r.read_for_ui()
        except PngError as e:
            FileErrorMessage(str(e), self, logs).show()
            return
        self.png_label.setPixmap(png.to_qpixmap())

        self.previous_png = png

    def save_png(self):
        if not self.previous_png:
            return

        image = self.png_label.pixmap().toImage()
        width, height = image.width(), image.height()

        # todo: support other formats
        bpx = 3 if self.previous_png.ihdr_chunk.color_type == 2 else 1
        pxls = bytes([
            pxl for y in range(height)
            for x in range(width)
            for pxl in image.pixelColor(x, y).getRgb()[:bpx]
        ])

        new_file_name = QFileDialog.getSaveFileName(
            self, "Save PNG file", "", "PNG (*.png)"
        )[0]

        if not new_file_name:
            return

        gamma = 0
        if self.previous_png.gamma_chunk:
            gamma = self.previous_png.gamma_chunk.get_gamma()

        try:
            with PngIO(new_file_name, 'wb') as w:
                w.write(
                    width=width,
                    height=height,
                    bit_depth=self.previous_png.ihdr_chunk.bit_depth,
                    color_type=self.previous_png.ihdr_chunk.color_type,
                    compression_method=self.previous_png.ihdr_chunk.compression_method,
                    filter_method=self.previous_png.ihdr_chunk.filter_method,
                    interlace_method=self.previous_png.ihdr_chunk.interlace_method,
                    data=pxls,
                    gamma=gamma,
                )
        except PngError as e:
            FileErrorMessage(str(e), self, logs).show()
            return

        logs.info(f"Saved PNG file to {new_file_name}")


if __name__ == '__main__':
    app = QApplication([])
    w = PngViewWidget()
    w.show()
    app.exec()

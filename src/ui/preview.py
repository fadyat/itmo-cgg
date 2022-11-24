from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)

from src.entities.pnm import PnmFileUI
from src.files.pnm import PnmIO
from src.typedef import logs
from src.ui.errors import PnmFileErrorMessage
from src.utils.channels import try_delete_superfluous_channels
from src.utils.converter import ColorFormat, ColorConverter
from src.utils.dithering.resolver import DitheringAlgo, apply_dithering
from src.utils.gamma import assign_gamma, GammaOption, convert_gamma


class FilePreview(QWidget):
    prev_correct_image: PnmFileUI = None

    def __init__(self):
        super().__init__()
        self.label = QLabel("Preview")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setPixmap(QtGui.QPixmap())
        self.init_layout()
        self.show()

    def init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.label)

    def update_preview(
        self,
        file_name: str,
        prev_color_format: ColorFormat,
        new_color_format: ColorFormat,
        disabled_channels: list[bool],
        dithering_algo: DitheringAlgo,
        dithering_bits: int,
        prev_gamma: float,
        next_gamma: float,
        gamma_option: GammaOption = GammaOption.ASSIGN,
    ) -> bool:
        try:
            with PnmIO(file_name) as r:
                img = r.read_for_ui()
        except Exception as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return False

        px_map = QtGui.QPixmap(QSize(img.width, img.height))
        painter = QtGui.QPainter(px_map)
        converter = ColorConverter(new_color_format)
        dithering_bits_values = [
            i / (2 ** dithering_bits - 1)
            for i in range(2 ** dithering_bits)
        ]

        for i in range(0, img.get_size(), img.bytes_per_px):
            px = img.get_px(i, disabled_channels)
            px_upd = converter.convert_px(prev_color_format, px)

            if gamma_option == GammaOption.ASSIGN:
                px_upd = assign_gamma(px_upd, prev_gamma, next_gamma)
            elif gamma_option == GammaOption.CONVERT:
                px_upd = convert_gamma(px_upd, prev_gamma, next_gamma)

            img.set_px(i, px_upd)

        for i in range(0, img.get_size(), img.bytes_per_px):
            px = apply_dithering(dithering_algo, img, i, disabled_channels, dithering_bits_values)
            painter.setPen(QtGui.QColor(*[
                max(0, min(255, int(i * 255)))
                for i in px
            ]))

            painter.drawPoint(QPoint(img.get_x(i), img.get_y(i)))
            img.set_px(i, px)

        painter.end()
        self.label.setPixmap(px_map)
        self.prev_correct_image = img
        return True

    def save_preview(
        self,
        save_as: str,
        disabled_channels: list[bool],
    ):
        if not self.prev_correct_image:
            PnmFileErrorMessage("No image to save", self, logs).show()
            return

        opt_content = try_delete_superfluous_channels(
            self.prev_correct_image.content, disabled_channels
        )

        if len(opt_content) != len(self.prev_correct_image.content):
            self.prev_correct_image.content = opt_content
            self.prev_correct_image.bytes_per_px = 1
            self.prev_correct_image.pnm_format = "P5"
            logs.info("Channels deleted, changed format to P5")

        integers_content = [
            max(0, min(255, int(i * 255)))
            for i in self.prev_correct_image.content
        ]

        with PnmIO(save_as, "wb") as w:
            w.write(
                pnm_format=self.prev_correct_image.pnm_format,
                width=self.prev_correct_image.width,
                height=self.prev_correct_image.height,
                image_content=integers_content,
                max_color_value=self.prev_correct_image.max_color,
            )

    def get_selected_file_format(self):
        return self.prev_correct_image.pnm_format

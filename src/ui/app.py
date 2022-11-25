from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QComboBox,
    QStyleFactory,
    QCheckBox, )

from src import config
from src.ui.gamma import GammaWidget
from src.ui.preview import FilePreview
from src.ui.scaling import ScalingWidget
from src.utils.converter import ColorFormat
from src.utils.dithering.resolver import DitheringAlgo
from src.utils.gamma import GammaOption
from src.utils.label import create_beauty_label


class ApplicationWindow(QMainWindow):
    toolbar_height: int = 30
    selected_file: str = "/Users/artyomfadeyev/GitHub/cg22-project-NeedForGirl/docs/lena.pnm"
    picture_color_format: ColorFormat = ColorFormat.RGB
    new_color_format: ColorFormat = ColorFormat.RGB
    dithering_algo: DitheringAlgo = DitheringAlgo.NONE
    channels: list[QCheckBox] = []
    disabled_channels = [False, False, False]
    dithering_bits: int = 1

    def __init__(self):
        super().__init__()
        self.init_window_itself()
        file_menu = self.menuBar().addMenu("File")
        self.toolbar = self.init_toolbar()

        self.select_action = file_menu.addAction("Select")
        self.select_action.triggered.connect(self.select_file)
        self.preview = FilePreview()

        self.edit_action = file_menu.addAction("Save")
        self.edit_action.triggered.connect(self.save_file)

        self.gamma_action = file_menu.addAction("Gamma")
        self.gamma_action.triggered.connect(self.change_gamma)

        self.scaling_action = file_menu.addAction("Scaling")
        self.scaling_action.triggered.connect(self.change_scaling)

        self.toolbar.addWidget(create_beauty_label("From"))
        self.picture_color_format_selector = QComboBox(self)
        self.picture_color_format_selector.addItems(config.COLOR_MODELS)
        self.picture_color_format_selector.currentTextChanged.connect(self.change_color_format)
        self.picture_color_format_selector.setStyle(QStyleFactory.create("Fusion"))
        self.picture_color_format_selector.setStyleSheet(
            "QComboBox { font-size: 10px; padding-left: 5px; }"
        )
        self.toolbar.addWidget(self.picture_color_format_selector)

        self.toolbar.addWidget(create_beauty_label("To"))
        self.new_color_format_selector = QComboBox(self)
        self.new_color_format_selector.addItems(config.COLOR_MODELS)
        self.new_color_format_selector.currentTextChanged.connect(self.change_color_format)
        self.new_color_format_selector.setStyle(QStyleFactory.create("Fusion"))
        self.new_color_format_selector.setStyleSheet(
            "QComboBox { font-size: 10px; padding-left: 5px; }"
        )
        self.toolbar.addWidget(self.new_color_format_selector)

        self.toolbar.addWidget(create_beauty_label("Dithering"))
        self.dithering_selector = QComboBox(self)
        self.dithering_selector.addItems(config.DITHERING_ALGORITHMS)
        self.dithering_selector.currentTextChanged.connect(self.change_dithering)
        self.dithering_selector.setStyle(QStyleFactory.create("Fusion"))
        self.dithering_selector.setStyleSheet(
            "QComboBox { font-size: 10px; padding-left: 5px; }"
        )
        self.toolbar.addWidget(self.dithering_selector)
        self.toolbar.setStyleSheet(
            "QToolBar { background-color: #e0e0e0; padding-left: 5px; }"
        )
        self.dithering_bits_selector = QComboBox(self)
        self.dithering_bits_selector.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        self.dithering_bits_selector.currentTextChanged.connect(self.change_dithering)
        self.dithering_bits_selector.setStyle(QStyleFactory.create("Fusion"))
        self.dithering_bits_selector.setStyleSheet(
            "QComboBox { font-size: 10px; padding-left: 5px; }"
        )
        self.toolbar.addWidget(self.dithering_bits_selector)

        for i in range(3):
            self.toolbar.addSeparator()
            self.channel = QCheckBox(self)
            self.channel.setText(f"Channel {i + 1}")
            self.channel.stateChanged.connect(self.change_channel)
            self.channel.setStyleSheet("QCheckBox { font-size: 10px; padding-left: 5px; }")
            self.channel.setStyle(QStyleFactory.create("Fusion"))
            self.toolbar.addWidget(self.channel)
            self.channels.append(self.channel)

        self.edit_gamma_widget = GammaWidget(self)
        self.scaling_widget = ScalingWidget(self)
        self.setCentralWidget(self.preview)

    def init_window_itself(self):
        self.setWindowTitle("Photo Editor")
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowState(Qt.WindowState.WindowMaximized)

    def init_toolbar(self):
        toolbar = self.addToolBar("Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setFixedHeight(self.toolbar_height)
        return toolbar

    def select_file(self):
        if not (file_name := QFileDialog.getOpenFileName(self, "Open file", "", "")[0]):
            return

        if self.preview.update_preview(
            file_name,
            self.picture_color_format,
            self.new_color_format,
            self.disabled_channels,
            self.dithering_algo,
            self.dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
        ):
            self.selected_file = file_name

        if self.preview.get_selected_file_format() == config.P5:
            self.channels[1].setEnabled(False)
            self.channels[2].setEnabled(False)
        else:
            self.channels[1].setEnabled(True)
            self.channels[2].setEnabled(True)

        for i in range(3):
            self.channels[i].setChecked(False)

        self.scaling_widget.set_width(self.preview.prev_correct_image.width)
        self.scaling_widget.set_height(self.preview.prev_correct_image.height)

    def change_channel(self):
        disabled_channels = self.get_disabled_channels()

        if self.preview.update_preview(
            self.selected_file,
            self.picture_color_format,
            self.new_color_format,
            disabled_channels,
            self.dithering_algo,
            self.dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
        ):
            self.disabled_channels = disabled_channels

    def change_color_format(self):
        picture_color_format = self.picture_color_format_selector.currentText()
        new_color_format = self.new_color_format_selector.currentText()

        if self.preview.update_preview(
            self.selected_file,
            ColorFormat[picture_color_format],
            ColorFormat[new_color_format],
            self.disabled_channels,
            self.dithering_algo,
            self.dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
        ):
            self.picture_color_format = ColorFormat[picture_color_format]
            self.new_color_format = ColorFormat[new_color_format]

    def change_dithering(self):
        dithering_algo = self.dithering_selector.currentText()
        dithering_bits = int(self.dithering_bits_selector.currentText())

        if self.preview.update_preview(
            self.selected_file,
            self.picture_color_format,
            self.new_color_format,
            [False, False, False],
            DitheringAlgo[dithering_algo],
            dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
        ):
            self.dithering_algo = DitheringAlgo[dithering_algo]
            self.dithering_bits = dithering_bits

    def save_file(self):
        if not (file_name := QFileDialog.getSaveFileName(self, "Save file", "", "")[0]):
            return

        self.preview.save_preview(file_name, self.disabled_channels)

    def change_gamma(self):
        self.edit_gamma_widget.show()

    def change_scaling(self):
        self.scaling_widget.show()

    def apply_gamma(
        self,
        gamma_option: GammaOption,
    ):
        if self.preview.update_preview(
            self.selected_file,
            self.picture_color_format,
            self.new_color_format,
            self.disabled_channels,
            self.dithering_algo,
            self.dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
            gamma_option=gamma_option,
        ):
            if gamma_option == GammaOption.CONVERT:
                self.edit_gamma_widget.set_from_gamma(self.edit_gamma_widget.get_to_gamma())

    def get_disabled_channels(self):
        is_p5 = not self.channels[1].isEnabled()

        if is_p5 and self.channels[0].isChecked():
            return [True, True, True]
        elif is_p5 and not self.channels[0].isChecked():
            return [False, False, False]

        return [
            self.channels[i].isChecked()
            for i in range(3)
        ]

    def apply_scaling(self):
        new_width, new_height = self.scaling_widget.get_width(), self.scaling_widget.get_height()
        algorithm = self.scaling_widget.get_scaling_algorithm()

        if self.preview.update_preview(
            self.selected_file,
            self.picture_color_format,
            self.new_color_format,
            self.disabled_channels,
            self.dithering_algo,
            self.dithering_bits,
            self.edit_gamma_widget.get_from_gamma(),
            self.edit_gamma_widget.get_to_gamma(),
            scaling_algo=algorithm,
            new_width=new_width,
            new_height=new_height,
        ):
            self.scaling_widget.set_width(new_width)
            self.scaling_widget.set_height(new_height)

    def close(self) -> bool:
        self.preview.close()
        self.edit_gamma_widget.close()
        self.scaling_widget.close()
        return super().close()


if __name__ == "__main__":
    app = QApplication([])
    window = ApplicationWindow()
    window.show()
    app.exec()

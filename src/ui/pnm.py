import enum
import os
import typing

from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QHBoxLayout,
)

from src import config
from src.entities.pnm import PnmFile
from src.errors.pnm import PnmError
from src.files.pnm import PnmIO
from src.typedef import logs
from src.ui.errors import PnmFileErrorMessage
from src.utils.converter import ColorConverter, ColorFormat


class Option(enum.Enum):
    NOTHING = 0
    RENDER = 1
    EDITING = 2
    PREVIEW = 3


class EditFileWindow(QWidget):
    picture_format: QComboBox
    picture_format_label: QLabel
    resize_table_button: QPushButton
    picture_max_color: QLineEdit
    picture_max_color_label: QLabel
    picture_content: QTableWidget
    picture_content_label: QLabel

    def __init__(
            self,
    ):
        super().__init__()
        self.setWindowTitle('Edit PNM file')
        self.setGeometry(0, 0, 500, 500)
        self.setLayout(QVBoxLayout())

        self.setup_header()
        self.setup_content()

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_changes)
        self.layout().addWidget(self.save_button)

    def setup_header(
            self,
    ):
        format_layout = QHBoxLayout()
        self.picture_format = QComboBox(self)
        self.picture_format.addItems(config.PNM_SUPPORTED_FORMATS)
        self.picture_format_label = QLabel('Format', self)
        self.picture_format.currentIndexChanged.connect(self.resize_table)
        format_layout.addWidget(self.picture_format_label)
        format_layout.addWidget(self.picture_format)
        self.layout().addLayout(format_layout)  # type: ignore

        color_layout = QHBoxLayout()
        self.picture_max_color = QLineEdit(self)
        self.picture_max_color_label = QLabel('Max color', self)
        color_layout.addWidget(self.picture_max_color_label)
        color_layout.addWidget(self.picture_max_color)
        self.layout().addLayout(color_layout)  # type: ignore

    def setup_content(
            self,
    ):
        picture_content_layout = QHBoxLayout()
        self.picture_content_label = QLabel('Content', self)
        picture_content_layout.addWidget(self.picture_content_label)
        self.layout().addLayout(picture_content_layout)  # type: ignore

        self.picture_content = QTableWidget(self)
        self.picture_content.setGeometry(0, 0, 500, 500)
        self.picture_content.verticalHeader().hide()
        self.picture_content.horizontalHeader().hide()
        self.layout().addWidget(self.picture_content)

    def edit_file(
            self,
            pnm_format: str,
            width: int,
            height: int,
            max_color: int,
            bytes_per_pixel: int,
            content: typing.List[int],
    ):
        self.picture_format.setCurrentText(pnm_format)
        self.picture_max_color.setText(str(max_color))
        self.create_table(
            width=width,
            height=height,
            bytes_per_pixel=bytes_per_pixel,
            content=content,
        )

    def create_table(
            self,
            width: int,
            height: int,
            bytes_per_pixel: int,
            content: typing.Optional[typing.List[int]] = None,
    ):
        self.picture_content_label.setText(
            f'Content {width}, {height}, {bytes_per_pixel}'
        )
        self.picture_content.setColumnCount(bytes_per_pixel * width)
        self.picture_content.setRowCount(height)
        for i in range(
                0,
                width * height * bytes_per_pixel,
        ):
            self.picture_content.setItem(
                i // (width * bytes_per_pixel),
                i % (width * bytes_per_pixel),
                QTableWidgetItem(str(content[i])),
            )

    def save_changes(
            self,
    ):
        saved_file = QFileDialog.getSaveFileName(self, "Save File", "", "")[0]
        if not saved_file:
            return

        bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[self.picture_format.currentText()]
        actual_width = (
                int(self.picture_content.model().columnCount()) // bytes_per_pixel
        )
        try:
            with PnmIO(saved_file, 'wb') as f:
                f.write(
                    pnm_format=self.picture_format.currentText(),
                    width=actual_width,
                    height=int(self.picture_content.model().rowCount()),
                    image_content=self.get_table_content(),
                    max_color_value=int(self.picture_max_color.text()),
                )
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            if not os.path.getsize(saved_file):
                os.remove(saved_file)
            return

        self.close()

    def get_table_content(self):
        model = self.picture_content.model()
        return list(
            int(model.index(i, j).data())
            for i in range(model.rowCount())
            for j in range(model.columnCount())
        )

    def resize_table(self):
        new_bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[
            self.picture_format.currentText()
        ]
        new_width = (self.picture_content.model().columnCount()) // new_bytes_per_pixel
        self.picture_content_label.setText(
            f'Content {new_width}, '
            f'{self.picture_content.model().rowCount()}, '
            f'{new_bytes_per_pixel}'
        )


# class ChangeColorModel(QWidget):
#     picture_format: QComboBox
#     picture_format_label: QLabel
#     resize_table_button: QPushButton
#     picture_max_color: QLineEdit
#     picture_max_color_label: QLabel
#     picture_content: QTableWidget
#     picture_content_label: QLabel
#
#     def __init__(
#             self,
#     ):
#         super().__init__()
#         self.clear_picture_button = QPushButton("Change color model", self)


class Window(QMainWindow):
    option = Option.NOTHING
    selected_file: str = ...
    current_rendered_file: PnmFile = ...
    current_color_model: ColorFormat = ColorFormat.RGB

    def __init__(
            self,
    ):
        super().__init__()
        self.setWindowTitle("Best redactor ever")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.render_button = QPushButton("Render image", self)
        self.render_button.clicked.connect(self.render_image)

        self.clear_picture_button = QPushButton("Clear", self)
        self.clear_picture_button.clicked.connect(self.clear_picture)

        self.edit_file_button = QPushButton("Edit image", self)
        self.edit_file_button.clicked.connect(self.edit_file_content)
        self.color_model_layout = QHBoxLayout()
        self.color_model = QComboBox(self)
        self.color_model.addItems(config.COLOR_MODELS)
        self.color_model.currentIndexChanged.connect(self.change_color_model)
        # self.color_model_label = QLabel('Change color model', self)
        # self.color_model_layout.addWidget(self.color_model_label)

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addWidget(self.render_button)
        self.toolbar.addWidget(self.edit_file_button)
        self.toolbar.addWidget(self.clear_picture_button)
        self.toolbar.addWidget(self.color_model)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.edit_file_window = EditFileWindow()

    def change_color_model(
            self,
    ):
        color_model = ColorFormat[self.color_model.currentText()]
        if self.selected_file is Ellipsis:
            raise Exception("Upload any file")  # todo
        # todo: remove copy paste
        try:
            with PnmIO(self.selected_file, mode='rb') as r:
                pnm_file = r.read_for_ui()
                converter = ColorConverter(color_model)
                pnm_file.content = converter.convert(self.current_color_model, pnm_file.content, pnm_file.bytes_per_pixel)
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return
        try:
            with PnmIO(self.selected_file, 'wb') as f:
                f.write(
                    pnm_format=pnm_file.pnm_format,
                    width=pnm_file.width,
                    height=pnm_file.height,
                    image_content=pnm_file.content,
                    max_color_value=pnm_file.max_color,
                )
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            if not os.path.getsize(self.selected_file):
                os.remove(self.selected_file)
            return
        self.current_color_model = color_model

    def render_image(
            self,
    ):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        if not self.selected_file:
            return

        self.option = Option.RENDER
        self.update()

    def clear_picture(
            self,
    ):
        self.option = Option.NOTHING
        self.update()

    def edit_file_content(
            self,
    ):
        logs.info('Edit file')
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        if not self.selected_file:
            return

        self.option = Option.EDITING
        try:
            with PnmIO(self.selected_file, mode='rb') as r:
                pnm_file = r.read_for_ui()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        self.edit_file_window.show()
        self.edit_file_window.edit_file(
            pnm_format=pnm_file.pnm_format,
            width=pnm_file.width,
            height=pnm_file.height,
            max_color=pnm_file.max_color,
            bytes_per_pixel=pnm_file.bytes_per_pixel,
            content=pnm_file.content,
        )

    def real_render_image(
            self,
    ):
        painter = QPainter(self)
        try:
            with PnmIO(self.selected_file, mode='rb') as r:
                pnm_file = r.read()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        for i in range(
                0,
                pnm_file.get_size(),
                pnm_file.bytes_per_pixel,
        ):
            rgb = pnm_file.content[i: i + pnm_file.bytes_per_pixel]
            if pnm_file.bytes_per_pixel == 1:
                rgb *= 3

            painter.setPen(QColor(*rgb))
            real_position = i // pnm_file.bytes_per_pixel
            painter.drawPoint(
                real_position % pnm_file.width, real_position // pnm_file.width
            )
        painter.end()

    def paintEvent(
            self,
            e: QtGui.QPaintEvent,
    ):
        if self.option == Option.RENDER:
            logs.info('Render image')
            self.real_render_image()

        # setting option for nothing
        # because when resizing window it's reading file again
        self.option = Option.NOTHING

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
)

from src.errors.pnm import PnmError
from src.files.pnm import PnmFile
from src.typedef import logs
from src.ui.errors import PnmFileErrorMessage


class Option(enum.Enum):
    NOTHING = 0
    RENDER = 1
    EDITING = 2
    PREVIEW = 3


class EditFileWindow(QWidget):
    picture_format: QLineEdit
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
        self.picture_format = QLineEdit(self)
        self.picture_format_label = QLabel('Format', self)
        self.layout().addWidget(self.picture_format_label)
        self.layout().addWidget(self.picture_format)

        self.picture_max_color = QLineEdit(self)
        self.picture_max_color_label = QLabel('Max color', self)
        self.layout().addWidget(self.picture_max_color_label)
        self.layout().addWidget(self.picture_max_color)

    def setup_content(
        self,
    ):
        self.picture_content = QTableWidget(self)
        self.picture_content_label = QLabel('Content', self)
        self.picture_content.setFixedSize(500, 500)
        self.picture_content.verticalHeader().hide()
        self.picture_content.horizontalHeader().hide()
        self.layout().addWidget(self.picture_content_label)
        self.layout().addWidget(self.picture_content)

    def edit_file(
        self,
        pnm_format: str,
        width: int,
        height: int,
        max_color: int,
        bytes_per_pixel: int,
        content: typing.Tuple[int],
    ):
        self.picture_format.setText(pnm_format)
        self.picture_max_color.setText(str(max_color))
        self.picture_content_label.setText(
            f'Content {width}, {height}, {bytes_per_pixel}'
        )
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
        content: typing.Optional[typing.Tuple[int]] = None,
    ):
        self.picture_content.setColumnCount(width)
        self.picture_content.setRowCount(height)
        for i in range(
            0,
            width * height * bytes_per_pixel,
            bytes_per_pixel,
        ):
            real_position = i // bytes_per_pixel
            self.picture_content.setItem(
                real_position // width,
                real_position % width,
                QTableWidgetItem(
                    ','.join(str(x) for x in content[i: i + bytes_per_pixel])
                ),
            )

    def save_changes(
        self,
    ):
        saved_file = QFileDialog.getSaveFileName(self, "Save File", "", "")[0]
        if not saved_file:
            return
        model = self.picture_content.model()
        content = []
        for i in range(model.rowCount()):
            for j in range(model.columnCount()):
                content.extend([int(x) for x in model.index(i, j).data().split(',')])

        try:
            with PnmFile(saved_file, 'wb') as f:
                f.write(
                    pnm_format=self.picture_format.text(),
                    width=int(self.picture_content.model().columnCount()),
                    height=int(self.picture_content.model().rowCount()),
                    image_content=content,
                    max_color_value=int(self.picture_max_color.text()),
                )
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            if not os.path.getsize(saved_file):
                os.remove(saved_file)
            return

        self.close()


class Window(QMainWindow):
    option = Option.NOTHING
    selected_file: str = ...

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

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addWidget(self.render_button)
        self.toolbar.addWidget(self.edit_file_button)
        self.toolbar.addWidget(self.clear_picture_button)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.edit_file_window = EditFileWindow()

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
            with PnmFile(self.selected_file, mode='rb') as reader:
                content = reader.read_for_ui()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        self.edit_file_window.show()
        self.edit_file_window.edit_file(
            pnm_format=reader.pnm_format,
            width=reader.width,
            height=reader.height,
            max_color=reader.max_color_value,
            bytes_per_pixel=reader.bytes_per_pixel,
            content=content,
        )

    def real_render_image(
        self,
    ):
        painter = QPainter(self)
        try:
            with PnmFile(self.selected_file, mode='rb') as reader:
                content = reader.read()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        for i in range(
            0,
            reader.width * reader.height * reader.bytes_per_pixel,
            reader.bytes_per_pixel,
        ):
            painter.setPen(QColor(*content[i: i + reader.bytes_per_pixel]))
            real_position = i // reader.bytes_per_pixel
            painter.drawPoint(
                real_position % reader.width, real_position // reader.width
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

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
    QPlainTextEdit,
    QLineEdit,
    QLabel,
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
    picture_width: QLineEdit
    picture_width_label: QLabel
    picture_height: QLineEdit
    picture_height_label: QLabel
    picture_max_color: QLineEdit
    picture_max_color_label: QLabel
    picture_content: QPlainTextEdit
    picture_content_label: QLabel

    def __init__(
        self,
    ):
        super().__init__()
        self.setWindowTitle('Edit PNM file')
        self.setGeometry(0, 0, 500, 500)
        self.setLayout(QVBoxLayout())

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_changes)  # type: ignore
        self.layout().addWidget(self.save_button)

        self.setup_header()
        self.setup_content()

    def setup_header(
        self,
    ):
        self.picture_format = QLineEdit(self)
        self.picture_format_label = QLabel('Format', self)
        self.layout().addWidget(self.picture_format_label)
        self.layout().addWidget(self.picture_format)

        self.picture_width = QLineEdit(self)
        self.picture_width_label = QLabel('Width', self)
        self.layout().addWidget(self.picture_width_label)
        self.layout().addWidget(self.picture_width)

        self.picture_height = QLineEdit(self)
        self.picture_height_label = QLabel('Height', self)
        self.layout().addWidget(self.picture_height_label)
        self.layout().addWidget(self.picture_height)

        self.picture_max_color = QLineEdit(self)
        self.picture_max_color_label = QLabel('Max color', self)
        self.layout().addWidget(self.picture_max_color_label)
        self.layout().addWidget(self.picture_max_color)

    def setup_content(
        self,
    ):
        self.picture_content = QPlainTextEdit(self)
        self.picture_content_label = QLabel('Content', self)
        self.layout().addWidget(self.picture_content_label)
        self.layout().addWidget(self.picture_content)

    def edit_file(
        self,
        pnm_format: str,
        width: int,
        height: int,
        max_color: int,
        content: typing.Tuple[int],
    ):
        self.picture_format.setText(pnm_format)
        self.picture_width.setText(str(width))
        self.picture_height.setText(str(height))
        self.picture_max_color.setText(str(max_color))
        self.picture_content.setPlainText(' '.join((str(x) for x in content)))

    def save_changes(
        self,
    ):
        if not (
            saved_file := QFileDialog.getSaveFileName(self, "Save File", "", "")[0]
        ):
            return

        try:
            with PnmFile(saved_file, 'wb') as f:
                f.write(
                    pnm_format=self.picture_format.text(),
                    width=int(self.picture_width.text()),
                    height=int(self.picture_height.text()),
                    image_content=tuple(
                        int(x) for x in self.picture_content.toPlainText().split()
                    ),
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
        self.setWindowTitle("Test")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.render_button = QPushButton("Render image", self)
        # noinspection PyUnresolvedReferences
        self.render_button.clicked.connect(self.render_image)

        self.clear_picture_button = QPushButton("Clear", self)
        # noinspection PyUnresolvedReferences
        self.clear_picture_button.clicked.connect(self.clear_picture)

        self.edit_file_button = QPushButton("Edit image", self)
        # noinspection PyUnresolvedReferences
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
        match self.option:
            case Option.RENDER:
                logs.info('Render image')
                self.real_render_image()

        self.option = Option.NOTHING

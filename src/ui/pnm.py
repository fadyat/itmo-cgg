import enum
import logging
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
)

from src.errors.pnm import PnmError
from src.files.pnm import PnmFile
from src.ui.errors import PnmFileErrorMessage


class Option(enum.Enum):
    NOTHING = 0
    RENDER = 1
    EDITING = 2


class EditFileWindow(QWidget):

    def __init__(
        self,
    ):
        super().__init__()
        self.setWindowTitle('Edit PNM file')
        self.setGeometry(0, 0, 500, 500)
        self.setLayout(QVBoxLayout())

        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_changes)  # type: ignore

        self.text_field = QPlainTextEdit(self)
        self.layout().addWidget(self.text_field)
        self.layout().addWidget(self.save_button)

    def edit_file(
        self,
        content: typing.Tuple[int],
    ):
        self.text_field.setPlainText(
            ' '.join((str(x) for x in content))
        )

    def save_changes(
        self,
    ):
        ...


class Window(QMainWindow):
    option = Option.NOTHING
    selected_file: str = ...

    def __init__(
        self,
    ):
        super().__init__()
        self.setWindowTitle("Test")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.render_button = QPushButton("Click me", self)
        # noinspection PyUnresolvedReferences
        self.render_button.clicked.connect(self.render_image)

        self.clear_picture_button = QPushButton("Clear", self)
        # noinspection PyUnresolvedReferences
        self.clear_picture_button.clicked.connect(self.clear_picture)

        self.edit_file_button = QPushButton("Edit file", self)
        # noinspection PyUnresolvedReferences
        self.edit_file_button.clicked.connect(self.edit_file_content)

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addWidget(self.render_button)
        self.toolbar.addWidget(self.edit_file_button)
        self.toolbar.addWidget(self.clear_picture_button)
        self.toolbar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.edit_file_window = EditFileWindow()

    def render_image(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        if not self.selected_file:
            return

        self.option = Option.RENDER
        self.update()

    def clear_picture(self):
        self.option = Option.NOTHING
        self.update()

    def edit_file_content(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        if not self.selected_file:
            return

        self.option = Option.EDITING
        logs.info('Edit file')
        try:
            with PnmFile(self.selected_file, mode='rb') as reader:
                content = reader.read_for_ui()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e), self, logs).show()
            return

        self.edit_file_window.show()
        self.edit_file_window.edit_file(content)

    def real_render_image(self):
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
            painter.setPen(QColor(content[i], content[i + 1], content[i + 2]))
            real_position = i // reader.bytes_per_pixel
            painter.drawPoint(
                real_position % reader.width,
                real_position // reader.width
            )
        painter.end()

    def paintEvent(
        self,
        e: QtGui.QPaintEvent,
    ):
        logs.info('Paint event')
        match self.option:
            case Option.NOTHING:
                logs.info('Nothing to do')
                pass
            case Option.RENDER:
                logs.info('Render image')
                self.real_render_image()

        self.option = Option.NOTHING


# fixme
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logs = logging.getLogger(__name__)

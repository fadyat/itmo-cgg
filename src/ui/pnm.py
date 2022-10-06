from PyQt6.QtGui import QPainter, QColor, QPaintEvent
from PyQt6.QtWidgets import (
    QPushButton,
    QWidget,
    QFileDialog,
    QVBoxLayout,
    QApplication,
    QPlainTextEdit,
)

from src.errors.pnm import PnmError
from src.files.pnm import PnmFile
from src.ui.errors import PnmFileErrorMessage


# todo: split class into smaller ones
class PnmWidget(QWidget):
    render_button: QPushButton = ...
    selected_file: str | None = None
    is_rendering: bool = False

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 500, 500)
        self.centralize()
        self.setWindowTitle("Pnm reader")
        self.setLayout(QVBoxLayout())
        self.setup_render_button()
        self.setup_edit_button()

    def centralize(self):
        qr = self.frameGeometry()
        qr.moveCenter(self.screen().availableGeometry().center())
        self.move(qr.topLeft())

    def setup_render_button(self):
        self.render_button = QPushButton("Render image")
        # noinspection PyUnresolvedReferences
        self.render_button.clicked.connect(self.select_file_for_rendering)
        self.layout().addWidget(self.render_button)

    def setup_edit_button(self):
        edit_button = QPushButton("Edit image")
        # noinspection PyUnresolvedReferences
        edit_button.clicked.connect(self.select_file_for_editing)
        self.layout().addWidget(edit_button)

    def select_file_for_rendering(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        self.is_rendering = True
        self.update()

    def select_file_for_editing(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        self.is_rendering = False
        self.update()

    def paintEvent(self, event: QPaintEvent):
        QWidget.paintEvent(self, event)
        if not self.selected_file:
            return

        if self.is_rendering:
            qp = QPainter()
            qp.begin(self)
            self.render_picture(qp)
            qp.end()
        else:
            ...

    def render_picture(self, qp):
        try:
            # todo: he draws a picture all right, but it's
            #  done always when the window is resized or closed etc.
            with PnmFile(self.selected_file, mode='rb') as reader:
                content = reader.read_all()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(
                message=str(e),
                parent=self,
            ).show()
            self.selected_file = None
            return

        # it's doesn't work with picture have width more than screen width
        # it's doesn't work with picture have height more than screen height
        self.setGeometry(0, 0, reader.width, reader.height)

        # todo: optimize this
        for i in range(
            0,
            reader.width * reader.height * reader.bytes_per_pixel,
            reader.bytes_per_pixel,
        ):
            qp.setPen(QColor(content[i], content[i + 1], content[i + 2]))
            real_position = i // reader.bytes_per_pixel
            qp.drawPoint(real_position % reader.width, real_position // reader.width)

    def edit_picture(self, qp):
        with PnmFile(self.selected_file, mode='rb') as reader:
            content = reader.read_all()


class TextEditor(QWidget):
    text_edit: QPlainTextEdit = ...

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.setGeometry(400, 400, 350, 300)
        self.setup_text_edit()

    def setup_text_edit(self):
        # todo: optimize file editing
        # todo: pass file from select button
        self.text_edit = QPlainTextEdit(self)
        self.text_edit.resize(500, 500)
        with PnmFile('../../docs/shrek.pnm', mode='rb') as reader:
            content = reader.read_all()

        # self.text_edit.setPlainText(str(content))
        self.text_edit.setPlainText("hello")

    def setup_save_edited_file_button(self):
        save_button = QPushButton("Save")
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.save_edited_file)
        self.layout().addWidget(save_button)

    def save_edited_file(self):
        # todo: save edited file
        # understand to read it correct??
        # using self.text_edit.toPlainText()
        ...


def main():
    app = QApplication([])
    editor = TextEditor()
    editor.show()
    app.exec()


if __name__ == '__main__':
    main()

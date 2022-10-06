from PyQt6.QtGui import QPainter, QColor, QPaintEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QFileDialog, QVBoxLayout

from src.errors.pnm import PnmError
from src.files.pnm import PnmFile
from src.ui.errors import PnmFileErrorMessage


class PnmWidget(QWidget):
    selected_file = None

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setWindowTitle("Pnm reader")
        self.setGeometry(0, 0, 500, 500)
        self.setLayout(layout)
        self.button = QPushButton("Render image")
        layout.addWidget(self.button)
        # noinspection PyUnresolvedReferences
        self.button.clicked.connect(self.select_file)

    def select_file(self):
        self.selected_file = QFileDialog.getOpenFileName(self, "Open File", "", "")[0]
        self.update()

    def paintEvent(self, event: QPaintEvent):
        QWidget.paintEvent(self, event)
        if self.selected_file:
            qp = QPainter()
            qp.begin(self)
            self.draw_picture(qp)
            qp.end()

    def draw_picture(self, qp):
        try:
            # todo: he draws a picture all right, but it's
            #  done always when the window is resized or closed etc.
            with PnmFile(self.selected_file, mode='rb') as reader:
                content = reader.read_all()
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            PnmFileErrorMessage(str(e))  # fixme:  Recursive repaint detected
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

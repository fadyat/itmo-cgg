from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QPushButton, QWidget, QFileDialog, QVBoxLayout

from src.decorators import catch_with_error_message
from src.files.pnm import PnmFile


class PnmWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(SelectFileButton())
        self.setWindowTitle("Pnm reader")
        self.setGeometry(0, 0, 500, 500)
        self.setLayout(layout)


class SelectFileButton(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("Select file")
        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.get_file)

    @catch_with_error_message
    def get_file(self, *args, **kwargs):
        filename = QFileDialog.getOpenFileName(self, "Open File", "", "")
        with PnmFile(filename[0], mode='rb') as reader:
            content = reader.read_all()

        print('valid')
        ...


class Painter(QWidget):
    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_picture(qp)
        qp.end()

    def draw_picture(self, qp):
        # todo: he draws a picture all right, but it's
        #  done always when the window is resized or closed etc.
        with PnmFile(self.image_path, mode='rb') as reader:
            content = reader.read_all()

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

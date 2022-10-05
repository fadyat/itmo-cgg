from PyQt6.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget

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

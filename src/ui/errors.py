from PyQt6.QtWidgets import QMessageBox


class PnmFileErrorMessage(QMessageBox):

    def __init__(self):
        super().__init__()
        self.setIcon(QMessageBox.Icon.Critical)
        self.setText('Error')
        self.setInformativeText('Invalid file')
        self.setWindowTitle('Error')

from PyQt6.QtWidgets import QMessageBox


class PnmFileErrorMessage(QMessageBox):
    def __init__(self, message):
        super().__init__()
        self.setIcon(QMessageBox.Icon.Critical)
        self.setInformativeText(message)
        self.setWindowTitle(message)
        self.exec()

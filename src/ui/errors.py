from PyQt6.QtWidgets import QMessageBox, QWidget


class PnmFileErrorMessage(QMessageBox):
    def __init__(
        self,
        message: str,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setInformativeText(message)
        self.setWindowTitle(message)

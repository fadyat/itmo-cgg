import logging

from PyQt6.QtWidgets import QMessageBox, QWidget


class FileErrorMessage(QMessageBox):
    def __init__(
        self,
        message: str,
        parent: QWidget,
        logs: logging.Logger,
    ):
        super().__init__(parent)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setInformativeText(message)
        self.setWindowTitle(message)
        logs.error(message)

from PyQt6.QtWidgets import QLabel


def create_beauty_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("QLabel { font-size: 10px; }")
    return label

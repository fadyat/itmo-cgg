from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QStyleFactory, QHBoxLayout, QPushButton

from src.utils.gamma import GammaOption
from src.utils.label import create_beauty_label


class GammaWidget(QWidget):
    gamma_from: float = 2.4
    gamma_to: float = 2.4

    def __init__(
        self,
        parent: QWidget,
    ):
        super().__init__()
        self.parent = parent

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.from_layout = QHBoxLayout()
        self.from_layout.addWidget(create_beauty_label("Gamma from: "))
        self.from_gamma_input = QLineEdit()
        self.from_gamma_input.setText(str(self.gamma_from))
        self.from_gamma_input.setStyle(QStyleFactory.create("Fusion"))
        self.from_gamma_input.setStyleSheet("QLineEdit { font-size: 10px; padding-left: 5px; }")
        self.from_gamma_input.setEnabled(False)
        self.from_layout.addStretch()
        self.from_layout.addWidget(self.from_gamma_input)
        self.layout.addLayout(self.from_layout)

        self.to_layout = QHBoxLayout()
        self.to_layout.addWidget(create_beauty_label("Gamma to:"))
        self.to_gamma_input = QLineEdit()
        self.to_gamma_input.setText(str(self.gamma_to))
        self.to_gamma_input.setStyle(QStyleFactory.create("Fusion"))
        self.to_gamma_input.setStyleSheet("QLineEdit { font-size: 10px; padding-left: 5px; }")
        self.to_layout.addStretch()
        self.to_layout.addWidget(self.to_gamma_input)
        self.layout.addLayout(self.to_layout)

        self.gamma_options_layout = QHBoxLayout()
        self.apply_gamma_button = QPushButton("Assign gamma")
        self.apply_gamma_button.clicked.connect(self.assign_gamma)
        self.apply_gamma_button.setStyle(QStyleFactory.create("Fusion"))
        self.apply_gamma_button.setStyleSheet("QPushButton { font-size: 10px; }")
        self.gamma_options_layout.addWidget(self.apply_gamma_button)

        self.convert_gamma_button = QPushButton("Convert gamma")
        self.convert_gamma_button.clicked.connect(self.convert_gamma)
        self.convert_gamma_button.setStyle(QStyleFactory.create("Fusion"))
        self.convert_gamma_button.setStyleSheet("QPushButton { font-size: 10px; }")
        self.gamma_options_layout.addWidget(self.convert_gamma_button)
        self.layout.addLayout(self.gamma_options_layout)

    def get_from_gamma(self) -> float:
        try:
            gamma = float(self.from_gamma_input.text())
        except ValueError:
            gamma = 2.4
            self.from_gamma_input.setText("2.4")

        return gamma

    def get_to_gamma(self) -> float:
        try:
            gamma = float(self.to_gamma_input.text())
        except ValueError:
            gamma = 2.4
            self.to_gamma_input.setText("2.4")

        return gamma

    def assign_gamma(self):
        self.close()
        self.parent.apply_gamma(GammaOption.ASSIGN)  # type: ignore

    def convert_gamma(self):
        self.close()
        self.parent.apply_gamma(GammaOption.CONVERT)  # type: ignore

    def set_from_gamma(self, gamma: float):
        self.from_gamma_input.setText(str(gamma))

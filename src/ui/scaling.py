from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, \
    QStyleFactory, QMessageBox, QComboBox

from src import config
from src.utils.label import create_beauty_label
from src.utils.scaling.resolver import ScalingAlgo


class ScalingWidget(QWidget):

    def __init__(
        self,
        main_window: QWidget,
    ):
        super().__init__()
        self.main_window = main_window

        self.width_layout = QHBoxLayout()
        self.width_layout.addWidget(create_beauty_label('Width:'))
        self.width_input = QLineEdit()
        self.width_input.setStyle(QStyleFactory.create('Fusion'))
        self.width_layout.addStretch()
        self.width_layout.addWidget(self.width_input)

        self.height_layout = QHBoxLayout()
        self.height_layout.addWidget(create_beauty_label('Height:'))
        self.height_input = QLineEdit()
        self.height_input.setStyle(QStyleFactory.create('Fusion'))
        self.height_layout.addStretch()
        self.height_layout.addWidget(self.height_input)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.width_layout)
        self.main_layout.addLayout(self.height_layout)
        self.setLayout(self.main_layout)

        self.scaling_algorithm_layout = QHBoxLayout()
        self.scaling_algorithm_layout.addWidget(create_beauty_label('Algorithm:'))
        self.scaling_algorithm_selector = QComboBox(self)
        self.scaling_algorithm_selector.addItems(config.SCALING_ALGORITHMS)
        self.scaling_algorithm_selector.setStyle(QStyleFactory.create('Fusion'))
        self.scaling_algorithm_selector.setStyleSheet(
            "QComboBox { font-size: 10px; }"
        )
        self.scaling_algorithm_layout.addStretch()
        self.scaling_algorithm_layout.addWidget(self.scaling_algorithm_selector)
        self.main_layout.addLayout(self.scaling_algorithm_layout)

        self.displacement_layout = QHBoxLayout()
        self.displacement_layout.addWidget(create_beauty_label('Displacement:'))
        self.displacement_input_x = QLineEdit()
        self.displacement_input_x.setStyle(QStyleFactory.create('Fusion'))
        self.displacement_input_x.setText('0')
        self.displacement_layout.addStretch()
        self.displacement_layout.addWidget(self.displacement_input_x)

        self.displacement_input_y = QLineEdit()
        self.displacement_input_y.setStyle(QStyleFactory.create('Fusion'))
        self.displacement_input_y.setText('0')
        self.displacement_layout.addStretch()
        self.displacement_layout.addWidget(self.displacement_input_y)
        self.main_layout.addLayout(self.displacement_layout)

        self.apply_scaling_button = QPushButton('Apply')
        self.apply_scaling_button.clicked.connect(self.apply_scaling)
        self.apply_scaling_button.setStyle(QStyleFactory.create('Fusion'))
        self.apply_scaling_button.setStyleSheet('QPushButton { font-size: 10px; }')
        self.main_layout.addWidget(self.apply_scaling_button)

        self.validation_notifier = QMessageBox()
        self.validation_notifier.setWindowTitle('Error')
        self.validation_notifier.setText('Width and height must\nbe positive integers')
        self.validation_notifier.setStyle(QStyleFactory.create('Fusion'))
        self.validation_notifier.setStyleSheet(
            'QMessageBox { font-size: 10px; } QPushButton { font-size: 10px; }'
        )
        self.validation_notifier.setIcon(QMessageBox.Icon.Warning)

    def apply_scaling(self):
        width = self.get_width()
        height = self.get_height()

        if width == 0 or height == 0:
            self.validation_notifier.show()
            return

        self.close()
        self.main_window.apply_scaling()  # type: ignore

    def get_width(self) -> int:
        try:
            width = int(self.width_input.text())
        except ValueError:
            width = 0

        return width

    def get_height(self) -> int:
        try:
            height = int(self.height_input.text())
        except ValueError:
            height = 0

        return height

    def get_scaling_algorithm(self) -> ScalingAlgo:
        return ScalingAlgo[self.scaling_algorithm_selector.currentText()]

    def set_width(self, width: int):
        self.width_input.setText(str(width))

    def set_height(self, height: int):
        self.height_input.setText(str(height))

    def get_displacement_x(self) -> int:
        try:
            displacement_x = int(self.displacement_input_x.text())
        except ValueError:
            displacement_x = 0

        return displacement_x

    def get_displacement_y(self) -> int:
        try:
            displacement_y = int(self.displacement_input_y.text())
        except ValueError:
            displacement_y = 0

        return displacement_y

    def set_displacement_x(self, displacement_x: int):
        self.displacement_input_x.setText(str(displacement_x))

    def set_displacement_y(self, displacement_y: int):
        self.displacement_input_y.setText(str(displacement_y))

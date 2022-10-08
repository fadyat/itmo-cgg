import sys

import fire
from PyQt6.QtWidgets import QApplication

from src.ui.pnm import Window


def ui():
    app = QApplication(sys.argv)
    Window().show()
    sys.exit(app.exec())


if __name__ == '__main__':
    fire.Fire({'ui': ui})

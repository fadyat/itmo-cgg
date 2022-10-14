import os.path
import sys

import fire
from PyQt5.QtWidgets import QApplication

from src.ui.pnm import Window


def repo_root():
    return os.path.abspath(os.path.join(__file__, os.path.pardir))


def ui():
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    fire.Fire({'ui': ui})

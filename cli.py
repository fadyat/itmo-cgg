import fire
from PyQt6.QtWidgets import QApplication

from src.decorators import catch
from src.files.pnm import PnmFile
from src.ui.pnm import PnmWidget


@catch
def read_pnm(
    image_path: str = './docs/shrek.pnm',
):
    with PnmFile(image_path, mode='rb') as reader:
        reader.read_all()


@catch
def write_pnm(
    image_path: str = './docs/shrek.pnm',
    output_path: str = './docs/shrek_copy.pnm',
):
    with PnmFile(image_path, mode='rb') as reader:
        picture_body = reader.read_all()

    with PnmFile(output_path, mode='wb') as writer:
        writer.write(
            pnm_format=reader.pnm_format,
            width=reader.width,
            height=reader.height,
            image_content=picture_body,
            max_color_value=reader.max_color_value,
        )


def ui():
    app = QApplication([])
    pnm_window = PnmWidget()
    pnm_window.show()
    app.exec()


if __name__ == '__main__':
    fire.Fire({'read': read_pnm, 'write': write_pnm, 'ui': ui})

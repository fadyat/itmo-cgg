import fire

from src.readers.pnm import PnmReader


def read_pnm(
    image_path: str = './docs/shrek.pnm',
):
    with PnmReader(image_path) as reader:
        reader.read_header()


if __name__ == '__main__':
    fire.Fire({
        'read': read_pnm,
    })

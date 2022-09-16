import typing

from src import config
from src.errors.pnm import PnmHeaderError


class PnmReader:
    __encoding = 'utf-8'

    def __init__(self, image_path: str):
        self.__image_path = image_path

    def get_file(self):
        return self.__file

    def __enter__(self):
        self.__file = open(self.__image_path, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()

    def read_header(
        self,
    ):
        # doesn't support comments in a header
        self.__file.seek(0)
        pnm_format = self.__get_pnm_format()
        width, height = self.__get_file_size()
        max_color_value = self.__get_max_color_value()

        # todo: remove
        print(pnm_format, width, height, max_color_value)

    def __read_line(self) -> str:
        return self.__file.readline().decode(self.__encoding).strip()

    def __get_pnm_format(self) -> str:

        if (pnm_format := self.__read_line()) not in config.PNM_SUPPORTED_FORMATS:
            raise PnmHeaderError('Unsupported format %s' % pnm_format)

        return pnm_format

    def __get_file_size(self) -> typing.Tuple[int, int]:
        file_size = self.__read_line()

        try:
            width, height = tuple(map(int, file_size.split(' ')))
        except ValueError:
            raise PnmHeaderError('Invalid file size %s' % file_size)

        return width, height

    def __get_max_color_value(self) -> int:
        max_color_value = self.__file.readline().decode(self.__encoding).strip()

        try:
            max_color_value = int(max_color_value)
        except ValueError:
            raise PnmHeaderError('Invalid max color value %s' % max_color_value)

        if max_color_value > 255:
            raise PnmHeaderError('Max color value %s is too big' % max_color_value)

        return max_color_value

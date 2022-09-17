import typing

from src import config
from src.validators.pnm import (
    validate_max_color,
    validate_width_and_height,
    validate_pnm_format,
    validate_file,
)


class PnmReader:
    pnm_format = ...
    width = ...
    height = ...
    max_color_value = ...
    bytes_per_pixel = ...

    def __init__(
        self,
        image_path: str,
    ):
        self.__image_path = image_path

    def __enter__(
        self,
    ) -> 'PnmReader':
        self.__file = open(self.__image_path, 'rb')
        return self

    def __exit__(
        self,
        exc_type: typing.Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: typing.Any | None,
    ):
        self.__file.close()

    def read(
        self,
    ):
        validate_file(self.__file)
        self.__read_header()
        yield from self.__read_body()

    def __read_header(
        self,
    ):
        self.__file.seek(0)
        self.pnm_format = self.__get_pnm_format()
        self.bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[self.pnm_format]
        self.width, self.height = self.__get_file_size()
        self.max_color_value = self.__get_max_color_value()

    def __read_body(
        self,
    ):
        # todo: могут быть мемы когда значение ширины не кратно 3, надо подумать и почитать
        for y in range(self.height):
            for x in range(0, self.width, self.bytes_per_pixel):
                # todo: возвращать массив пикселей, а не массив байт?
                # понадобится для рисовалки картиночек, надо обсудить

                # todo: добавить валидацию значений пикселей через ord(byte)
                yield self.__file.read(self.bytes_per_pixel)

    def __read_line(
        self,
    ) -> str:
        return self.__file.readline().decode('utf-8').strip()

    def __get_pnm_format(
        self,
    ) -> str:
        pnm_format = self.__read_line()
        return validate_pnm_format(pnm_format)

    def __get_file_size(
        self,
    ) -> typing.Tuple[int, int]:
        file_size = self.__read_line()
        return validate_width_and_height(file_size)

    def __get_max_color_value(
        self,
    ) -> int:
        max_color_value = self.__read_line()
        return validate_max_color(max_color_value)

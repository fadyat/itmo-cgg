import typing

from src import config
from src.errors.pnm import PnmError
from src.validators.pnm import (
    validate_max_color,
    validate_width_and_height,
    validate_pnm_format,
    validate_file,
    validate_image_content,
)


class PnmFile:
    pnm_format = ...
    width = ...
    height = ...
    max_color_value = ...
    bytes_per_pixel = ...

    def __init__(
        self,
        image_path: str,
        mode='rb',
    ):
        self.__image_path = image_path
        self.mode = mode

    def __enter__(
        self,
    ) -> 'PnmFile':
        # mypy complains, when not passed a mode directly to open
        self.__file = open(self.__image_path, self.mode)  # type: ignore
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()
        self.__file = None

    def read(
        self,
    ) -> bytes:
        validate_file(self.__file)  # type: ignore
        self.__read_header()
        content = self.__file.read(self.width * self.height * self.bytes_per_pixel)

        if self.__file.read(1):
            raise PnmError("Wrong file size in header")

        return content  # type: ignore

    def read_for_ui(
        self,
    ) -> typing.Tuple[int]:
        validate_file(self.__file)  # type: ignore
        self.__read_header()

        content = tuple(
            ord(self.__file.read(1))
            for _ in range(self.width)
            for _ in range(self.height)
            for _ in range(self.bytes_per_pixel)
        )

        if self.__file.read(1):
            raise PnmError("Wrong file size in header")

        return content  # type: ignore

    def __read_header(
        self,
    ):
        self.__file.seek(0)
        self.pnm_format = self.__get_pnm_format()
        self.bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[self.pnm_format]
        self.width, self.height = self.__get_file_size()
        self.max_color_value = self.__get_max_color_value()

    def __read_line(
        self,
    ) -> str:
        return self.__file.readline().decode('utf-8').strip()  # type: ignore

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

    def write(
        self,
        pnm_format: str,
        height: int,
        width: int,
        image_content: typing.Tuple[int],
        max_color_value: int = 255,
    ):
        validate_file(self.__file)  # type: ignore
        validate_image_content(
            image_content=image_content,
            width=width,
            height=height,
            bytes_per_pixel=config.PNM_BYTES_PER_PIXEL[pnm_format],
        )

        self.__write_header(
            pnm_format=pnm_format,
            height=height,
            width=width,
            max_color_value=max_color_value,
        )
        self.__write_body(
            image_content=image_content,
        )

    def __write_header(
        self,
        pnm_format: str,
        height: int,
        width: int,
        max_color_value: int,
    ):
        self.__write_pnm_format(pnm_format)
        self.__write_file_size(width, height)
        self.__write_max_color_value(max_color_value)

    def __write_body(
        self,
        image_content: typing.Sequence[int],
    ):
        for color_code in image_content:
            self.__file.write(color_code.to_bytes(1, 'big'))  # type: ignore

    def __write_line(
        self,
        line: str | int,
    ):
        self.__file.write(f"{line}\n".encode('utf-8'))  # type: ignore

    def __write_pnm_format(
        self,
        pnm_format: str,
    ):
        validate_pnm_format(pnm_format)
        self.__write_line(pnm_format)

    def __write_file_size(
        self,
        width: int,
        height: int,
    ):
        validate_width_and_height((width, height))
        self.__write_line(f"{width} {height}")

    def __write_max_color_value(
        self,
        max_color_value: int,
    ):
        validate_max_color(max_color_value)
        self.__write_line(max_color_value)

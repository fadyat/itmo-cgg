import typing

from src import config
from src.entities.pnm import PnmFile, PnmFileUI
from src.errors.pnm import PnmError, PnmSizeError
from src.validators.pnm import (
    validate_max_color,
    validate_width_and_height,
    validate_pnm_format,
    validate_file,
    validate_image_content,
    validate_color_value,
)


class PnmIO:
    __pnm_file: PnmFile

    def __init__(
        self,
        image_path: str,
        mode='rb',
    ):
        self.__image_path = image_path
        self.mode = mode

    def __enter__(
        self,
    ) -> 'PnmIO':
        try:
            self.__file = open(self.__image_path, self.mode)
        except FileNotFoundError:
            raise PnmError("File not found")

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        self.__file.close()
        self.__file = None

    def read(
        self,
    ) -> PnmFile:
        self.__pnm_file = PnmFile()
        validate_file(self.__file)  # type: ignore
        self.__read_header()
        self.__pnm_file.content = self.__file.read(self.__pnm_file.get_size())

        if self.__file.read(1):
            raise PnmSizeError("Wrong file size in header")

        return self.__pnm_file

    def read_for_ui(
        self,
    ) -> PnmFileUI:
        self.__pnm_file = PnmFile()
        validate_file(self.__file)  # type: ignore
        self.__read_header()

        self.__pnm_file.content = [
            ord(self.__file.read(1)) for _ in range(self.__pnm_file.get_size())
        ]

        if self.__file.read(1):
            raise PnmSizeError("Wrong file size in header")

        return PnmFileUI(
            pnm_format=self.__pnm_file.pnm_format,
            width=self.__pnm_file.width,
            height=self.__pnm_file.height,
            max_color=self.__pnm_file.max_color,
            bytes_per_pixel=self.__pnm_file.bytes_per_pixel,
            content=self.__pnm_file.content,
        )

    def __read_header(
        self,
    ):
        self.__file.seek(0)
        self.__pnm_file.pnm_format = self.__get_pnm_format()
        self.__pnm_file.bytes_per_pixel = config.PNM_BYTES_PER_PIXEL[
            self.__pnm_file.pnm_format
        ]
        self.__pnm_file.width, self.__pnm_file.height = self.__get_file_size()
        self.__pnm_file.max_color = self.__get_max_color_value()

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
        image_content: typing.List[int],
        max_color_value: int = 255,
    ):
        try:
            validate_file(self.__file)  # type: ignore
        except AttributeError:
            raise PnmError("File is not opened")

        validate_image_content(
            image_content=image_content,
            width=width,
            height=height,
            pnm_format=pnm_format,
        )

        self.__write_header(
            pnm_format=pnm_format,
            height=height,
            width=width,
            max_color_value=max_color_value,
        )
        self.__write_body(
            image_content=image_content,
            max_color_value=max_color_value,
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
        image_content: typing.List[int],
        max_color_value: int,
    ):
        for color_code in image_content:
            # validate_color_value(color_code, max_color_value) # deprecated
            color_code = 0 if color_code < 0 else color_code and 255 if color_code > 255 else color_code
            self.__file.write(color_code.to_bytes(1, 'big'))  # type: ignore

    def __write_line(
        self,
        line: typing.Union[str, int],
    ):
        return self.__file.write(f"{line}\n".encode('utf-8'))  # type: ignore

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

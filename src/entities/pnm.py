import dataclasses
import typing


@dataclasses.dataclass
class PnmFile:
    def __init__(self):
        pass

    pnm_format: str
    width: int
    height: int
    max_color_value: int
    bytes_per_pixel: int
    content: bytes

    def get_size(self):
        return self.width * self.height * self.bytes_per_pixel


@dataclasses.dataclass
class PnmFileUI:
    pnm_format: str
    width: int
    height: int
    max_color_value: int
    bytes_per_pixel: int
    content: typing.Sequence[int]

    def get_size(self):
        return self.width * self.height * self.bytes_per_pixel

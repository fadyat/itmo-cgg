import dataclasses
import typing


@dataclasses.dataclass
class PnmFile:
    def __init__(self):
        pass

    def create(
        self,
        pnm_format: str,
        width: int,
        height: int,
        max_color: int,
        bytes_per_pixel: int,
        content: bytes,
    ):
        self.pnm_format = pnm_format
        self.width = width
        self.height = height
        self.max_color = max_color
        self.bytes_per_pixel = bytes_per_pixel
        self.content = content
        return self

    pnm_format: str
    width: int
    height: int
    max_color: int
    bytes_per_pixel: int
    content: bytes

    def get_size(self):
        return self.width * self.height * self.bytes_per_pixel


@dataclasses.dataclass
class PnmFileUI:
    pnm_format: str
    width: int
    height: int
    max_color: int
    bytes_per_pixel: int
    content: typing.Sequence[int]

    def get_size(self):
        return self.width * self.height * self.bytes_per_pixel

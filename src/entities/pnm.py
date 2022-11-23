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
    bytes_per_px: int
    content: typing.List[float]

    def get_size(self):
        return self.width * self.height * self.bytes_per_px

    def get_px(self, x, disabled_channels) -> typing.List[float]:
        first_px = x
        colors = self.content[first_px: first_px + self.bytes_per_px]

        if len(colors) == 1:
            colors = [colors[0], colors[0], colors[0]]

        for i, px in enumerate(colors):
            if disabled_channels[i]:
                colors[i] = 0

        return colors

    def set_px(self, x, val):
        for i in range(self.bytes_per_px):
            self.content[x + i] = val[i]

    def get_px_255(self, x, disabled_channels) -> typing.List[int]:

        return [
            min(255, max(int(color * 255), 0))
            for color in self.get_px(x, disabled_channels)
        ]

    def get_x(self, i):
        real_pos = i // self.bytes_per_px
        return real_pos % self.width

    def get_y(self, i):
        real_pos = i // self.bytes_per_px
        return real_pos // self.width

    def __str__(self):
        return f"{self.pnm_format} {self.width} {self.height} {self.max_color} {self.bytes_per_px}"

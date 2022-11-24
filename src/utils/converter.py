import typing
from enum import Enum


class ColorFormat(Enum):
    RGB = 0
    HSL = 1
    HSV = 2
    YCbCr601 = 3
    YCbCr709 = 4
    YCoCg = 5
    CMY = 6


class HueBasedConverter:

    @classmethod
    def count_hue(
        cls,
        pixel: typing.Sequence[float],
    ):
        r, g, b = pixel[0], pixel[1], pixel[2]
        c_min, c_max = min(pixel), max(pixel)
        delta = c_max - c_min

        if delta == 0:
            h = 0
        elif c_max == r:
            h = 60 * (((g - b) / delta) % 6)
        elif c_max == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)

        return h / 360

    @classmethod
    def convert_to_rgb(
        cls,
        hue: float,
        c: float,
        x: float,
        m: float,
    ) -> list[float]:
        if 0 <= hue < 60:
            r, g, b = c, x, 0
        elif 60 <= hue < 120:
            r, g, b = x, c, 0
        elif 120 <= hue < 180:
            r, g, b = 0, c, x
        elif 180 <= hue < 240:
            r, g, b = 0, x, c
        elif 240 <= hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return [r + m, g + m, b + m]


class HslConverter(HueBasedConverter):
    @classmethod
    def rgb_to_hsl(
        cls,
        pixel: list[float],
    ):
        pixel = pixel[0], pixel[1], pixel[2]
        c_min, c_max = min(pixel), max(pixel)
        delta = c_max - c_min

        h = cls.count_hue(pixel)
        s = 0 if delta == 0 else delta / (1 - abs(c_max + c_min - 1))
        l = (c_max + c_min) / 2

        return [h, s, l]

    @classmethod
    def hsl_to_rgb(
        cls,
        pixel: list[float],
    ):
        h, s, l = pixel[0], pixel[1], pixel[2]
        h *= 360
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        return cls.convert_to_rgb(h, c, x, m)


class HsvConverter(HueBasedConverter):

    @classmethod
    def rgb_to_hsv(
        cls,
        pixel: list[float],
    ):
        pixel = pixel[0], pixel[1], pixel[2]
        c_min, c_max = min(pixel), max(pixel)
        delta = c_max - c_min

        h = cls.count_hue(pixel)
        s = 0 if c_max == 0 else delta / c_max
        v = c_max

        return [h, s, v]

    @classmethod
    def hsv_to_rgb(
        cls,
        pixel: list[float],
    ):
        h, s, v = pixel[0], pixel[1], pixel[2]
        h *= 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        return cls.convert_to_rgb(h, c, x, m)


class YCbCrBased:

    @classmethod
    def from_rgb(
        cls,
        pixel: list[float],
        kr: float,
        kb: float,
    ):
        r, g, b = pixel[0], pixel[1], pixel[2]

        y = kr * r + (1 - kr - kb) * g + kb * b
        cb = (b - y) / (2 * (1 - kb))
        cr = (r - y) / (2 * (1 - kr))

        cb += 0.5
        cr += 0.5

        return [y, cb, cr]

    @classmethod
    def to_rgb(
        cls,
        pixel: list[float],
        kr: float,
        kb: float,
    ):
        y, cb, cr = pixel[0], pixel[1], pixel[2]

        cb -= 0.5
        cr -= 0.5

        r = y + 2 * (1 - kr) * cr
        g = y - kb / (1 - kb - kr) * 2 * (1 - kb) * cb - kr / (1 - kb - kr) * 2 * (1 - kr) * cr
        b = y + 2 * (1 - kb) * cb

        return [r, g, b]


class YCbCr601Converter(YCbCrBased):
    kr = 0.299
    kb = 0.114

    @classmethod
    def rgb_to_ycbcr601(
        cls,
        pixel: list[float],
    ):
        return cls.from_rgb(pixel, cls.kr, cls.kb)

    @classmethod
    def ycbcr601_to_rgb(
        cls,
        pixel: list[float],
    ):
        return cls.to_rgb(pixel, cls.kr, cls.kb)


class YCoCgConverter:

    @classmethod
    def rgb_to_ycocg(
        cls,
        pixel: list[float],
    ):
        r, g, b = pixel[0], pixel[1], pixel[2]

        y = r / 4 + g / 2 + b / 4
        co = r / 2 - b / 2
        cg = -r / 4 + g / 2 - b / 4

        co += 0.5
        cg += 0.5

        return [y, co, cg]

    @classmethod
    def ycocg_to_rgb(
        cls,
        pixel: list[float],
    ):
        y, co, cg = pixel[0], pixel[1], pixel[2]

        co -= 0.5
        cg -= 0.5

        r = y + co - cg
        g = y + cg
        b = y - co - cg

        return [r, g, b]


class YCbCr709Converter(YCbCrBased):
    kr = 0.2126
    kb = 0.0722

    @classmethod
    def rgb_to_ycbcr709(
        cls,
        pixel: list[float],
    ):
        return cls.from_rgb(pixel, cls.kr, cls.kb)

    @classmethod
    def ycbcr709_to_rgb(
        cls,
        pixel: list[float],
    ):
        return cls.to_rgb(pixel, cls.kr, cls.kb)


class CmyConverter:

    @classmethod
    def rgb_to_cmy(
        cls,
        pixel: list[float],
    ):
        return [1 - pixel[0], 1 - pixel[1], 1 - pixel[2]]

    @classmethod
    def cmy_to_rgb(
        cls,
        pixel: list[float],
    ):
        return [1 - pixel[0], 1 - pixel[1], 1 - pixel[2]]


class ColorConverter:
    def __init__(
        self,
        convert_to: ColorFormat,
    ):
        self.convert_to = convert_to

    def convert_px(
        self,
        convert_from: ColorFormat,
        px: list[float],
    ):
        if self.convert_to == convert_from:
            return px

        rgb_px = self._convert_to_rgb(convert_from, px, 3)
        return self._convert_from_rgb(self.convert_to, rgb_px, 3)

    @classmethod
    def _convert_to_rgb(
        cls,
        convert_from: ColorFormat,
        content: list[float],
        bytes_per_pixel: int,
    ):
        convertor_function = None
        if convert_from == ColorFormat.RGB:
            return content

        if convert_from == ColorFormat.HSL:
            convertor_function = HslConverter.hsl_to_rgb
        elif convert_from == ColorFormat.HSV:
            convertor_function = HsvConverter.hsv_to_rgb
        elif convert_from == ColorFormat.YCbCr601:
            convertor_function = YCbCr601Converter.ycbcr601_to_rgb
        elif convert_from == ColorFormat.YCbCr709:
            convertor_function = YCbCr709Converter.ycbcr709_to_rgb
        elif convert_from == ColorFormat.CMY:
            convertor_function = CmyConverter.cmy_to_rgb
        elif convert_from == ColorFormat.YCoCg:
            convertor_function = YCoCgConverter.ycocg_to_rgb
        elif convertor_function is None:
            raise ValueError(f"Unsupported color format: {convert_from}")

        return [
            j for i in range(0, len(content), bytes_per_pixel)
            for j in convertor_function(content[i:i + bytes_per_pixel])
        ]

    @classmethod
    def _convert_from_rgb(
        cls,
        convert_to: ColorFormat,
        content: list[float],
        bytes_per_pixel: int,
    ):
        convertor_function = None
        if convert_to == ColorFormat.RGB:
            return content

        if convert_to == ColorFormat.HSL:
            convertor_function = HslConverter.rgb_to_hsl
        elif convert_to == ColorFormat.HSV:
            convertor_function = HsvConverter.rgb_to_hsv
        elif convert_to == ColorFormat.YCbCr601:
            convertor_function = YCbCr601Converter.rgb_to_ycbcr601
        elif convert_to == ColorFormat.YCbCr709:
            convertor_function = YCbCr709Converter.rgb_to_ycbcr709
        elif convert_to == ColorFormat.CMY:
            convertor_function = CmyConverter.rgb_to_cmy
        elif convert_to == ColorFormat.YCoCg:
            convertor_function = YCoCgConverter.rgb_to_ycocg
        elif convertor_function is None:
            raise ValueError(f"Unsupported color format: {convert_to}")

        return [
            j for i in range(0, len(content), bytes_per_pixel)
            for j in convertor_function(content[i:i + bytes_per_pixel])
        ]

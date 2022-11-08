from enum import Enum


class SupportedFormats(Enum):
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
        pixel: list[float],
    ):
        r, g, b = pixel[0] / 255, pixel[1] / 255, pixel[2] / 255
        c_min, c_max = min(r, g, b), max(r, g, b)
        delta = c_max - c_min

        if delta == 0:
            h = 0
        elif c_max == r:
            h = 60 * (((g - b) / delta) % 6)
        elif c_max == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)

        return h

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

        return [round((r + m) * 255), round((g + m) * 255), round((b + m) * 255)]


class HslConverter(HueBasedConverter):
    @classmethod
    def rgb_to_hsl(
        cls,
        pixel: list[float],
    ):
        c_min, c_max = min(pixel), max(pixel)
        delta = c_max - c_min

        h = cls.count_hue(pixel)
        s = 0 if c_max == 0 else delta / (1 - abs(c_max + c_min - 1))
        l = (c_max + c_min) / 2

        return [h, s, l]

    @classmethod
    def hsl_to_rgb(
        cls,
        pixel: list[float],
    ):
        h, s, l = pixel
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
        r, g, b = pixel[0] / 255, pixel[1] / 255, pixel[2] / 255

        y = kr * r + (1 - kr - kb) * g + kb * b
        cb = (b - y) / (2 * (1 - kb))
        cr = (r - y) / (2 * (1 - kr))

        return [y, cb, cr]

    @classmethod
    def to_rgb(
        cls,
        pixel: list[float],
        kr: float,
        kb: float,
    ):
        y, cb, cr = pixel[0], pixel[1], pixel[2]

        r = y + 2 * (1 - kr) * cr
        g = y - 2 * (1 - kb) * kb * cb - 2 * (1 - kr) * kr * cr
        b = y + 2 * (1 - kb) * cb

        return [round(r * 255), round(g * 255), round(b * 255)]


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
        return [255 - pixel[0], 255 - pixel[1], 255 - pixel[2]]

    @classmethod
    def cmy_to_rgb(
        cls,
        pixel: list[float],
    ):
        return [255 - pixel[0], 255 - pixel[1], 255 - pixel[2]]


class ColorConverter:
    def __init__(
        self,
        convert_to: SupportedFormats,
    ):
        self.convert_to = convert_to

    def convert(
        self,
        convert_from: SupportedFormats,
        content: list[float],
    ):
        if self.convert_to == convert_from:
            return content

        rgb_content = self._convert_to_rgb(convert_from, content)
        return self._convert_from_rgb(self.convert_to, rgb_content)

    @classmethod
    def _convert_to_rgb(
        cls,
        convert_from: SupportedFormats,
        content: list[float],
    ):
        if convert_from == SupportedFormats.RGB:
            return content

        if convert_from == SupportedFormats.HSL:
            return HslConverter.hsl_to_rgb(content)

        if convert_from == SupportedFormats.HSV:
            return HsvConverter.hsv_to_rgb(content)

        if convert_from == SupportedFormats.YCbCr601:
            return YCbCr601Converter.ycbcr601_to_rgb(content)

        if convert_from == SupportedFormats.YCbCr709:
            return YCbCr709Converter.ycbcr709_to_rgb(content)

        if convert_from == SupportedFormats.CMY:
            return CmyConverter.cmy_to_rgb(content)

    @classmethod
    def _convert_from_rgb(
        cls,
        convert_to: SupportedFormats,
        content: list[float],
    ):
        if convert_to == SupportedFormats.RGB:
            return content

        if convert_to == SupportedFormats.HSL:
            return HslConverter.rgb_to_hsl(content)

        if convert_to == SupportedFormats.HSV:
            return HsvConverter.rgb_to_hsv(content)

        if convert_to == SupportedFormats.YCbCr601:
            return YCbCr601Converter.rgb_to_ycbcr601(content)

        if convert_to == SupportedFormats.YCbCr709:
            return YCbCr709Converter.rgb_to_ycbcr709(content)

        if convert_to == SupportedFormats.CMY:
            return CmyConverter.rgb_to_cmy(content)

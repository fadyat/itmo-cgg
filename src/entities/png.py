import dataclasses
import enum
import typing
import zlib

from PyQt6 import QtGui

from src.errors.png import (
    PngBitDepthError, PngColorTypeError, PngError, PngChunkTypeError,
    PngChunkError
)
from src.utils.png import get_chunk_length


class ChunkType(enum.Enum):
    IHDR = 0
    PLTE = 1
    IDAT = 2
    IEND = 3
    tRNS = 4
    cHRM = 5
    gAMA = 6
    iCCP = 7
    sBIT = 8
    sRGB = 9
    cICP = 10
    tEXt = 11
    zTXt = 12
    iTXt = 13
    bKGD = 14
    hIST = 15
    pHYs = 16
    sPLT = 17
    eXIf = 18
    tIME = 19
    acTL = 20
    fcTL = 21
    fdAT = 22
    orNT = 23


class Chunk:
    LENGTH_BYTES_COUNT, TYPE_BYTES_COUNT, CRC_BYTES_COUNT = 4, 4, 4

    def __init__(
        self,
        length: int,
        ctype: str,
        data: typing.List[int],
        crc: str,
    ):
        self.length = length
        self.ctype = ChunkType[ctype]
        self.data = data
        self.crc = crc

    def __repr__(self) -> str:
        return (
            f"Chunk(length={self.length}, ctype={self.ctype}, "
            f"data={len(self.data)}, crc={self.crc})"
        )


class IHDRChunk(Chunk):
    WIDTH_BYTES_COUNT, HEIGHT_BYTES_COUNT = 4, 4
    BIT_DEPTH_BYTES_COUNT, COLOR_TYPE_BYTES_COUNT, COMPRESSION_METHOD_BYTES_COUNT = 1, 1, 1
    FILTER_METHOD_BYTES_COUNT, INTERLACE_METHOD_BYTES_COUNT = 1, 1

    def __init__(
        self,
        length: int,
        ctype: str,
        data: typing.List[int],
        crc: str,
    ):
        super().__init__(length, ctype, data, crc)

        left, right = 0, self.WIDTH_BYTES_COUNT
        self.width = get_chunk_length(data[left:right])

        left, right = right, right + self.HEIGHT_BYTES_COUNT
        self.height = get_chunk_length(data[left:right])

        left, right = right, right + self.BIT_DEPTH_BYTES_COUNT
        self.bit_depth = get_chunk_length(data[left:right])

        left, right = right, right + self.COLOR_TYPE_BYTES_COUNT
        self.color_type = get_chunk_length(data[left:right])

        left, right = right, right + self.COMPRESSION_METHOD_BYTES_COUNT
        self.compression_method = get_chunk_length(data[left:right])

        left, right = right, right + self.FILTER_METHOD_BYTES_COUNT
        self.filter_method = get_chunk_length(data[left:right])

        left, right = right, right + self.INTERLACE_METHOD_BYTES_COUNT
        self.interlace_method = get_chunk_length(data[left:right])
        # self.__validate()

    def __repr__(self) -> str:
        return (
            f"IHDRChunk(length={self.length}, ctype={self.ctype}, "
            f"data={len(self.data)}, crc={self.crc}, "
            f"width={self.width}, height={self.height}, "
            f"bit_depth={self.bit_depth}, color_type={self.color_type}, "
            f"compression_method={self.compression_method}, "
            f"filter_method={self.filter_method}, "
            f"interlace_method={self.interlace_method})"
        )

    def __validate(self):
        if self.length != 13:
            raise PngChunkError('Invalid IHDR chunk length')

        if self.ctype != ChunkType.IHDR:
            raise PngChunkTypeError('Invalid chunk type, expected IHDR')

        if self.bit_depth not in [1, 2, 4, 8, 16]:
            raise PngBitDepthError('Invalid IHDR chunk bit depth')

        if self.color_type not in [0, 2, 3, 4, 6]:
            raise PngColorTypeError('Invalid IHDR chunk color type')

        if self.bit_depth != 8:
            raise PngBitDepthError('Only 8-bit depth is supported')

        if self.color_type in [4, 6]:
            raise PngColorTypeError('Alpha channel is not supported')

        if self.interlace_method != 0:
            raise PngError('Interlacing is not supported')

        if self.filter_method != 0:
            raise PngError('Filtering is not supported')


class GammaChunk(Chunk):

    def __init__(
        self,
        length: int,
        ctype: str,
        data: typing.List[int],
        crc: str,
    ):
        super().__init__(length, ctype, data, crc)

        # The value is encoded as a 4-byte unsigned integer, representing gamma times 100000.
        # For example, a gamma of 1/2.2 would be stored as 45455.
        self.gamma = get_chunk_length(data)

    def get_gamma(self) -> float:
        return self.gamma / 100000


@dataclasses.dataclass
class PngFileUI:

    def __init__(
        self,
        ihdr_chunk: IHDRChunk,
        idat_chunks: typing.List[Chunk],
        iend_chunk: Chunk,
        ancillary_chunks: typing.List[Chunk],
    ):
        self.ihdr_chunk = ihdr_chunk
        self.idat_chunks = idat_chunks
        self.iend_chunk = iend_chunk
        self.ancillary_chunks = ancillary_chunks

    def __repr__(self) -> str:
        return (
            f"PngFileUI(\n\tihdr_chunk={self.ihdr_chunk}, "
            f"\n\tidat_chunks={len(self.idat_chunks)}, "
            f"\n\tiend_chunk={self.iend_chunk}, "
            f"\n\tancillary_chunks={len(self.ancillary_chunks)}\n)"
        )

    def to_qpixmap(self) -> QtGui.QPixmap:
        painter = QtGui.QPainter()
        pixmap = QtGui.QPixmap(self.ihdr_chunk.width, self.ihdr_chunk.height)

        decompressed_data = zlib.decompress(b''.join([
            bytes(chunk.data) for chunk in self.idat_chunks
        ]))

        # todo: support 3-rd color type
        bpx = 1
        if self.ihdr_chunk.color_type == 2:
            bpx = 3

        scanline_length = self.ihdr_chunk.width * bpx
        scanlines = [
            (decompressed_data[i], decompressed_data[i + 1:i + scanline_length + 1])
            for i in range(0, len(decompressed_data), scanline_length + 1)
        ]

        # todo: add gamma correction
        reconstructed_pxs = []
        painter.begin(pixmap)
        for i, (filter_type, scanline) in enumerate(scanlines):
            for j in range(0, scanline_length, bpx):
                for k in range(bpx):
                    add_val = apply_filter(
                        filter_type=filter_type,
                        reconstructed_filters=reconstructed_pxs,
                        bpx=bpx,
                        row=i,
                        col=j + k,
                        scanline_length=scanline_length,
                    )
                    px = (scanline[j + k] + add_val) % 256
                    reconstructed_pxs.append(px)

                rgb = reconstructed_pxs[-bpx:]
                if bpx == 1:
                    rgb = [rgb[0], rgb[0], rgb[0]]

                painter.setPen(QtGui.QColor(*rgb))
                painter.drawPoint(j // bpx, i)

        painter.end()

        return pixmap


def apply_filter(
    filter_type: int,
    reconstructed_filters: typing.List[int],
    row: int,
    col: int,
    scanline_length: int,
    bpx: int,
):
    if filter_type == 0:
        return 0

    def left():
        return (
            reconstructed_filters[row * scanline_length + col - bpx]
            if col >= bpx else 0
        )

    def up():
        return (
            reconstructed_filters[(row - 1) * scanline_length + col]
            if row > 0 else 0
        )

    def up_left():
        return (
            reconstructed_filters[(row - 1) * scanline_length + col - bpx]
            if row > 0 and col >= bpx else 0
        )

    def avg():
        return (left() + up()) // 2

    def paeth():
        a, b, c = left(), up(), up_left()
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b

        return c

    if filter_type == 1:
        return left()

    if filter_type == 2:
        return up()

    if filter_type == 3:
        return avg()

    if filter_type == 4:
        return paeth()

    raise PngError('Invalid filter type')

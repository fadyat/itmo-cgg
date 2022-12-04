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

    def to_qimage(self) -> QtGui.QImage:
        image = QtGui.QImage(
            self.ihdr_chunk.width,
            self.ihdr_chunk.height,
            QtGui.QImage.Format.Format_RGB888,
        )

        decompressed_data = zlib.decompress(b''.join([
            bytes(chunk.data)
            for chunk in self.idat_chunks
        ]))

        recon = []
        bpx = 3
        stride = self.ihdr_chunk.width * bpx

        def paeth(a, b, c):
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                pr = a
            elif pb <= pc:
                pr = b
            else:
                pr = c
            return pr

        def recon_a(r, c):
            return (
                recon[r * stride + c - bpx]
                if c >= bpx else 0
            )

        def recon_b(r, c):
            return (
                recon[(r - 1) * stride + c]
                if r >= 1 else 0
            )

        def recon_c(r, c):
            return (
                recon[(r - 1) * stride + c - bpx]
                if r >= 1 and c >= bpx else 0
            )

        i = 0
        for row in range(self.ihdr_chunk.height):
            filter_type = decompressed_data[i]
            i += 1
            for col in range(stride):
                px = decompressed_data[i]
                if filter_type == 1:
                    px += recon_a(row, col)
                elif filter_type == 2:
                    px += recon_b(row, col)
                elif filter_type == 3:
                    px += (recon_a(row, col) + recon_b(row, col)) // 2
                elif filter_type == 4:
                    px += paeth(recon_a(row, col), recon_b(row, col), recon_c(row, col))

                recon.append(px % 256)
                if len(recon) % 3 == 0:
                    image.setPixel(
                        col // bpx, row, QtGui.qRgb(recon[-3], recon[-2], recon[-1]),
                    )
                i += 1

        return image

import dataclasses
import enum
import typing

from src.errors.png import (
    PngBitDepthError, PngColorTypeError, PngError, PngChunkTypeError,
    PngChunkError
)
from src.utils.png import get_chunk_length


class ChunkType(enum.Enum):
    IHDR = 0
    IDAT = 2
    IEND = 3
    gAMA = 4


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

    def is_critical(self) -> bool:
        return self.ctype in [ChunkType.IHDR, ChunkType.IDAT, ChunkType.IEND]


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
        # self.__validate() todo: uncomment

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
        critical_chunks: typing.List[Chunk],
        ancillary_chunks: typing.List[Chunk],
    ):
        self.__critical_chunks = critical_chunks
        self.__ancillary_chunks = ancillary_chunks

    def __repr__(self) -> str:
        return (
            f"PngFileUI(critical_chunks={len(self.__critical_chunks)}, "
            f"ancillary_chunks={len(self.__ancillary_chunks)})"
        )

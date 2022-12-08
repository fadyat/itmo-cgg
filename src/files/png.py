import struct
import typing
import zlib

from src.entities.png import Chunk, ChunkType, IHDRChunk, PngFileUI, GammaChunk
from src.errors.png import (
    PngError,
)
from src.utils.png import get_chunk_length


class PngIO:
    HEADER_BYTES_COUNT = 8

    def __init__(
        self,
        image_path: str,
        mode='rb',
    ):
        self.__image_path = image_path
        self.mode = mode

    def __enter__(self):
        self.__file = open(self.__image_path, self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__file.close()
        self.__file = None

    def read_for_ui(self) -> PngFileUI:
        """ https://docs.fileformat.com/image/png/ """

        _ = self.__read_header()
        ihdr_chunk, iend_chunk = None, None
        idat_chunks, ancillary_chunks = [], []
        while True:
            chunk = self.__read_chunk()
            if chunk.ctype == ChunkType.IHDR:
                if ihdr_chunk is not None:
                    raise PngError('Only one IHDR chunk is allowed')

                ihdr_chunk = IHDRChunk(
                    length=chunk.length,
                    ctype=chunk.ctype.name,
                    data=chunk.data,
                    crc=chunk.crc,
                )
                continue

            if chunk.ctype == ChunkType.gAMA:
                ancillary_chunks.append(GammaChunk(
                    length=chunk.length,
                    ctype=chunk.ctype.name,
                    data=chunk.data,
                    crc=chunk.crc,
                ))
                continue

            if chunk.ctype == ChunkType.IEND:
                if iend_chunk is not None:
                    raise PngError('Only one IEND chunk is allowed')

                iend_chunk = chunk
                break

            if chunk.ctype == ChunkType.IDAT:
                idat_chunks.append(chunk)
                continue

            ancillary_chunks.append(chunk)

        return PngFileUI(
            ihdr_chunk=ihdr_chunk,
            idat_chunks=idat_chunks,
            ancillary_chunks=ancillary_chunks,
            iend_chunk=iend_chunk,
        )

    def __read_header(
        self,
    ) -> typing.List[int]:
        return self.__read_bytes(self.HEADER_BYTES_COUNT)

    def __read_bytes(
        self,
        cnt: int,
    ) -> typing.List[int]:
        return list(self.__file.read(cnt))

    def __read_bytes_as_string(
        self,
        cnt: int,
    ) -> str:
        return ''.join(map(chr, self.__read_bytes(cnt)))

    def __read_bytes_as_hex(
        self,
        cnt: int,
    ):
        return ''.join(map(lambda x: f'{x:02x}', self.__read_bytes(cnt)))

    def __read_chunk(
        self,
    ) -> Chunk:
        chunk_length = get_chunk_length(self.__read_bytes(Chunk.LENGTH_BYTES_COUNT))

        return Chunk(
            length=chunk_length,
            ctype=self.__read_bytes_as_string(Chunk.TYPE_BYTES_COUNT),
            data=self.__read_bytes(chunk_length),
            crc=self.__read_bytes_as_hex(Chunk.CRC_BYTES_COUNT),
        )

    def write(
        self,
        width: int,
        height: int,
        color_type: int,
        data: bytes,
        bit_depth: int = 8,
        compression_method: int = 0,
        filter_method: int = 0,
        interlace_method: int = 0,
        gamma: float = 2.2,
    ):
        self.__write_file_signature()
        self.__write_ihdr(
            width=width,
            height=height,
            color_type=color_type,
            bit_depth=bit_depth,
            compression_method=compression_method,
            filter_method=filter_method,
            interlace_method=interlace_method,
        )
        self.__write_gamma(gamma)

        bpx = 3 if color_type == 2 else 1
        self.__write_idat(data, width, bpx)
        self.__write_iend()

    def __write_file_signature(
        self,
    ):
        self.__file.write(b'\x89PNG\r\n\x1a\n')  # type: ignore

    def __write_ihdr(
        self,
        width: int,
        height: int,
        bit_depth: int,
        color_type: int,
        compression_method: int,
        filter_method: int,
        interlace_method: int,
    ):
        ihdr_data = struct.pack(
            '>IIBBBBB',
            width,
            height,
            bit_depth,
            color_type,
            compression_method,
            filter_method,
            interlace_method,
        )

        self.__write_chunk(b'IHDR', ihdr_data)

    def __write_iend(self):
        self.__write_chunk(b'IEND', b'')

    def __write_idat(
        self,
        data: bytes,
        width: int,
        bpx: int,
    ):
        scanlines = self.__split_data_by_scanlines(data, width * bpx)
        filtered_scanlines = self.__apply_filters(scanlines, b'\x00')
        compressed_data = zlib.compress(filtered_scanlines)
        self.__write_chunk(b'IDAT', compressed_data)

    @staticmethod
    def __apply_filters(
        scanlines: typing.List[bytes],
        filter_type: bytes,
    ) -> bytes:
        return b''.join([
            filter_type + scanline
            for scanline in scanlines
        ])

    @staticmethod
    def __split_data_by_scanlines(
        data: bytes,
        width: int,
    ) -> typing.List[bytes]:
        scanline_size = width
        return [
            data[i:i + scanline_size]
            for i in range(0, len(data), scanline_size)
        ]

    def __write_chunk(
        self,
        chunk_name: bytes,
        chunk_data: bytes,
    ):
        if len(chunk_name) != 4:
            raise PngError('Chunk name must be 4 bytes long')

        crc = zlib.crc32(chunk_name + chunk_data)
        crc = struct.pack('!I', crc)

        length = struct.pack('!I', len(chunk_data))

        chunk = b''.join([length, chunk_name, chunk_data, crc])
        self.__file.write(chunk)  # type: ignore

    def __write_gamma(
        self,
        gamma: float,
    ):
        png_gamma_format = struct.pack('>I', 45455)
        if gamma != 0:
            png_gamma_format = struct.pack('>I', int(1 / (gamma * 100000)))

        self.__write_chunk(b'gAMA', png_gamma_format)

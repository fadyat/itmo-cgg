import typing

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

import typing

from src.entities.png import Chunk, ChunkType, IHDRChunk, PngFileUI
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
        critical_chunks, ancillary_chunks = [], []
        while True:
            chunk = self.__read_chunk()
            if chunk.ctype == ChunkType.IHDR:
                chunk = IHDRChunk(
                    length=chunk.length,
                    ctype=chunk.ctype.name,
                    data=chunk.data,
                    crc=chunk.crc,
                )

            if chunk.is_critical():
                critical_chunks.append(chunk)
            else:
                ancillary_chunks.append(chunk)

            if chunk.ctype == ChunkType.IEND:
                break

        return PngFileUI(
            critical_chunks=critical_chunks,
            ancillary_chunks=ancillary_chunks,
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


if __name__ == '__main__':
    with PngIO('../../docs/ai.png') as png:
        try:
            pngui = png.read_for_ui()
        except PngError as e:
            print(e)
        else:
            print(pngui)

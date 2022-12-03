import enum
import typing


class ChunkType(enum.Enum):
    IHDR = 0
    IDAT = 2
    IEND = 3


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

    def read_for_ui(self) -> typing.List[Chunk]:
        """ https://docs.fileformat.com/image/png/ """

        _ = self.__read_header()
        chunks = []
        while True:
            chunk = self.__read_chunk()
            if chunk.ctype == ChunkType.IHDR:
                chunks.append(IHDRChunk(
                    length=chunk.length,
                    ctype=chunk.ctype.name,
                    data=chunk.data,
                    crc=chunk.crc,
                ))
                continue

            chunks.append(chunk)
            if chunk.ctype == ChunkType.IEND:
                break

        return chunks

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


def get_chunk_length(
    bts: typing.List[int],
) -> int:
    length, power = 0, 0
    for x in reversed(bts):
        length += int(hex(x)[2:], 16) * (256 ** power)
        power += 1

    return length


if __name__ == '__main__':
    with PngIO('../../docs/ai.png') as png:
        chunks = png.read_for_ui()

    for chunk in chunks:
        print(chunk)

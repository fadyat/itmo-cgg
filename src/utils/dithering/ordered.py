def bayer_matrix_8x8():
    matrix = [
        [0, 32, 8, 40, 2, 34, 10, 42],
        [48, 16, 56, 24, 50, 18, 58, 26],
        [12, 44, 4, 36, 14, 46, 6, 38],
        [60, 28, 52, 20, 62, 30, 54, 22],
        [3, 35, 11, 43, 1, 33, 9, 41],
        [51, 19, 59, 27, 49, 17, 57, 25],
        [15, 47, 7, 39, 13, 45, 5, 37],
        [63, 31, 55, 23, 61, 29, 53, 21],
    ]

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            matrix[i][j] /= 64

    return matrix


def ordered_dithering(
    content: list[float],
    width: int,
    bayer_matrix=None,
    bytes_per_px: int = 3,
):
    if bayer_matrix is None:
        bayer_matrix = bayer_matrix_8x8()

    return [
        j for i in range(0, len(content), bytes_per_px)
        for j in ordered_pixel(
            content[i],
            i // bytes_per_px % width,
            i // bytes_per_px // width,
            bayer_matrix,
            bytes_per_px,
        )
    ]


def ordered_pixel(
    pixel: float,
    x: int,
    y: int,
    bayer_matrix: list[list[int]],
    bytes_per_px: int = 3,
) -> list[float]:
    value = bayer_matrix[y % len(bayer_matrix)][x % len(bayer_matrix)]
    color = 0 if value > pixel else 1
    return [color for _ in range(bytes_per_px)]


def ordered_dithering_bytes(
    content: list[int],
    width: int,
    bayer_matrix=None,
    bytes_per_px: int = 3,
):
    if bayer_matrix is None:
        bayer_matrix = bayer_matrix_8x8()

    return [
        j for i in range(0, len(content), bytes_per_px)
        for j in ordered_pixel_byte(
            content[i],
            i // bytes_per_px % width,
            i // bytes_per_px // width,
            bayer_matrix,
            bytes_per_px,
        )
    ]


def ordered_pixel_byte(
    pixel: int,
    x: int,
    y: int,
    bayer_matrix: list[list[int]],
    bytes_per_px: int = 3,
) -> list[int]:
    value = 255 * bayer_matrix[y % len(bayer_matrix)][x % len(bayer_matrix)]
    color = 0 if value > pixel else 255
    return [color for _ in range(bytes_per_px)]

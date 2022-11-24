from src.utils.dithering import find_closest_px


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


bayer_matrix = bayer_matrix_8x8()


def ordered_pixel(
    pixel: list[float],
    x: int,
    y: int,
    dithering_bits_values: list[float],
) -> list[float]:
    bayer = bayer_matrix[y % len(bayer_matrix)][x % len(bayer_matrix[0])]
    avg = sum(pixel) / len(pixel)
    r = 1 / len(dithering_bits_values)
    color = find_closest_px(
        (avg + r * (bayer - .5)),
        dithering_bits_values
    )
    return [color, color, color]

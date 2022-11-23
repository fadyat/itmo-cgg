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
) -> list[int]:
    bayer = bayer_matrix[y % len(bayer_matrix)][x % len(bayer_matrix[0])]
    avg = sum(pixel) / len(pixel)
    color = 0 if bayer >= avg else 1
    return [color, color, color]

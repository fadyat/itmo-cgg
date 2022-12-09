import typing


def get_chunk_length(
    bts: typing.List[int],
) -> int:
    length, power = 0, 0
    for x in reversed(bts):
        length += int(hex(x)[2:], 16) * (256 ** power)
        power += 1

    return length

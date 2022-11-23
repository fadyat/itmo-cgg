def atkinson_dithering_bytes(
    content: list[int],
    width: int,
    bytes_per_px: int = 3,
):
    for i in range(0, len(content), bytes_per_px):
        px = content[i]
        new_px = 0 if px < 128 else 255
        content[i] = new_px
        error = px - new_px
        for j in range(1, bytes_per_px):
            content[i + j] = content[i]

        pxs_for_error_diffusion = [
            i + bytes_per_px,
            i + 2 * bytes_per_px,
            i + width * bytes_per_px - bytes_per_px,
            i + width * bytes_per_px,
            i + width * bytes_per_px + bytes_per_px,
            i + 2 * width * bytes_per_px,
        ]

        for px in pxs_for_error_diffusion:
            if px < len(content):
                content[px] += error // 8
                for j in range(1, bytes_per_px):
                    content[px + j] = content[px]

    return content

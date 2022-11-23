def floyd_steinberg_dithering_bytes(
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

        next_px = i + bytes_per_px
        if next_px < len(content):
            content[next_px] += error * 7 // 16
            for j in range(1, bytes_per_px):
                content[next_px + j] = content[next_px]

        bottom_px = i + width * bytes_per_px
        if bottom_px < len(content):
            content[bottom_px] += error * 5 // 16
            for j in range(1, bytes_per_px):
                content[bottom_px + j] = content[bottom_px]

        next_bottom_px = bottom_px + bytes_per_px
        if next_bottom_px < len(content):
            content[next_bottom_px] += error * 1 // 16
            for j in range(1, bytes_per_px):
                content[next_bottom_px + j] = content[next_bottom_px]

        prev_bottom_px = bottom_px - bytes_per_px
        if prev_bottom_px < len(content):
            content[prev_bottom_px] += error * 3 // 16
            for j in range(1, bytes_per_px):
                content[prev_bottom_px + j] = content[prev_bottom_px]

    return content

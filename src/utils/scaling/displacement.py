from src.entities.pnm import PnmFileUI


def displace(
    img: PnmFileUI,
    x: int = 0,
    y: int = 0,
):
    if x == 0 and y == 0:
        return

    new_content = [0.0] * len(img.content)
    for row_idx in range(img.height):
        if row_idx + y < 0 or row_idx + y >= img.height:
            continue

        for col_idx in range(img.width):
            if col_idx + x < 0 or col_idx + x >= img.width:
                continue

            begin = (col_idx + row_idx * img.width) * img.bytes_per_px
            new_begin = ((col_idx + x) + (row_idx + y) * img.width) * img.bytes_per_px
            new_content[new_begin: new_begin + img.bytes_per_px] = img.content[
                                                                   begin: begin + img.bytes_per_px]

    img.content = new_content

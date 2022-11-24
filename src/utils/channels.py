def try_delete_superfluous_channels(
    content: list[float],
    disabled_channels: list[bool],
):
    disabled = sum(disabled_channels)
    if disabled < 2:
        return content

    if disabled == 3:
        return [0 for _ in range(len(content) // 3)]

    return [
        content[i] for i in range(len(content))
        if not disabled_channels[i % 3]
    ]

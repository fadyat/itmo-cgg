class PngError(Exception):

    def __init__(
        self,
        message: str,
    ):
        self.message = message

    def __str__(
        self,
    ):
        return self.message


class PngColorTypeError(PngError):
    ...


class PngBitDepthError(PngError):
    ...


class PngChunkTypeError(PngError):
    ...


class PngChunkError(PngError):
    ...

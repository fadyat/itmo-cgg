PNM_BYTES_PER_PIXEL = {'P5': 1, 'P6': 3}
PNM_SUPPORTED_FORMATS = tuple(PNM_BYTES_PER_PIXEL.keys())
P5 = PNM_SUPPORTED_FORMATS[0]
P6 = PNM_SUPPORTED_FORMATS[1]
COLOR_MODELS = {'RGB': 1, 'HSL': 2, 'HSV': 3, 'YCbCr601': 4, 'YCbCr709': 5, 'YCoCg': 6, 'CMY': 7}
DITHERING_ALGORITHMS = {
    'None': 1, 'Random': 2, 'Ordered 8x8': 3, 'Floyd-Steinberg': 4, 'Atkinson': 5
}

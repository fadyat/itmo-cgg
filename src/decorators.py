import functools

from src.errors.pnm import PnmError


def debug_log(do: bool = False):
    def decorate(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if do:
                print(f.__name__, args, kwargs)
                print('some data', result[:min(10, len(result))])

        return wrapper

    return decorate


def catch(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except PnmError as e:
            print(e)

    return wrapper

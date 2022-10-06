import functools

from src.errors.pnm import PnmError


def debug_log(do: bool = False):
    def wrapper(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            result = f(*args, **kwargs)
            if do:
                print(f.__name__, args, kwargs)
                print('some data', result[: min(10, len(result))])

            return result

        return decorated

    return wrapper


def catch(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except (PnmError, UnicodeDecodeError, ValueError, TypeError) as e:
            print(e)
        else:
            return result

    return wrapper

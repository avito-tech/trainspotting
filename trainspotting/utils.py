from functools import wraps as wraps_fn
from typing import (
    Iterable,
    Type,
    TypeVar,
)

T = TypeVar('T')


def first(iterable: Iterable):
    iterator = iter(iterable)
    return next(iterator)


def wraps(obj):
    def decorator(wrapper):
        if isinstance(obj, type):

            class Wrapper(obj):
                __name__ = obj.__name__
                __qualname__ = obj.__qualname__
                __module__ = obj.__module__

                def __new__(cls, *args, **kwargs):
                    return wrapper(*args, **kwargs)

            return Wrapper

        return wraps_fn(obj)(wrapper)

    return decorator


def match_interface(cls: Type[T], interface: Type[T], *, strict_validation: bool = False) -> bool:
    try:
        return issubclass(cls, interface)
    except TypeError:
        # protocol can be non runtime checkable
        # returns False (interfaces doesn't match) if strict_validation
        return not strict_validation

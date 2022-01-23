import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Optional,
    Type,
    TypeVar,
)

from trainspotting.utils import wraps

T = TypeVar('T')

MISSING = object()


class AbstractField(ABC):
    @abstractmethod
    def get(self) -> Optional[T]:
        ...


class FieldException(Exception):
    ...


@dataclass
class EnvField(AbstractField):
    var_name: str
    obj_type: Type[T] = str  # type: ignore
    default: Any = MISSING
    optional: bool = False

    def get(self) -> Optional[T]:
        value = os.getenv(self.var_name, MISSING)

        if value is MISSING:
            if self.default is MISSING and not self.optional:
                raise FieldException(
                    f'Failed to get {self.var_name}. '
                    f'Value is missing, but argument is not optional',
                )

            return self.default

        return self.obj_type(value)  # type: ignore


def factory(obj_type: Type[T], **factory_kwargs) -> Type[T]:
    @wraps(obj_type)
    def _wrapper(*args, **kwargs):
        fields = {
            name: obj for name, obj in factory_kwargs.items() if isinstance(obj, AbstractField)
        }

        for name, value in fields.items():
            field_value = value.get()

            if field_value is not MISSING:
                factory_kwargs[name] = field_value
            else:
                factory_kwargs.pop(name)

        kwargs = {**factory_kwargs, **kwargs}
        return obj_type(*args, **kwargs)

    return _wrapper

from collections import OrderedDict
from functools import partial
from inspect import isfunction
from typing import (
    Any,
    Callable,
    Iterator,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
)

from trainspotting.clients import is_client
from trainspotting.logger import BaseLogger, Logger
from trainspotting.utils import wraps

T = TypeVar('T')


class DependenciesContainerProtocol(Protocol):
    def set(self, obj: Type[T], **obj_kwargs: Any):
        ...

    def get(self, obj: Type[T]) -> Optional[Callable[[], T]]:
        ...

    async def connect(self):
        ...

    async def disconnect(self):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    def __iter__(self) -> Iterator[Tuple[Type[T], Callable[[], T]]]:
        ...

    @property
    def logger(self) -> BaseLogger:
        ...


class SingletonDependenciesContainer:
    def __init__(self, logger_fabric: Callable[[], BaseLogger] = Logger):
        self._deps: OrderedDict = OrderedDict()
        self._logger: BaseLogger = logger_fabric()

    def set(self, obj: Type[T], **obj_kwargs):
        if isfunction(obj):
            self._deps[obj] = wraps(obj)(partial(obj, **obj_kwargs))
        else:
            injected = obj(**obj_kwargs)  # type: ignore

            @wraps(obj)
            def constructor():
                return injected

            self._deps[obj] = constructor

    def get(self, obj: Type[T]) -> Optional[Callable[[], T]]:
        return self._deps.get(obj)

    async def connect(self):
        for cls, injected in self:
            if is_client(cls):
                self.logger.debug(f'Connecting {cls}...')
                await injected().connect()

    async def disconnect(self):
        for cls, injected in reversed(list(self)):
            if is_client(cls):
                self.logger.debug(f'Disconnecting {cls}...')

                try:
                    await injected().disconnect()
                except Exception:
                    self.logger.exception(f'Error while disconnecting {cls}')

    @property
    def logger(self) -> BaseLogger:
        return self._logger

    async def __aenter__(self):
        await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    def __iter__(self) -> Iterator[Tuple[Type[T], Callable[[], T]]]:
        for obj_type, injected in self._deps.items():
            yield obj_type, injected

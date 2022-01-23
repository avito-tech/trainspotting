from typing import (
    Protocol,
    Type,
    runtime_checkable,
)


@runtime_checkable
class ClientProtocol(Protocol):
    async def connect(self):
        ...

    async def disconnect(self):
        ...


def is_client(cls: Type[ClientProtocol]) -> bool:
    try:
        return issubclass(cls, ClientProtocol)
    except TypeError:
        return False

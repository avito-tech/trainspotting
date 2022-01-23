from dataclasses import dataclass
from typing import (
    Optional,
    Protocol,
    Type,
)
from unittest.mock import patch

import pytest

from trainspotting import InjectionError
from trainspotting.factory import EnvField, factory


def test_fail_inject(injector_fabric):
    class ClientProtocol(Protocol):
        ...

    @dataclass
    class TestClient:
        one_more: str

    def use_client(client: ClientProtocol):
        ...

    config = {ClientProtocol: TestClient}
    with pytest.raises(InjectionError):
        injector_fabric(config).inject(use_client)


def test_fail_provider_inject(injector_fabric):
    class ClientProtocol(Protocol):
        ...

    def use_client(client: ClientProtocol):
        ...

    config = {}
    with pytest.raises(TypeError):
        injector_fabric(config).inject(use_client)()


def test_success_inject(injector_fabric):
    class ClientOneProtocol(Protocol):
        def foo(self) -> str:
            ...

    @dataclass
    class Something:
        def foo(self) -> str:
            return 'foo'

    class SomeEntityProtocol(Protocol):
        def bar(self) -> int:
            ...

    class Empty:
        def bar(self) -> int:
            return 1337

    class ClientTwoProtocol(Protocol):
        ...

    @dataclass
    class TestClient(ClientTwoProtocol):
        some_cls: Type[SomeEntityProtocol]
        client_one: ClientOneProtocol

    @dataclass
    class UserOfClient:
        client_two: ClientTwoProtocol

    config = {
        # provider bindings
        ClientOneProtocol: Something,
        ClientTwoProtocol: TestClient,
        SomeEntityProtocol: Empty,
    }

    injected_client: UserOfClient = injector_fabric(config).inject(UserOfClient)()
    assert isinstance(injected_client.client_two, TestClient)

    assert injected_client.client_two.some_cls is Empty
    assert isinstance(injected_client.client_two.client_one, Something)


def test_success_inject_with_field(injector_fabric):
    class ClientOneProtocol(Protocol):
        one: int
        two: Optional[int]

    @dataclass
    class Something:
        one: int
        two: Optional[int]

    @dataclass
    class TestClient:
        client_one: ClientOneProtocol

    config = {
        ClientOneProtocol: factory(
            Something,
            one=EnvField('ONE', int),
            two=EnvField('TWO', int, default=None),
        ),
    }

    env = {'ONE': '1'}
    with patch('trainspotting.factory.os.getenv', env.get):
        injected_client = injector_fabric(config).inject(TestClient)()

    assert isinstance(injected_client.client_one, Something)

    assert injected_client.client_one.one == 1
    assert injected_client.client_one.two is None


def test_lazy_inject(injector_fabric):
    class ClientOneProtocol(Protocol):
        ...

    class ClientOne:
        ...

    default_value = 1

    def use_client(client: ClientOneProtocol = default_value):
        return client

    injector = injector_fabric({ClientOneProtocol: ClientOne})
    injected = injector.lazy_inject(use_client)

    assert injected() is default_value

    injector.do_lazy_injections()
    assert type(injected()) is ClientOne


def test_lazy_inject_class(injector_fabric):
    class ClientOneProtocol(Protocol):
        ...

    class ClientOne:
        ...

    default_value = 1

    @dataclass
    class UserOfClientOne:
        client: ClientOneProtocol = default_value

        def get_client(self):
            return self.client

    injector = injector_fabric({ClientOneProtocol: ClientOne})
    injected = injector.lazy_inject(UserOfClientOne)

    assert injected().get_client() is default_value

    injector.do_lazy_injections()
    assert type(injected().get_client()) is ClientOne


def test_mro_inject(injector_fabric):
    class ClientOneProtocol(Protocol):
        ...

    class ClientTwoProtocol(Protocol):
        ...

    class ClientOne:
        ...

    class ClientTwo:
        ...

    @dataclass
    class BaseClass:
        client_one: ClientOneProtocol

    @dataclass
    class ClassWithParent(BaseClass):
        client_two: ClientTwoProtocol

    injector = injector_fabric({ClientOneProtocol: ClientOne, ClientTwoProtocol: ClientTwo})
    injected = injector.inject(ClassWithParent)()

    assert type(injected.client_one) == ClientOne
    assert type(injected.client_two) == ClientTwo


def test_add_config(injector_fabric):
    config = {
        'key_one': '1',
        'key_two': '2',
    }

    injector = injector_fabric(config)
    injector.add_config(
        {
            'key_one': '10',
            'key_three': '3',
        },
    )

    assert injector.deps_cfg == {
        'key_one': '10',
        'key_two': '2',
        'key_three': '3',
    }


def test_class_wrapping(injector_fabric):
    config = {
        'key_one': '1',
        'key_two': '2',
    }

    class Client:
        ...

    injector = injector_fabric(config)
    injected = injector.inject(Client)

    assert issubclass(injected, Client)

    for cls, injected in injector.deps:
        assert issubclass(cls, Client)
        assert issubclass(injected, Client)

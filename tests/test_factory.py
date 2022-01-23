from dataclasses import dataclass
from typing import Optional, get_type_hints
from unittest.mock import patch

import pytest
from trainspotting.factory import (
    EnvField,
    FieldException,
    factory,
)


def test_simple_fabric():
    @dataclass
    class TestClient:
        a: int

    client = factory(TestClient, a=1)
    assert client().a == 1
    assert get_type_hints(client) == {'a': int}


def test_fabric_mro():
    @dataclass
    class TestClient:
        a: int

    @dataclass
    class NewClient(TestClient):
        b: str = 2

    client = factory(NewClient)
    assert get_type_hints(client) == {'a': int, 'b': str}


def test_fabric_with_env_field():
    @dataclass
    class TestClient:
        first: int
        second_optional: Optional[int] = None
        third_optional: Optional[int] = None
        fourth_optional: Optional[int] = None

    env = {
        'MY_ENV': '1',
        'SECOND_ENV': '2',
    }

    with patch('trainspotting.factory.os.getenv', env.get):
        client = factory(
            TestClient,
            first=EnvField('MY_ENV', int),
            second_optional=EnvField('SECOND_ENV', int, optional=True),
            third_optional=EnvField('THIRD_ENV', int, optional=True),
            fourth_optional=EnvField('FOURTH_ENV', int, default=123),
        )()

    assert client.first == 1
    assert client.second_optional == 2
    assert client.third_optional is None
    assert client.fourth_optional == 123

    @dataclass
    class NotOptionalClient:
        first: int

    with pytest.raises(FieldException):
        factory(
            NotOptionalClient,
            first=EnvField('MY_ENV', int),
        )()

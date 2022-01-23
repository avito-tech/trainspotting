import pytest

from trainspotting import SingletonDependenciesContainer


@pytest.mark.parametrize(
    'container_type, expected_is_same_instance',
    ((SingletonDependenciesContainer, True),),
)
def test_dependencies_containers(container_type, expected_is_same_instance):
    container = container_type()

    class TestClient:
        def __init__(self, flag: bool):
            self.flag = flag

    container.set(TestClient, flag=True)

    client_one = container.get(TestClient)()
    assert isinstance(client_one, TestClient)

    client_two = container.get(TestClient)()
    assert isinstance(client_two, TestClient)

    is_same_instance = client_one is client_two
    assert is_same_instance == expected_is_same_instance

    iterated_types = []

    for obj_type, injected in container:
        assert isinstance(injected(), obj_type)
        iterated_types.append(obj_type)

    assert iterated_types == [TestClient]


@pytest.mark.asyncio
async def test_clients_connect_order():
    container = SingletonDependenciesContainer()
    connected = []
    disconnected = []

    class BaseClient:
        async def connect(self):
            connected.append(self.__class__)

        async def disconnect(self):
            disconnected.append(self.__class__)

    class FirstClient(BaseClient):
        ...

    class SecondClient(BaseClient):
        ...

    class ThirdClient(BaseClient):
        ...

    class NotClient:
        ...

    container.set(FirstClient)
    container.set(SecondClient)
    container.set(NotClient)
    container.set(ThirdClient)

    async with container:
        assert connected == [FirstClient, SecondClient, ThirdClient]

    assert disconnected == [ThirdClient, SecondClient, FirstClient]

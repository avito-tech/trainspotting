import pytest

from trainspotting import DependencyInjector


@pytest.fixture
def injector_fabric():
    def _fabric(cfg):
        return DependencyInjector(cfg)

    return _fabric

from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Type,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from trainspotting.containers import DependenciesContainerProtocol, SingletonDependenciesContainer
from trainspotting.utils import (
    first,
    match_interface,
    wraps,
)

T = TypeVar('T')


class InjectionError(Exception):
    ...


@dataclass
class DependencyInjector:
    """
    Injects dependencies. Uses deps_cfg for deps initialization

    Use strict_validation=True to raise InjectionError
    if protocols are not runtime checkable
    """

    deps_cfg: Dict[Any, Any] = field(default_factory=dict)
    deps: DependenciesContainerProtocol = field(default_factory=SingletonDependenciesContainer)
    strict_validation: bool = False

    _postponed: List[Callable[[], Any]] = field(default_factory=list, init=False)

    def inject(self, obj: Type[T]) -> Callable[[], T]:
        """ Idempotent operation """
        obj = get_origin(obj) or obj
        injected = self.deps.get(obj)

        if injected is not None:
            return injected

        self.deps.logger.debug(f'Injecting {obj}...')

        try:
            return self._inject(obj)
        except TypeError as e:
            raise InjectionError(f'Failed to inject {obj}') from e

    def lazy_inject(self, obj: Type[T]) -> Type[T]:
        @wraps(obj)
        def wrapper(*args, **kwargs):
            return obj(*args, **kwargs)

        def _inject():
            nonlocal obj
            obj = self.inject(obj)

        self._postponed.append(_inject)
        return wrapper

    def do_lazy_injections(self):
        while self._postponed:
            self._postponed.pop()()

    def add_config(self, additional_cfg: Dict[Any, Any]):
        self.deps_cfg = {**self.deps_cfg, **additional_cfg}

    def _inject(self, obj: Type[T]) -> Callable[[], T]:
        type_hints = get_type_hints(obj)
        kwargs = {}

        for name, cls in type_hints.items():
            if get_origin(cls) is type:
                provider = first(get_args(cls))
                provided_obj = self.deps_cfg.get(provider)

                if provided_obj is None:
                    continue

                if not match_interface(
                    provided_obj,
                    provider,
                    strict_validation=self.strict_validation,
                ):
                    raise InjectionError(f'{provided_obj} does not realize {provider} interface')

                kwargs[name] = provided_obj
            else:
                provider = get_origin(cls) or cls
                provided_obj = self.deps_cfg.get(provider)

                if provided_obj is None:
                    continue

                if not match_interface(
                    provided_obj,
                    provider,
                    strict_validation=self.strict_validation,
                ):
                    raise InjectionError(f'{provided_obj} does not realize {provider} interface')

                # If all deps are injected then it will be okay
                # Other wise will raise exception (You should add more deps to config)
                kwargs[name] = self.inject(provided_obj)()

        self.deps.set(obj, **kwargs)
        return self.deps.get(obj)  # type: ignore

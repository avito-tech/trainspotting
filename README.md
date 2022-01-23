![trainspotting](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Trainspotting-logo.svg/456px-Trainspotting-logo.svg.png)
## Choose dependency injection
* Friendly with MyPy
* Supports lazy injections
* Supports fabrics with environment variables
* Can connect/disconnect clients in correct order 
### Install
```
pip install trainspotting
```

### Contact
Feel free to ask questions in telegram [t.me/PulitzerKenny](<https://t.me/PulitzerKenny>)

### Examples
```python
from typing import Protocol
from dataclasses import dataclass
from trainspotting import DependencyInjector
from trainspotting.factory import factory, EnvField


class TransportProtocol(Protocol):
    def go(self): ...

class EngineProtocol(Protocol):
    def start(self): ...

class HeadlightsProtocol(Protocol):
    def light(self): ...

@dataclass
class Driver:
    transport: TransportProtocol
    
    def drive(self):
        self.transport.go()

@dataclass
class V8Engine:
    sound: str

    def start(self):
        print(self.sound)

@dataclass
class XenonHeadlights:
    brightness: int

    def light(self):
        print(f'LIGHT! {self.brightness}')

@dataclass
class Car:
    engine: EngineProtocol
    headlights: HeadlightsProtocol

    def go(self):
        self.engine.start()
        self.headlights.light()

def get_config():
    return {
        EngineProtocol: factory(V8Engine, sound=EnvField('ENGINE_SOUND')),
        HeadlightsProtocol: factory(
            XenonHeadlights, 
            brightness=EnvField('HEADLIGHTS_BRIGHTNESS', int)
        ),
        TransportProtocol: Car,
    }

injector = DependencyInjector(get_config())
injected_driver = injector.inject(Driver)
injected_driver().drive()
```

#### Clients connect/disconnect
Connect can be used for async class initialization 
```python
import aioredis

from typing import Protocol
from trainspotting import DependencyInjector

class ClientProtocol(Protocol):
    async def do(self):
        ...

class RedisClient:
    def __init__(self):
        self.pool = None
        
    async def do(self):
        if not self.pool:
            raise ValueError
        print('did something')
    
    async def connect(self):
        self.pool = await aioredis.create_redis_pool(('127.0.0.1', 6379))
        print('connected')
        
    async def disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()
        print('disconnected')


async def main(client: ClientProtocol):
    await client.do()


injector = DependencyInjector({ClientProtocol: RedisClient})
injected = injector.inject(main)

async with injector.deps:  # connected
    await injected() # did something
# disconnected
```

#### Types Injection
```python
class EntityProtocol(Protocol):
    def do(self): ...

class Entity:
    def do(self):
        print('do something')

@dataclass
class SomeUsefulClass:
    entity: Type[EntityProtocol]

injector.add_config({EntityProtocol: Entity})
injector.inject(SomeUsefulClass)
```

#### Lazy injections
```python
@injector.lazy_inject
async def some_func(client: ClientProtocol):
    await client.do_something()


some_func()  # raise TypeError, missing argument client
injector.do_lazy_injections()
some_func()  # ok
```

#### Extend or change config
```python
injector.add_config({ClientProtocol: Client})
```

#### EnvField
```python
import os
from typing import Protocol
from dataclasses import dataclass
from trainspotting import DependencyInjector
from trainspotting.factory import factory, EnvField


class ClientProtocol(Protocol):
    def do(self):
        ...


@dataclass
class Client(ClientProtocol):
    url: str
    log_prefix: str
    timeout: int = 5

    def do(self):
        print(f'{self.log_prefix}: sent request to {self.url} with timeout {self.timeout}')


injector = DependencyInjector({
    ClientProtocol: factory(
        Client,
        url=EnvField('SERVICE_URL'),
        log_prefix=EnvField('LOG_PREFIX', default='CLIENT'),
        timeout=EnvField('SERVICE_TIMEOUT', int, optional=True),
    )
})


def main(client: ClientProtocol):
    client.do()
    
    
os.environ.update({'SERVICE_URL': 'some_url'})
injected = injector.inject(main)
injected()  # CLIENT: sent request to some_url with timeout 5
```


#### Supports type validation
```python
from typing import Protocol, runtime_checkable
from trainspotting import DependencyInjector


@runtime_checkable
class ClientProtocol(Protocol):
    def do(self):
        ...


class Client:
    def do(self):
        print('did something')


class BadClient:
    def wrong_do(self):
        ...
    

def main(client: ClientProtocol):
    client.do()

injector = DependencyInjector({
    ClientProtocol: BadClient,
})

injector.inject(main)()  # raise InjectionError: <class 'BadClient'> does not realize <class 'ClientProtocol'> interface

injector = DependencyInjector({
    ClientProtocol: Client,
})

injector.inject(main)()  # prints: did something
```
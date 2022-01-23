import logging as logger
from dataclasses import dataclass


class BaseLogger:
    """ You can use this logger to disable injector logs """

    def debug(self, msg, *args, **kwargs):
        ...

    def exception(self, msg, *args, exc_info=True, **kwargs):
        ...


@dataclass
class Logger(BaseLogger):
    log: logger.Logger = logger  # type: ignore

    def debug(self, msg, *args, **kwargs):
        self.log.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.log.exception(msg, *args, exc_info=exc_info, **kwargs)

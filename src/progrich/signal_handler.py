import signal
from types import FrameType
from typing import Callable, ClassVar, Self

type HandlerFn = Callable[[int, FrameType | None], None]


class SignalHandler:
    _default: ClassVar[Self | None] = None
    original_handler: signal._HANDLER | None = None
    handlers: dict[int, HandlerFn]

    def __init__(self, signal_num: signal.Signals = signal.SIGINT):
        self.signal_num = signal_num
        self.original_handler = signal.signal(signal_num, self)
        self.handlers = dict()

    @classmethod
    def default(cls) -> Self:
        """
        Get the default SignalHandler.

        This same instance will be used for all signal handlers, so that there is no
        issue with replacing the original handler.
        """
        if cls._default is None:
            cls._default = cls()
        return cls._default

    def register(self, obj: object, fn: HandlerFn):
        obj_id = id(obj)
        self.handlers[obj_id] = fn

    def unregister(self, obj: object):
        obj_id = id(obj)
        if obj_id not in self.handlers:
            raise ValueError(f"No handler registered for object {obj_id} - {obj!r}")

    def __call__(self, signal_num: int, frame: FrameType | None = None):
        for handler in self.handlers.values():
            handler(signal_num, frame)
        if self.original_handler is not None and callable(self.original_handler):
            self.original_handler(signal_num, frame)

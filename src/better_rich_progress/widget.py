from abc import ABC, abstractmethod

from rich.console import RenderableType


class Widget(ABC):
    """
    The Base for any widgets. As long as a class implements this, it can be included in
    the progress display.
    """

    active: bool
    visible: bool

    @abstractmethod
    def is_done(self) -> bool:
        raise NotImplementedError("is_done method is not implemented")

    @abstractmethod
    def __rich__(self) -> RenderableType:
        raise NotImplementedError("__rich__ method is not implemented")

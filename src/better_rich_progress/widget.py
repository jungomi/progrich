from abc import ABC, abstractmethod
from typing import Literal

from rich.console import RenderableType

type WidgetState = Literal["idle", "running", "completed", "aborted"]


class Widget(ABC):
    """
    The Base for any widgets. As long as a class implements this, it can be included in
    the progress display.
    """

    active: bool = False
    visible: bool = False
    state: WidgetState = "idle"

    @abstractmethod
    def __rich__(self) -> RenderableType:
        raise NotImplementedError("__rich__ method is not implemented")

    def is_done(self) -> bool:
        return self.state == "completed" or self.state == "aborted"

    def is_running(self) -> bool:
        return self.state == "running"

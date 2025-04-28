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
    persist: bool = False
    state: WidgetState = "idle"

    @abstractmethod
    def __rich__(self) -> RenderableType:
        raise NotImplementedError("__rich__ method is not implemented")

    def is_done(self) -> bool:
        return self.state == "completed" or self.state == "aborted"

    def is_running(self) -> bool:
        return self.state == "running"

    def start(self, reset: bool = False):
        if self.is_done():
            raise RuntimeError(
                f"{self.__class__.__name__} has already been completed, "
                "cannot start it!"
            )
        if self.is_running() and not reset:
            return
        self.active = True
        self.visible = True
        self.state = "running"

    def stop(self):
        if self.is_done():
            raise RuntimeError(
                f"Cannot stop {self.__class__.__name__} as it is not running."
            )
        self.state = "completed"
        self.active = False
        if not self.persist:
            self.visible = False

    def pause(self):
        self.state = "idle"

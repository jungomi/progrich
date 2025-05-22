from abc import ABC, abstractmethod
from typing import Literal

from rich.console import RenderableType

type WidgetState = Literal["idle", "running", "completed", "aborted"]


class Widget(ABC):
    """
    The Base for any widgets. As long as a class implements this, it can be included in
    the progress display.

    Every widget needs to implement the __rich__ method which creates a rich
    representation that will be rendered.
    """

    active: bool = False
    visible: bool = False
    persist: bool = False
    state: WidgetState = "idle"

    @abstractmethod
    def __rich__(self) -> RenderableType:
        raise NotImplementedError("__rich__ method is not implemented")

    def is_done(self) -> bool:
        """
        Check whether the widget is done.

        Returns:
            out (bool): Whether the widget is done.
        """
        return self.state == "completed" or self.state == "aborted"

    def is_running(self) -> bool:
        """
        Check whether the widget is running.

        Returns:
            out (bool): Whether the widget is running.
        """
        return self.state == "running"

    def start(self, reset: bool = False):
        """
        Start the widget.

        If the widget supports it, it can also be reset.

        Args:
            reset (bool): Reset the progress, i.e. restarting it. [Default: False]
        """
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
        """
        Stop the widget.

        This marks the widget as terminated and unless it is supposed to persist,
        it will no longer be shown.
        """
        if self.is_done():
            raise RuntimeError(
                f"Cannot stop {self.__class__.__name__} as it is not running."
            )
        self.state = "completed"
        self.active = False
        if not self.persist:
            self.visible = False

    def pause(self):
        """
        Pause the widget without hiding it.
        """
        self.state = "idle"

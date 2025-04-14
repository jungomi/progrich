from types import TracebackType
from typing import Self, override

from rich.console import RenderableType
from rich.spinner import Spinner as RichSpinner

from .manager import ProgressManager
from .widget import Widget


class Spinner(Widget):
    """
    A simple wrapper around rich's Spinner, but customised and integrated with other
    widgets.

    For example:

    ⠦ Saving new best model to: log/example/best
    """

    def __init__(
        self,
        text: str,
        spinner: str = "dots",
        persist: bool = False,
        manager: ProgressManager | None = None,
    ):
        self.text = text
        self.spinner = spinner
        self.persist = persist
        self.manager = manager or ProgressManager.default()
        self.manager.add(self)
        self.status = RichSpinner(spinner, text=text)

    @override
    def __rich__(self) -> RenderableType:
        return self.status

    def __enter__(self) -> Self:
        self.manager.__enter__()
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if not self.is_done():
            self.stop()
        self.manager.__exit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    def __del__(self):
        if not self.is_done():
            self.stop()
        self.manager.disable(self)

    def start(self, reset: bool = False):
        if self.is_done():
            raise RuntimeError("Spinner has already been completed, cannot start it!")
        if self.is_running() and not reset:
            return
        self.active = True
        self.visible = True
        self.manager.enable(widget=self)
        self.state = "running"

    def stop(self):
        if self.is_done():
            raise RuntimeError("Cannot stop Spinner as it is not running.")
        self.state = "completed"
        self.active = False
        if not self.persist:
            self.visible = False
            self.manager.update()
        self.manager.disable(widget=self)

    def pause(self):
        # Not really supported
        self.state = "idle"

    def update(self, text: str):
        self.text = text
        self.status = RichSpinner(self.spinner, text=self.text)
        self.manager.update()

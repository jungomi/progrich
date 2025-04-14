from typing import override

from rich.console import RenderableType
from rich.spinner import Spinner as RichSpinner

from .manager import ManagedWidget, ProgressManager


class Spinner(ManagedWidget):
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
        super().__init__(persist=persist, manager=manager)
        self.text = text
        self.spinner = spinner
        self.status = RichSpinner(spinner, text=text)

    @override
    def __rich__(self) -> RenderableType:
        return self.status

    def update(self, text: str):
        self.text = text
        self.status = RichSpinner(self.spinner, text=self.text)
        self.manager.update()

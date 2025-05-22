from typing import override

from rich.console import RenderableType
from rich.spinner import Spinner as RichSpinner

from .manager import ManagedWidget, Manager


class Spinner(ManagedWidget):
    """
    A simple wrapper around rich's Spinner, but customised and integrated with other
    widgets.

    For example:

    ⠦ Saving new best model to: log/example/best
    """

    final_text: str | None

    def __init__(
        self,
        text: str,
        spinner: str = "dots",
        persist: bool = False,
        manager: Manager | None = None,
    ):
        super().__init__(persist=persist, manager=manager)
        self.text = text
        self.spinner = spinner
        self.status = RichSpinner(spinner, text=text)
        self.final_text = None

    @override
    def __rich__(self) -> RenderableType:
        if self.is_done() and self.final_text:
            return self.final_text
        return self.status

    def update(self, text: str):
        self.text = text
        self.status = RichSpinner(self.spinner, text=self.text)
        self.manager.update()

    def success(self, text: str | None = None, icon: str = "✔"):
        self.persist = True
        self.final_text = f"[green]{icon}[/green] {text or self.text}"
        self.stop()

    def fail(self, text: str | None = None, icon: str = "✖"):
        self.persist = True
        self.final_text = f"[red]{icon}[/red] {text or self.text}"
        self.stop()
        self.state = "aborted"

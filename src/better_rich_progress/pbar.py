from types import TracebackType
from typing import Literal, Self

from rich.console import Console
from rich.progress import Progress, ProgressColumn

from .columns import default_columns
from .manager import ProgressManager

type ProgressState = Literal["idle", "running", "completed", "aborted"]


class ProgressBar:
    """
    A simple wrapper around rich's Progress, but customised and simplified to be
    closer to what tqdm uses as defaults, as that makes much more sense than rich's
    defaults.

    For example:

    Epoch 1 - Train   4% ━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━  36/800 • 0:01:09 • ETA 0:18:08
    """

    state: ProgressState

    def __init__(
        self,
        desc: str,
        total: float,
        current: float = 0,
        prefix: str = "",
        progress: Progress | None = None,
        persist: bool = False,
        manager: ProgressManager | None = None,
    ):
        self.desc = desc
        self.total = total
        self.current = current
        self.prefix = prefix
        self.progress = progress or self.create_rich_progress()
        self.task_id = self.progress.add_task(
            desc,
            total=total,
            completed=current,  # pyright: ignore[reportArgumentType]
            start=False,
            visible=False,
            prefix=prefix,
        )
        self.state = "idle"
        self.persist = persist
        self.manager = manager or ProgressManager.default()
        self.manager.add(self.progress)

    @staticmethod
    def create_rich_progress(
        columns: list[ProgressColumn] | None = None, console: Console | None = None
    ) -> Progress:
        if columns is None:
            columns = default_columns()
        return Progress(*columns, console=console)

    def is_done(self) -> bool:
        return self.state == "completed" or self.state == "aborted"

    def is_running(self) -> bool:
        return self.state == "running"

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
        # TODO: Handle shared progress across multiple bars.
        self.manager.remove(self.progress)

    def start(self, reset: bool = False):
        if self.is_done():
            raise RuntimeError(
                "ProgressBar has already been completed, cannot start it!"
            )
        if self.is_running() and not reset:
            return
        if reset:
            self.progress.reset(self.task_id, start=True, visible=True)
            self.current = 0
        else:
            self.progress.update(self.task_id, visible=True)
            self.progress.start_task(self.task_id)
        self.state = "running"

    def stop(self):
        if self.is_done():
            raise RuntimeError("Cannot stop ProgressBar as it is not running.")
        self.progress.stop_task(self.task_id)
        if not self.persist:
            self.progress.remove_task(self.task_id)
        self.state = "completed" if self.current >= self.total else "aborted"
        if self.state == "completed":
            self.manager.complete(self.progress)

    def pause(self):
        self.progress.stop_task(self.task_id)
        self.state = "idle"

    def advance(self, num: float = 1.0):
        if not self.is_running():
            raise RuntimeError("Cannot advance ProgressBar as it is not running.")
        if self.current >= self.total:
            raise RuntimeError(
                f"ProgressBar already reached the total ({self.total}), "
                "cannot advance any further."
            )
        self.progress.update(self.task_id, advance=num)
        self.current += num

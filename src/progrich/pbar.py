from typing import Self, override

from rich.console import Console, RenderableType
from rich.progress import Progress, ProgressColumn

from .columns import default_columns
from .manager import ManagedWidget, ProgressManager


class ProgressBar(ManagedWidget):
    """
    A simple wrapper around rich's Progress, but customised and simplified to be
    closer to what tqdm uses as defaults, as that makes much more sense than rich's
    defaults.

    For example:

    Epoch 1 - Train   4% ━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━  36/800 • 0:01:09 • ETA 0:18:08
    """

    progress: Progress

    def __init__(
        self,
        desc: str,
        total: float,
        current: float = 0,
        prefix: str = "",
        progress: Progress | Self | None = None,
        persist: bool = False,
        manager: ProgressManager | None = None,
    ):
        super().__init__(persist=persist, manager=manager)
        self.desc = desc
        self.total = total
        self.current = current
        self.prefix = prefix
        # When the progress is another ProgressBar, this new pbar should be added to the
        # existing Progress widget from rich, hence reuse it.
        if isinstance(progress, ProgressBar):
            progress = progress.progress
        self.progress = progress or self.create_rich_progress(
            console=self.manager.get_console()
        )
        self.task_id = self.progress.add_task(
            desc,
            total=total,
            completed=current,  # pyright: ignore[reportArgumentType]
            start=False,
            visible=False,
            prefix=prefix,
        )

    @staticmethod
    def create_rich_progress(
        columns: list[ProgressColumn] | None = None, console: Console | None = None
    ) -> Progress:
        if columns is None:
            columns = default_columns()
        return Progress(*columns, console=console)

    @override
    def __rich__(self) -> RenderableType:
        return self.progress

    def start(self, reset: bool = False):
        super().start(reset=reset)
        if reset:
            self.progress.reset(self.task_id, start=True, visible=True)
            self.current = 0
        else:
            self.progress.update(self.task_id, visible=True)
            self.progress.start_task(self.task_id)

    def stop(self):
        super().stop()
        if not self.persist:
            self.progress.remove_task(self.task_id)
        self.state = "completed" if self.current >= self.total else "aborted"

    def pause(self):
        super().pause()
        self.progress.stop_task(self.task_id)

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

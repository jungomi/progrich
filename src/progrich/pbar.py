from collections.abc import Collection, Generator
from typing import Self, override

from rich.console import Console, RenderableType
from rich.progress import Progress, ProgressColumn

from .columns import default_columns
from .manager import ManagedWidget, Manager


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
        manager: Manager | None = None,
    ):
        """
        Args:
            desc (str): Description to be shown on the progress bar.
            total (float): Total number of steps in the progress. Can also have decimal
                points, for example for showing the progress of a download.
            current (float): Current step in the progress. [Default: 0]
            prefix (str): Prefix to be shown at the beginning of the progress bar.
                [Default: ""]
            progress (Progress | ProgressBar, optional): Use an existing rich Progress
                to display the progress bar. If it's not given, it will create a new
                one. It is recommended to share the same Progress as it will align them
                better, since some parts are dynamicaly sized.
            persist (bool): Whether to persist the progress bar once it is finished.
                [Default: False]
            manager (Manager, optional): Manager that handles displaying the progress
                bar. If not specified, it will use the default (global) Manager. Unless
                you need to create your own manager, you can leave this out and it
                everything is handled automatically.
        """
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

    @classmethod
    def iter[T](
        cls,
        iterable: Collection[T],
        desc: str = "",
        prefix: str = "",
        progress: Progress | Self | None = None,
        persist: bool = False,
        manager: Manager | None = None,
    ) -> Generator[T]:
        """
        Creater an iterator over a collection (iterable whose size is known) and
        automatically show a progress bar for it.

        Args:
            iterable (Collection[T]): Collection to be iterated over.
            desc (str): Description to be shown on the progress bar. [Default: ""]
            prefix (str): Prefix to be shown at the beginning of the progress bar.
                [Default: ""]
            progress (Progress | ProgressBar, optional): Use an existing rich Progress
                to display the progress bar. If it's not given, it will create a new
                one. It is recommended to share the same Progress as it will align them
                better, since some parts are dynamicaly sized.
            persist (bool): Whether to persist the progress bar once it is finished.
                [Default: False]
            manager (Manager, optional): Manager that handles displaying the progress
                bar. If not specified, it will use the default (global) Manager. Unless
                you need to create your own manager, you can leave this out and it
                everything is handled automatically.

        Yields:
            obj (T): Each object in the iterable.
        """
        with cls(
            total=len(iterable),
            desc=desc,
            prefix=prefix,
            progress=progress,
            persist=persist,
            manager=manager,
        ) as pbar:
            for obj in iterable:
                yield obj
                pbar.advance()

    @override
    def __rich__(self) -> RenderableType:
        return self.progress

    def start(self, reset: bool = False):
        """
        Start the progress bar.

        Args:
            reset (bool): Reset the progress, i.e. restarting it. [Default: False]
        """
        super().start(reset=reset)
        if reset:
            self.progress.reset(self.task_id, start=True, visible=True)
            self.current = 0
        else:
            self.progress.update(self.task_id, visible=True)
            self.progress.start_task(self.task_id)

    def stop(self):
        """
        Stop the progress bar.

        This marks the progress as terminated and unless the progress bar is persisted,
        it will no longer be shown.
        """
        super().stop()
        if not self.persist:
            self.progress.remove_task(self.task_id)
        self.state = "completed" if self.current >= self.total else "aborted"

    def pause(self):
        """
        Pause the progress bar without hiding it.
        """
        super().pause()
        self.progress.stop_task(self.task_id)

    def advance(self, num: float = 1.0):
        """
        Advance the progress.

        The progress must be running and cannot exceed the total.

        Args:
            num (float): By how much the progress is advanced [Default: 1.0]
        """
        if not self.is_running():
            raise RuntimeError("Cannot advance ProgressBar as it is not running.")
        if self.current >= self.total:
            raise RuntimeError(
                f"ProgressBar already reached the total ({self.total}), "
                "cannot advance any further."
            )
        self.progress.update(self.task_id, advance=num)
        self.current += num

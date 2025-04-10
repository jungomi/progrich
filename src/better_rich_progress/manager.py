from dataclasses import dataclass
from types import TracebackType
from typing import ClassVar, Self

from rich.console import Console, Group
from rich.live import Live
from rich.progress import Progress


@dataclass
class ManagedProgressBar:
    progress: Progress
    done: bool = False

    def has_bars(self) -> bool:
        return len(self.progress.tasks) > 0


class ProgressManager:
    """
    A progress bar manager that handles multiple bars.

    Rich does not allow to have multiple progress bars at the same time, without having
    to manually create a group that handles the progress bars together, which is kind of
    awful design to begin with, so this takes care of that.

    For example, two progress bars that are shown simultaneously:
        - Total: Shows the total time elapsed for the epochs
        - Train/Validation: Shows the progress in each train/validation epoch (batches)

    Would look roughly like this:

    [ 1/10]   Total   0% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    0/10 • 0:01:09 • ETA -:--:--
    Epoch 1 - Train   4% ━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━  36/800 • 0:01:09 • ETA 0:18:08
    """

    _default: ClassVar[Self | None] = None
    _ctx_count: int = 0
    pbars: dict[int, ManagedProgressBar]

    @classmethod
    def default(cls) -> Self:
        if cls._default is None:
            cls._default = cls()
        return cls._default

    def __init__(
        self,
        console: Console | None = None,
        completed_on_top: bool = False,
    ):
        self.completed_on_top = completed_on_top
        self.live = Live(Group(), console=console)
        self.pbars = {}

    def __enter__(self) -> Self:
        self._ctx_count += 1
        self.live.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if self._ctx_count <= 0:
            raise RuntimeError("__exit__ was called more often than __enter__")
        self._ctx_count -= 1
        if self._ctx_count == 0:
            self.live.__exit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    def __del__(self):
        self.close()

    def enable(self) -> Self:
        self.live.__enter__()
        self.update()
        return self

    def disable(self) -> Self:
        self.live.update(Group(), refresh=True)
        self.close()
        return self

    def close(self):
        self.live.__exit__(None, None, None)

    def clear(self):
        self.disable()
        self.pbars = {}
        self.update()

    def _get_pbars(self) -> list[Progress]:
        if self.completed_on_top:
            completed: list[Progress] = []
            running: list[Progress] = []
            for pbar in self.pbars.values():
                # Ignore progress bars that have no tasks
                if not pbar.has_bars():
                    continue
                if pbar.done:
                    completed.append(pbar.progress)
                else:
                    running.append(pbar.progress)
            return completed + running
        else:
            return [pbar.progress for pbar in self.pbars.values() if pbar.has_bars()]

    def add(self, progress: Progress):
        obj_id = id(progress)
        self.pbars[obj_id] = ManagedProgressBar(progress, done=False)
        self.update()

    def complete(self, progress: Progress):
        obj_id = id(progress)
        pbar = self.pbars.get(obj_id)
        if pbar is None:
            raise ValueError("Cannot complete provided progress, as it was not added.")
        pbar.done = True
        self.update()

    def remove(self, progress: Progress):
        obj_id = id(progress)
        if obj_id not in self.pbars:
            raise ValueError("Cannot remove provided progress, as it was not added.")
        del self.pbars[obj_id]
        self.update()

    def update(self):
        self.live.update(Group(*self._get_pbars()), refresh=True)

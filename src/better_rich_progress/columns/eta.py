from rich.console import RenderableType
from rich.progress import ProgressColumn, Task
from rich.style import Style
from rich.table import Column
from rich.text import Text

from ..fmt import DurationHumanRedable, format_duration
from .utils import task_elapsed_till_last_step


class ETAColumn(ProgressColumn):
    """
    Displays the elapsed time of the progress.

    Values up to one day are given as [H:]MM:SS and everything above with human readable
    suffixes.

    Examples:
        - 14
        - 01:52
        - 1d2h9s
    """

    # Refresh twice a second to prevent jitter
    max_refresh = 0.5
    human_readable: DurationHumanRedable

    def __init__(
        self,
        table_column: Column | None = None,
        style: str | Style = "cyan",
        human_readable: DurationHumanRedable = "when-large",
        icon_unknown: str = "⁇",
    ):
        self.style = style
        self.human_readable = human_readable
        self.icon_unknown = icon_unknown
        super().__init__(table_column=table_column)

    def render(self, task: Task) -> RenderableType:
        completed = task.completed
        total = task.total
        elapsed = task_elapsed_till_last_step(task)
        if elapsed is None or elapsed == 0 or completed == 0 or total is None:
            return Text(f"ETA {self.icon_unknown} ", style=self.style)
        remaining = elapsed * (total - completed) / completed
        return Text(
            f"ETA {format_duration(remaining, human_readable=self.human_readable)}",
            style=self.style,
        )

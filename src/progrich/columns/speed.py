from rich.console import RenderableType
from rich.progress import ProgressColumn, Task
from rich.style import Style
from rich.table import Column
from rich.text import Text

from ..fmt import format_duration_human_readable, format_large_num_si
from .utils import task_elapsed_till_last_step


class SpeedColumn(ProgressColumn):
    """
    Displays the speed of the progress.

    Large values are by default formatted with human readable suffixes.

    Examples:
        - 14s/it
        - 1m53s/it
        - 2it/s
    """

    # Refresh twice a second to prevent jitter
    max_refresh = 0.5

    def __init__(
        self,
        table_column: Column | None = None,
        style: str | Style = "blue",
        icon: str = "󱥸",
    ):
        self.style = style
        self.icon = icon
        super().__init__(table_column=table_column or Column(justify="right"))

    def render(self, task: Task) -> RenderableType:
        completed = task.completed
        elapsed = task_elapsed_till_last_step(task)
        if elapsed is None or elapsed == 0 or completed == 0:
            return Text(f"{self.icon} it/s", style=self.style)
        speed = completed / elapsed
        if speed < 1:
            return Text(
                f"{format_duration_human_readable(1 / speed)}/it", style=self.style
            )
        return Text(f"{format_large_num_si(speed)} it/s", style=self.style)

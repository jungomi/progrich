from rich.console import RenderableType
from rich.progress import ProgressColumn, Task
from rich.style import Style
from rich.table import Column
from rich.text import Text

from ..fmt import DurationHumanRedable, format_duration


class ElapsedColumn(ProgressColumn):
    """
    Displays the elapsed time of the progress.

    Values up to one day are given as [H:]MM:SS and everything above with human readable
    suffixes.

    Examples:
        - 14
        - 01:52
        - 1d2h9s
    """

    human_readable: DurationHumanRedable

    def __init__(
        self,
        table_column: Column | None = None,
        style: str | Style = "yellow",
        human_readable: DurationHumanRedable = "when-large",
    ):
        self.style = style
        self.human_readable = human_readable
        super().__init__(table_column=table_column or Column(justify="right"))

    def render(self, task: Task) -> RenderableType:
        elapsed = task.finished_time if task.finished else task.elapsed
        return Text(
            format_duration(elapsed or 0, human_readable=self.human_readable),
            style=self.style,
        )

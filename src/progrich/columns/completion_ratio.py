from rich.console import RenderableType
from rich.progress import ProgressColumn, Task
from rich.style import Style
from rich.table import Column
from rich.text import Text

from ..fmt import DurationHumanRedable, format_large_num


class CompletionRatioColumn(ProgressColumn):
    """
    Displays the completion ratio of progress.

    Large values are by default formatted with human readable suffixes.

    Examples:
        - 5 / 10
        - 800 / 2.7k
        - 1.2M / 3.5B
    """

    human_readable: DurationHumanRedable

    def __init__(
        self,
        table_column: Column | None = None,
        style: str | Style = "green",
        human_readable: DurationHumanRedable = "when-large",
    ):
        self.style = style
        self.human_readable = human_readable
        super().__init__(table_column=table_column or Column(justify="right"))

    def render(self, task: Task) -> RenderableType:
        completed = task.completed
        completed_str = format_large_num(completed, human_readable=self.human_readable)
        total = task.total
        if total is None:
            return Text(completed_str, style=self.style)
        total_str = format_large_num(total, human_readable=self.human_readable)
        total_digits = len(str(int(total)))
        # Pad the completed string to the same length as the total, so that it won't
        # jump around when it increases.
        # When it's human readable, it might be shorter, but it should always at least
        # have 6 characters (up to 1 million before it's shortened).
        # But don't go up to 6 chars, if the maximum will never have this many digits.
        min_len = max(len(total_str), min(total_digits, 6))
        return Text(f"{completed_str:>{min_len}}/{total_str}", style=self.style)

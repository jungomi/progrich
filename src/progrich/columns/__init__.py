from rich.progress import BarColumn, ProgressColumn, TextColumn

from .completion_ratio import CompletionRatioColumn
from .elapsed import ElapsedColumn
from .eta import ETAColumn
from .speed import SpeedColumn

__all__ = [
    "CompletionRatioColumn",
    "ElapsedColumn",
    "ETAColumn",
    "SpeedColumn",
    "default_columns",
]


def default_columns(separator: str = "[dim]•[/dim]") -> list[ProgressColumn]:
    return [
        TextColumn("{task.fields[prefix]}"),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(
            bar_width=None,
            style="dim",
            complete_style="none",
            finished_style="green"
        ),
        CompletionRatioColumn(),
        TextColumn(separator),
        ElapsedColumn(),
        TextColumn(separator),
        ETAColumn(human_readable="always"),
        TextColumn(separator),
        SpeedColumn(),
    ]

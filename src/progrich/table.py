import copy
from typing import Any, override

from rich import box
from rich.console import RenderableType
from rich.table import Table as RichTable

from .manager import ManagedWidget, Manager


class Table(ManagedWidget):
    """
    A simple wrapper around rich's Table, but customised to automatically update when
    a new row is added as well as and integrated with other widgets.

    For example:

    ──────────────────────────────────────────────────────────
     Epoch              Loss            Accuracy
    ──────────────────────────────────────────────────────────
     0                  0.3             0.69
     1                  0.25            0.72
     2                  0.2             0.75
    ─────────────────────────────────────────────────────────
    """

    def __init__(
        self,
        column_names: list[str],
        rows: list[list[Any]] = [],
        title: str | None = None,
        max_rows: int = 10,
        rich_table: RichTable | None = None,
        persist: bool = False,
        manager: Manager | None = None,
    ):
        """
        Args:
            column_names (list[str]): Name of the columns (headers).
            rows (list[list[Any]]): A list of rows to add to the table. Each row must be
                a list with a value for each of the columns.
                [Default: [] (empty table)]
            title (str, optional): Title to show above the table.
            max_rows (int): Maximum number of rows to display. Whenever there are more
                rows available, only the last max_rows rows will be shown
                (the beginning will be hidden). The rows are still present, but not
                shown in the output table, you can access them with table.rows.
                [Default: 10]
            rich_table (RichTable, optional): The rich Table to use for displaying the
                table. This allows configuring extra style options in the table.
            persist (bool): Whether to persist the progress bar once it is finished.
                [Default: False]
            manager (Manager, optional): Manager that handles displaying the progress
                bar. If not specified, it will use the default (global) Manager. Unless
                you need to create your own manager, you can leave this out and it
                everything is handled automatically.
        """
        super().__init__(persist=persist, manager=manager)
        assert max_rows > 0, f"max_rows={max_rows} is not permitted, must be > 0"
        self.column_names = column_names
        self.rows = rows
        self.max_rows = max_rows
        self.base_table = rich_table or RichTable(
            box=box.HORIZONTALS,
            border_style="dim",
            caption_style="",
            min_width=60,
        )
        for column in column_names:
            self.base_table.add_column(column)
        if title:
            self.base_table.title = title

    def __len__(self) -> int:
        return len(self.rows)

    @override
    def __rich__(self) -> RenderableType:
        table = copy.deepcopy(self.base_table)
        # Only display the maximum rows (from the back)
        for row in self.rows[-self.max_rows :]:
            table.add_row(*[str(val) for val in row])
        return table

    def insert_row(self, values: list[Any]):
        """
        Insert a row at the end of the table.

        If it exceeds the maximum number of rows, the first one will no longer be
        visible.

        Args:
            values (list[Any]): List of values for each column in the row.
        """
        self.rows.append(values)
        self.manager.update()

    def remove_row(self, index: int = -1):
        """
        Remove a row at the given index.

        The index is based on the total number of rows, not the visible ones.

        Args:
            index (int): Index to remove (can be negative) [Default: -1]
        """
        num_rows = len(self.rows)
        if index < 0:
            index = num_rows + index
        self.rows = self.rows[:index] + self.rows[index + 1 :]
        self.manager.update()

    def clear(self):
        """
        Clear the table by removing all rows.
        """
        self.rows = []
        self.manager.update()

    @override
    def stop(self):
        # This is a special case, where disabling it will not persist it in any case. So
        # to circumvent this, it is never persisted, but instead printed when it's
        # stopped. Which gives the desired result of persisting the table properly,
        # while not keeping the widget around for no reason.
        should_print = self.persist
        self.persist = False
        super().stop()
        if should_print:
            self.manager.get_console().print(self)

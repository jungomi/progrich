from dataclasses import dataclass, field
from types import TracebackType
from typing import ClassVar, Self, override

from rich.console import Console, Group
from rich.live import Live

from .widget import Widget


@dataclass
class EnabledTracker:
    manual: bool | None = None
    ctx: int = 0
    widgets: set[int] = field(default_factory=set)

    def is_enabled(self) -> bool:
        if self.manual is None:
            return self.ctx > 0 or len(self.widgets) > 0
        else:
            return self.manual

    def add_widget(self, widget: Widget):
        obj_id = id(widget)
        self.widgets.add(obj_id)

    def remove_widget(self, widget: Widget):
        obj_id = id(widget)
        if obj_id in self.widgets:
            self.widgets.remove(obj_id)

    def clear_widgets(self):
        self.widgets = set()


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
    _enabled_tracker: EnabledTracker
    completed_on_top: bool
    live: Live
    widgets: dict[int, Widget]

    @classmethod
    def default(cls) -> Self:
        """
        Get the default ProgressManager.

        This same instance will be used by all progress widgets for which no explicit
        ProgressManager has been given. Therefore, they will automatically be managed in
        the same place, which makes the rendering work seamlessly.
        """
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
        self.widgets = {}
        self._enabled_tracker = EnabledTracker()

    def __enter__(self) -> Self:
        self._enabled_tracker.ctx += 1
        self.live.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if self._enabled_tracker.ctx <= 0:
            raise RuntimeError("__exit__ was called more often than __enter__")
        self._enabled_tracker.ctx -= 1
        if self.live.is_started and not self._enabled_tracker.is_enabled():
            self.live.__exit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    def __del__(self):
        self._enabled_tracker.manual = None
        self._enabled_tracker.clear_widgets()
        self.update()
        # Some clean up, because calling __exit__ on the live causes an error as the
        # console object is no longer available during shutdown of Python.
        # This just restores the terminal.
        if self.live.console.is_alt_screen:
            self.live.console.set_alt_screen(False)
        self.live.console.clear_live()
        self.live.console.show_cursor()

    def enable(self, widget: Widget | None = None) -> Self:
        if widget:
            self._enabled_tracker.add_widget(widget)
        else:
            self._enabled_tracker.manual = True
        self.live.__enter__()
        self.update()
        return self

    def disable(self, widget: Widget | None = None) -> Self:
        if widget:
            self._enabled_tracker.remove_widget(widget)
        else:
            self._enabled_tracker.manual = False
        self.update()
        if not self._enabled_tracker.is_enabled():
            self.close()
        return self

    def close(self):
        self.live.stop()

    def clear(self):
        self.disable()
        self.widgets = {}
        self._enabled_tracker.manual = None
        self._enabled_tracker.clear_widgets()
        self.update()

    def _get_widgets(self) -> list[Widget]:
        visible_widgets = []
        if self.completed_on_top:
            completed: list[Widget] = []
            running: list[Widget] = []
            for widget in self.widgets.values():
                if not widget.visible:
                    continue
                if widget.is_done():
                    completed.append(widget)
                else:
                    running.append(widget)
            visible_widgets = completed + running
        else:
            visible_widgets = [
                widget for widget in self.widgets.values() if widget.visible
            ]
        # When the manager is disabled, it should only show the widget that persist.
        if not self._enabled_tracker.is_enabled():
            visible_widgets = [widget for widget in visible_widgets if widget.persist]
        return visible_widgets

    def add(self, widget: Widget):
        obj_id = id(widget)
        self.widgets[obj_id] = widget
        self.update()

    def remove(self, widget: Widget):
        obj_id = id(widget)
        if obj_id not in self.widgets:
            raise ValueError("Cannot remove provided widget, as it was not added.")
        del self.widgets[obj_id]
        self.update()

    def update(self):
        if self.live.is_started:
            # Multiple widgets may use the same underlying rich renderable, hence
            # duplicates need to be removed. This can be achieved by converting the list
            # to a dict and back to a list. This preserves the order, since dicts are
            # kept in insertion order in Python.
            renderables = [widget.__rich__() for widget in self._get_widgets()]
            renderables = list(dict.fromkeys(renderables))
            self.live.update(Group(*renderables))


class ManagedWidget(Widget):
    manager: ProgressManager

    def __init__(self, persist: bool = False, manager: ProgressManager | None = None):
        self.persist = persist
        self.manager = manager or ProgressManager.default()
        self.manager.add(self)

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
        self.manager._enabled_tracker.remove_widget(self)
        if not self.is_done():
            super().stop()
            if not self.persist:
                self.manager.update()

    @override
    def start(self, reset: bool = False):
        super().start(reset)
        self.manager.enable(widget=self)

    @override
    def stop(self):
        super().stop()
        if not self.persist:
            # This update is done in order to clear the widget from the Live group,
            # as the stop set it to inactive/invisible, so the rendering needs to be
            # updated before it can be disabled.
            self.manager.update()
        self.manager.disable(widget=self)

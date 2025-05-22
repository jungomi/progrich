# Progrich

Progress bars, spinners and other widgets from [rich][rich] made more intuitive and with more sensible defaults.

## Why not use the built-in progress widgets of rich?

[rich][rich] is a very powerful terminal rendering library that allows creating beautiful outputs. While it already
includes progress bars and spinners, they can be a pain to use. For example, when you want to combine multiple widgets
at the same time, you will have to manually manage one Live widget and group everything into that one, otherwise it will
raise an error. This is not very intuitive at all, and that could be managed automatically without the user having to
think about it.

That is exactly what this library provides. It uses the existing rich widgets and juggles them around to be displayed in
a single Live widget. In 99% of the cases you'll be able to just create your progress widgets and they will be stacked
automatically (similar to tqdm).

### Questionable defaults

The API of rich is somewhat clunky for such simple widgets and they use some questionable defaults. As an
example, the default progress bar (over an iterator) is not adapted to the current terminal width, only shows the
percentage of the progress and the estimate. No time elapsed, no info on number of iterations and the estimate is
calculated based on a single iteration, rather than taking into account the total time elapsed so far, which is severely
inaccurate if not every iteration takes the exact same time. To make matters worse, if an iteration takes longer than 30
seconds, it will not show any estimate at all, making it completely useless.

It is absolutely incomprehensible why they chose these defaults, especially since [tqdm][tqdm] already existed before
it, which has much more sensible defaults that stood the test of time.


## Installation

Progrich is available on PyPI and can be installed like any other dependency.

### uv (recommended)

[uv][uv] is recommended for managing the dependencies of your project.

```sh
uv add progrich
```

### pip

```sh
pip install progrich
```

## ProgressBar

### Basic

```python
from progrich import ProgressBar

pbar = ProgressBar("Basic example", total=20)

# Start the progress, which displays it.
pbar.start()

for i in range(20):
    # Do some work
    ...

    # Advance the progress bar by one step (optionally, specify by how many steps it is advanced)
    pbar.advance()

# Finish the progress, which also hides it unless the ProgressBar was created with persist=True.
pbar.stop()
```

### `with` statement

Starting and stopping the progress bar is a common operation and therefore `ProgressBar` implements a context manager,
which means it can be used in a `with` statement, greatly simplifying the usage.

```python
from progrich import ProgressBar

with ProgressBar("`with` example", total=20) as pbar:
    for i in range(20):
        # Do some work
        ...

        # Advance the progress bar by one step (optionally, specify by how many steps it is advanced)
        pbar.advance()
```

### Iterator

A common operation is to show a progress bar for any iterable. This is supported with the `ProgressBar.iter()` method,
which takes the same argument as the constructor, except that it takes a collection (iterable whose size is known)
instead of a total number of steps.

```python
from progrich import ProgressBar

for i in ProgressBar.iter(range(20), desc="iter example"):
    # Do some work
    ...
```

This is similar to tqdm, but instead of having an overloaded function, it is a separate method to make it more explicit.

### Combining multiple progress bars

Creating multiple progress bars will work out of the box, however due to some components having a dynamic width, they
are not as nicely aligned.

To alleviate the alignment issue, you can provide an existing progress widget which will share the underlying progress
display in order to combine them into a uniform representation.

```python
from progrich import ProgressBar

# The progress for the total training, which will be persisted once the training
# finishes, as it might be helpful to see the total time it took at the end.
pbar_total = ProgressBar("Total", total=5, persist=True, prefix="[Training]")
pbar_total.start()

# Train for 5 epochs
for i in range(5):
    # Each epoch runs throw the whole training dataset
    for batch in ProgressBar.iter(
        train_dataset,
        desc="Train Set",
        prefix=f"Epoch {i + 1}",
        # Share the same progress display!
        progress=pbar_total,
    ):
        # Training loop
        ...

    # Evaluate current model at the end of each epoch
    for batch in ProgressBar.iter(
        validation_dataset,
        desc="Validation Set",
        prefix=f"Epoch {i + 1}",
        # Share the same progress display!
        progress=pbar_total,
    ):
        # Evaluation loop
        ...

    # Epoch ends, so increment the total progress.
    pbar_total.advance()

pbar_total.stop()
```

By specifying `progress=pbar_total` they two progress bars will be aligned more nicely.

## Spinner

The spinner follows the same general API as progress bar, except that there is no count as it is an undetermined
progress indicator.

The most common use case will be showing a spinner when launching a long running operation with no real progress
indication to let the user know that something is happening. For this, using a spinner in a `with` statement is ideal.

```python
from progrich import Spinner

with Spinner("Waiting for server to start..."):
    server = start_server()
```

### ✔ Success / ✖ Fail

It might be helpful to finish the spinner with a message that shows whether the longer running operation succeeded or
failed or to just keep a trace of finished tasks. The methods `Spinner.success()` and `Spinner.fail()` do exactly that
and show the provided message with a coloured icon.

```python
from progrich import Spinner

with Spinner("Waiting for server to start...") as spinner:
    try:
        server = start_server()
        # Finishes with a message like: ✔ Server started on port 3000
        spinner.success(f"Server started on port {server.port}")
    except OSError as e:
        # Finishes with a message like: ✖ Server failed to start with error: port 3000 already in use
        spinner.fail(f"Server failed to start with error: {e}")
```

If no message is provided the message from the spinner will be used instead. You can change the icon that is displayed
by adding the `icon=` argument.

## Manager

In order to combine multiple widgets seamlessly, a `Manager` is used where each of the widgets is added. A default
(global) manager is used automatically if no manager is specified manually. So in most cases you don't need to worry
about creating one yourself.

If you want to customise certain aspects of the manager, you have two options:

- Create a `Manager` yourself and pass it to any widget you create.
- Modify the default manager.

### Modify the default Manager

You can retrieve the default manager with `Manager.default()`.

For example, if you run a distributed program and want to only show the progress in the main process, you can disable
the console for all other processes.

```python
from rich.console import Console
from progrich import Manager

manager = Manager.default()
if not is_main_process:
    # Use a console with quiet=True, so that there is no output.
    manager.set_console(Console(quiet=True))
```

## Implementing a custom widget

You can easily implement your own custom widget by subclassing `ManagedWidget`.

The only required method to implement is `def __rich__(self) -> RenderableType`, which returns any rich-compatible
renderable that will be displayed.

If you plan to use an existing dynamic rich widget, it is as simple as storing that widget in your class and returning
it from the `__rich__` method. *Everything else is handled for you!*

You might also need to customise the `start()` and `stop()` methods, but for everything you are free to any custom
methods or attributes that facilitate handling the state of your widget.

Take a look at the provided widgets, such as [`ProgressBar` in src/progrich/pbar.py](src/progrich/pbar.py) or
[`Spinner` in src/progrich/spinner.py](src/progrich/spinner.py) to get a better understanding.

[rich]: https://github.com/Textualize/rich
[tqdm]: https://github.com/tqdm/tqdm
[uv]: https://docs.astral.sh/uv/

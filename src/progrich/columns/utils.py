from rich.progress import Task


# Simple helper to get the elapsed time of the task
def task_elapsed_till_last_step(task: Task) -> float | None:
    if task.start_time is None:
        return None
    with task._lock:
        progress = task._progress
        if not progress:
            return None
        last_step = progress[-1].timestamp
        return last_step - task.start_time

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional


class Status(Enum):
    """Enumeration for task completion status."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class TaskError(Exception):
    """Base exception class for task manager specific errors."""

    pass


class TaskNotFoundError(TaskError):
    """Exception raised when a requested task does not exist."""

    def __init__(self, task_id: int):
        super().__init__(f"Task with ID {task_id} was not found.")


@dataclass
class Task:
    """Data class representing a individual task entity."""

    id: int
    title: str
    description: str
    status: Status = Status.PENDING
    created_at: str = datetime.now().isoformat()

    def mark_status(self, new_status: Status) -> None:
        """Updates the status of the task."""
        self.status = new_status


class TaskStorageManager:
    """Context manager to cleanly handle saving data to disk automatically."""

    def __init__(self, filename: str, registry: Dict[int, Task]):
        self.filename = filename
        self.registry = registry

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Automatically serialize and save the data when exiting the context block
        serializable_data = {
            str(k): {**asdict(v), "status": v.status.name}
            for k, v in self.registry.items()
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=4)


class TaskManager:
    """Core engine to manage life cycle operations of tasks."""

    def __init__(self, storage_file: str = "tasks_db.json"):
        self.storage_file: str = storage_file
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Internal helper to load previously saved JSON data safely."""
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for k, v in raw_data.items():
                    v["status"] = Status[v["status"]]
                    task = Task(**v)
                    self._tasks[task.id] = task
                if self._tasks:
                    self._next_id = max(self._tasks.keys()) + 1
        except (FileNotFoundError, json.JSONDecodeError):
            self._tasks = {}

    def create_task(self, title: str, description: str) -> Task:
        """Creates and logs a brand new task."""
        new_task = Task(id=self._next_id, title=title, description=description)
        self._tasks[new_task.id] = new_task
        self._next_id += 1

        # Utilize the custom storage context manager
        with TaskStorageManager(self.storage_file, self._tasks):
            pass

        return new_task

    def get_all_tasks(self) -> List[Task]:
        """Returns a list of all active or pending tasks."""
        return list(self._tasks.values())

    def update_task_status(self, task_id: int, status: Status) -> Task:
        """Finds a task and shifts its lifecycle status."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.mark_status(status)

        with TaskStorageManager(self.storage_file, self._tasks):
            pass

        return task


# ==========================================
# EXECUTION WRAPPER
# ==========================================
def main():
    print("--- Initializing Advanced Task Manager ---")
    manager = TaskManager(storage_file="my_tasks.json")

    # 1. Populate Sample Tasks
    print("\n[Action] Creating mock tasks...")
    t1 = manager.create_task("Fix Bug #104", "Resolve null pointer execution thread.")
    t2 = manager.create_task("Code Review", "Review backend authentication logic updates.")

    # 2. Query Tasks
    print("\n[Action] Fetching current tasks:")
    for task in manager.get_all_tasks():
        print(f" - Id: {task.id} | {task.title} -> [{task.status.name}]")

    # 3. Modify State
    print(f"\n[Action] Progressing Task #{t1.id} to IN_PROGRESS...")
    manager.update_task_status(t1.id, Status.IN_PROGRESS)

    # 4. Graceful Error Handling Showcase
    print("\n[Action] Attempting to access non-existent task to test exceptions:")
    try:
        manager.update_task_status(999, Status.COMPLETED)
    except TaskNotFoundError as error:
        print(f" Caught expected exception: {error}")


if __name__ == "__main__":
    main()

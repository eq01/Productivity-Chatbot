import json
import os
import uuid
from typing import List, Optional

from config import Config
from models.task import Task


class TaskService:
    def __init__(self):
        self.tasks_file = Config.TASKS_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
        if not os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'w') as f:
                json.dump([], f)

    def _load_tasks_from_file(self) -> List[Task]:
        with open(self.tasks_file, 'r') as f:
            data = json.load(f)
            return [Task.from_dict(tasks) for tasks in data]

    def _save_tasks_to_file(self, tasks: List[Task]):
        with open(self.tasks_file, 'w') as f:
            json.dump([tasks.to_dict() for tasks in tasks], f, indent=2)

    def add_task(self, task_data: dict) -> Task:
        tasks = self._load_tasks_from_file()
        task_data['id'] = str(uuid.uuid4())
        new_task = Task.from_dict(task_data)
        tasks.append(new_task)
        self._save_tasks_to_file(tasks)
        return new_task

    def delete_task(self, task_id: str) -> bool:
        tasks = self._load_tasks_from_file()
        initial_length = len(tasks)
        tasks = [task for task in tasks if task.id != task_id]
        if len(tasks) < initial_length:
            self._save_tasks_to_file(tasks)
            return True
        return False

    def get_task(self, task_id: str) -> Optional[Task]:
        tasks = self._load_tasks_from_file()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: str, updates: dict) -> Optional[Task]:
        tasks = self._load_tasks_from_file()
        for i, task in enumerate(tasks):
            if task.id == task_id:
                task_dict = task.to_dict()
                task_dict.update(updates)
                tasks[i] = Task.from_dict(task_dict)
                self._save_tasks_to_file(tasks)
                return tasks[i]
        return None

    def clear_tasks(self):
        self._save_tasks_to_file([])

    def get_all_tasks(self) -> List[Task]:
        return self._load_tasks_from_file()

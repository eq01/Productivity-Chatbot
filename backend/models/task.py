from datetime import datetime
from typing import Optional

# class object representing a singular task given by the user.
class Task:
    # constructor
    def __init__(self,
                 usr_id: str,
                 title: str,
                 description: Optional[str]=None,
                 due_date: Optional[str]=None,
                 due_time: Optional[str]=None,
                 priority: str = "medium",
                 status: str = "todo",
                 created_at: Optional[str]=None,
                 task_type: str = "work",
                 duration_est: Optional[int]=None, ):
        self.id = usr_id
        self.title = title
        self.description = description
        self.due_date = due_date # YYYY-MM-DD format
        self.due_time = due_time # HH:MM format
        self.priority = priority # one of low, med, high
        self.status = status # one of todo, in prog, done
        self.created_at = created_at
        self.task_type = task_type # personal, work, quick
        self.duration_est = duration_est # in mins

    # convert task into data to store
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'due_time': self.due_time,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at,
            'task_type': self.task_type,
            'duration_est': self.duration_est
        }

    # return the task from the given data
    @staticmethod
    def from_dict(info):
        return Task(**info)
from datetime import datetime, timedelta
from typing import List, Dict
from backend.models.task import Task

class WorkloadBalancer:
    """Monitors daily workload while providing warnings when duration and/or tasks
    exceeds a certain threshold"""

    DAILY_LIMITS = {
        'personal': 3,
        'work': 3,
        'quick': 5
    }

    RECOMMENDED_DAILY_MINS = 480
    MAX_MINS = 600

    def __init__(self, tasks: List[Task]):
        self.tasks = tasks

    def get_tasks_for_date(self, date_str: str) -> List[Task]:
        """Get all tasks for given date"""
        return [
            task for task in self.tasks
            if task.due_date == date_str and task.status in ['todo', 'in_progress']
        ]

    def check_new_task_impact(self, new_task_data: Dict) -> Dict:
        """Check how adding a new task impacts the workload"""
        due_date = new_task_data.get['due_date']

        if not due_date:
            return {
                'can_add': True,
                'warnings': [],
                'message': "No due date specified, so no workload impact."
            }

        curr_tasks = self.get_tasks_for_date(due_date)

        task_type = new_task_data.get('task_type', 'work')
        curr_count = sum(1 for t in curr_tasks if t.task_type == task_type)
        new_count = curr_count + 1

        curr_mins = sum(t.duration_est or 0 for t in curr_tasks)
        new_mins = curr_mins + new_task_data.get('duration_estimate', 0)

        warnings = []
        can_add = True

        if new_count > self.DAILY_LIMITS[task_type]:
            warnings.append(f"⚠️ This will be your {new_count}th {task_type} task on {due_date} (recommended: {self.DAILY_LIMITS[task_type]})")
            if new_count > self.DAILY_LIMITS[task_type] + 2:
                can_add = False

        if new_mins > self.MAX_MINS:
            hours = new_mins / 60
            warnings.append(f"🚨 This will bring your total to {round(hours, 1)} hours on {due_date}. Consider choosing a different day.")
            can_add = False
        elif new_mins > self.RECOMMENDED_DAILY_MINS:
            hours = new_mins / 60
            warnings.append("⚠️ This will bring your total to {round(hours, 1)} hours on {due_date}. You'll have a busy day!")

        if can_add and len(warnings) == 0:
            message = f"Good choice! {due_date} has a balanced workload."
        elif can_add:
            message = f"You can add this task, but be mindful of your workload!"
        else:
            message = "Consider choosing a different day to avoid overload :(."

        return {
            'can_add': can_add,
            'warnings': warnings,
            'message': message,
            'new_category_count': new_count,
            'new_total_hours': round(new_mins / 60, 1),
        }

import json
import os

# to do list history
TO_DO = "tasks.json"

# load tasks in
def load_tasks():
    if not os.path.exists(TO_DO):
        return []
    with open(TO_DO, "r") as f:
        return json.load(f)

# save the tasks
def save_tasks(tasks):
    with open(TO_DO, "w") as f:
        json.dump(tasks, f, indent=2)

# add a task to the list
def add_task(task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    num_tasks = []
    for i in range(len(tasks)):
        num = i + 1
        task_text = tasks[i]
        num_task = str(num) + ". " + task_text
        num_tasks.append(num_task)
    return "\n".join(num_tasks)

# remove a task from the list
def remove_task(task):
    tasks = load_tasks()
    if task in tasks:
        tasks.remove(task)
        save_tasks(tasks)
        return f"Successfully removed: {task}"
    return f"{task} not found in tasks"

# clear a task from the list
def clear_tasks():
    save_tasks([])
    return "Tasks cleared"

# list all tasks in the list if any
def list_tasks():
    tasks = load_tasks()
    if tasks:
        num_tasks = []
        for i in range(len(tasks)):
            num = i + 1
            task_text = tasks[i]
            num_task = str(num) + ". " + task_text
            num_tasks.append(num_task)
        return "\n".join(num_tasks)
    return "Your to-do list is empty"
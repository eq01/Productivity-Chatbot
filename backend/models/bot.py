import openai as oai
from dotenv import load_dotenv
import os

from backend.models.commands import add_task, remove_task, list_tasks, clear_tasks

# configurations
load_dotenv()
oai.api_key = os.getenv("KEY")

# conversation context
model_theme = [{"role": "system", "content": "You are a supportive productivity assistant"}]

def productivity_chatbot(user_input):
    input_lowercase = user_input.lower()

    # dealing with to-do list commands

    # add
    if input_lowercase.startswith("/add"):
        task = user_input[4:].strip()
        if task:
            response = add_task(task)
            return f"Added task: {task}\n\n**Your tasks:**\n{response}"
        else:
            return "no task specified, please provide a task"

    # remove
    elif input_lowercase.startswith("/remove"):
        task = user_input[7:].strip()
        if task:
            return remove_task(task)
        else:
            return "Please specify task to remove"

    # list
    elif input_lowercase.startswith("/list"):
        return list_tasks()

    # clear
    elif input_lowercase.startswith("/clear"):
        return clear_tasks()
    return None
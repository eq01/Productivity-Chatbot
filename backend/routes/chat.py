from flask import Blueprint, jsonify, request
from services.openai_service import OpenAIService
from services.tasks_service import TaskService
import openai
from config import Config

chat_bp = Blueprint('chat', __name__)
openai_service = OpenAIService()
tasks_service = TaskService()

openai.api_key = Config.OPENAI_API_KEY

@chat_bp.route('/message', methods=['POST'])
def send_message():
    """Send a message to the AI assistant"""
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Message not found'}), 400

    user_message = data['message']
    response = openai_service.chat(user_message)
    return jsonify({'response': response}), 200

@chat_bp.route('/daily-summary', methods=['GET'])
def get_daily_summary():
    """Get the daily summary for the user"""
    tasks = tasks_service.get_all_tasks()
    tasks_dict = [task.to_dict() for task in tasks]

    summary = openai_service.generate_daily_summary(tasks_dict)

    return jsonify({
        'summary': summary,
        'task_count': len(tasks)
    }), 200


@chat_bp.route('/match-task', methods=['POST'])
def match_task():
    """Use AI to match user input to a task"""
    data = request.get_json()

    if not data or 'user_input' not in data or 'tasks' not in data:
        return jsonify({'error': 'Missing data'}), 400

    user_input = data['user_input']
    tasks = data['tasks']

    if not tasks:
        return jsonify({'matched_index': None}), 200

    # Build prompt for AI
    task_descriptions = []
    for task in tasks:
        desc = f"Index {task['index']}: {task['title']}"
        if task.get('due_date'):
            desc += f" on {task['due_date']}"
        if task.get('due_time'):
            desc += f" at {task['due_time']}"
        task_descriptions.append(desc)

    prompt = f"""User wants to delete a task. Match their request to one of these tasks:

{chr(10).join(task_descriptions)}

User said: "{user_input}"

Which task index matches best? Respond with ONLY the index number, or -1 if no match.
Examples:
- User: "remove the meeting at 5pm" → if task 2 is "Team meeting at 5pm", respond: 2
- User: "delete groceries" → if task 0 is "Buy groceries", respond: 0
- User: "cancel tomorrow's call" → if task 1 is "Client call tomorrow", respond: 1

Response (number only):"""

    try:
        import openai
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You match user requests to task indices. Respond with only a number."},
                {"role": "user", "content": prompt}
            ]
        )

        matched_index = int(response.choices[0].message.content.strip())

        if matched_index >= 0 and matched_index < len(tasks):
            return jsonify({'matched_index': matched_index}), 200
        else:
            return jsonify({'matched_index': None}), 200

    except Exception as e:
        print(f"Error matching task: {e}")
        return jsonify({'matched_index': None}), 200
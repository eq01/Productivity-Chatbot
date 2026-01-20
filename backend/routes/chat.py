from flask import Blueprint, jsonify, request
from backend.services.openai_service import OpenAIService
from backend.services.tasks_service import TaskService

chat_bp = Blueprint('chat', __name__)
openai_service = OpenAIService()
tasks_service = TaskService()

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
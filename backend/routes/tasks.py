from flask import Blueprint, request, jsonify
from backend.services.tasks_service import TaskService
from backend.services.nlp_parser_service import NLPParser
from backend.services.balancer_service import WorkloadBalancer
from backend.services.calendar_services import CalendarService

tasks_bp = Blueprint('tasks', __name__)
task_service = TaskService()
nlp_parser = NLPParser()
calendar_service = CalendarService()

@tasks_bp.route('/', methods=['GET'])
def get_all_tasks():
    """Get all of the tasks"""
    tasks = task_service.get_all_tasks()
    return jsonify([task.to_dict() for task in tasks]), 200

@tasks_bp.route('/', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()

    if not data or 'input' not in data:
        return jsonify({'error': 'Missing input'}), 400

    user_input = data['input']

    parsed_task =nlp_parser.parse_task(user_input)

    all_tasks = task_service.get_all_tasks()
    balancer = WorkloadBalancer(all_tasks)
    workload_check = balancer.check_new_task_impact(parsed_task)

    new_task = task_service.add_task(parsed_task)
    event_id = None

    if data.get('sync_calendar', False) and parsed_task.get('due_date'):
        try:
            if calendar_service.is_authenticated():
                event_id = calendar_service.create_event(new_task.to_dict())
                task_service.update_task(new_task.id, {'calendar_event_id': event_id})
                new_task.calendar_event_id = event_id
        except Exception as e:
            print(f"Calendar sync error: {e}")

    return jsonify({
        'task': new_task.to_dict(),
        'workload_check': workload_check
    }), 201

@tasks_bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.get_json()
    updated_task = task_service.update_task(task_id, data)

    if updated_task:
        return jsonify(updated_task.to_dict()), 200
    return jsonify({'error': 'Task not found'}), 404

@tasks_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = task_service.get_task(task_id)

    if task and task.calendar_event_id:
        if calendar_service.is_authenticated():
            try:
                calendar_service.delete_event(task.calendar_event_id)
                print(f"Deleted calendar event: {task.calendar_event_id}")
            except Exception as e:
                print(f"Calendar delete failed: {e}")

    success = task_service.delete_task(task_id)
    if success:
        return jsonify({'message': 'Task deleted'}), 200
    return jsonify({'error': 'Task not found'}), 404
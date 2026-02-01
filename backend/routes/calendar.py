from flask import Blueprint, request, jsonify, redirect
from services.calendar_services import CalendarService

calender_bp = Blueprint('calender', __name__)
calender_service = CalendarService()

@calender_bp.route('/auth', methods=['GET'])
def initiate_auth():
    """Authenticate user"""
    auth_url = calender_service.get_auth_url()
    return jsonify({'auth_url': auth_url}), 200

@calender_bp.route('/callback', methods=['GET'])
def oauth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    try:
        calender_service.handle_oauth_callback(code)

        return redirect('https://localhost:8501?auth=success')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@calender_bp.route('/status', methods=['GET'])
def get_auth_status():
    """Check if user is authenticated with Google Calendar"""
    is_authenticated = calender_service.is_authenticated()
    return jsonify({'authenticated': is_authenticated}), 200

@calender_bp.route('/events', methods=['GET'])
def get_events():
    """Get upcoming events"""
    if not calender_service.is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401

    max_results = request.args.get('max_results', 10, type=int)
    events = calender_service.get_upcoming_events(max_results=max_results)
    return jsonify({'events': events}), 200

@calender_bp.route('/sync-task/<task_id>', methods=['POST'])
def sync_task(task_id):
    """Sync task"""
    if not calender_service.is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401

    from backend.services.tasks_service import TaskService
    task_service = TaskService()

    task = task_service.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        event_id = calender_service.create_event(task.to_dict())
        task_service.update_task(task_id, {'calendar_event_id': event_id})
        return jsonify({'message': 'Task synced to calendar', 'event_id': event_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
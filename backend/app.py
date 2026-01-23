from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    from backend.routes.tasks import tasks_bp
    from routes.chat import chat_bp
    from routes.calendar import calender_bp

    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(calender_bp, url_prefix='/api/calendar')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)


from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    from routes.tasks import tasks_bp
    from routes.chat import chat_bp
    from routes.calendar import calender_bp

    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(calender_bp, url_prefix='/api/calendar')

    return app
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Railway sets this automatically
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


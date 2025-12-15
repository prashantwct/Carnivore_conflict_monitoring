from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import os

# Initialize extensions outside the factory function
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    CORS(app) # Enable CORS for frontend/mobile app communication

    # ------------------------------------------------------------------
    # --- BLUEPRINTS & ROUTES ---
    # ------------------------------------------------------------------

    # Example Health Check Route
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """A simple route to check if the server is running."""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            db_status = "OK"
        except Exception as e:
            db_status = f"Error: {e}"

        return jsonify({
            "status": "up",
            "db_status": db_status,
            "message": "Tiger Conflict Monitoring API is running."
        }), 200

    # TODO: Register Blueprints for /api/v1/auth, /api/v1/incidents, etc.

    return app

if __name__ == '__main__':
    # Ensure you have your .env file set up before running!
    # To initialize the database structure, you would typically use a migration tool 
    # or run the commands in db/init.sql manually first.
    
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask app starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

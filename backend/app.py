from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import os

# Import all models to ensure SQLAlchemy is aware of them
# The 'db' object will be imported from models.py now
from backend.api.models import db, User, Incident, Media # Import models and the db object
# You will also need to pip install werkzeug for password hashing
from werkzeug.security import generate_password_hash

# Note: Removed the original 'db = SQLAlchemy()' initialization here, 
# as it's now imported from models.py

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    CORS(app) 

    # ------------------------------------------------------------------
    # --- Database Initialization within Application Context ---
    # ------------------------------------------------------------------
    with app.app_context():
        # This will create all tables defined in models.py if they do not exist
        # It also triggers the PostGIS DDL listener (CREATE EXTENSION)
        db.create_all() 
        print("Database tables checked/created successfully using SQLAlchemy.")

        # --- Initial Test User Creation (for immediate testing) ---
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('adminpass', method='pbkdf2:sha256')
            admin_user = User(
                username='admin',
                hashed_password=hashed_pw,
                full_name='System Administrator',
                user_role='Administrator'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default 'admin' user created (Password: adminpass). CHANGE IT IMMEDIATELY!")


    # ------------------------------------------------------------------
    # --- ROUTES ---
    # ------------------------------------------------------------------
    # Health Check Route
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute(db.select(func.now())) # Test database connection
            db_status = "OK"
        except Exception as e:
            db_status = f"Error: {e}"

        return jsonify({"status": "up", "db_status": db_status}), 200

    # TODO: Register Blueprints for /api/v1/auth, /api/v1/incidents, etc.

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

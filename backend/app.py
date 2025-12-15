import os
import uuid
import datetime
import jwt
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import ARRAY, DateTime, func, Text
from sqlalchemy.schema import DDL
from sqlalchemy.event import listen
from werkzeug.security import generate_password_hash

# --- 1. CONFIGURATION (DIRECTLY SET FOR RELIABILITY) ---
DATABASE_URL = 'postgresql://neondb_owner:npg_sgW7xo9LGHAC@ep-dark-field-aho6iapv-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
SECRET_KEY = 'a-highly-secret-key-for-local-testing'

# --- 2. INITIALIZATION ---
db = SQLAlchemy()
app = Flask(__name__)

# *** DIRECT APPLICATION CONFIGURATION (The fix) ***
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
# *************************************************

db.init_app(app)
CORS(app) 

# --- 3. POSTGIS DDL SETUP ---
def enable_postgis_extension(target, connection, **kw):
    connection.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
listen(db.metadata, 'before_create', enable_postgis_extension)

# --- 4. DATABASE MODELS (Remain unchanged) ---
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    user_role = db.Column(db.String(50), nullable=False) 
    created_at = db.Column(DateTime(timezone=True), default=datetime.datetime.now)
    incidents = db.relationship('Incident', backref='reporter', lazy='dynamic')

class Incident(db.Model):
    __tablename__ = 'incidents'
    incident_id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(15), unique=True, nullable=False)
    geom_wkt = db.Column(db.Text, nullable=False) 
    obs_date_time = db.Column(DateTime(timezone=True), nullable=False)
    report_date_time = db.Column(DateTime(timezone=True), default=datetime.datetime.now)
    conflict_type = db.Column(db.String(50), nullable=False) 
    priority_level = db.Column(db.String(15), nullable=False) 
    evidence_type = db.Column(ARRAY(db.String(100))) 
    reporter_comments = db.Column(db.Text)
    current_status = db.Column(db.String(50), default='Reported')
    reporter_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

class Media(db.Model):
    __tablename__ = 'media'
    media_id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.incident_id', ondelete='CASCADE'), nullable=False)
    storage_path = db.Column(db.String(255), nullable=False) 
    media_type = db.Column(db.String(10), nullable=False) 
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

# --- 5. UTILITY FUNCTIONS (Remain unchanged) ---
def calculate_priority(conflict_type):
    if conflict_type in ['Human Injury', 'Direct Sighting near village']:
        return 'P-1_CRITICAL'
    elif conflict_type in ['Cattle Depredation (Fresh)', 'Tiger Sighting in public area']:
        return 'P-2_HIGH'
    elif conflict_type in ['Fresh Pugmark/Scat']:
        return 'P-3_ELEVATED'
    else:
        return 'P-4_ROUTINE'

# --- 6. ROUTES (API ENDPOINTS - Remain unchanged) ---
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(db.select(func.now()))
        db_status = "OK"
    except Exception as e:
        db_status = f"Error: {e}"
    return jsonify({"status": "up", "db_status": db_status}), 200

@app.route('/api/v1/incidents/', methods=['POST'])
def submit_incident():
    try:
        data = request.get_json()
        if not all(k in data for k in ('conflict_type', 'geom_wkt', 'obs_date_time')):
            return jsonify({"message": "Missing required incident data (type, location, time)."}), 400
        priority = calculate_priority(data['conflict_type'])
        tracking_code = f"T-{datetime.datetime.now().year}-{uuid.uuid4().hex[:4].upper()}"
        temporary_user_id = 1 
        new_incident = Incident(
            tracking_code=tracking_code,
            geom_wkt=data['geom_wkt'],
            obs_date_time=datetime.datetime.fromisoformat(data['obs_date_time']),
            conflict_type=data['conflict_type'],
            priority_level=priority,
            reporter_user_id=temporary_user_id,
            evidence_type=data.get('evidence_type', []),
            reporter_comments=data.get('reporter_comments')
        )
        db.session.add(new_incident)
        db.session.commit()
        return jsonify({
            "message": "Incident reported successfully.",
            "incident_id": new_incident.incident_id,
            "tracking_code": tracking_code,
            "priority": priority
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Server error: {e}"}), 500

@app.route('/api/v1/incidents/', methods=['GET'])
def get_all_incidents():
    try:
        incidents = Incident.query.order_by(Incident.priority_level).all()
        results = []
        for incident in incidents:
            results.append({
                "id": incident.incident_id,
                "tracking_code": incident.tracking_code,
                "priority": incident.priority_level,
                "type": incident.conflict_type,
                "location_wkt": incident.geom_wkt,
                "obs_time": incident.obs_date_time.isoformat(),
                "status": incident.current_status,
                "reporter_id": incident.reporter_user_id,
                "comments": incident.reporter_comments
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving data."}), 500

# --- 7. STARTUP AND DATABASE INITIALIZATION ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        print("Database tables checked/created successfully using direct URL.")

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
            print("Default 'admin' user created (Password: adminpass).")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"Flask app starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)

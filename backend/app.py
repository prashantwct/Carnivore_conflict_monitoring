import os
import uuid
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import ARRAY, DateTime, func
from werkzeug.security import generate_password_hash

# -----------------------------
# Database instance (GLOBAL)
# -----------------------------
db = SQLAlchemy()

# -----------------------------
# App Factory
# -----------------------------
def create_app(database_url = os.getenv("DATABASE_URL")
print("DEBUG DATABASE_URL =", database_url)
):
    app = Flask(__name__)

    # -----------------------------
    # Configuration (MUST be before db.init_app)
    # -----------------------------
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Add it to Codespaces secrets."
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

    # -----------------------------
    # Init extensions
    # -----------------------------
    db.init_app(app)
    CORS(app)

    # -----------------------------
    # Models
    # -----------------------------
    class User(db.Model):
        __tablename__ = "users"

        user_id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        hashed_password = db.Column(db.String(255), nullable=False)
        full_name = db.Column(db.String(100), nullable=False)
        user_role = db.Column(db.String(50), nullable=False)
        created_at = db.Column(
            DateTime(timezone=True),
            server_default=func.now()
        )

    class Incident(db.Model):
        __tablename__ = "incidents"

        incident_id = db.Column(db.Integer, primary_key=True)
        tracking_code = db.Column(db.String(20), unique=True, nullable=False)
        geom_wkt = db.Column(db.Text, nullable=False)  # WKT string
        obs_date_time = db.Column(DateTime(timezone=True), nullable=False)
        report_date_time = db.Column(
            DateTime(timezone=True),
            server_default=func.now()
        )
        conflict_type = db.Column(db.String(50), nullable=False)
        priority_level = db.Column(db.String(20), nullable=False)
        evidence_type = db.Column(ARRAY(db.String(100)))
        reporter_comments = db.Column(db.Text)
        current_status = db.Column(db.String(50), default="Reported")
        reporter_user_id = db.Column(
            db.Integer,
            db.ForeignKey("users.user_id"),
            nullable=False
        )

    # -----------------------------
    # Utility
    # -----------------------------
    def calculate_priority(conflict_type):
        if conflict_type in ["Human Injury", "Direct Sighting near village"]:
            return "P-1_CRITICAL"
        elif conflict_type in ["Cattle Depredation (Fresh)", "Tiger Sighting in public area"]:
            return "P-2_HIGH"
        elif conflict_type in ["Fresh Pugmark/Scat"]:
            return "P-3_ELEVATED"
        return "P-4_ROUTINE"

    # -----------------------------
    # Routes
    # -----------------------------
    @app.route("/api/v1/health", methods=["GET"])
    def health_check():
        try:
            db.session.execute(func.now())
            return jsonify({"status": "up", "db": "ok"}), 200
        except Exception:
            return jsonify({"status": "up", "db": "error"}), 200

    @app.route("/api/v1/incidents/", methods=["POST"])
    def submit_incident():
        try:
            data = request.get_json()

            required = ["conflict_type", "geom_wkt", "obs_date_time"]
            if not all(k in data for k in required):
                return jsonify({"message": "Missing required fields"}), 400

            priority = calculate_priority(data["conflict_type"])
            tracking_code = f"T-{datetime.datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"

            new_incident = Incident(
                tracking_code=tracking_code,
                geom_wkt=data["geom_wkt"],
                obs_date_time=datetime.datetime.fromisoformat(data["obs_date_time"]),
                conflict_type=data["conflict_type"],
                priority_level=priority,
                reporter_user_id=1,  # TEMP dev user
                evidence_type=data.get("evidence_type", []),
                reporter_comments=data.get("reporter_comments"),
            )

            db.session.add(new_incident)
            db.session.commit()

            return jsonify({
                "message": "Incident reported",
                "incident_id": new_incident.incident_id,
                "tracking_code": tracking_code,
                "priority": priority
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/incidents/", methods=["GET"])
    def get_incidents():
        incidents = Incident.query.order_by(
            Incident.priority_level.asc()
        ).all()

        return jsonify([
            {
                "id": i.incident_id,
                "tracking_code": i.tracking_code,
                "priority": i.priority_level,
                "type": i.conflict_type,
                "location": i.geom_wkt,
                "obs_time": i.obs_date_time.isoformat(),
                "status": i.current_status
            }
            for i in incidents
        ])

    # -----------------------------
    # Create tables + default admin (DEV ONLY)
    # -----------------------------
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                hashed_password=generate_password_hash("adminpass"),
                full_name="System Administrator",
                user_role="Administrator",
            )
            db.session.add(admin)
            db.session.commit()

    return app


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, DateTime, Enum, func, Text, BigInteger
from sqlalchemy.schema import DDL
from sqlalchemy.event import listen
import datetime

# Initialize SQLAlchemy outside, assume it's imported from app.py
db = SQLAlchemy()

# --- DDL to ensure PostGIS is enabled when the database is connected ---
# This is a method to execute raw SQL (like CREATE EXTENSION) via SQLAlchemy
# Note: The database must be created manually first (e.g., CREATE DATABASE tiger_db;)

def enable_postgis_extension(target, connection, **kw):
    connection.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

listen(db.metadata, 'before_create', enable_postgis_extension)


# 1. User Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20))
    # Enforce role validity
    user_role = db.Column(db.String(50), nullable=False) 
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(DateTime(timezone=True), default=datetime.datetime.now)
    
    # Define relationship for incidents reported by this user
    incidents = db.relationship('Incident', backref='reporter', lazy='dynamic')


# 2. Incident Model
class Incident(db.Model):
    __tablename__ = 'incidents'
    incident_id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(15), unique=True, nullable=False)
    
    # PostGIS Geometry type: We use SQLAlchemy's support for func.ST_SetSRID for integration
    # Note: Requires GeoAlchemy2 for full ORM support, but we use raw function calls for core geom here
    # Placeholder for geometry type which will be inserted/retrieved using raw SQL functions
    # For now, we will store WKT (Well-Known Text) or JSON representation if GeoAlchemy2 is excluded.
    # In a real build, we would add the GeoAlchemy2 library. For this setup, we store a Text placeholder.
    geom_wkt = db.Column(db.Text, nullable=False) 

    obs_date_time = db.Column(DateTime(timezone=True), nullable=False)
    report_date_time = db.Column(DateTime(timezone=True), default=datetime.datetime.now)

    conflict_type = db.Column(db.String(50), nullable=False) 
    priority_level = db.Column(db.String(15), nullable=False) 
    
    evidence_type = db.Column(ARRAY(db.String(100))) # PostgreSQL Array Type
    num_tigers_observed = db.Column(db.SmallInteger)
    prey_type = db.Column(db.String(50)) 
    prey_age_size = db.Column(db.String(50))

    current_status = db.Column(db.String(50), default='Reported', nullable=False)
    assigned_team_id = db.Column(db.Integer)
    reporter_comments = db.Column(db.Text)
    
    reporter_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # Define relationship for linked media
    media_files = db.relationship('Media', backref='incident', lazy='dynamic')


# 3. Media Model
class Media(db.Model):
    __tablename__ = 'media'
    media_id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.incident_id', ondelete='CASCADE'), nullable=False)
    storage_path = db.Column(db.String(255), nullable=False) 
    media_type = db.Column(db.String(10), nullable=False) 
    file_size_bytes = db.Column(BigInteger)
    is_primary = db.Column(db.Boolean, default=False)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    upload_date_time = db.Column(DateTime(timezone=True), default=datetime.datetime.now)

-- Enable PostGIS extension for geospatial functions
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. users Table (Authentication and Roles)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    user_role VARCHAR(50) NOT NULL, -- 'Field_Reporter', 'Supervisor', 'Decision_Maker'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_role CHECK (user_role IN ('Field_Reporter', 'Supervisor', 'Decision_Maker', 'Administrator'))
);

-- 2. incidents Table (Core Conflict Data)
CREATE TABLE incidents (
    incident_id SERIAL PRIMARY KEY,
    tracking_code VARCHAR(15) UNIQUE NOT NULL, 
    
    -- PostGIS Geometry type for location
    geom GEOMETRY(Point, 4326) NOT NULL, 
    
    obs_date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    report_date_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    conflict_type VARCHAR(50) NOT NULL, 
    priority_level VARCHAR(15) NOT NULL, 
    
    evidence_type VARCHAR(100)[], 
    num_tigers_observed SMALLINT,
    prey_type VARCHAR(50), 
    prey_age_size VARCHAR(50),

    current_status VARCHAR(50) NOT NULL DEFAULT 'Reported',
    assigned_team_id INT,
    reporter_comments TEXT,
    
    reporter_user_id INT NOT NULL REFERENCES users (user_id),
    
    CONSTRAINT chk_priority CHECK (priority_level IN ('P-1_CRITICAL', 'P-2_HIGH', 'P-3_ELEVATED', 'P-4_ROUTINE'))
);

CREATE INDEX idx_priority_level ON incidents (priority_level);
CREATE INDEX idx_geom ON incidents USING GIST (geom); 

-- 3. media Table (Photo/Video Linkage)
CREATE TABLE media (
    media_id SERIAL PRIMARY KEY,
    incident_id INT NOT NULL REFERENCES incidents (incident_id) ON DELETE CASCADE,
    storage_path VARCHAR(255) NOT NULL, 
    media_type VARCHAR(10) NOT NULL, 
    file_size_bytes BIGINT,
    is_primary BOOLEAN DEFAULT FALSE,
    uploaded_by_user_id INT NOT NULL REFERENCES users (user_id),
    upload_date_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

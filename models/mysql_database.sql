CREATE TABLE LOCATION (
    location_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(100),
    city VARCHAR(50),
    latitude DOUBLE,
    longitude DOUBLE,
    intersection_type VARCHAR(50),
    traffic_volume_category VARCHAR(20),
    estado VARCHAR(50)
);

CREATE TABLE CAMERA (
    camera_id VARCHAR(10) PRIMARY KEY,
    model VARCHAR(50),
    firmware_version VARCHAR(10),
    staus VARCHAR(10),
    last_check_in TIMESTAMP,
    resolution VARCHAR(10),
    framerate INTEGER,
    view_angle_dregrees INTEGER,
    ml_detection_model BIT,
    image_storage_policy VARCHAR(100),
    lane_ref INTEGER
);

CREATE TABLE LANE (
    lane_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(100),
    location_ref VARCHAR(10),
    lane_type VARCHAR(100),
    direction VARCHAR(100)
);

CREATE TABLE TRAFFIC_LIGHT (
    firmware_version VARCHAR(10),
    traffic_light_id VARCHAR(50) PRIMARY KEY,
    staus VARCHAR(10),
    model VARCHAR(50),
    last_check_in TIMESTAMP,
    default_green_s INTEGER,
    default_yellow_s INTEGER,
    default_red_s INTEGER,
    min_green_s INTEGER,
    min_red_s INTEGER,
    pedestrian_button_active BIT,
    lane_ref INTEGER
);

CREATE TABLE TRAFFIC_SENSOR (
    last_check_in TIMESTAMP,
    traffic_sensor_id VARCHAR(50) PRIMARY KEY,
    firmware_version VARCHAR(10),
    staus VARCHAR(10),
    model VARCHAR(50),
    sampling_rate_s INTEGER,
    detection_method VARCHAR(50),
    velocity_threshold_kph INTEGER,
    lane_ref INTEGER
);

CREATE TABLE INCIDENT_REPORT (
    incident_report_id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP,
    incident_type VARCHAR(50),
    status VARCHAR(50),
    image_url VARCHAR(100),
    camera_ref VARCHAR(10)
);

CREATE TABLE STATUS_CHANGE (
    timestamp TIMESTAMP,
    status_change_id INTEGER PRIMARY KEY,
    phase_duration_s INTEGER,
    current_state VARCHAR(10),
    traffic_light_ref VARCHAR(10)
);

CREATE TABLE TRAFFIC_COUNT (
    traffic_count_id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP,
    avg_speed_kph DOUBLE,
    count INTEGER,
    traffic_sensor_ref VARCHAR(10)
);
 
ALTER TABLE CAMERA ADD CONSTRAINT FK_CAMERA_2
    FOREIGN KEY (lane_ref)
    REFERENCES LANE (lane_id)
    ON DELETE CASCADE;
 
ALTER TABLE LANE ADD CONSTRAINT FK_LANE_2
    FOREIGN KEY (location_ref)
    REFERENCES LOCATION (location_id)
    ON DELETE RESTRICT;
 
ALTER TABLE TRAFFIC_LIGHT ADD CONSTRAINT FK_TRAFFIC_LIGHT_2
    FOREIGN KEY (lane_ref)
    REFERENCES LANE (lane_id)
    ON DELETE CASCADE;
 
ALTER TABLE TRAFFIC_SENSOR ADD CONSTRAINT FK_TRAFFIC_SENSOR_2
    FOREIGN KEY (lane_ref)
    REFERENCES LANE (lane_id)
    ON DELETE CASCADE;
 
ALTER TABLE INCIDENT_REPORT ADD CONSTRAINT FK_INCIDENT_REPORT_2
    FOREIGN KEY (camera_ref)
    REFERENCES CAMERA (camera_id)
    ON DELETE CASCADE;
 
ALTER TABLE STATUS_CHANGE ADD CONSTRAINT FK_STATUS_CHANGE_2
    FOREIGN KEY (traffic_light_ref)
    REFERENCES TRAFFIC_LIGHT (traffic_light_id)
    ON DELETE CASCADE;
 
ALTER TABLE TRAFFIC_COUNT ADD CONSTRAINT FK_TRAFFIC_COUNT_2
    FOREIGN KEY (traffic_sensor_ref)
    REFERENCES TRAFFIC_SENSOR (traffic_sensor_id)
    ON DELETE CASCADE;
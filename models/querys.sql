-- Fluxo semafórico
SELECT 
    tl.traffic_light_id,
    ts.traffic_sensor_id,
    tc.timestamp,
    tc.count,
    tc.avg_speed_kph
FROM TRAFFIC_LIGHT tl
JOIN TRAFFIC_SENSOR ts
    ON ts.lane_ref = tl.lane_ref
LEFT JOIN TRAFFIC_COUNT tc
    ON tc.traffic_sensor_ref = ts.traffic_sensor_id
WHERE tl.traffic_light_id = 'SEM-001-01'
ORDER BY tc.timestamp DESC;

-- Leituras com excesso de velocidade
SELECT 
    c.timestamp, 
    c.avg_speed_kph,
    t.velocity_threshold_kph AS velocity_limit_kph,
    t.traffic_sensor_id,
    loc.description AS location,
    l.description AS lane,
    l.direction AS direction
FROM TRAFFIC_COUNT c
JOIN TRAFFIC_SENSOR t
    ON t.traffic_sensor_id = c.traffic_sensor_ref
JOIN LANE l
    ON l.lane_id = t.lane_ref
JOIN LOCATION loc
    ON loc.location_id = l.location_ref
WHERE
    c.avg_speed_kph > t.velocity_threshold_kph
ORDER BY c.timestamp DESC;

-- Possíveis congestionamentos
SELECT
    t.traffic_sensor_id,
    c.timestamp,
    c.avg_speed_kph,
    t.velocity_threshold_kph AS velocity_limit_kph,
    loc.description AS location,
    l.description AS lane,
    l.direction
FROM TRAFFIC_COUNT c
JOIN TRAFFIC_SENSOR t
    ON t.traffic_sensor_id = c.traffic_sensor_ref
JOIN LANE l
    ON l.lane_id = t.lane_ref
JOIN LOCATION loc
    ON loc.location_id = l.location_ref
JOIN (
    SELECT 
        c.traffic_sensor_ref,
        MAX(c.timestamp) AS last_timestamp
    FROM TRAFFIC_COUNT c
    JOIN TRAFFIC_SENSOR t
        ON t.traffic_sensor_id = c.traffic_sensor_ref
    WHERE c.avg_speed_kph < t.velocity_threshold_kph / 2
    GROUP BY c.traffic_sensor_ref
) AS last_low_speed
    ON last_low_speed.traffic_sensor_ref = c.traffic_sensor_ref
    AND last_low_speed.last_timestamp = c.timestamp

ORDER BY t.traffic_sensor_id ASC;


-- Acidentes em aberto
SELECT
    i.incident_report_id,
    i.timestamp,
    loc.description AS location,
    l.description AS lane,
    l.direction AS direction,
    loc.city AS city,
    loc.state AS state,
    i.camera_ref AS camera_id,
    i.image_url,
    i.status
FROM INCIDENT_REPORT i
JOIN CAMERA c
    ON c.camera_id = i.camera_ref
JOIN LANE l
    ON l.lane_id = c.lane_ref
JOIN LOCATION loc
    ON loc.location_id = l.location_ref
WHERE 
    i.incident_type = 'accident' AND
    i.status = 'open';

-- Local com mais acidentes

SELECT 
    loc.location_id,
    COUNT(*) AS accidents_count,
    loc.description,
    loc.city,
    loc.state,
    loc.intersection_type,
    loc.traffic_volume_category
FROM INCIDENT_REPORT i
JOIN CAMERA c
    ON c.camera_id = i.camera_ref
JOIN LANE l
    ON l.lane_id = c.lane_ref
JOIN LOCATION loc
    ON loc.location_id = l.location_ref
WHERE i.incident_type = 'accident'
GROUP BY 
    loc.location_id
ORDER BY accidents_count DESC
LIMIT 1;

-- Obter fase semafórica
SELECT
    t.traffic_light_id,
    s.timestamp,
    s.phase_id,
    s.phase_duration_s,
    s.current_state,
    l.description AS lane,
    l.direction
FROM TRAFFIC_LIGHT t
JOIN STATUS_CHANGE s
    ON s.traffic_light_ref = t.traffic_light_id
JOIN LANE l
    ON l.lane_id = t.lane_ref
JOIN (
    SELECT 
        s.traffic_light_ref,
        MAX(s.timestamp) AS last_timestamp
    FROM STATUS_CHANGE s
    JOIN TRAFFIC_LIGHT t
        ON t.traffic_light_id = s.traffic_light_ref
    GROUP BY t.traffic_light_id
) AS last_status
    ON last_status.traffic_light_ref = t.traffic_light_id
    AND last_status.last_timestamp = s.timestamp
WHERE
    l.location_ref = 'LOC-001';


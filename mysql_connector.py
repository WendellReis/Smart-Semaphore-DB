import mysql.connector
import os
import time
from mysql.connector import Error

EMOJI = '🐘'
DATABASE = 'iot_monitoring'

def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQLPASSWD")
        )

        if conn.is_connected():
            print("✅ Conectado com sucesso ao MySQL!")
            return conn, conn.cursor(dictionary=True)

    except Error as e:
        print("❌ Erro ao conectar ao MySQL:", e)
        return None, None

def insert_locations(cursor, locations,debug=True):
    query = """
        INSERT INTO LOCATION (
            location_id,
            description,
            city,
            latitude,
            longitude,
            intersection_type,
            traffic_volume_category,
            state
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            l["location_id"],
            l["description"],
            l["city"],
            l["coordinates"]["latitude"],
            l["coordinates"]["longitude"],
            l["intersection_type"],
            l["traffic_volume_category"],
            l["state"]
        )
        for l in locations
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'🐘 Inseridos {len(locations)} ({table_size(cursor,'LOCATION')[0]['size_mb']} MB) registros na tabela LOCATIONS em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_lanes(cursor, lanes,debug=True):
    query = """
        INSERT INTO LANE (
            lane_id,
            description,
            location_ref,
            lane_type,
            direction
        ) VALUES (%s, %s, %s, %s, %s)
    """

    values = [
        (
            l["lane_id"],
            l["description"],
            l["location_ref"],
            l["lane_type"],
            l["direction"],
        )
        for l in lanes
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'🐘 Inseridos {len(lanes)} ({table_size(cursor,'LANE')[0]['size_mb']} MB) registros na tabela LANE em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_cameras(cursor, cameras,debug=True):
    query = """
        INSERT INTO CAMERA (
            camera_id,
            model,
            firmware_version,
            last_check_in,
            lane_ref,
            status,
            resolution,
            framerate,
            view_angle_dregrees,
            ml_detection_enabled,
            image_storage_policy
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
    """

    values = [
        (
            c["device_id"],
            c["model"],
            c["firmware_version"],
            c["last_check_in"],
            c["lane_ref"],
            c["status"],
            c["config"]["resolution"],
            c["config"]["framerate"],
            c["config"]["view_angle_degrees"],
            c["config"]["ml_detection_enabled"],
            c["config"]["image_storage_policy"]
        )
        for c in cameras
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio
    
    if debug:
        print(f'{EMOJI} Inseridos {len(cameras)} ({table_size(cursor,'CAMERA')[0]['size_mb']} MB) registros na tabela CAMERA em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_traffic_sensors(cursor,traffic_sensors,debug=True):
    query = """
        INSERT INTO TRAFFIC_SENSOR (
            traffic_sensor_id,
            model,
            firmware_version,
            last_check_in,
            lane_ref,
            status,
            sampling_rate_s,
            detection_method,
            velocity_threshold_kph
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
    """

    values = [
        (
            t["device_id"],
            t["model"],
            t["firmware_version"],
            t["last_check_in"],
            t["lane_ref"],
            t["status"],
            t["config"]["sampling_rate_s"],
            t["config"]["detection_method"],
            t["config"]["velocity_threshold_kph"]
        )
        for t in traffic_sensors
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'{EMOJI} Inseridos {len(traffic_sensors)} ({table_size(cursor,'TRAFFIC_SENSOR')[0]['size_mb']} MB) registros na tabela TRAFFIC_SENSOR em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_traffic_lights(cursor,traffic_lights,debug=True):
    query = """
        INSERT INTO TRAFFIC_LIGHT (
            traffic_light_id,
            model,
            firmware_version,
            last_check_in,
            lane_ref,
            status,
            default_green_s,
            default_yellow_s,
            default_red_s,
            min_green_s,
            min_red_s,
            pedestrian_button_active
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s,%s)
    """

    values = [
        (
            t["device_id"],
            t["model"],
            t["firmware_version"],
            t["last_check_in"],
            t["lane_ref"],
            t["status"],
            t["config"]["default_green_s"],
            t["config"]["default_yellow_s"],
            t["config"]["default_red_s"],
            t["config"]["min_green_s"],
            t["config"]["min_red_s"],
            t["config"]["pedestrian_button_active"]
        )
        for t in traffic_lights
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'{EMOJI} Inseridos {len(traffic_lights)} ({table_size(cursor,'TRAFFIC_LIGHT')[0]['size_mb']} MB) registros na tabela TRAFFIC_LIGHT em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_incident_reports(cursor,incidents,debug=True):
    query = """
        INSERT INTO INCIDENT_REPORT (
            timestamp,
            incident_type,
            status,
            image_url,
            camera_ref
        ) VALUES (%s, %s, %s, %s, %s)
    """

    values = [
        (
            i['timestamp'],
            i['incident_type'],
            i['status'],
            i['image_url'],
            i['metadata']['device_ref']
        )
        for i in incidents
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'{EMOJI} Inseridos {len(incidents)} ({table_size(cursor,'INCIDENT_REPORT')[0]['size_mb']} MB) registros na tabela INCIDENT_REPORT em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_status_changes(cursor,status,debug=True):
    query = """
        INSERT INTO STATUS_CHANGE (
            timestamp,
            current_state,
            phase_duration_s,
            traffic_light_ref,
            phase_id
        ) VALUES (%s, %s, %s, %s, %s)
    """

    values = [
        (
            s['timestamp'],
            s['current_state'],
            s['phase_duration_s'],
            s['metadata']['device_ref'],
            s['phase_id']
        )
        for s in status
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio

    if debug:
        print(f'{EMOJI} Inseridos {len(status)} ({table_size(cursor,'STATUS_CHANGE')[0]['size_mb']} MB) registros na tabela STATUS_CHANGE em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_traffic_counts(cursor,counts,debug=True):
    query = """
        INSERT INTO TRAFFIC_COUNT (
            timestamp,
            avg_speed_kph,
            count,
            traffic_sensor_ref
        ) VALUES (%s, %s, %s, %s)
    """

    values = [
        (
            c['timestamp'],
            c['avg_speed_kph'],
            c['count'],
            c['metadata']['device_ref']
        )
        for c in counts
    ]

    inicio = time.time()
    cursor.executemany(query, values)
    tempo_execucao = time.time() - inicio
    if debug:
        print(f'{EMOJI} Inseridos {len(counts)} ({table_size(cursor,'TRAFFIC_COUNT')[0]['size_mb']} MB) registros na tabela TRAFFIC_COUNT em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def clear_table(cursor, table):
    inicio = time.time()
    cursor.execute(f"DELETE FROM {table}")
    quantidade = cursor.rowcount
    tempo_execucao = time.time() - inicio
    print(f"{EMOJI} Removidos {quantidade} registros da tabela {table} em {tempo_execucao:.4f} segundos.")

    return tempo_execucao

def clear_database(conn,cursor):
    print(f'🗑️ Limpando tabelas...')
    tables = [
        "INCIDENT_REPORT",
        "STATUS_CHANGE",
        "TRAFFIC_COUNT",
        "CAMERA",
        "TRAFFIC_LIGHT",
        "TRAFFIC_SENSOR",
        "LANE",
        "LOCATION"
    ]

    tempo_execucao = 0
    for t in tables:
        tempo_execucao+=clear_table(cursor,t)
    conn.commit()
    return tempo_execucao

def table_size(cursor,name):
    query = """
        SELECT 
            table_name,
            ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        ORDER BY size_mb DESC;
    """

    cursor.execute(query,(DATABASE,name))
    size = cursor.fetchall()
    return size

def insert_reading(conn,cursor,reading):
    tipo = reading['reading_type']
    if tipo == 'incident_report':
        tempo_execucao = time.time()
        insert_incident_reports(cursor,[reading],False)
        conn.commit()
        tempo_execucao = time.time() - tempo_execucao
    elif tipo == 'traffic_count':
        tempo_execucao = time.time()
        insert_traffic_counts(cursor,[reading],False)
        conn.commit()
        tempo_execucao = time.time() - tempo_execucao
    else:
        tempo_execucao = time.time()
        insert_status_changes(cursor,[reading],False)
        conn.commit()
        tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao

def populate_database(conn,cursor,locations,lanes,devices,readings):
    print(f'{EMOJI} Povoando base de dados...')

    traffic_sensors,traffic_lights,cameras = [],[],[]
    for d in devices:
        tipo = d["device_type"] 
        if tipo == "traffic_sensor":
            traffic_sensors.append(d)
        elif tipo == "traffic_light":
            traffic_lights.append(d)
        elif tipo == "camera":
            cameras.append(d)

    rd = {}
    rd['incident_report'] = []
    rd['status_change'] = []
    rd['traffic_count'] = []

    for r in readings:
        rd[r['reading_type']].append(r)

    tempo_execucao = insert_locations(cursor,locations)
    tempo_execucao+=insert_lanes(cursor,lanes)
    tempo_execucao+=insert_cameras(cursor,cameras)
    tempo_execucao+=insert_traffic_lights(cursor,traffic_lights)
    tempo_execucao+=insert_traffic_sensors(cursor,traffic_sensors)
    tempo_execucao+=insert_incident_reports(cursor,rd['incident_report'])
    tempo_execucao+=insert_status_changes(cursor,rd['status_change'])
    tempo_execucao+=insert_traffic_counts(cursor,rd['traffic_count'])

    conn.commit()
    return tempo_execucao

def find_readings(cursor, sensor_id):
    query = "SELECT * FROM TRAFFIC_COUNT WHERE traffic_sensor_ref = %s"

    inicio = time.time()
    cursor.execute(query, (sensor_id,))
    cursor.fetchall() 
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def delete_device(cursor,sensor_id): 
    query = "DELETE FROM TRAFFIC_SENSOR WHERE traffic_sensor_id = %s"

    inicio = time.time()
    cursor.execute(query, (sensor_id,))
    cursor.fetchall() 
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def update_firmware_version(conn,cursor,sensor_id,version):
    query = """ UPDATE TRAFFIC_LIGHT  
                SET firmware_version = %s
                WHERE traffic_light_id = %s
            """
    
    inicio = time.time()
    cursor.execute(query, (version,sensor_id))
    conn.commit()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_traffic_light_flow(cursor,traffic_light_id):
    query = """ SELECT 
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
                WHERE tl.traffic_light_id = %s
                ORDER BY tc.timestamp DESC;
        """
    
    inicio = time.time()
    cursor.execute(query, (traffic_light_id,))
    cursor.fetchall()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_overspeed_readings(cursor):
    query = """ SELECT 
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
        """
    
    inicio = time.time()
    cursor.execute(query)
    cursor.fetchall()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_possible_congestions(cursor):
    query = """ SELECT
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
        """
    
    inicio = time.time()
    cursor.execute(query)
    cursor.fetchall()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_open_accidents(cursor):
    query = """SELECT
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
        """
    
    inicio = time.time()
    cursor.execute(query)
    cursor.fetchall()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_most_dangerous_location(cursor):
    query = """SELECT 
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
        """
    
    inicio = time.time()
    cursor.execute(query)
    cursor.fetchall()
    tempo_execucao = time.time() - inicio

    return tempo_execucao

def get_traffic_lights_states(cursor,traffic_light_id):
        query = """ SELECT
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
                    l.location_ref = %s;
        """
        inicio = time.time()
        cursor.execute(query, (traffic_light_id,))
        cursor.fetchall()
        tempo_execucao = time.time() - inicio

        return tempo_execucao
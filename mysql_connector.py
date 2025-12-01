import mysql.connector
import os
import time
from mysql.connector import Error

EMOJI = '🐘'

def connect_to_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQLPASSWD")
        )

        if conn.is_connected():
            print("✅ Conectado com sucesso ao MySQL!")
            return conn, conn.cursor()

    except Error as e:
        print("❌ Erro ao conectar ao MySQL:", e)
        return None, None


def insert_locations(cursor, locations):
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

    print(f'🐘 Inseridos {len(locations)} registros na tabela LOCATIONS em {tempo_execucao:.4f} segundos.')
    return tempo_execucao


def insert_lanes(cursor, lanes):
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

    print(f'🐘 Inseridos {len(lanes)} registros na tabela LANE em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_cameras(cursor, cameras):
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

    print(f'{EMOJI} Inseridos {len(cameras)} registros na tabela CAMERA em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_traffic_sensors(cursor,traffic_sensors):
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

    print(f'{EMOJI} Inseridos {len(traffic_sensors)} registros na tabela TRAFFIC_SENSOR em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def insert_traffic_lights(cursor,traffic_lights):
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

    print(f'{EMOJI} Inseridos {len(traffic_lights)} registros na tabela TRAFFIC_LIGHT em {tempo_execucao:.4f} segundos.')
    return tempo_execucao

def clear_table(cursor, table):
    inicio = time.time()
    cursor.execute(f"DELETE FROM `{table}`")
    quantidade = cursor.rowcount
    tempo_execucao = time.time() - inicio
    print(f"🗑️  Removidos {quantidade} registros da tabela {table} em {tempo_execucao:.4f} segundos.")

    return tempo_execucao


def clear_database(conn,cursor):
    print(f'{EMOJI} Limpando tabelas...')
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

    tempo_execucao = insert_locations(cursor,locations)
    tempo_execucao+=insert_lanes(cursor,lanes)
    tempo_execucao+=insert_cameras(cursor,cameras)
    tempo_execucao+=insert_traffic_lights(cursor,traffic_lights)
    tempo_execucao+=insert_traffic_sensors(cursor,traffic_sensors)

    conn.commit()
    


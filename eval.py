import os
import json
import mongo_connector
import random
import mysql_connector

SEED = 4321

def load_data(filedir):
    if not os.path.exists(filedir):
        print(f"❌ Erro: Arquivo não encontrado em {filedir}")
        return None
        
    try:
        with open(filedir, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📂 Dados de '{filedir}.json' carregados com sucesso.")
            return data
    except json.JSONDecodeError as e:
        print(f"❌ Erro de decodificação JSON no arquivo {filedir}.json: {e}")
        return None


def print_time(text, value):
    print(f"{text}: {value:.4f} segundos.")

SPACES = 71

EMO_MONGO = "🍃"
EMO_MYSQL = "🐘"

OP_EMO = {
    "POV": "📥",
    "INSERT": "🧩",
    "FIND": "🔍",
    "DELETE": "🗑️ ",
    "UPDATE": "🔧",
    "FLOW": "🚦",
    "STATUS": "🚦",
    "OVER": "⚡",
    "CONGESTION": "🚗",
    "ACCIDENT": "🚨",
    "DANGER": "💀",
}


def eval():
    random.seed(SEED)
    print("⚙️  Conectando com banco de dados...")

    db_mongo = mongo_connector.connect_to_mongodb("mongodb://localhost:27017/")
    db_mongo = db_mongo["iot_monitoring"]

    conn, cursor = mysql_connector.connect_to_mysql()
    cursor.execute("USE iot_monitoring")
    conn.commit()

    print("\n🔗 Conectado com iot_monitoring.\n")

    locations = load_data('log/locations.json')
    lanes = load_data('log/lanes.json')
    devices = load_data('log/devices.json')
    readings = load_data('log/readings.json')

    sensors = [d for d in devices if d['device_type'] == 'traffic_sensor']
    samples = random.sample(readings, 100)

    # Testes com MongoDB
    print()
    print(" Mongodb ".center(SPACES,"-"))
    time_mongo = {}

    time_mongo["T-CLEAR"] = mongo_connector.clear_database(db_mongo)

    print("\n⏱️  Testes de tempo:")

    MONGO_OPS = [
        ("T-POV",OP_EMO["POV"],lambda: mongo_connector.populate_database(db_mongo, locations, lanes, devices, readings)),
        ("T-INSERT-READING",OP_EMO["INSERT"],lambda:sum(mongo_connector.insert_one(db_mongo, "readings", s) for s in samples) / 100),
        ("T-FIND-READINGS",OP_EMO["FIND"],lambda: sum(mongo_connector.find_readings(db_mongo, s["device_id"]) for s in sensors) / len(sensors)),
        ("T-DELETE-DEVICE-CASCATE", OP_EMO["DELETE"],lambda:(
             mongo_connector.delete_one(db_mongo, "readings", {"metada.device": "TRS-005-01"}) +
             mongo_connector.delete_one(db_mongo, "devices", {"device_id": "TRS-005-01"})
        )),
        ("T-UPDATE-FIRMWARE",OP_EMO["UPDATE"],lambda: mongo_connector.update_one(db_mongo,"devices",{"device_id": "SEM-001-01"}, {"$set": {"firmware_version": "3.0"}})),
        ("T-GET-TRAFFIC-LIGHT-FLOW",OP_EMO["FLOW"],lambda: mongo_connector.get_traffic_light_flow(db_mongo, "SEM-001-01")),
        ("T-GET-TRAFFIC-LIGHTS-STATUS", OP_EMO["STATUS"], lambda: mongo_connector.get_traffic_lights_states(db_mongo,'LOC-001')),
        ("T-GET-OVERSPEED-READINGS", OP_EMO["OVER"],lambda: mongo_connector.get_overspeed_overspeed(db_mongo)),
        ("T-GET-POSSIBLE-CONGESTIONS", OP_EMO["CONGESTION"],lambda: mongo_connector.get_possible_congestions(db_mongo)),
        ("T-GET-OPEN-ACCIDENTS", OP_EMO["ACCIDENT"],lambda: mongo_connector.get_open_accidents(db_mongo)),
        ("T-GET-MOST-DANGEROUS-LOCATION", OP_EMO["DANGER"],lambda: mongo_connector.get_most_dangerous_location(db_mongo)),
    ]

    for op, emo, func in MONGO_OPS:
        time_mongo[op] = func()
        print_time(f"{EMO_MONGO} {emo} {op}", time_mongo[op])

    
    # Testes com MySQL

    print("\n"+" MySQL ".center(SPACES, "-"))
    print()
    time_mysql = {}

    time_mysql["T-CLEAR"]=mysql_connector.clear_database(conn, cursor)

    print("\n⏱️  Testes de tempo:")

    MYSQL_OPS = [
        ("T-POV", OP_EMO["POV"],lambda: mysql_connector.populate_database(conn, cursor, locations, lanes, devices, readings)),
        ("T-INSERT-READING",OP_EMO["INSERT"],lambda: sum(mysql_connector.insert_reading(conn, cursor, s) for s in samples) / 100),
        ("T-FIND-READINGS", OP_EMO["FIND"], lambda: sum(mysql_connector.find_readings(cursor, s["device_id"]) for s in sensors) / len(sensors)),
        ("T-DELETE-DEVICE-CASCATE", OP_EMO["DELETE"], lambda: mysql_connector.delete_device(cursor, "TRS-005-01")),
        ("T-UPDATE-FIRMWARE",OP_EMO["UPDATE"],lambda: mysql_connector.update_firmware_version(conn, cursor, "SEM-001-01", "3.0")),
        ("T-GET-TRAFFIC-LIGHT-FLOW", OP_EMO["FLOW"],lambda: mysql_connector.get_traffic_light_flow(cursor, "SEM-001-01")),
        ("T-GET-TRAFFIC-LIGHTS-STATUS", OP_EMO["STATUS"], lambda: mysql_connector.get_traffic_lights_states(cursor,'LOC-001')),
        ("T-GET-OVERSPEED-READINGS", OP_EMO["OVER"],lambda: mysql_connector.get_overspeed_readings(cursor)),
        ("T-GET-POSSIBLE-CONGESTIONS", OP_EMO["CONGESTION"], lambda: mysql_connector.get_possible_congestions(cursor)),
        ("T-GET-OPEN-ACCIDENTS", OP_EMO["ACCIDENT"],lambda: mysql_connector.get_open_accidents(cursor)),
        ("T-GET-MOST-DANGEROUS-LOCATION", OP_EMO["DANGER"], lambda: mysql_connector.get_most_dangerous_location(cursor)),
    ]

    for op,emo,func in MYSQL_OPS:
        time_mysql[op]=func()
        print_time(f"{EMO_MYSQL} {emo} {op}",time_mysql[op])

if __name__ == "__main__":
    eval()

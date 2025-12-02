import os
import json
import mongo_connector
import time
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

def print_time(text,value):
    print(f'{text}: {value:.4f} segundos.')

def eval():
    # Conectando ao banco de dados
    random.seed(SEED)
    #user = os.environ['mongodb_user']
    #password = os.environ['mongodb_password']


    local_uri = "mongodb://localhost:27017/"
    #uri = f"mongodb+srv://{user}:{password}@cluster0.drkxjcd.mongodb.net/?appName=Cluster0"

    print('⚙️  Conectando com banco de dados...')
    db_mongo = mongo_connector.connect_to_mongodb(local_uri)
    conn, cursor = mysql_connector.connect_to_mysql()
    
    db_mongo = db_mongo["iot_monitoring"]
    cursor.execute('USE iot_monitoring')
    conn.commit()
    print(f'\n🔗 Conectado com iot_monitoring.\n')
    
    # Extraindo dados dos arquivos json
    locations = load_data('log/locations.json')
    lanes = load_data('log/lanes.json')
    devices = load_data('log/devices.json')
    readings = load_data('log/readings.json')


    # Mongodb

    time_mongo = {}
    print(" Mongodb ".center(31,'-'))
    time_mongo['T-CLEAR']=mongo_connector.clear_database(db_mongo)

    samples = random.sample(readings,100)
    time_mongo['T-POV'] = mongo_connector.populate_database(db_mongo,locations,lanes,devices,readings) 
    print("\n⏱️  Testes de tempo:")


    print_time(f"🍃 T-POV",time_mongo['T-POV'])

    time_mongo['T-INSERT-READING'] = 0
    for s in samples:
        time_mongo['T-INSERT-READING'] += mongo_connector.insert_one(db_mongo,"readings",s)
    time_mongo['T-INSERT-READING']/=100
    print_time(f"🍃 T-INSERT-READING",time_mongo['T-INSERT-READING'])

    time_mongo['T-FIND-READINGS'] = 0
    
    sensors = []
    for d in devices:
        if d['device_type'] == 'traffic_sensor':
            sensors.append(d)
    
    for s in sensors:
        time_mongo['T-FIND-READINGS']+=mongo_connector.find_readings(db_mongo,s['device_id'])
    time_mongo['T-FIND-READINGS']/=len(sensors)
    print_time(f"🍃 T-FIND-READINGS",time_mongo['T-FIND-READINGS'])

    traffic_sensor_id = 'TRS-005-01'
    filter = {"metada.device": traffic_sensor_id}
    time_mongo['T-DELETE-DEVICE-CASCATE'] = mongo_connector.delete_one(db_mongo,'readings',filter)
    filter = {"device_id": traffic_sensor_id}
    time_mongo['T-DELETE-DEVICE-CASCATE'] += mongo_connector.delete_one(db_mongo,'devices',filter)
    print_time(f"🍃 T-DELETE-DEVICE-CASCATE",time_mongo['T-DELETE-DEVICE-CASCATE'])

    traffic_light_id = 'SEM-001-01'
    filter = {"device_id":traffic_light_id}
    update = {"$set": {"firmware_version": "3.0"}}
    time_mongo['T-UPDATE-FIRMWARE'] = mongo_connector.update_one(db_mongo,'devices',filter,update)
    print_time(f"🍃 T-UPDATE-FIRMWARE",time_mongo['T-UPDATE-FIRMWARE'])

    time_mongo['T-FLOW'] = mongo_connector.get_traffic_light_flow(db_mongo,traffic_light_id)
    print_time(f"🍃 T-FLOW",time_mongo['T-FLOW'])

    time_mongo['T-GET-OVERSPEED-READINGS'] = mongo_connector.get_overspeed_overspeed(db_mongo)
    print_time(f"🍃 T-GET-OVERSPEED-READINGS",time_mongo['T-GET-OVERSPEED-READINGS'])

    time_mongo['T-GET-POSSIBLE-CONGESTIONS'] = mongo_connector.get_possible_congestions(db_mongo)
    print_time(f"🍃 T-GET-POSSIBLE-CONGESTIONS",time_mongo['T-GET-POSSIBLE-CONGESTIONS'])

    time_mongo['T-GET-OPEN-ACCIDENTS'] = mongo_connector.get_open_accidents(db_mongo)
    print_time("🍃 T-GET-OPEN-ACCIDENTS", time_mongo['T-GET-OPEN-ACCIDENTS'])

    time_mongo['T-GET-MOST-DANGEROUS-LOCATION'] = mongo_connector.get_most_dangerous_location(db_mongo)
    print_time("🍃 T-GET-MOST-DANGEROUS-LOCATION", time_mongo['T-GET-MOST-DANGEROUS-LOCATION'])

    # Mysql
    time_mysql = {}
    print()
    print(" MySql ".center(31,'-'))
    time_mysql['T-CLEAR']=mysql_connector.clear_database(conn,cursor)

    print()
    time_mysql['T-POV'] = mysql_connector.populate_database(conn,cursor,locations,lanes,devices,readings)

    print("\n⏱️  Testes de tempo:")
    print_time(f"🐘 T-POV",time_mysql['T-POV'])
    
    time_mysql['T-INSERT-READING'] = 0
    for s in samples:
        time_mysql['T-INSERT-READING'] += mysql_connector.insert_reading(conn,cursor,s)

    time_mysql['T-INSERT-READING']/=100
    print_time(f'🐘 T-INSERT-READING',time_mysql['T-INSERT-READING'])

    time_mysql['T-FIND-READINGS'] = 0
    
    for s in sensors:
        time_mysql['T-FIND-READINGS']+=mysql_connector.find_readings(cursor,s['device_id'])
    time_mysql['T-FIND-READINGS']/=len(sensors)
    print_time(f"🐘 T-FIND-READINGS",time_mysql['T-FIND-READINGS'])

    time_mysql['T-DELETE-DEVICE-CASCATE'] = mysql_connector.delete_device(cursor,traffic_sensor_id)
    print_time(f"🐘 T-DELETE-DEVICE-CASCATE",time_mysql['T-DELETE-DEVICE-CASCATE'])

    time_mysql['T-UPDATE-FIRMWARE'] = mysql_connector.update_firmware_version(conn,cursor,traffic_light_id,'3.0')
    print_time(f"🐘 T-UPDATE-FIRMWARE",time_mysql['T-UPDATE-FIRMWARE'])

    time_mysql['T-FLOW'] = mysql_connector.get_traffic_light_flow(cursor,traffic_light_id)
    print_time(f"🐘 T-FLOW",time_mysql['T-FLOW'])

    time_mysql['T-GET-OVERSPEED-READINGS'] = mysql_connector.get_overspeed_readings(cursor)
    print_time(f"🐘 T-GET-OVERSPEED-READINGS",time_mysql['T-GET-OVERSPEED-READINGS'])

    time_mysql['T-GET-POSSIBLE-CONGESTIONS'] = mysql_connector.get_possible_congestions(cursor)
    print_time("🐘 T-GET-POSSIBLE-CONGESTIONS", time_mysql['T-GET-POSSIBLE-CONGESTIONS'])

    time_mysql['T-GET-OPEN-ACCIDENTS'] = mysql_connector.get_open_accidents(cursor)
    print_time("🐘 T-GET-OPEN-ACCIDENTS", time_mysql['T-GET-OPEN-ACCIDENTS'])

    time_mysql['T-GET-MOST-DANGEROUS-LOCATION'] = mysql_connector.get_most_dangerous_location(cursor)
    print_time("🐘 T-GET-MOST-DANGEROUS-LOCATION", time_mysql['T-GET-MOST-DANGEROUS-LOCATION'])

if __name__ == "__main__":
    eval()


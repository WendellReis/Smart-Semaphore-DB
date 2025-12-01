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
        
def clear_database(db_mongo):
    print('\n🍃  Limpando collections...')
    tempo_execucao = 0
    for c in ['locations','lanes','devices','readings']:
        tempo_execucao+=mongo_connector.clean_collection(db_mongo,c)
    return tempo_execucao

def populate_database(db_mongo,locations,lanes,devices,readings):
    print('\n🍃 Povoando base de dados...')
    t1 = mongo_connector.insert_many(db_mongo,'locations',locations)
    t2 = mongo_connector.insert_many(db_mongo,'lanes',lanes)
    t3 = mongo_connector.insert_many(db_mongo,'devices',devices)
    t4 = mongo_connector.insert_many(db_mongo,'readings',readings)
    
    if t1 is not None and t2 is not None and t3 is not None and t4 is not None:
        return t1+t2+t3+t4

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

    time_mongo = {}
    time_mysql = {}

    # Limpa as collections antes de povoar o banco
    time_mongo['clear']=clear_database(db_mongo)
    print()
    time_mysql['clear']=mysql_connector.clear_database(conn,cursor)

    # Popula o banco de dados
    time_mongo['pov'] = populate_database(db_mongo,locations,lanes,devices,readings)
    print()
    time_mysql['pov'] = mysql_connector.populate_database(conn,cursor,locations,lanes,devices,readings)

    print("\n⏱️  Testes de tempo:")
    print_time("🍃 T-POV",time_mongo['clear'])
    print_time("🐘 T-POV",time_mysql['clear'])
    
    '''

    # Tempo médio de inserção
    samples = random.sample(readings,100)
    temp = 0
    for s in samples:
        temp += mongo_connector.insert_one(db_mongo,"readings",s)

    print_time("T-INSERT-READING",temp/100)

    temp = 0
    for s in samples:
        temp += mongo_connector.delete_one(db_mongo,"readings",s)
    print_time("T-DELETE-READING",temp/100)
    
    samples = random.sample(devices,100)
    temp = 0
    for s in samples:
        temp += mongo_connector.findReadings(db_mongo,s["device_id"])
    print_time("T-FIND-READINGS",temp/100)

    temp = 0
    for l in locations:
        filtro = {"location_ref": l['location_id'],"device_type":"traffic_light"}
        update = {"$set": {"phase_id": "PHASE_TEST"}}
        temp += mongo_connector.update_many(db_mongo,"location",filtro,update)
    
    print_time("T-UPDATE-PHASE",temp/len(locations))

    print_time("TQ1 - Tempo para obter fluxo de semaforo",mongo_connector.fluxo(db_mongo))
    print_time("TQ2 - Tempo para obter historico de excesso de velocidade",mongo_connector.historico(db_mongo))
    print_time("TQ3 - Tempo para obter leituras de congestionamentos",mongo_connector.ultimas_leituras(db_mongo))
    print_time("TQ4 - Tempo para obter acidentes em aberto",mongo_connector.acidentes_abertos(db_mongo))
    print_time("TQ5 - Tempo para obter local mais perigoso",mongo_connector.local_mais_acidentes(db_mongo))
    '''

if __name__ == "__main__":
    eval()


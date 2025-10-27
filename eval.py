import os
import json
import mongo_connector
import time
import random

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
        
def clear_database(db):
    print('\n⚙️  Limpando collections...')
    mongo_connector.clean_collection(db,'locations')
    mongo_connector.clean_collection(db,'devices')
    mongo_connector.clean_collection(db,'readings')

def populate_database(db,locations,devices,readings):
    print('\n⚙️  Povoando base de dados...')
    t1 = mongo_connector.insert_many(db,'locations',locations)
    t2 = mongo_connector.insert_many(db,'devices',devices)
    t3 = mongo_connector.insert_many(db,'readings',readings)
    
    if t1 is not None and t2 is not None and t3 is not None:
        return t1+t2+t3

def print_time(text,value):
    print(f'⏱️  {text}: {value:.4f} segundos.')

def eval():
    # Conectando ao banco de dados
    random.seed(SEED)
    user = os.environ['mongodb_user']
    password = os.environ['mongodb_password']

    uri = f"mongodb+srv://{user}:{password}@cluster0.drkxjcd.mongodb.net/?appName=Cluster0"

    print('⚙️  Conecntando com banco de dados...')
    db = mongo_connector.connect_to_mongodb(uri)
    if db is None:
        return
    
    db = db["iot_monitoring"]
    print(f'🔗 Conentado com iot_monitoring.')
    
    # Extraindo dados dos arquivos json
    locations = load_data('log/locations.json')
    devices = load_data('log/devices.json')
    readings = load_data('log/readings.json')        

    '''
    # Limpa as collections antes de povoar o banco
    #clear_database(db)

    # Popula o banco de dados
    #temp = populate_database(db,locations,devices,readings)

    print("\n⚙️  Testes de tempo:")
    #print_time("T-POV",temp)

    # Tempo médio de inserção
    samples = random.sample(readings,100)
    temp = 0
    for s in samples:
        temp += mongo_connector.insert_one(db,"readings",s)

    print_time("T-INSERT-READING",temp/100)

    # Tempo médio para deleção de leitura
    temp = 0
    for s in samples:
        temp += mongo_connector.delete_one(db,"readings",s)
    print_time("T-DELETE-READING",temp/100)
    
    # Tempo médio para consultar leituras
    samples = random.sample(devices,100)
    temp = 0
    for s in samples:
        temp += mongo_connector.findReadings(db,s["device_id"])
    print_time("T-FIND-READINGS",temp/100)

    # Atualização de fase
    temp = 0
    for l in locations:
        filtro = {"location_ref": l['location_id'],"device_type":"traffic_light"}
        update = {"$set": {"phase_id": "PHASE_TEST"}}
        temp += mongo_connector.update_many(db,"location",filtro,update)
    
    print_time("T-UPDATE-PHASE",temp/len(locations))

    '''

if __name__ == "__main__":
    eval()


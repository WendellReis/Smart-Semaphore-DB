import os
import json
import mongo_connector

def loadData(filedir):

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

def populateDatabase(db,data):
    pass

def eval():
    # Conectando ao banco de dados
    db = db = mongo_connector.connect_to_mongodb()
    if db is None:
        return
    
    # Extraindo dados dos arquivos json
    locations = loadData('log/locations.json')
    devices = loadData('log/devices.json')
    readings = loadData('log/readings.json')




if __name__ == "__main__":
    eval()


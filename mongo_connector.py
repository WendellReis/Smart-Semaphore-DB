from pymongo import MongoClient
from datetime import datetime
import os

user = os.environ['mongodb_user']
password = os.environ['mongodb_password']

MONGO_URI = f"mongodb+srv://{user}:{password}@cluster0.drkxjcd.mongodb.net/?appName=Cluster0"

def connect_to_mongodb():
    try:
        client = MongoClient(MONGO_URI)

        client.admin.command('ping')
        print(f"✅ Conectado com sucesso ao MongoDB em: {MONGO_URI}")

        return client
    
    except Exception as e:
        print(f"❌ Erro de conexão ao MongoDB local: {e}")
        return None
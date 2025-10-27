from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
import time

def connect_to_mongodb(uri):
    try:
        client = MongoClient(uri)

        client.admin.command('ping')
        print(f"✅ Conectado com sucesso ao MongoDB em: {uri}")

        return client
    
    except Exception as e:
        print(f"❌ Erro de conexão ao MongoDB local: {e}")
        return None
    
def clean_collection(db,collection):
    col = db[collection]

    inicio = time.time()
    delete_result = col.delete_many({})
    tempo_execucao = time.time() - inicio

    print(f"🗑️  Removidos {delete_result.deleted_count} documentos da collection {collection} em {tempo_execucao:.4f} segundos.")
    return tempo_execucao

def insert_many(db,collection,data):
    for d in data:
        d["_id"] = ObjectId()
    
    inicio = time.time()
    db[collection].insert_many(data)
    tempo_execucao = time.time() - inicio
    print(f"💾  Inseridos {len(data)} documentos da collection {collection} em {tempo_execucao:.4f} segundos.")
    return tempo_execucao

def insert_one(db,collection,data):
    data["_id"] = ObjectId()
    inicio = time.time()
    db[collection].insert_one(data)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def delete_one(db,collection,filter):
    inicio = time.time()
    db[collection].delete_one(filter)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def find(db,collection,filter):
    inicio = time.time()
    db[collection].find(filter)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

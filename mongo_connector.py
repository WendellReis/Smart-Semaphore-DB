from pymongo import MongoClient, DESCENDING
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

    print(f"🍃 Removidos {delete_result.deleted_count} documentos da collection {collection} em {tempo_execucao:.4f} segundos.")
    return tempo_execucao

def collection_size(db, collection_name):
    stats = db.command("collStats", collection_name)
    return stats["storageSize"] / 1024 / 1024

def insert_many(db,collection,data):
    for d in data:
        d["_id"] = ObjectId()
    
    inicio = time.time()
    db[collection].insert_many(data)
    tempo_execucao = time.time() - inicio
    print(f"🍃 Inseridos {len(data)} ({collection_size(db,collection):.2f} MB) documentos da collection {collection} em {tempo_execucao:.4f} segundos.")
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

def delete_many(db,collection,filter):
    inicio = time.time()
    db[collection].delete_one(filter)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def find(db,collection,filter):
    inicio = time.time()
    db[collection].find(filter)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def update_many(db,collection,filter,update):
    inicio = time.time()
    db[collection].update_many(filter,update)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def update_one(db,collection,filter,update):
    inicio = time.time()
    db[collection].update_many(filter,update)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def find_readings(db,device_id):
    filtro = {"metadata.device_ref": device_id}
    inicio = time.time()
    db['readings'].find(filtro)
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def populate_database(db_mongo,locations,lanes,devices,readings):
    print('\n🍃 Povoando base de dados...')
    t1 = insert_many(db_mongo,'locations',locations)
    t2 = insert_many(db_mongo,'lanes',lanes)
    t3 = insert_many(db_mongo,'devices',devices)
    t4 = insert_many(db_mongo,'readings',readings)
    
    if t1 is not None and t2 is not None and t3 is not None and t4 is not None:
        return t1+t2+t3+t4

def clear_database(db_mongo):
    print('\n🗑️  Limpando collections...')
    tempo_execucao = 0
    for c in ['locations','lanes','devices','readings']:
        tempo_execucao+=clean_collection(db_mongo,c)
    return tempo_execucao

def get_traffic_light_flow(db_mongo,traffic_light_id):
    tempo_execucao = time.time()
    pipeline = [
        {"$match": {"device_id": traffic_light_id}},

        {
            "$lookup": {
                "from": "devices",
                "let": {"semaforoLane": "$lane_ref"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$device_type", "traffic_sensor"]},
                                    {"$eq": ["$lane_ref", "$$semaforoLane"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "traffic_sensor"
            }
        },

        {"$unwind": "$traffic_sensor"},

        {
            "$project": {
                "traffic_light_id": "$device_id",
                "traffic_sensor_id": "$traffic_sensor.device_id",
                "_id": 0
            }
        },

        {
            "$lookup": {
                "from": "readings",
                "localField": "traffic_sensor_id",
                "foreignField": "metadata.device_ref",
                "as": "reading"
            }
        },

        {"$unwind": "$reading"},

        {
            "$project": {
                "traffic_light_id": 1,
                "traffic_sensor_id": 1,
                "timestamp": "$reading.timestamp",
                "count": "$reading.count",
                "avg_speed_kph": "$reading.avg_speed_kph"
            }
        },

        {"$sort": {"timestamp": -1}}
    ]
    db_mongo["devices"].aggregate(pipeline, maxTimeMS=60000,allowDiskUse=True)
    tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao
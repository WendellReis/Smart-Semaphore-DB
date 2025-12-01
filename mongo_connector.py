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

def findReadings(db,device_id):
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

def historico(db):
    inicio = time.time()
    cursor = db['readings'].aggregate([
    {
        '$match': {
            'reading_type': 'traffic_count'
        }
    }, {
        '$lookup': {
            'from': 'devices', 
            'localField': 'metadata.device_ref', 
            'foreignField': 'device_id', 
            'as': 'device_info'
        }
    }, {
        '$unwind': {
            'path': '$device_info'
        }
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': 'metadata.location_ref', 
            'foreignField': 'location_id', 
            'as': 'location_info'
        }
    }, {
        '$unwind': {
            'path': '$location_info'
        }
    }, {
        '$project': {
            '_id': 0, 
            'timestamp': '$timestamp', 
            'local_description': '$location_info.description', 
            'lane': '$device_info.lane_description', 
            'count': '$count', 
            'device_id': '$device_info.device_id', 
            'avg_speed_kph_limit': '$device_info.config.velocity_threshold_kph', 
            'avg_speed_kph_reported': '$avg_speed_kph'
        }
    }
])
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def acidentes_abertos(db):
    inicio = time.time()
    cursor = db['readings'].aggregate([
    {
        '$match': {
            'incident_type': 'accident'
        }
    }, {
        '$lookup': {
            'from': 'devices', 
            'localField': 'metadata.device_ref', 
            'foreignField': 'device_id', 
            'as': 'device_info'
        }
    }, {
        '$unwind': {
            'path': '$device_info'
        }
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': 'device_info.location_ref', 
            'foreignField': 'location_id', 
            'as': 'location_info'
        }
    }, {
        '$unwind': {
            'path': '$location_info'
        }
    }, {
        '$group': {
            '_id': '$metadata.location_ref', 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'count': -1
        }
    }, {
        '$limit': 1
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': '_id', 
            'foreignField': 'location_id', 
            'as': 'location_info'
        }
    }, {
        '$unwind': {
            'path': '$location_info'
        }
    }, {
        '$project': {
            '_id': 0, 
            'location_id': '$_id', 
            'accident_count': '$count', 
            'description': '$location_info.description', 
            'city': '$location_info.city', 
            'state': '$location_info.state', 
            'num_lanes': '$location_info.num_lanes', 
            'intersection_type': '$location_info.intersection_type', 
            'traffic_volume_category': '$location_info.traffic_volume_category'
        }
    }
])
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def ultimas_leituras(db):
    inicio = time.time()
    cursor = db['readings'].aggregate([
    {
        '$match': {
            'reading_type': 'traffic_count', 
            'count': {
                '$ne': 0
            }
        }
    }, {
        '$sort': {
            'metadata.device_ref': 1, 
            'timestamp': -1
        }
    }, {
        '$lookup': {
            'from': 'devices', 
            'localField': 'metadata.device_ref', 
            'foreignField': 'device_id', 
            'as': 'device_info'
        }
    }, {
        '$unwind': {
            'path': '$device_info'
        }
    }, {
        '$group': {
            '_id': '$device_info.device_id', 
            'reading': {
                '$first': '$$ROOT'
            }
        }
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': 'reading.device_info.location_ref', 
            'foreignField': 'location_id', 
            'as': 'location'
        }
    }, {
        '$unwind': {
            'path': '$location'
        }
    }, {
        '$project': {
            '_id': 0, 
            'device_id': '$_id', 
            'timestamp': '$reading.timestamp', 
            'local_description': '$location.description', 
            'lane': '$reading.device_info.lane_description', 
            'sampling_rate_s': '$reading.device_info.config.sampling_rate_s', 
            'avg_speed_kph_limit': '$reading.device_info.config.velocity_threshold_kph', 
            'avg_speed_kph_reported': '$reading.avg_speed_kph', 
            'count': '$reading.count'
        }
    }
])
    tempo_execucao = time.time() - inicio
    return tempo_execucao

def local_mais_acidentes(db):
    inicio = time.time()
    cursor = db['readings'].aggregate([
    {
        '$match': {
            'incident_type': 'accident'
        }
    }, {
        '$lookup': {
            'from': 'devices', 
            'localField': 'metadata.device_ref', 
            'foreignField': 'device_id', 
            'as': 'device_info'
        }
    }, {
        '$unwind': {
            'path': '$device_info'
        }
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': 'device_info.location_ref', 
            'foreignField': 'location_id', 
            'as': 'location_info'
        }
    }, {
        '$unwind': {
            'path': '$location_info'
        }
    }, {
        '$group': {
            '_id': '$metadata.location_ref', 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$sort': {
            'count': -1
        }
    }, {
        '$limit': 1
    }, {
        '$lookup': {
            'from': 'locations', 
            'localField': '_id', 
            'foreignField': 'location_id', 
            'as': 'location_info'
        }
    }, {
        '$unwind': {
            'path': '$location_info'
        }
    }, {
        '$project': {
            '_id': 0, 
            'location_id': '$_id', 
            'accident_count': '$count', 
            'description': '$location_info.description', 
            'city': '$location_info.city', 
            'state': '$location_info.state', 
            'num_lanes': '$location_info.num_lanes', 
            'intersection_type': '$location_info.intersection_type', 
            'traffic_volume_category': '$location_info.traffic_volume_category'
        }
    }
])
    tempo_execucao = time.time() - inicio
    return tempo_execucao


def fluxo(db):
    inicio = time.time()
    cursor = db['devices'].aggregate([
    {
        '$match': {
            'device_id': 'SEM-001-01'
        }
    }, {
        '$lookup': {
            'from': 'devices', 
            'let': {
                'semaforoLane': '$lane_description'
            }, 
            'pipeline': [
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$device_type', 'traffic_sensor'
                                    ]
                                }, {
                                    '$eq': [
                                        '$lane_description', '$$semaforoLane'
                                    ]
                                }
                            ]
                        }
                    }
                }
            ], 
            'as': 'traffic_sensor'
        }
    }, {
        '$unwind': {
            'path': '$traffic_sensor'
        }
    }, {
        '$project': {
            'traffic_sensor_id': '$traffic_sensor.device_id', 
            '_id': 0
        }
    }, {
        '$lookup': {
            'from': 'readings', 
            'localField': 'traffic_sensor_id', 
            'foreignField': 'metadata.device_ref', 
            'as': 'reading'
        }
    }, {
        '$unwind': {
            'path': '$reading'
        }
    }, {
        '$project': {
            'timestamp': '$reading.timestamp', 
            'count': '$reading.count', 
            'avg_speed_kph': '$reading.avg_speed_kph'
        }
    }, {
        '$sort': {
            'timestamp': -1
        }
    }
])
    tempo_execucao = time.time() - inicio
    return tempo_execucao
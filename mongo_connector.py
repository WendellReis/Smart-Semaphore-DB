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

def get_overspeed_overspeed(db_mongo):
    tempo_execucao = time.time()
    pipeline = [
        {
            '$match': {
                'reading_type': 'traffic_count', 
                '$expr': {
                    '$gt': [
                        '$avg_speed_kph', '$velocity_threshold_kph'
                    ]
                }
            }
        }, {
            '$sort': {
                'timestamp': -1
            }
        }, {
            '$lookup': {
                'from': 'locations', 
                'localField': 'metadata.location_ref', 
                'foreignField': 'location_id', 
                'as': 'location'
            }
        }, {
            '$lookup': {
                'from': 'lanes', 
                'localField': 'metadata.lane_ref', 
                'foreignField': 'lane_id', 
                'as': 'lane'
            }
        }, {
            '$project': {
                '_id': 0, 
                'timestamp': '$timestamp', 
                'avg_speed_kph': '$avg_speed_kph', 
                'velocity_limit_kph': '$velocity_threshold_kph', 
                'traffic_sensor_id': '$metadata.device_ref', 
                'location': {
                    '$arrayElemAt': [
                        '$location.description', 0
                    ]
                }, 
                'lane': {
                    '$arrayElemAt': [
                        '$lane.description', 0
                    ]
                }, 
                'direction': {
                    '$arrayElemAt': [
                        '$lane.direction', 0
                    ]
                }
            }
        }
    ]
    db_mongo["readings"].aggregate(pipeline, maxTimeMS=60000,allowDiskUse=True)
    tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao

def get_possible_congestions(db_mongo):
    tempo_execucao = time.time()
    pipeline = [
        {
            '$match': {
                'reading_type': 'traffic_count', 
                'count': {
                    '$ne': 0
                }, 
                '$expr': {
                    '$lt': [
                        '$avg_speed_kph', {
                            '$divide': [
                                '$velocity_threshold_kph', 2
                            ]
                        }
                    ]
                }
            }
        }, {
            '$sort': {
                'timestamp': -1
            }
        }, {
            '$group': {
                '_id': '$metadata.device_ref', 
                'last_reading': {
                    '$first': '$$ROOT'
                }
            }
        }, {
            '$lookup': {
                'from': 'locations', 
                'localField': 'last_reading.metadata.location_ref', 
                'foreignField': 'location_id', 
                'as': 'location'
            }
        }, {
            '$lookup': {
                'from': 'lanes', 
                'localField': 'last_reading.metadata.lane_ref', 
                'foreignField': 'lane_id', 
                'as': 'lane'
            }
        }, {
            '$project': {
                '_id': 0, 
                'traffic_sensor_id': '$_id', 
                'timestamp': '$last_reading.timestamp', 
                'count': '$count', 
                'avg_speed_kph': '$last_reading.avg_speed_kph', 
                'velocity_limit_kph': '$last_reading.velocity_threshold_kph', 
                'location': {
                    '$arrayElemAt': [
                        '$location.description', 0
                    ]
                }, 
                'lane': {
                    '$arrayElemAt': [
                        '$lane.lane_type', 0
                    ]
                }, 
                'direction': {
                    '$arrayElemAt': [
                        '$lane.direction', 0
                    ]
                }
            }
        }, {
            '$sort': {
                'traffic_sensor_id': 1
            }
        }
    ]
    db_mongo["readings"].aggregate(pipeline, maxTimeMS=60000,allowDiskUse=True)
    tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao

def get_open_accidents(db_mongo):
    tempo_execucao = time.time()
    pipeline = [
        {
            '$match': {
                'incident_type': 'accident', 
                'status': 'open'
            }
        }, {
            '$lookup': {
                'from': 'locations', 
                'localField': 'metadata.location_ref', 
                'foreignField': 'location_id', 
                'as': 'location'
            }
        }, {
            '$lookup': {
                'from': 'lanes', 
                'localField': 'metadata.lane_ref', 
                'foreignField': 'lane_id', 
                'as': 'lane'
            }
        }, {
            '$project': {
                '_id': 0, 
                'incident_type': 1, 
                'timestamp': '$timestamp', 
                'location': {
                    '$arrayElemAt': [
                        '$location.description', 0
                    ]
                }, 
                'lane': {
                    '$arrayElemAt': [
                        '$lane.description', 0
                    ]
                }, 
                'direction': {
                    '$arrayElemAt': [
                        '$lane.direction', 0
                    ]
                }, 
                'city': {
                    '$arrayElemAt': [
                        '$location.city', 0
                    ]
                }, 
                'state': {
                    '$arrayElemAt': [
                        '$location.state', 0
                    ]
                }, 
                'device_id': '$metadata.device_ref', 
                'image_url': '$image_url', 
                'status': '$status'
            }
        }
    ]
    db_mongo["readings"].aggregate(pipeline, maxTimeMS=60000,allowDiskUse=True)
    tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao

def get_most_dangerous_location(db_mongo):
    tempo_execucao = time.time()
    pipeline = [
        {
            '$match': {
                'incident_type': 'accident'
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
                'accidents_count': '$count', 
                'description': '$location_info.description', 
                'city': '$location_info.city', 
                'state': '$location_info.state', 
                'intersection_type': '$location_info.intersection_type', 
                'traffic_volume_category': '$location_info.traffic_volume_category'
            }
        }
    ]
    db_mongo["readings"].aggregate(pipeline, maxTimeMS=60000,allowDiskUse=True)
    tempo_execucao = time.time() - tempo_execucao
    return tempo_execucao

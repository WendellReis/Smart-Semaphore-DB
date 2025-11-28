from datetime import datetime, timedelta, timezone
from faker import Faker
import json
import random

from models.location import Location
from models.lane import Lane
from models.device import TrafficLight, TrafficSensor, Camera

LOG_PATH = 'log'
SEED = 1234
LOCATIONS = 15
READINGS_PER_DEVICE = 1000
CAMERA_PROB = 0.2
TRAFFIC_SENSOR_PROB = 1

INTERSECTION_REFERENCE_DATA = [
    {
        "intersection_type": "T-junction",
        "num_lanes": 4,
        "num_traffic_lights": 4
    },
    {
        "intersection_type": "four_way_perpendicular",
        "num_lanes": 4,
        "num_traffic_lights": 4
    },
    {
        "intersection_type": "rotary_with_signal",
        "num_lanes": 5,
        "num_traffic_lights": 4
    },
    {
        "intersection_type": "y_junction",
        "num_lanes": 3,
        "num_traffic_lights": 3
    },
    {
        "intersection_type": "pedestrian_priority",
        "num_lanes": 4,
        "num_traffic_lights": 4
    }
]

TRAFFIC_REFERENCE_LEVELS = ['low','medium','high']

MODEL_SPECS = {
    "edge_gateway": ["SmartCTL X1", "EdgeBox Pro", "Gateway IoT-500"],
    "traffic_light": ["PhaseController M1", "Actuator 2000", "LED Light Hub"],
    "traffic_sensor": ["Loop Detector v3", "Radar 4D", "IR Sensor E1"],
    "camera": ["Cam-Traffic G18", "Vision Sensor V2", "SONY G95 PRO"]
}

STATUS = ["online","offline","maintenance"]
TRAFFIC_PHASES = ["P1", "P2", "P3", "P4", "P5"]

DIRECTIONS = ["Sentido Norte", "Sentido Sul", "Sentido Leste", "Sentido Oeste"]
LANE_TYPES = ["Fluxo Principal", "Faixa de Giro à Esquerda", "Faixa de Ônibus", "Acesso"]

RESOLUTION = ["480p","720p","1080p","1440p","4K"]
FRAMERATE = [24,30,45,50,60]

ML_MODELS_GATEWAY = [
    "AdaptiveFlow_Predictor_v3.1.2",
    "TimeSeries_TrafficOptimizer_v2.0.5",
    "QLearning_PhaseScheduler_v1.9.0",
    "DynamicCycle_Allocator_v4.0.1",
    "Reinforcement_TrafficLogic_v4.5.0"
]

CONTROL_MODES = ["adaptative","fixed"]

VIEW_ANGLE_DEGREES = [30,45,60,75,90,120,150,180,240,360]
IMAGE_STORAGE_POLICY = ["cloud_only","local_cache"]

SAMPLING_RATE_S = [5,10,15,20,25,30,35,40,45,50,55,60]
DETECTION_METHOD = ["radar","camera_based"]
VELOCITY_THRESHOLD = [30,40,50,60,80,90,100,110,120]

INCIDENTS_TYPES = ['accident','traffic_jam','congestion']

END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=7)

def generateIncident():
    return random.choice(INCIDENTS_TYPES)

def generateControlMode():
    return random.choice(CONTROL_MODES)

def generateVelocityThresholdKph():
    return random.choice(VELOCITY_THRESHOLD)

def generateDetectionMethod():
    return random.choice(DETECTION_METHOD)

def generateSamplingRate():
    return random.choice(SAMPLING_RATE_S)

def generateImageStoragePolicy():
    return random.choice(IMAGE_STORAGE_POLICY)

def generateViewAngleDegrees():
    return random.choice(VIEW_ANGLE_DEGREES)

def generateMlModel(device_type):
    if device_type == "edge_gateway":
        return random.choice(ML_MODELS_GATEWAY)
    return "Unknown Model"

def generateSeconds():
    return random.randint(5,90)

def generateResolution():
    return random.choice(RESOLUTION)

def generateFramerate():
    return random.choice(FRAMERATE)

def generateModel(device_type):
    if device_type in MODEL_SPECS:
        return random.choice(MODEL_SPECS[device_type])
    return "Unknown Model"

def generateFirmwareVersion():
    major = random.randint(1, 4)
    minor = random.randint(0, 9)
    patch = random.randint(1, 20)
    
    return f"{major}.{minor}.{patch}"

def generateRandomTimestamp(start_date, end_date):
    time_between_dates = end_date - start_date
    seconds_between_dates = int(time_between_dates.total_seconds())
    
    random_seconds = random.randrange(seconds_between_dates)
    
    random_datetime = start_date + timedelta(seconds=random_seconds)

    return random_datetime.astimezone(timezone.utc).isoformat()

def generateStatus():
    return random.choice(STATUS)

def generateTrafficPhase():
    return random.choice(TRAFFIC_PHASES)

def generateColor():
    return random.choice(['green','red','yellow'])

def generateBool(prob):
    chance = random.random()
    return chance <= prob

def generateLocations(size):
    fake = Faker('pt_BR')

    locations = []
    prefx = 'LOC-'
    city = 'Leopoldina'
    state = 'Minas Gerais'

    for i in range(size):
        if i+1 < 10:
            location_id = prefx + '00' + str(i+1)
        elif i+1 < 100:
            location_id = prefx + '0' + str(i+1)
        else:
            location_id = prefx + str(i+1)

        description = fake.street_address()
        latitude = random.uniform(-90.0, 90.0)
        longitude = random.uniform(-180.0, 180.0)

        intersection = random.choice(INTERSECTION_REFERENCE_DATA)
        intersection_type = intersection['intersection_type']
        num_lanes = intersection['num_lanes']
        traffic_volume_category = random.choice(TRAFFIC_REFERENCE_LEVELS)

        locations.append(
            Location(
                location_id=location_id,
                description=description,
                city=city,
                state=state,
                longitude=longitude,
                latitude=latitude,
                intersection_type=intersection_type,
                num_lanes=num_lanes,
                traffic_volume_category=traffic_volume_category
            ).to_mongo_document()
        )
    
    return locations

def generateDevicesAndLanes(locations):
    fake = Faker('pt_BR')
    devices = []
    lanes = []

    for l in locations:
        # Gera semáforos do cruzamento
        for t in INTERSECTION_REFERENCE_DATA:
            if t['intersection_type'] == l['intersection_type']:
                quant = t['num_traffic_lights']
                break
        
        cam_count = 1
        sensor_count = 1
        phase = generateTrafficPhase() # Todos os semáforos de um mesmo cruzamento estão na mesma fase
        for i in range(1,quant+1):
            lane_id = f'LNE-{l['location_id'].replace("LOC-","")}-0{i}'
            lanes.append(
                Lane(
                    lane_id=lane_id,
                    direction=random.choice(DIRECTIONS),
                    lane_type=random.choice(LANE_TYPES),
                    description=fake.street_address(),
                    location_ref=l['location_id']
                ).to_mongo_document()
            )
        

            devices.append(
                TrafficLight(
                    device_id=f'SEM-{l['location_id'].replace("LOC-","")}-0{i}',
                    location_ref=l['location_id'],
                    model=generateModel('traffic_light'),
                    firmware_version=generateFirmwareVersion(),
                    status=generateStatus(),
                    last_check_in=generateRandomTimestamp(START_DATE, END_DATE),
                    phase_id=phase,
                    lane_ref=lane_id,
                    default_green_s=generateSeconds(),
                    default_yellow_s=generateSeconds(),
                    default_red_s=generateSeconds(),
                    min_green_s=generateSeconds(),
                    min_red_s=generateSeconds(),
                    pedestrian_button_active=generateBool(0.5)
                ).to_mongo_document()
            )

            if generateBool(CAMERA_PROB):
                devices.append(
                    Camera(
                        device_id=f'CAM-{l['location_id'].replace("LOC-","")}-0{cam_count}',
                        location_ref=l['location_id'],
                        model=generateModel("camera"),
                        firmware_version=generateFirmwareVersion(),
                        status=generateStatus(),
                        last_check_in=generateRandomTimestamp(START_DATE,END_DATE),
                        resolution=generateResolution(),
                        framerate=generateFramerate(),
                        view_angle_degrees=generateViewAngleDegrees(),
                        ml_detection_enabled=generateBool(0.5),
                        image_storage_policy=generateImageStoragePolicy(),
                        lane_ref=lane_id, # Mesma lane do semáforo
                    ).to_mongo_document()
                )
                cam_count+=1
            

            if generateBool(TRAFFIC_SENSOR_PROB):
                devices.append(
                    TrafficSensor(
                        device_id=f'TRS-{l['location_id'].replace("LOC-","")}-0{sensor_count}',
                        location_ref=l['location_id'],
                        model=generateModel("traffic_sensor"),
                        firmware_version=generateFirmwareVersion(),
                        status=generateStatus(),
                        last_check_in=generateRandomTimestamp(START_DATE,END_DATE),
                        sampling_rate_s=generateSamplingRate(),
                        lane_ref=lane_id, # Mesma lane do semáforo
                        detection_method=generateDetectionMethod(),
                        velocity_threshold_kph=generateVelocityThresholdKph()
                    ).to_mongo_document()
                )
                sensor_count+=1
    
    return devices,lanes
        
def generateReadings(devices):
    readings = []

    for d in devices:
        incident_count = {}
        for i in range(1,READINGS_PER_DEVICE+1):
            if d['location_ref'] not in incident_count:
                incident_count[d['location_ref']] = 0

            reading = {}
            reading["timestamp"] = generateRandomTimestamp(START_DATE,END_DATE)
            metadata = {
                'device_ref': d['device_id'],
                'location_ref': d['location_ref'],
                'lane_ref': d['lane_ref']
            }

            type = d['device_type']
            if type == 'traffic_light':
                reading['reading_type'] = 'status_change'
                reading['current_state'] = generateColor()
                reading['phase_duration'] = generateSeconds()
            elif type == 'traffic_sensor':
                reading['reading_type'] = 'traffic_count'
                reading['count'] = random.randint(0,50)
                if reading['count'] == 0:
                    reading['avg_speed_kph'] = 0
                else:
                    reading['avg_speed_kph'] = random.randint(1,140)
                reading['velocity_threshold_kph'] = d['config']['velocity_threshold_kph']
            elif type == 'camera':
                reading['reading_type'] = 'incident_report'
                reading['incident_type'] = generateIncident()
                reading['status'] = random.choice(['open','resolved'])
                reading['image_url'] = (
                    f"s://incidents/INC-{d['location_ref'].replace('LOC-', '')}-"
                    f"{incident_count[d['location_ref']] + 1}.png"
                )
                incident_count[d['location_ref']]+=1
            
            reading['metadata'] = metadata
            readings.append(reading)

    return readings

def saveData(filename,data):
    with open(f'{LOG_PATH}/{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)

if __name__ == "__main__":
    Faker.seed(SEED)
    random.seed(SEED)

    locations = generateLocations(LOCATIONS)
    devices,lanes = generateDevicesAndLanes(locations)
    readings = generateReadings(devices)

    saveData('locations',locations)
    saveData('lanes',lanes)
    saveData('devices',devices)
    saveData('readings',readings)

    print(f'📥 Locations Gerados: {len(locations)}.')
    print(f'📥 Lanes Gerados: {len(lanes)}.')
    print(f'📥 Devices Gerados: {len(devices)}.')
    print(f'📥 Readings Gerados: {len(readings)}.')
    print(f'💾 Total Documentos Gerados: {len(locations)+len(devices)+len(readings)}')
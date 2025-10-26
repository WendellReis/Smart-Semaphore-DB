from datetime import datetime, timedelta, timezone
from faker import Faker
import json
import random

from models.location import Location
from models.device import EdgeGateway, TrafficLight, TrafficSensor, Camera

SEED = 1234
LOCATIONS = 10
READINGS = 4000

INTERSECTION_REFERENCE_DATA = [
    {
        "intersection_type": "T-junction",
        "num_lanes": 4,
        "num_traffic_lights": 4
    },
    {
        "intersection_type": "four_way_perpendicular",
        "num_lanes": 6,
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

def generateLocations(size):
    fake = Faker('pt_BR')

    locations = []
    prefx = 'LOC-'
    city = 'Leopoldina'
    state = 'Minas Gerais'

    for i in range(size):
        if i < 10:
            location_id = prefx + '00' + str(i+1)
        elif i < 100:
            location_id = prefx + '0' + str(i+1)
        else:
            location_id = prefx + str(i+1)

        description = fake.street_address()
        latitude = random.uniform(-90.0, 90.0)
        longitude = random.uniform(-180.0, 180.0)
        coordinates = [latitude,longitude]

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
                coordinates=coordinates,
                intersection_type=intersection_type,
                num_lanes=num_lanes,
                traffic_volume_category=traffic_volume_category
            ).to_mongo_document()
        )
    
    return locations
        
if __name__ == "__main__":
    Faker.seed(SEED)

    locations = generateLocations(LOCATIONS)

    print(locations)
    pass
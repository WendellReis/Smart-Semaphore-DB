from datetime import datetime, timedelta, timezone
from faker import Faker
import json
import random

from models.location import Location
from models.device import EdgeGateway, TrafficLight, TrafficSensor, Camera

SEED = 1234

if __name__ == "__main__":
    fake = Faker('pt_BR')
    print(fake.name())
    pass
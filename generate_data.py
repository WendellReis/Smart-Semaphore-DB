import random
from faker import Faker

SEED = 1234

if __name__ == "__main__":
    fake = Faker('pt_BR')
    print(fake.name())
    pass
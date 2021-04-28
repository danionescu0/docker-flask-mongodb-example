from faker import Faker
from faker.providers import geo
from faker.providers import company


faker = Faker("en_US")
faker.add_provider(geo)
print(faker.longitude())
print(faker.latitude())
print(faker.location_on_land())

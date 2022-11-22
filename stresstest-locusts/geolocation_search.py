from locust import HttpUser, TaskSet, task
from faker import Faker


class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000

    @task
    class GeolocationStresstest(TaskSet):
        def __init__(self, parent):
            super().__init__(parent)
            self.__faker = Faker("en_US")

        def on_start(self):
            self.token = self.login()
            self.client.headers = {"Authorization": "Bearer " + self.token}

        def login(self):
            response = self.client.post(
                "/login", data={"username": "admin", "password": "secret"}
            )
            return response.headers["jwt-token"]

        @task(1)
        def add_location(self):
            coordonates = self.__faker.location_on_land()
            data = {
                "lat": coordonates[0],
                "lng": coordonates[1],
                "name": coordonates[2],
            }
            self.client.post("/location", data)

        @task(2)
        def search(self):
            self.client.get(
                "/location/{0}/{1}".format(
                    self.__faker.latitude(), self.__faker.longitude()
                )
            )

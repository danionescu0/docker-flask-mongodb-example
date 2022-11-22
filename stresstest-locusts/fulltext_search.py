from locust import HttpUser, TaskSet, task
from faker import Faker


class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000
    auth = ("admin", "changeme")

    @task
    class FulltextSearchStresstest(TaskSet):
        def __init__(self, parent):
            super().__init__(parent)
            self.__faker = Faker("en_US")

        @task(1)
        def add_random_text(self):
            data = {"expression": self.__faker.text()}
            self.client.put("/fulltext", data, auth=RegistredUser.auth)

        @task(2)
        def search(self):
            self.client.get("/search/" + self.__faker.text(), auth=RegistredUser.auth)

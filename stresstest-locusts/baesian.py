from random import randrange

from locust import HttpUser, TaskSet, task


class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000

    @task
    class BaesianStresstest(TaskSet):
        @task(1)
        def create_item(self):
            id = self.__get_item_id()
            url = "/item/{0}".format(id)
            self.client.post(url, {"name": "item_{0}".format(id)})

        @task(2)
        def add_vote(self):
            item_id = self.__get_item_id()
            user_id = self.__get_user_id()
            url = "/item/vote/{0}".format(item_id)
            self.client.put(url, {"mark": randrange(0, 10), "userid": user_id})

        @task(3)
        def get_by_id(self):
            self.client.get("/item/{0}".format(self.__get_item_id()))

        def __get_item_id(self) -> int:
            return randrange(10, 50)

        def __get_user_id(self) -> int:
            return randrange(1, 3)

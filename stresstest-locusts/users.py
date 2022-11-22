from random import randrange

from locust import HttpUser, TaskSet, task


class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000

    @task
    class CrudStresstest(TaskSet):
        def __get_random_user(self):
            userid = str(randrange(0, 10000))
            username = "testuser_{0}".format(userid)
            email = "some-email{0}@yahoo.com".format(userid)

            return userid, username, email

        @task(1)
        def add_user(self):
            user_data = self.__get_random_user()
            user = {
                "id": user_data[0],
                "name": user_data[1],
                "email": user_data[2],
            }
            self.client.put("/users/" + user_data[0], user)

        @task(2)
        def update_user(self):
            user_data = self.__get_random_user()
            user = {
                "id": user_data[0],
                "name": "upd_" + user_data[1],
                "email": "upd_" + user_data[2],
            }
            self.client.post("/users/" + user_data[0], user)

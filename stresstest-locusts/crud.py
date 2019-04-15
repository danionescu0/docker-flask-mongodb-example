from locust import HttpLocust, TaskSet, task


class CrudStresstest(TaskSet):
    def on_start(self):
        print("Starting tests")

    def on_stop(self):
        print("Tests finished")

    @task(2)
    def index(self):
        self.client.get("/random-list")

    @task(1)
    def profile(self):
        self.client.get("/random-list")


class CrudUsecase(HttpLocust):
    task_set = CrudStresstest
    min_wait = 5000
    max_wait = 9000
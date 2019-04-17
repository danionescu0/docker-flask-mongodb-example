from locust import HttpLocust, TaskSet, task


class CrudStresstest(TaskSet):

    @task(1)
    def add_user(self):
        userid = '4'
        user = {
            'id': userid,
            'email': 'some-email@yahoo.com',
            'name': 'testuser'
        }
        self.client.put('/users/' + userid, user)


class CrudUsecase(HttpLocust):
    task_set = CrudStresstest
    min_wait = 5000
    max_wait = 9000
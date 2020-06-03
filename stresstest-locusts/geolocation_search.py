from random import randrange, uniform

from locust import HttpUser, TaskSet, task

class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000

    @task
    class GeolocationStresstest(TaskSet):
        @task(1)
        def add_location(self):
            coordonates = self.__get_coordonates()
            data = {
                'lat': coordonates[0],
                'lng': coordonates[1],
                'name': 'Some name ' + str(randrange(0, 1000))
            }
            print(data)
            self.client.post('/location', data)

        @task(2)
        def search(self):
            coordonates = self.__get_coordonates()
            self.client.get('/location/{0}/{1}'.format(coordonates[0], coordonates[1]))

        def __get_coordonates(self):
            return round(uniform(-90, 90), 5), round(uniform(-180, 180), 5),
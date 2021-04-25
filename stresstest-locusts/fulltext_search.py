from random import randrange

from locust import HttpUser, TaskSet, task


class RegistredUser(HttpUser):
    min_wait = 5000
    max_wait = 9000
    auth = ("admin", "changeme")

    @task
    class FulltextSearchStresstest(TaskSet):
        @task(1)
        def add_random_text(self):
            data = {
                'expression': self.__generate_random_expression()
            }
            self.client.put('/fulltext', data, auth=RegistredUser.auth)

        @task(2)
        def search(self):
            self.client.get('/search/' + self.__generate_random_expression(2), auth=RegistredUser.auth)

        def __generate_random_expression(self, nr_words=10):
            possible_words = ['some', 'ana', 'it', 'the', 'has', 'who', 'one', 'three', 'table', 'wow', 'super']
            possible_words_len = len(possible_words)
            random_words = [possible_words[randrange(0, possible_words_len)] for i in range(0, nr_words)]
            return ' '.join(random_words)

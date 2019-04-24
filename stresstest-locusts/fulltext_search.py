from random import randrange

from locust import HttpLocust, TaskSet, task


class FulltextSearchStresstest(TaskSet):
    @task(1)
    def add_random_text(self):
        data = {
            'expression': self.__generate_random_expression()
        }
        self.client.put('/fulltext', data)

    @task(2)
    def search(self):
        self.client.get('/search/' +  self.__generate_random_expression(2))

    def __generate_random_expression(self, nr_words=10):
        possible_words = ['some', 'ana', 'it', 'the', 'has', 'who', 'one', 'three', 'table', 'wow', 'super']
        possible_words_len = len(possible_words)
        random_words = [possible_words[randrange(0, possible_words_len)] for i in range(0, nr_words)]
        print(random_words)
        return ' '.join(random_words)


class FulltextUsecase(HttpLocust):
    task_set = FulltextSearchStresstest
    min_wait = 5000
    max_wait = 9000
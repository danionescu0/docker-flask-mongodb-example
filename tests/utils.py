from pymongo import MongoClient


class MongoDb:
    def __init__(self, host='mongodb', dbname='demo') -> None:
        self.__host = host
        self.__dbname = dbname

    def create_connection(self):
        self.__connection = MongoClient(self.__host, 27017)[self.__dbname]

    def get(self, collection: str, query: dict, limit: int = 10, offset: int = 0):
        return list(self.__connection[collection].find(query).limit(limit).skip(offset))

    def upsert(self, collection: str, key, data: dict):
        self.__connection[collection].update_one({'_id': key}, {'$set': data}, upsert=True)

    def delete(self, collection: str, key):
        self.__connection[collection].delete_one({'_id': key})


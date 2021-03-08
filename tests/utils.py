from pymongo import MongoClient


class MongoDb:
    def __init__(self, host="mongodb", dbname="demo") -> None:
        self.__host = host
        self.__dbname = dbname

    def create_connection(self):
        self.__connection = MongoClient(self.__host, 27017)[self.__dbname]

    def set_collection(self, collection):
        self.__collection = collection

    def get(self, query: dict, limit: int = 10, offset: int = 0):
        return list(
            self.__connection[self.__collection].find(query).limit(limit).skip(offset)
        )

    def upsert(self, key, data: dict):
        self.__connection[self.__collection].update_one(
            {"_id": key}, {"$set": data}, upsert=True
        )

    def delete(self, key):
        self.__connection[self.__collection].delete_one({"_id": key})

    def drop(self):
        self.__connection[self.__collection].drop()

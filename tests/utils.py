import uuid
from pymongo import MongoClient, database
from bson.objectid import ObjectId


def get_random_objectid():
    return ObjectId(str(uuid.uuid4())[:12].encode("utf-8"))


class MongoDb:
    def __init__(self, host="mongodb", dbname="demo") -> None:
        self.__host = host
        self.__dbname = dbname

    def create_connection(self):
        self.connection = MongoClient(self.__host, 27017)[self.__dbname]


class Collection:
    def __init__(self, db: database.Database, collection_name: str):
        self.__db = db
        self.__collection = collection_name

    def get(self, query: dict, limit: int = 10, offset: int = 0):
        return list(self.__db[self.__collection].find(query).limit(limit).skip(offset))

    def upsert(self, key, data: dict):
        self.__db[self.__collection].update_one(
            {"_id": key}, {"$set": data}, upsert=True
        )

    def delete(self, key):
        self.__db[self.__collection].delete_one({"_id": key})

    def delete_many(self, index=None, key=None):
        if index and key:
            self.__db[self.__collection].delete_many({index: key})
        else:
            self.__db[self.__collection].delete_many({})

    def drop(self):
        self.__db[self.__collection].drop()

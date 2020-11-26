import json
from typing import Optional, List
from bson import json_util


from pymongo import MongoClient, errors
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
users = MongoClient('mongo', 27017).demo.users


class User(BaseModel):
    userid: str
    email: str
    name: str


@app.put("/users/{item_id}")
def add_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(status_code=500, detail="Email or name not present in user!")
    try:
        users.insert_one({
            '_id': userid,
            'email': user.email,
            'name': user.name
        })
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=500, detail="Duplicate user id!")
    return format_user(users.find_one({'_id': userid}))


@app.post("/users/{item_id}")
def update_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(status_code=500, detail="Email or name must be present in parameters!")
    set = {}
    if user.email is not None:
        set['email'] = user.email
    if user.name is not None:
        set['name'] = user.name
    users.update_one({'_id': userid}, {'$set': set})
    return format_user(users.find_one({'_id': userid}))


@app.get("/users/{item_id}", response_model=User)
def get_user(userid: int):
    user = users.find_one({'_id': userid})
    if None == user:
        raise HTTPException(status_code=404, detail="User not found")
    return format_user(user)


@app.get("/users", response_model=List[User])
def get_users(limit: Optional[int] = 10, offset: Optional[int] = 0):
    user_list = users.find().limit(limit).skip(offset)
    if None == users:
        return []

    extracted = [format_user(data) for data in user_list]
    return extracted


@app.delete("/users/{item_id}", response_model=User)
def delete_user(userid: int):
    user = users.find_one({'_id': userid})
    users.delete_one({'_id': userid})
    return format_user(user)

def format_user(user):
    if user is None:
        return None
    return \
        {'userid': user['_id'],
         'name': user['name'],
         'email': user['email']
         }
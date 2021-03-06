from typing import Optional, List

from pymongo import MongoClient, errors
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr


app = FastAPI()
users = MongoClient("mongodb", 27017).demo.users


class User(BaseModel):
    userid: int
    email: EmailStr
    name: str = Field(..., title="Name of the user", max_length=50)


@app.put("/users/{userid}")
def add_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(
            status_code=500, detail="Email or name not present in user!"
        )
    try:
        users.insert_one({"_id": userid, "email": user.email, "name": user.name})
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=500, detail="Duplicate user id!")
    return format_user(users.find_one({"_id": userid}))


@app.post("/users/{userid}")
def update_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(
            status_code=500, detail="Email or name must be present in parameters!"
        )
    set = {}
    if user.email is not None:
        set["email"] = user.email
    if user.name is not None:
        set["name"] = user.name
    users.update_one({"_id": userid}, {"$set": set})
    return format_user(users.find_one({"_id": userid}))


@app.get("/users/{userid}", response_model=User)
def get_user(userid: int):
    user = users.find_one({"_id": userid})
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


@app.delete("/users/{userid}", response_model=User)
def delete_user(userid: int):
    user = users.find_one({"_id": userid})
    users.delete_one({"_id": userid})
    return format_user(user)


def format_user(user):
    if user is None:
        return None
    return {"userid": user["_id"], "name": user["name"], "email": user["email"]}

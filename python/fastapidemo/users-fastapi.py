from typing import Optional, List
from datetime import datetime

from pymongo import errors
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr


app = FastAPI()
users_async = motor.motor_asyncio.AsyncIOMotorClient("mongodb", 27017).demo.users


class User(BaseModel):
    userid: int
    email: EmailStr
    name: str = Field(..., title="Name of the user", max_length=50)
    birth_date: Optional[datetime]
    country: Optional[str] = Field(..., title="Country of origin", max_length=50)

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d")}


class UpdateUser(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str] = Field(title="Name of the user", max_length=50)
    birth_date: Optional[datetime]
    country: Optional[str] = Field(title="Country of origin", max_length=50)

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d")}


@app.post("/users/{userid}", response_model=User)
async def add_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(
            status_code=500, detail="Email or name not present in user!"
        )
    mongo_user = jsonable_encoder(user)
    mongo_user['_id'] = userid
    try:
        await users_async.insert_one(mongo_user)
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=500, detail="Duplicate user id!")
    db_item = await users_async.find_one({"_id": userid})
    return format_user(db_item)


@app.put("/users/{userid}", response_model=User)
async def update_user(userid: int, user: UpdateUser):
    mongo_user = jsonable_encoder(user)
    mongo_user_no_none = {k: v for k, v in mongo_user.items() if v is not None}
    await users_async.update_one({"_id": userid}, {"$set": mongo_user_no_none})
    return format_user(await users_async.find_one({"_id": userid}))


@app.get("/users/{userid}", response_model=User)
async def get_user(userid: int):
    user = await users_async.find_one({"_id": userid})
    if None == user:
        raise HTTPException(status_code=404, detail="User not found")
    return format_user(user)


@app.get("/users", response_model=List[User])
async def get_users(limit: Optional[int] = 10, offset: Optional[int] = 0):
    items_cursor = users_async.find().limit(limit).skip(offset)
    items = await items_cursor.to_list(limit)
    return list(map(format_user, items))


@app.delete("/users/{userid}", response_model=User)
async def delete_user(userid: int):
    user = await users_async.find_one({"_id": userid})
    await users_async.delete_one({"_id": userid})
    return format_user(user)


def format_user(user: dict) -> dict:
    if user is None:
        return None
    return {
        "userid": user["_id"],
        "name": user["name"],
        "email": user["email"],
        "birth_date": datetime.strptime(user['birth_date'], "%Y-%m-%d"),
        "country": user["country"]
    }

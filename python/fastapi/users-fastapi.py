from typing import Optional, List

from pymongo import errors
import motor.motor_asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr


app = FastAPI()
users_async = motor.motor_asyncio.AsyncIOMotorClient("mongodb", 27017).demo.users


class User(BaseModel):
    userid: int
    email: EmailStr
    name: str = Field(..., title="Name of the user", max_length=50)


@app.post("/users/{userid}")
async def add_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(
            status_code=500, detail="Email or name not present in user!"
        )
    try:
        await users_async.insert_one(
            {"_id": userid, "email": user.email, "name": user.name}
        )
    except errors.DuplicateKeyError as e:
        raise HTTPException(status_code=500, detail="Duplicate user id!")
    db_item = await users_async.find_one({"_id": userid})
    return format_user(db_item)


@app.put("/users/{userid}")
async def update_user(userid: int, user: User):
    if user.email is None and user.name is None:
        raise HTTPException(
            status_code=500, detail="Email or name must be present in parameters!"
        )
    updated_user = {}
    if user.email is not None:
        updated_user["email"] = user.email
    if user.name is not None:
        updated_user["name"] = user.name
    await users_async.update_one({"_id": userid}, {"$set": updated_user})
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


def format_user(user):
    if user is None:
        return None
    return {"userid": user["_id"], "name": user["name"], "email": user["email"]}

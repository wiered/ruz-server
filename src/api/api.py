"""This is api module.

This module contains web api.
"""

__all__ = ["app"]
__version__ = "1.0"
__author__ = "Wiered"

from datetime import datetime
import os
from typing import List

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from db import DB
import models

app = FastAPI()
db = DB(
    os.environ.get("DB_NAME"),
    os.environ.get("DB_USER"),
    os.environ.get("DB_HOST"),
    os.environ.get("DB_PASSWORD"),
    os.environ.get("DB_PORT")
    )

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

# ========================
# Exists
@app.get("/exists/user")
async def isUserKnown(request: Request, id: int):
    return db.isUserKnown(id)

@app.get("/exists/group")
async def isGroupInDB(request: Request, id: int):
    return db.isGroupInDB(id)

@app.get("/exists/week")
async def isWeekInDB(request: Request, group_id: int, date: str):
    return db.isWeekInDB(group_id, date)

@app.get("/exists/day")
async def isDayInDB(request: Request, group_id: int, date: str):
    return db.isDayInDB(group_id, date)

@app.get("/exists/range")
async def isDateRangeInDB(request: Request, group_id: int, start: str, end: str):
    return db.isDateRangeInDB(group_id, start, end)

# ========================
# User
@app.get("/user")
async def getUser(request: Request, id: int):
    if not db.isUserKnown(id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    return db.getUser(id)

@app.post("/user")
async def addUser(request: Request, user: models.User):
    if db.isUserKnown(user.id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User already exists"}
        )

    db.addUser(user.id, user.group_id, user.group_name, user.sub_group, user.is_premium)

    return JSONResponse(
        content={"message": "User added"},
        status_code=status.HTTP_200_OK
    )

@app.put("/user")
async def updateUser(request: Request, user: models.User):
    if not db.isUserKnown(user.id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    db.updateUser(**user.json())

    return JSONResponse(
        content={"message": "User updated"},
        status_code=status.HTTP_200_OK
    )

@app.put("/user/group")
async def updateUserGroup(request: Request, user: models.User):
    if not db.isUserKnown(user.id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    db.updateUserGroup(user.id, user.group_id, user.group_name, user.sub_group)

    return JSONResponse(
        content={"message": "User updated"},
        status_code=status.HTTP_200_OK
    )

@app.delete("/user")
async def deleteUser(request: Request, id: int):
    if not db.isUserKnown(id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    db.deleteUser(id)

    return JSONResponse(
        content={"message": "User deleted"},
        status_code=status.HTTP_200_OK
    )

# ========================
# Group
@app.get("/group")
async def getGroup(request: Request, id: int):
    if not db.isGroupInDB(id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    return db.getGroup(id)

@app.get("/groups")
async def getGroups(request: Request):
    return db.getGroups()

@app.post("/group")
async def addGroup(request: Request, group: models.Group):
    if db.isGroupInDB(group.group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group already exists"}
        )

    db.addGroup(group.group_id, group.group_name)

    return JSONResponse(
        content={"message": "Group added"},
        status_code=status.HTTP_200_OK
    )

@app.get("/group/user_count")
async def getUserCountByGroup(request: Request, id: int):
    if not db.isGroupInDB(id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    return db.getUserCountByGroup(id)

@app.delete('/group')
async def deleteGroup(request: Request, id: int):
    if not db.isGroupInDB(id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    db.deleteGroup(id)

    return JSONResponse(
        content={"message": "Group deleted"},
        status_code=status.HTTP_200_OK
    )

# ========================
# Schedule
@app.get("/schedule")
async def getSchedule(request: Request, user_id: int):
    if not db.isUserKnown(user_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    user = db.getUser(user_id)
    group_id = user.group_id

    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    return db.getSchedule(group_id)

@app.get("/schedule/week")
async def getScheduleForWeek(request: Request, user_id: int, date: str):
    if not db.isUserKnown(user_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    user = db.getUser(user_id)
    group_id = user.group_id
    sub_group = user.sub_group
    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    if not db.isWeekInDB(group_id, date):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Week doesn't exist"}
        )

    return db.getScheduleForWeek(group_id, sub_group, date)

@app.get("/schedule/day")
async def getScheduleForDay(request: Request, user_id: int, date: str):
    if not db.isUserKnown(user_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    user = db.getUser(user_id)
    group_id = user.group_id
    sub_group = user.sub_group

    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    return db.getScheduleForDay(group_id, sub_group, date)

@app.get("/schedule/range")
async def getScheduleInRange(request: Request, user_id: int, start: str, end: str):
    if not db.isUserKnown(user_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "User doesn't exist"}
        )

    user = db.getUser(user_id)
    group_id = user.group_id
    sub_group = user.sub_group

    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    if not db.isDateRangeInDB(group_id, start, end):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Date range doesn't exist"}
        )

    return db.getScheduleInRange(group_id, start, end, sub_group)

@app.get("/ping")
async def ping(request: Request):
    server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    return {"server_time": server_time}

@app.post("/schedule")
async def addScheduleToDB(request: Request, schedule: list[models.LessonWEB]):
    group_id = schedule[0].group_id
    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    db.addScheduleToDB(group_id, schedule)
    return JSONResponse(
        content={"message": "Schedule added"},
        status_code=status.HTTP_200_OK
    )

@app.post("/schedule/lesson")
def addLessonToSchedule(request: Request, lesson: models.LessonWEB):
    group_id = lesson.group_id
    if not db.isGroupInDB(group_id):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Group doesn't exist"}
        )

    db.addLessonToSchedule(lesson)
    return JSONResponse(
        content={"message": "Lesson added"},
        status_code=status.HTTP_200_OK
    )

@app.delete("/schedule")
async def deleteScheduleFromDB(request: Request, group_id: int):
    return db.deleteScheduleFromDB(group_id)

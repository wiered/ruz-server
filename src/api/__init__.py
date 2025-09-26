from fastapi import APIRouter
from api.groups import router as groups_router
from api.users import router as users_router
from api.lecturers import router as lecturers_router
from api.kind_of_work import router as kind_of_work_router
from api.discipline import router as discipline_router
from api.auditorium import router as auditorium_router
from api.lesson import router as lesson_router

api_router = APIRouter()
api_router.include_router(groups_router, tags=["group"])
api_router.include_router(users_router, tags=["user"])
api_router.include_router(lecturers_router, tags=["lecturer"])
api_router.include_router(kind_of_work_router, tags=["kind_of_work"])
api_router.include_router(discipline_router, tags=["discipline"])
api_router.include_router(auditorium_router, tags=["auditorium"])
api_router.include_router(lesson_router, tags=["lesson"])

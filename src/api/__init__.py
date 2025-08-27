from fastapi import APIRouter
from api.groups import router as groups_router
from api.users import router as users_router

api_router = APIRouter()
api_router.include_router(groups_router, tags=["group"])
api_router.include_router(users_router, tags=["user"])


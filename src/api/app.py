import os
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, Security
from api.security import require_api_key
from api import api_router
from logging_config import LOGGING_CONFIG

# Setup logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.get("/public")
async def public():
    logger.info("public ok")
    return {"message": "public ok"}

@app.get("/protected")
async def protected(_api_key: str = Security(require_api_key)):
    logger.info("protected ok")
    return {"message": "protected ok"}

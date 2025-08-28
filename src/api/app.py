import os
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, Security
from api.security import require_api_key
from api import api_router

from logging_config import LOGGING_CONFIG, ColoredFormatter

# Setup logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if type(handler) is logging.StreamHandler:
        handler.setFormatter(ColoredFormatter('%(levelname)s:     %(asctime)s %(name)s - %(message)s'))

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

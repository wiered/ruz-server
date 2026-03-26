import os
import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request, Security
from ruz_server.api.security import require_api_key
from ruz_server.api import api_router

from ruz_server.logging_config import LOGGING_CONFIG, ColoredFormatter

# Setup logging
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(api_router, prefix="/api", dependencies=[Security(require_api_key)])

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.get("/public")
async def public():
    logger.info("public ok")
    return {"message": "public ok"}

@app.get("/protected")
async def protected(_: None = Security(require_api_key)):
    logger.info("protected ok")
    return {"message": "protected ok"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

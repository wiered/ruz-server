import os
import logging

from fastapi import FastAPI, Request, Security
from api.security import require_api_key

logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(name)s %(message)s",
    level=logging.INFO,
)

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.get("/public")
async def public():
    return {"message": "public ok"}

@app.get("/protected")
async def protected(_api_key: str = Security(require_api_key)):
    # сюда попадём только с валидным ключом
    return {"message": "protected ok"}

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

app = FastAPI()

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

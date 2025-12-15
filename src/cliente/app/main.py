from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.endpoints import router

app = FastAPI()

# Static and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API routes
app.include_router(router)

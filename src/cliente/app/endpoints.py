from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.gateway_client import gateway

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@router.get("/devices")
def get_devices():
    devices = gateway.get_devices()
    return {"devices": devices}

@router.post("/command")
def send_command(cmd: dict):
    status = gateway.send_command(
        cmd["actuatorId"],
        cmd["command"]
    )
    return {"status": status}
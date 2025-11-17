from fastapi import APIRouter
from app.ds.node import Node

router = APIRouter()
node = Node()  # example; adapt to your project

@router.get("/status")
def get_status():
    return node.get_state()

@router.post("/send")
def send_message(data: dict):
    return node.send(data)

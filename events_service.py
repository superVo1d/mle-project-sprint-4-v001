from fastapi import FastAPI
from pydantic import BaseModel
import logging
from typing import List, Dict

app = FastAPI(title="Events Service")

logger = logging.getLogger("uvicorn.error")

class EventStore:
    def __init__(self):
        self.store: Dict[int, List[int]] = {}

    def add_item(self, user_id: int, item_id: int):
        """
        Добавляет item_id в историю пользователя user_id.
        Если пользователь новый, сначала создает его.
        """
        if user_id not in self.store:
            self.store[user_id] = []

        self.store[user_id].append(item_id)

    def get_items(self, user_id: int) -> List[int]:
        """
        Возвращает историю пользователя user_id
        """
        if user_id in self.store:
            return self.store[user_id]

        return []


event_store = EventStore()

class ItemAddRequest(BaseModel):
    user_id: int
    item_id: int

@app.post("/add")
async def add_item(request: ItemAddRequest):
    """
    Добавляет item_id в историю пользователя user_id
    """
    event_store.add_item(request.user_id, request.item_id)

    return {"message": f"Item {request.item_id} added to user {request.user_id}."}

@app.get("/get", response_model=List[int])
async def get_items(user_id: int) -> List[int]:
    """
    Возвращает историю пользователя user_id
    """
    items = event_store.get_items(user_id)

    return items

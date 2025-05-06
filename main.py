from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from auth import auth_router
from firebase import db

app = FastAPI()

app.include_router(auth_router)

class Item(BaseModel):
    text: str
    is_done: bool = False


items = []

@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/items")
def create_item(item: Item) -> list[Item]:
    items.append(item)
    return items


@app.get("/items", response_model=list[Item])
def list_items(limit: int = 10) -> list[Item]:
    return items[0:limit]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

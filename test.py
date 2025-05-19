from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

test_router = APIRouter(prefix="/test", tags=["Testing"])

class Item(BaseModel):
    text: str
    is_done: bool = False


items = []

@test_router.get("/")
def root():
    return {"message": "Hello World"}


@test_router.post("/items")
def create_item(item: Item) -> list[Item]:
    items.append(item)
    return items


@test_router.get("/items", response_model=list[Item])
def list_items(limit: int = 10) -> list[Item]:
    return items[0:limit]


@test_router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

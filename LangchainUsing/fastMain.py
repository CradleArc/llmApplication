from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
@app.get("/protected")
async def protected(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items/{item_id}")
def create_item(item_id: int):
    return {"item_id": item_id}

@app.put("/items/{item_id}")
def update_item(item_id: int):
    return {"message": f"Item {item_id} has been updated."}

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = 10.5

@app.post("/items/")
def create_item(item: Item):
    return item

class ResponseItem(BaseModel):
    item_id: int
    name: str

@app.post("/items/response-model/")
def create_item_response(item: Item):
    return ResponseItem(item_id=1, name=item.name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
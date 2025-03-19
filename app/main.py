from fastapi import Depends, FastAPI
from typing import Annotated


from app.infrastructure.database import create_db_and_tables
from app.dependencies import verify_token

app = FastAPI(title="API")


@app.get("/")
async def health_check():
    return {"message": "It's fine"}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(verify_token)]):
    return {"token": token}

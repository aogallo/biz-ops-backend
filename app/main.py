from fastapi import Depends, FastAPI
from typing import Annotated


from app.infrastructure.database import create_db_and_tables
from app.dependencies import oauth2_scheme
from app.api.routes import auth

app = FastAPI(title="API")


@app.get("/")
async def health_check():
    return {"message": "It's fine"}


@app.on_event("startup")
def on_startup():
    # create_db_and_tables()
    pass


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


app.include_router(auth.router)

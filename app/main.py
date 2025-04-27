from fastapi import FastAPI
from app.core.config import settings
from app.infrastructure.database import create_db_and_tables
from app.routes import user_routes, vendor_routes

app = FastAPI(
    title=settings.API_TITLE, version=settings.API_VERSION, debug=settings.DEBUG
)


@app.get("/")
async def health_check():
    return {"message": "It's fine", "version": settings.API_VERSION}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(router=user_routes.router)
app.include_router(router=vendor_routes.router)

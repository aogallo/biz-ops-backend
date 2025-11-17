from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.infrastructure.database import get_session

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.post("/")
def create_invoice():
    pass

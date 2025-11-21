from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, verify_token
from app.domain.entities.product import Product, ProductCreate
from app.infrastructure.database import get_session
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate, current_user=Depends(get_current_user)
):
    """
    Create a new product.

    Returns the created product.
    """
    try:
        service = ProductService(current_user)
        return service.create_product(product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[Product])
def list_products(current_user=Depends(get_current_user)):
    """
    Get all products.

    Returns a list of all products in the system.
    """
    service = ProductService(current_user)
    return service.list_all_products()

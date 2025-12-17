from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.product.entity import ProductCreate as ProductCreateEntity
from app.internal.product.schema import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
)
from app.internal.product.service import ProductService
from app.schemas.common import PaginationResponse
from app.utils.pagination import calculate_offset

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[
        Depends(verify_token),
    ],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Create a new product.

    Returns the created product.
    """
    try:
        service = ProductService(session, current_user)
        # Convert schema to entity
        product_entity = ProductCreateEntity(**product.model_dump())
        created_product = service.create_product(product_entity)
        return ProductResponse.model_validate(created_product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all products with pagination."""
    offset = calculate_offset(page=page, page_size=limit)

    service = ProductService(session, current_user)
    result = service.list_all_products(offset=offset, limit=limit)

    pagination = PaginationResponse(
        total=result.count,
        page_size=limit,
        page_index=page - 1,
    )

    # Convert entities to response schemas
    products_response = [
        ProductResponse.model_validate(product) for product in result.products
    ]

    return ProductListResponse(
        products=products_response, pagination=pagination
    )

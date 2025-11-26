from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, verify_token
from app.domain.entities.account import AccountCreate as AccountCreateEntity
from app.infrastructure.database import get_session
from app.schemas.account_schema import AccountCreate, AccountResponse
from app.services.account_service import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(verify_token), Depends(get_session)],
)


@router.get("")
def list_accounts(current_user=Depends(get_current_user)):
    """List all accounts"""
    try:
        service = AccountService(current_user)
        return service.list_accounts()
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account: AccountCreate, current_user=Depends(get_current_user)
):
    """
    Create a new account.

    Returns the created account.
    """
    try:
        service = AccountService(current_user)
        # Convert schema to entity
        account_entity = AccountCreateEntity(**account.model_dump())
        created_account = service.create_account(account_entity)
        return AccountResponse.model_validate(created_account)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

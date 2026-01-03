from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user, verify_token
from app.internal.account.entity import AccountCreate as AccountCreateEntity
from app.internal.account.schema import AccountCreate, AccountResponse
from app.internal.account.service import AccountService

router = APIRouter(
    prefix="/organization/{organization_id}/accounts",
    tags=["Accounts"],
    dependencies=[Depends(verify_token)],
)


@router.get("", response_model=list[AccountResponse])
def list_accounts(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """List all accounts"""
    try:
        service = AccountService(session, current_user)
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
    account: AccountCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Create a new account.

    Returns the created account.
    """
    try:
        service = AccountService(session, current_user)
        # Convert schema to entity
        account_entity = AccountCreateEntity(**account.model_dump())
        created_account = service.create_account(account_entity)
        return AccountResponse.model_validate(created_account)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

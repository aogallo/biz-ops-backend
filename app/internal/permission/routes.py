"""Permission and role management API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.internal.permission.schema import (
    PermissionCreate,
    PermissionListResponse,
    PermissionResponse,
    RoleCreate,
    RoleListResponse,
    RolePermissionAssignmentResponse,
    RolePermissionListResponse,
    RoleResponse,
    UserPermissionAssignmentRequest,
    UserPermissionAssignmentResponse,
)
from app.internal.permission.service import PermissionService
from app.internal.user.entity import User

router = APIRouter()


@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Permissions"],
)
def create_permission(
    permission_data: PermissionCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Create a new permission.

    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    return service.create_permission(permission_data)


@router.get(
    "/permissions",
    response_model=PermissionListResponse,
    tags=["Permissions"],
)
def list_permissions(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    List all permissions.

    Returns all available permissions in the system.
    """
    service = PermissionService(session, current_user)
    permissions = service.list_all_permissions()
    return PermissionListResponse(
        permissions=permissions, total=len(permissions)
    )


@router.get(
    "/permissions/{permission_id}",
    response_model=PermissionResponse,
    tags=["Permissions"],
)
def get_permission(
    permission_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get a single permission by ID.
    """
    service = PermissionService(session, current_user)
    return service.get_permission_by_id(permission_id)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Roles"],
)
def create_role(
    role_data: RoleCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Create a new role.

    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    return service.create_role(role_data)


@router.get(
    "/roles",
    response_model=RoleListResponse,
    tags=["Roles"],
)
def list_roles(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    List all roles.

    Returns all available roles in the system.
    """
    service = PermissionService(session, current_user)
    roles = service.list_all_roles()
    return RoleListResponse(roles=roles, total=len(roles))


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    tags=["Roles"],
)
def get_role(
    role_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get a single role by ID.
    """
    service = PermissionService(session, current_user)
    return service.get_role_by_id(role_id)


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Roles"],
)
def delete_role(
    role_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Delete a role.

    Cannot delete system roles.
    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    service.delete_role(role_id)


@router.post(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=RolePermissionAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Role Permissions"],
)
def assign_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Assign a permission to a role.

    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    return service.assign_permission_to_role(role_id, permission_id)


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Role Permissions"],
)
def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Remove a permission from a role.

    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    service.remove_permission_from_role(role_id, permission_id)


@router.get(
    "/roles/{role_id}/permissions",
    response_model=RolePermissionListResponse,
    tags=["Role Permissions"],
)
def get_role_permissions(
    role_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get all permissions assigned to a role.
    """
    service = PermissionService(session, current_user)
    permissions = service.get_role_permissions(role_id)
    return RolePermissionListResponse(
        permissions=permissions, total=len(permissions)
    )


@router.post(
    "/users/{user_id}/permissions",
    response_model=UserPermissionAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User Permissions"],
)
def assign_direct_permission_to_user(
    user_id: UUID,
    assignment_data: UserPermissionAssignmentRequest,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Grant or revoke a direct permission to/from a user.

    Direct permissions override role-based permissions.
    Requires: Super admin access
    """
    service = PermissionService(session, current_user)
    return service.assign_direct_permission_to_user(
        user_id, assignment_data.permission_id, assignment_data.granted
    )


@router.get(
    "/users/{user_id}/permissions",
    response_model=PermissionListResponse,
    tags=["User Permissions"],
)
def get_user_effective_permissions(
    user_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get user's effective permissions (from roles + direct permissions).

    Returns the resolved set of permissions considering:
    1. Direct user permissions (grants and revokes)
    2. Role-based permissions via UserCompanyAccess
    """
    service = PermissionService(session, current_user)
    permissions = service.get_user_effective_permissions(user_id)
    return PermissionListResponse(
        permissions=permissions, total=len(permissions)
    )

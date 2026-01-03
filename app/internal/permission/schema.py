"""Permission and Role API schemas for requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ===================================================================
# Permission Schemas
# ===================================================================


class PermissionCreate(BaseModel):
    """Schema for creating a new permission."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    code: str
    description: str | None = None
    module_name: str | None = Field(
        default=None, alias="moduleName", serialization_alias="moduleName"
    )


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    description: str | None = None
    module_name: str | None = Field(
        default=None, alias="moduleName", serialization_alias="moduleName"
    )


class PermissionResponse(BaseModel):
    """Schema for permission response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    code: str
    description: str | None
    module_name: str | None = Field(
        alias="moduleName", serialization_alias="moduleName"
    )


# ===================================================================
# Role Schemas
# ===================================================================


class RoleCreate(BaseModel):
    """Schema for creating a new role."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    description: str | None = None
    is_system: bool = Field(default=False, serialization_alias="isSystem")


class RoleUpdate(BaseModel):
    """Schema for updating a role."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    description: str | None = None


class RoleResponse(BaseModel):
    """Schema for role response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    description: str | None
    is_system: bool = Field(serialization_alias="isSystem")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime | None = Field(serialization_alias="updatedAt")


class RoleWithPermissionsResponse(RoleResponse):
    """Schema for role response with permissions."""

    permissions: list[PermissionResponse] = []


# ===================================================================
# Role-Permission Assignment Schemas
# ===================================================================


class AssignPermissionRequest(BaseModel):
    """Schema for assigning a permission to a role."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    permission_id: UUID = Field(serialization_alias="permissionId")


class RemovePermissionRequest(BaseModel):
    """Schema for removing a permission from a role."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    permission_id: UUID = Field(serialization_alias="permissionId")


# ===================================================================
# User Permission Schemas
# ===================================================================


class GrantUserPermissionRequest(BaseModel):
    """Schema for granting a direct permission to a user."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: UUID = Field(serialization_alias="userId")
    permission_id: UUID = Field(serialization_alias="permissionId")


class RevokeUserPermissionRequest(BaseModel):
    """Schema for revoking a direct permission from a user."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: UUID = Field(serialization_alias="userId")
    permission_id: UUID = Field(serialization_alias="permissionId")


class CheckPermissionRequest(BaseModel):
    """Schema for checking if a user has a permission."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: UUID = Field(serialization_alias="userId")
    permission_code: str = Field(serialization_alias="permissionCode")


class CheckPermissionResponse(BaseModel):
    """Schema for permission check response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    has_permission: bool = Field(serialization_alias="hasPermission")
    permission_code: str = Field(serialization_alias="permissionCode")


# ===================================================================
# List Response Schemas
# ===================================================================


class PermissionListResponse(BaseModel):
    """Schema for list of permissions response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    permissions: list[PermissionResponse]
    total: int


class RoleListResponse(BaseModel):
    """Schema for list of roles response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    roles: list[RoleResponse]
    total: int


class RolePermissionListResponse(BaseModel):
    """Schema for list of permissions for a role."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    permissions: list[PermissionResponse]
    total: int


# ===================================================================
# Assignment Response Schemas
# ===================================================================


class RolePermissionAssignmentResponse(BaseModel):
    """Schema for role-permission assignment response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    role_id: UUID = Field(serialization_alias="roleId")
    permission_id: UUID = Field(serialization_alias="permissionId")


class UserPermissionAssignmentRequest(BaseModel):
    """Schema for user permission assignment request (grant or revoke)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    permission_id: UUID = Field(serialization_alias="permissionId")
    granted: bool  # True = grant, False = revoke


class UserPermissionAssignmentResponse(BaseModel):
    """Schema for user permission assignment response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: UUID = Field(serialization_alias="userId")
    permission_id: UUID = Field(serialization_alias="permissionId")
    granted: bool

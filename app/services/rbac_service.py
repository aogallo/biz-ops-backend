from app.domain.entities.permission import Permission
from app.domain.entities.role import Role
from app.domain.repositories.permission_repository import PermissionRepository
from app.domain.repositories.role_repository import RoleRepository


class RBACService:
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    def create_role(self, name: str, description: str | None = None) -> Role:
        role = Role(name=name, description=description)
        return self.role_repository.create_role(role)

    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: str | None = None,
    ) -> Permission:
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description,
        )
        return self.permission_repository.create_permission(permission)

    def assign_permission_to_role(
        self, permission_id: int, role_id: int
    ) -> bool:
        return self.permission_repository.assign_permission_to_role(
            permission_id, role_id
        )

    def assign_role_to_user(self, role_id: int, user_auth_id: str) -> bool:
        return self.role_repository.assign_role_to_user(role_id, user_auth_id)

    def check_permission(
        self, user_auth_id: str, resource: str, action: str
    ) -> bool:
        # Get user's roles and check if any role has the required permission
        user = self.role_repository.get_user_by_auth_id(user_auth_id)
        if not user:
            return False

        for role in user.roles:
            for permission in role.permissions:
                if (
                    permission.resource == resource
                    and permission.action == action
                ):
                    return True
        return False

    def get_user_permissions(self, user_auth_id: str) -> list[Permission]:
        user = self.role_repository.get_user_by_auth_id(user_auth_id)
        if not user:
            return []

        permissions = set()
        for role in user.roles:
            permissions.update(role.permissions)
        return list(permissions)

    def get_user_roles(self, user_auth_id: str) -> list[Role]:
        user = self.role_repository.get_user_by_auth_id(user_auth_id)
        if not user:
            return []
        return user.roles

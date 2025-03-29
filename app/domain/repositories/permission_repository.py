from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.permission import Permission

class PermissionRepository(ABC):
    @abstractmethod
    def create_permission(self, permission: Permission) -> Permission:
        pass

    @abstractmethod
    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        pass

    @abstractmethod
    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        pass

    @abstractmethod
    def get_all_permissions(self) -> List[Permission]:
        pass

    @abstractmethod
    def update_permission(self, permission_id: int, permission: Permission) -> Permission:
        pass

    @abstractmethod
    def delete_permission(self, permission_id: int) -> bool:
        pass

    @abstractmethod
    def assign_permission_to_role(self, permission_id: int, role_id: int) -> bool:
        pass

    @abstractmethod
    def remove_permission_from_role(self, permission_id: int, role_id: int) -> bool:
        pass 
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.role import Role

class RoleRepository(ABC):
    @abstractmethod
    def create_role(self, role: Role) -> Role:
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        pass

    @abstractmethod
    def get_role_by_name(self, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    def get_all_roles(self) -> List[Role]:
        pass

    @abstractmethod
    def update_role(self, role_id: int, role: Role) -> Role:
        pass

    @abstractmethod
    def delete_role(self, role_id: int) -> bool:
        pass

    @abstractmethod
    def assign_role_to_user(self, role_id: int, user_auth_id: str) -> bool:
        pass

    @abstractmethod
    def remove_role_from_user(self, role_id: int, user_auth_id: str) -> bool:
        pass 
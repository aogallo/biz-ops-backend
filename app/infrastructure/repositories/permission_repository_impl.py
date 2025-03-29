from typing import List, Optional
from sqlmodel import Session, select
from app.domain.entities.permission import Permission
from app.domain.entities.role import Role
from app.domain.repositories.permission_repository import PermissionRepository

class PermissionRepositoryImpl(PermissionRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_permission(self, permission: Permission) -> Permission:
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        result = self.db.exec(select(Permission).where(Permission.id == permission_id))
        return result.first()

    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        result = self.db.exec(select(Permission).where(Permission.name == name))
        return result.first()

    def get_all_permissions(self) -> List[Permission]:
        result = list(self.db.exec(select(Permission)))
        return result

    def update_permission(self, permission_id: int, permission: Permission) -> Permission:
        db_permission = self.get_permission_by_id(permission_id)
        if db_permission:
            for key, value in permission.dict(exclude_unset=True).items():
                setattr(db_permission, key, value)
            self.db.commit()
            self.db.refresh(db_permission)
        return db_permission

    def delete_permission(self, permission_id: int) -> bool:
        db_permission = self.get_permission_by_id(permission_id)
        if db_permission:
            self.db.delete(db_permission)
            self.db.commit()
            return True
        return False

    def assign_permission_to_role(self, permission_id: int, role_id: int) -> bool:
        permission = self.get_permission_by_id(permission_id)
        role = self.db.exec(select(Role).where(Role.id == role_id)).first()
        if permission and role:
            role.permissions.append(permission)
            self.db.commit()
            return True
        return False

    def remove_permission_from_role(self, permission_id: int, role_id: int) -> bool:
        permission = self.get_permission_by_id(permission_id)
        role = self.db.exec(select(Role).where(Role.id == role_id)).first()
        if permission and role:
            role.permissions.remove(permission)
            self.db.commit()
            return True
        return False 
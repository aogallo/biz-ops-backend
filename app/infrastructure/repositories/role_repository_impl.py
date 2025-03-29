from typing import List, Optional
from sqlmodel import Session, select
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.repositories.role_repository import RoleRepository

class RoleRepositoryImpl(RoleRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_role(self, role: Role) -> Role:
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        result = self.db.exec(select(Role).where(Role.id == role_id))
        return result.first()

    def get_role_by_name(self, name: str) -> Optional[Role]:
        result = self.db.exec(select(Role).where(Role.name == name))
        return result.first()

    def get_all_roles(self) -> List[Role]:
        result = list(self.db.exec(select(Role)))
        return result

    def update_role(self, role_id: int, role: Role) -> Role:
        db_role = self.get_role_by_id(role_id)
        if db_role:
            for key, value in role.dict(exclude_unset=True).items():
                setattr(db_role, key, value)
            self.db.commit()
            self.db.refresh(db_role)
        return db_role

    def delete_role(self, role_id: int) -> bool:
        db_role = self.get_role_by_id(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
            return True
        return False

    def assign_role_to_user(self, role_id: int, user_auth_id: str) -> bool:
        role = self.get_role_by_id(role_id)
        user = self.db.exec(select(User).where(User.auth_id == user_auth_id)).first()
        if role and user:
            user.roles.append(role)
            self.db.commit()
            return True
        return False

    def remove_role_from_user(self, role_id: int, user_auth_id: str) -> bool:
        role = self.get_role_by_id(role_id)
        user = self.db.exec(select(User).where(User.auth_id == user_auth_id)).first()
        if role and user:
            user.roles.remove(role)
            self.db.commit()
            return True
        return False 
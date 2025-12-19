import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password
from app.utils.exceptions import NotFoundException, ValidationException


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        if UserRepository.get_by_username(db, user_data["username"]):
            raise ValidationException("Username already exists")

        if UserRepository.get_by_email(db, user_data["email"]):
            raise ValidationException("Email already exists")

        role = db.query(Role).filter(Role.id == user_data["role_id"]).first()
        if not role:
            raise NotFoundException("Role")

        if "password" in user_data:
            user_data["password_hash"] = hash_password(user_data.pop("password"))

        return UserRepository.create(db, user_data)

    @staticmethod
    def get_user(db: Session, user_id: uuid.UUID) -> User:
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException("User")
        return user

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        role_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        return UserRepository.get_all(
            db, skip=skip, limit=limit, is_active=is_active, role_id=role_id, search=search
        )

    @staticmethod
    def count_users(
        db: Session,
        is_active: Optional[bool] = None,
        role_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        return UserRepository.count(db, is_active=is_active, role_id=role_id, search=search)

    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, update_data: dict) -> User:
        user = UserService.get_user(db, user_id)

        if "username" in update_data and update_data["username"]:
            existing = UserRepository.get_by_username(db, update_data["username"])
            if existing and existing.id != user_id:
                raise ValidationException("Username already exists")

        if "email" in update_data and update_data["email"]:
            existing = UserRepository.get_by_email(db, update_data["email"])
            if existing and existing.id != user_id:
                raise ValidationException("Email already exists")

        if "role_id" in update_data and update_data["role_id"]:
            role = db.query(Role).filter(Role.id == update_data["role_id"]).first()
            if not role:
                raise NotFoundException("Role")

        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        return UserRepository.update(db, user, update_data)

    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> None:
        user = UserService.get_user(db, user_id)
        UserRepository.delete(db, user)

    @staticmethod
    def deactivate_user(db: Session, user_id: uuid.UUID) -> User:
        user = UserService.get_user(db, user_id)
        return UserRepository.update(db, user, {"is_active": False})

    @staticmethod
    def activate_user(db: Session, user_id: uuid.UUID) -> User:
        user = UserService.get_user(db, user_id)
        return UserRepository.update(db, user, {"is_active": True})


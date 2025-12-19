import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.user import User


class UserRepository:
    @staticmethod
    def create(db: Session, user_data: dict) -> User:
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).options(
            joinedload(User.role)
        ).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).options(
            joinedload(User.role)
        ).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).options(
            joinedload(User.role)
        ).filter(User.email == email).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        role_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        query = db.query(User).options(
            joinedload(User.role)
        )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if role_id:
            query = query.filter(User.role_id == role_id)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(
        db: Session,
        is_active: Optional[bool] = None,
        role_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        query = db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if role_id:
            query = query.filter(User.role_id == role_id)

        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.count()

    @staticmethod
    def update(db: Session, user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()


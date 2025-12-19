import uuid
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.config import settings
from app.utils.exceptions import InvalidCredentialsException, InactiveUserException

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()

    if not user.is_active:
        raise InactiveUserException()

    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
    }

def refresh_access_token(db: Session, refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise InvalidCredentialsException("Invalid token type")
        
        user_id = payload.get("sub")
        
        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, TypeError):
            raise InvalidCredentialsException("Invalid user ID format")
        
        user = db.query(User).filter(User.id == user_uuid).first()
        
        if not user:
            raise InvalidCredentialsException("User not found")
        
        if not user.is_active:
            raise InactiveUserException()
        
        return {
            "access_token": create_access_token(str(user.id)),
            "refresh_token": create_refresh_token(str(user.id)),
        }
    except JWTError:
        raise InvalidCredentialsException("Invalid refresh token")

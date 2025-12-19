import uuid
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session, joinedload
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.utils.exceptions import InvalidCredentialsException, NotFoundException
from app.core.permissions import (
    Permission,
    RolePermission,
    PermissionDeniedException,
    require_super_admin,
    require_owner_or_admin,
)

security = HTTPBearer(
    scheme_name="BearerAuth",
    description="Masukkan token JWT kamu di sini. Contoh: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "access":
            raise InvalidCredentialsException("Invalid token type")

        user_id = payload.get("sub")
    except JWTError:
        raise InvalidCredentialsException("Invalid token")

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise InvalidCredentialsException("Invalid user ID format")

    
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_uuid).first()

    if not user:
        raise NotFoundException("User")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise InvalidCredentialsException("User account is inactive")
    return current_user


def get_super_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return require_super_admin(current_user)


def require_permission_dependency(permission: Permission):
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not RolePermission.has_permission(current_user, permission):
            raise PermissionDeniedException(
                f"You don't have permission to {permission.value}"
            )
        return current_user
    
    return permission_checker

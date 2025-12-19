from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_active_user, get_super_admin
from app.core.permissions import Permission, require_owner_or_admin, require_super_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.utils.audit import log_user_action, get_client_ip
from app.utils.response import success_response
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db),
):

    user = UserService.create_user(db, user_data.model_dump())
    
    log_user_action(
        db=db,
        user=current_user,
        action="create",
        target_user_id=user.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("", status_code=status.HTTP_200_OK)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    role_id: Optional[uuid.UUID] = Query(None, description="Filter by role ID"),
    search: Optional[str] = Query(None, description="Search by username or email"),
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db),
):
    users = UserService.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        role_id=role_id,
        search=search,
    )
    
    total = UserService.count_users(
        db=db,
        is_active=is_active,
        role_id=role_id,
        search=search,
    )
    
    if not users or total == 0:
        raise NotFoundException("User")
    
    return success_response(
        data={
            "items": [UserResponse.model_validate(user).model_dump() for user in users],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        message="Users retrieved successfully",
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    target_user = UserService.get_user(db, user_id)
    
    require_owner_or_admin(current_user, str(user_id))
    
    return success_response(
        data=UserResponse.model_validate(target_user).model_dump(),
        message="User retrieved successfully",
    )


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if str(current_user.id) != str(user_id):
        current_user = require_super_admin(current_user)
    
    update_dict = user_data.model_dump(exclude_unset=True)
    user = UserService.update_user(db, user_id, update_dict)
    
    log_user_action(
        db=db,
        user=current_user,
        action="update",
        target_user_id=user.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User updated successfully",
    )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db),
):
    UserService.delete_user(db, user_id)
    
    log_user_action(
        db=db,
        user=current_user,
        action="delete",
        target_user_id=user_id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=None,
        message="User deleted successfully",
    )


@router.post("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db),
):
    user = UserService.deactivate_user(db, user_id)
    
    log_user_action(
        db=db,
        user=current_user,
        action="deactivate",
        target_user_id=user.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User deactivated successfully",
    )


@router.post("/{user_id}/activate", status_code=status.HTTP_200_OK)
def activate_user(
    user_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_super_admin),
    db: Session = Depends(get_db),
):
    user = UserService.activate_user(db, user_id)
    
    log_user_action(
        db=db,
        user=current_user,
        action="activate",
        target_user_id=user.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=UserResponse.model_validate(user).model_dump(),
        message="User activated successfully",
    )

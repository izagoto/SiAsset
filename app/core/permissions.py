from enum import Enum
from typing import List
from fastapi import HTTPException, status
from app.models.user import User
from app.utils.exceptions import BaseAPIException


class Permission(Enum):
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    
    MANAGE_ROLES = "manage_roles"
    VIEW_ROLES = "view_roles"
    
    MANAGE_ASSETS = "manage_assets"
    VIEW_ASSETS = "view_assets"
    
    MANAGE_CATEGORIES = "manage_categories"
    VIEW_CATEGORIES = "view_categories"
    
    MANAGE_LOANS = "manage_loans"
    VIEW_OWN_LOANS = "view_own_loans"
    CREATE_LOAN = "create_loan"
    RETURN_LOAN = "return_loan"
    
    VIEW_AUDIT_LOGS = "view_audit_logs"


class RolePermission:
    
    SUPER_ADMIN_PERMISSIONS = [
        Permission.MANAGE_USERS,
        Permission.VIEW_USERS,
        Permission.MANAGE_ROLES,
        Permission.VIEW_ROLES,
        Permission.MANAGE_ASSETS,
        Permission.VIEW_ASSETS,
        Permission.MANAGE_CATEGORIES,
        Permission.VIEW_CATEGORIES,
        Permission.MANAGE_LOANS,
        Permission.VIEW_OWN_LOANS,
        Permission.CREATE_LOAN,
        Permission.RETURN_LOAN,
        Permission.VIEW_AUDIT_LOGS,
    ]
    
    USER_PERMISSIONS = [
        Permission.VIEW_ASSETS,
        Permission.VIEW_CATEGORIES,
        Permission.VIEW_OWN_LOANS,
        Permission.CREATE_LOAN,
        Permission.RETURN_LOAN,
    ]
    
    @classmethod
    def get_permissions_for_role(cls, role_name: str) -> List[Permission]:
        role_name_lower = role_name.lower()
        
        if role_name_lower == "super_admin" or role_name_lower == "admin":
            return cls.SUPER_ADMIN_PERMISSIONS
        elif role_name_lower == "user":
            return cls.USER_PERMISSIONS
        else:
            return []
    
    @classmethod
    def has_permission(cls, user: User, permission: Permission) -> bool:
        if not user.role:
            return False
        
        user_permissions = cls.get_permissions_for_role(user.role.name)
        return permission in user_permissions

class PermissionDeniedException(BaseAPIException):
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED",
        )


def require_permission(permission: Permission):
    def permission_checker(user: User = None):
        if not user:
            raise PermissionDeniedException("Authentication required")
        
        if not RolePermission.has_permission(user, permission):
            raise PermissionDeniedException(
                f"You don't have permission to {permission.value}"
            )
        
        return user
    
    return permission_checker


def require_super_admin(user: User) -> User:
    if not user.role or user.role.name.lower() not in ["super_admin", "admin"]:
        raise PermissionDeniedException("This action requires Super Admin access")
    return user


def require_owner_or_admin(user: User, resource_owner_id: str) -> User:
    if not user.role or user.role.name.lower() in ["super_admin", "admin"]:
        return user
    
    if str(user.id) != resource_owner_id:
        raise PermissionDeniedException("You can only access your own data")
    
    return user


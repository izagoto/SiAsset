from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_active_user, require_permission_dependency
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.schemas.auth import BaseResponse
from app.services.asset_service import AssetService
from app.utils.audit import log_asset_action, get_client_ip
from app.utils.response import success_response
from app.utils.exceptions import NotFoundException

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/create_asset", status_code=status.HTTP_201_CREATED)
def create_asset(
    asset_data: AssetCreate,
    request: Request,
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_ASSETS)),
    db: Session = Depends(get_db),
):
    asset = AssetService.create_asset(db, asset_data.model_dump())
    
    log_asset_action(
        db=db,
        user=current_user,
        action="create",
        asset_id=asset.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=AssetResponse.model_validate(asset).model_dump(),
        message="Asset created successfully",
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/list_assets", status_code=status.HTTP_200_OK)
def get_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by asset status"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name, code, or serial number"),
    current_user: User = Depends(require_permission_dependency(Permission.VIEW_ASSETS)),
    db: Session = Depends(get_db),
):
    assets = AssetService.get_assets(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        category_id=category_id,
        search=search,
    )
    
    total = AssetService.count_assets(
        db=db,
        status=status,
        category_id=category_id,
        search=search,
    )
    
    if not assets or total == 0:
        raise NotFoundException("Asset")
    
    return success_response(
        data={
            "items": [AssetResponse.model_validate(asset).model_dump() for asset in assets],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        message="Assets retrieved successfully",
    )


@router.get("/{asset_id}/get_asset", status_code=status.HTTP_200_OK)
def get_asset(
    asset_id: uuid.UUID,
    current_user: User = Depends(require_permission_dependency(Permission.VIEW_ASSETS)),
    db: Session = Depends(get_db),
):
    asset = AssetService.get_asset(db, asset_id)
    
    return success_response(
        data=AssetResponse.model_validate(asset).model_dump(),
        message="Asset retrieved successfully",
    )


@router.put("/{asset_id}/update_asset", status_code=status.HTTP_200_OK)
def update_asset(
    asset_id: uuid.UUID,
    asset_data: AssetUpdate,
    request: Request,
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_ASSETS)),
    db: Session = Depends(get_db),
):
    update_dict = asset_data.model_dump(exclude_unset=True)
    asset = AssetService.update_asset(db, asset_id, update_dict)
    
    log_asset_action(
        db=db,
        user=current_user,
        action="update",
        asset_id=asset.id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=AssetResponse.model_validate(asset).model_dump(),
        message="Asset updated successfully",
    )


@router.delete("/{asset_id}/delete_asset", status_code=status.HTTP_200_OK)
def delete_asset(
    asset_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_ASSETS)),
    db: Session = Depends(get_db),
):
    AssetService.delete_asset(db, asset_id)
    
    log_asset_action(
        db=db,
        user=current_user,
        action="delete",
        asset_id=asset_id,
        ip_address=get_client_ip(request),
    )
    
    return success_response(
        data=None,
        message="Asset deleted successfully",
    )

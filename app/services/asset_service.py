import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.asset import Asset
from app.models.asset_category import AssetCategory
from app.repositories.asset_repo import AssetRepository
from app.utils.exceptions import NotFoundException, ValidationException


class AssetService:
    @staticmethod
    def create_asset(db: Session, asset_data: dict) -> Asset:
        if AssetRepository.get_by_code(db, asset_data["asset_code"]):
            raise ValidationException("Asset code already exists")

        if AssetRepository.get_by_serial_number(db, asset_data["serial_number"]):
            raise ValidationException("Serial number already exists")

        category = db.query(AssetCategory).filter(
            AssetCategory.id == asset_data["category_id"]
        ).first()
        if not category:
            raise NotFoundException("Asset Category")

        return AssetRepository.create(db, asset_data)

    @staticmethod
    def get_asset(db: Session, asset_id: uuid.UUID) -> Asset:
        asset = AssetRepository.get_by_id(db, asset_id)
        if not asset:
            raise NotFoundException("Asset")
        return asset

    @staticmethod
    def get_assets(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[Asset]:
        return AssetRepository.get_all(
            db, skip=skip, limit=limit, status=status, category_id=category_id, search=search
        )

    @staticmethod
    def count_assets(
        db: Session,
        status: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        return AssetRepository.count(db, status=status, category_id=category_id, search=search)

    @staticmethod
    def update_asset(db: Session, asset_id: uuid.UUID, update_data: dict) -> Asset:
        asset = AssetService.get_asset(db, asset_id)

        if "serial_number" in update_data and update_data["serial_number"]:
            existing = AssetRepository.get_by_serial_number(db, update_data["serial_number"])
            if existing and existing.id != asset_id:
                raise ValidationException("Serial number already exists")

        if "category_id" in update_data and update_data["category_id"]:
            category = db.query(AssetCategory).filter(
                AssetCategory.id == update_data["category_id"]
            ).first()
            if not category:
                raise NotFoundException("Asset Category")

        return AssetRepository.update(db, asset, update_data)

    @staticmethod
    def delete_asset(db: Session, asset_id: uuid.UUID) -> None:
        asset = AssetService.get_asset(db, asset_id)
        AssetRepository.delete(db, asset)


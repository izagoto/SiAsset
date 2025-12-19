import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.asset import Asset


class AssetRepository:
    @staticmethod
    def create(db: Session, asset_data: dict) -> Asset:
        asset = Asset(**asset_data)
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def get_by_id(db: Session, asset_id: uuid.UUID) -> Optional[Asset]:
        return db.query(Asset).options(
            joinedload(Asset.category),
            joinedload(Asset.pic_user)
        ).filter(Asset.id == asset_id).first()

    @staticmethod
    def get_by_code(db: Session, asset_code: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.asset_code == asset_code).first()

    @staticmethod
    def get_by_serial_number(db: Session, serial_number: str) -> Optional[Asset]:
        return db.query(Asset).filter(Asset.serial_number == serial_number).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> List[Asset]:
        query = db.query(Asset).options(
            joinedload(Asset.category),
            joinedload(Asset.pic_user)
        )

        if status:
            query = query.filter(Asset.current_status == status)

        if category_id:
            query = query.filter(Asset.category_id == category_id)

        if search:
            search_filter = or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.asset_code.ilike(f"%{search}%"),
                Asset.serial_number.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(
        db: Session,
        status: Optional[str] = None,
        category_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
    ) -> int:
        query = db.query(Asset)

        if status:
            query = query.filter(Asset.current_status == status)

        if category_id:
            query = query.filter(Asset.category_id == category_id)

        if search:
            search_filter = or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.asset_code.ilike(f"%{search}%"),
                Asset.serial_number.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        return query.count()

    @staticmethod
    def update(db: Session, asset: Asset, update_data: dict) -> Asset:
        for key, value in update_data.items():
            if value is not None:
                setattr(asset, key, value)
        
        db.commit()
        db.refresh(asset)
        return asset

    @staticmethod
    def delete(db: Session, asset: Asset) -> None:
        db.delete(asset)
        db.commit()


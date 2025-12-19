from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class AssetBase(BaseModel):
    asset_code: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=150)
    serial_number: str = Field(..., min_length=1, max_length=150)
    category_id: uuid.UUID
    current_status: str = Field(default="active", max_length=50)
    asset_condition: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    pic_user_id: Optional[uuid.UUID] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=150)
    category_id: Optional[uuid.UUID] = None
    current_status: Optional[str] = Field(None, max_length=50)
    asset_condition: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    pic_user_id: Optional[uuid.UUID] = None


class AssetResponse(AssetBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


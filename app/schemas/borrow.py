from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from app.models.enums import LoanStatus

class LoanBase(BaseModel):
    asset_id: uuid.UUID
    due_date: Optional[datetime] = Field(None, description="Due date (optional for open-ended loans)")
    notes: Optional[str] = None

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class LoanStatusUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    notes: Optional[str] = None

class LoanResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    user_id: uuid.UUID
    requested_at: datetime
    borrowed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    loan_status: str
    notes: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    status_changed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LoanWithAsset(LoanResponse):
    asset_name: Optional[str] = None
    asset_code: Optional[str] = None
    user_username: Optional[str] = None


import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Text, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.models.enums import LoanStatus

class Borrow(Base):
    __tablename__ = "asset_loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    borrowed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    loan_status: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, default=LoanStatus.PENDING.value
    )

    notes: Mapped[str | None] = mapped_column(Text)
    
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="borrows")
    approver = relationship("User", foreign_keys=[approved_by])
    asset = relationship("Asset", back_populates="borrows")

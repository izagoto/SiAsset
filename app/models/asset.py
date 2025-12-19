import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    asset_code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(150), unique=True, index=True)

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id"), nullable=False, index=True
    )

    current_status: Mapped[str] = mapped_column(String(50), nullable=False, index=True, default="available")
    
    asset_condition: Mapped[str] = mapped_column(String(50))
    
    description: Mapped[str | None] = mapped_column(Text)
    
    pic_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category = relationship("AssetCategory", back_populates="assets")
    pic_user = relationship("User", foreign_keys=[pic_user_id], back_populates="managed_assets")
    borrows = relationship("Borrow", back_populates="asset")

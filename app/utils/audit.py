from fastapi import Request
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.user import User
from typing import Optional
import uuid

def get_client_ip(request: Request) -> Optional[str]:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    if request.client:
        return request.client.host
    
    return None


def create_audit_log(
    db: Session,
    user: User,
    action: str,
    entity: str,
    entity_id: uuid.UUID,
    ip_address: Optional[str] = None,
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip_address,
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log

def log_asset_action(
    db: Session,
    user: User,
    action: str,
    asset_id: uuid.UUID,
    ip_address: Optional[str] = None,
) -> AuditLog:
    return create_audit_log(
        db=db,
        user=user,
        action=action,
        entity="asset",
        entity_id=asset_id,
        ip_address=ip_address,
    )

def log_loan_action(
    db: Session,
    user: User,
    action: str,
    loan_id: uuid.UUID,
    ip_address: Optional[str] = None,
) -> AuditLog:
    return create_audit_log(
        db=db,
        user=user,
        action=action,
        entity="loan",
        entity_id=loan_id,
        ip_address=ip_address,
    )

def log_user_action(
    db: Session,
    user: User,
    action: str,
    target_user_id: uuid.UUID,
    ip_address: Optional[str] = None,
) -> AuditLog:
    return create_audit_log(
        db=db,
        user=user,
        action=action,
        entity="user",
        entity_id=target_user_id,
        ip_address=ip_address,
    )


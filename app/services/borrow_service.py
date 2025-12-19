import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.borrow import Borrow
from app.models.asset import Asset
from app.models.user import User
from app.models.enums import LoanStatus
from app.utils.exceptions import NotFoundException, ValidationException
from app.core.permissions import RolePermission, Permission


class LoanStatusTransitionError(ValidationException):
    def __init__(self, detail: str):
        super().__init__(detail=detail)


class LoanStatusValidator:
    VALID_TRANSITIONS = {
        LoanStatus.PENDING.value: [LoanStatus.APPROVED.value, LoanStatus.REJECTED.value],
        LoanStatus.APPROVED.value: [LoanStatus.BORROWED.value, LoanStatus.REJECTED.value],
        LoanStatus.REJECTED.value: [],
        LoanStatus.BORROWED.value: [LoanStatus.RETURNED.value, LoanStatus.OVERDUE.value],
        LoanStatus.RETURNED.value: [],
        LoanStatus.OVERDUE.value: [LoanStatus.RETURNED.value],
    }
    
    @classmethod
    def is_valid_transition(cls, current_status: str, new_status: str) -> bool:
        valid_next_statuses = cls.VALID_TRANSITIONS.get(current_status, [])
        return new_status in valid_next_statuses
    
    @classmethod
    def validate_transition(cls, current_status: str, new_status: str):
        if not cls.is_valid_transition(current_status, new_status):
            raise LoanStatusTransitionError(
                f"Invalid status transition from {current_status} to {new_status}"
            )


def create_loan_request(
    db: Session,
    user_id: uuid.UUID,
    asset_id: uuid.UUID,
    due_date: Optional[datetime] = None,
    notes: Optional[str] = None,
) -> Borrow:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise NotFoundException("Asset")
    
    if asset.current_status not in ["available"]:
        raise ValidationException("Asset is not available for borrowing")
    
    active_loan = db.query(Borrow).filter(
        and_(
            Borrow.asset_id == asset_id,
            Borrow.user_id == user_id,
            Borrow.loan_status.in_([LoanStatus.PENDING.value, LoanStatus.APPROVED.value, LoanStatus.BORROWED.value])
        )
    ).first()
    
    if active_loan:
        raise ValidationException("You already have an active loan request for this asset")
    
    loan = Borrow(
        asset_id=asset_id,
        user_id=user_id,
        due_date=due_date,
        notes=notes,
        loan_status=LoanStatus.PENDING.value,
        requested_at=datetime.now(timezone.utc),
    )
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    return loan


def approve_loan(
    db: Session,
    loan_id: uuid.UUID,
    approver_id: uuid.UUID,
    notes: Optional[str] = None,
) -> Borrow:
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")
    
    LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.APPROVED.value)
    
    loan.loan_status = LoanStatus.APPROVED.value
    loan.approved_by = approver_id
    loan.status_changed_at = datetime.now(timezone.utc)
    if notes:
        loan.notes = notes
    
    db.commit()
    db.refresh(loan)
    
    return loan


def reject_loan(
    db: Session,
    loan_id: uuid.UUID,
    approver_id: uuid.UUID,
    notes: Optional[str] = None,
) -> Borrow:
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")
    
    if loan.loan_status == LoanStatus.PENDING.value:
        LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.REJECTED.value)
    elif loan.loan_status == LoanStatus.APPROVED.value:
        LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.REJECTED.value)
    else:
        raise LoanStatusTransitionError(f"Cannot reject loan with status {loan.loan_status}")
    
    loan.loan_status = LoanStatus.REJECTED.value
    loan.approved_by = approver_id
    loan.status_changed_at = datetime.now(timezone.utc)
    if notes:
        loan.notes = notes
    
    asset = db.query(Asset).filter(Asset.id == loan.asset_id).first()
    if asset:
        asset.current_status = "available"
    
    db.commit()
    db.refresh(loan)
    
    return loan


def start_borrowing(
    db: Session,
    loan_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Borrow:
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")

    if str(loan.user_id) != str(user_id):
        raise ValidationException("You can only start borrowing your own approved loans")
    
    LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.BORROWED.value)
    
    loan.loan_status = LoanStatus.BORROWED.value
    loan.borrowed_at = datetime.now(timezone.utc)
    loan.status_changed_at = datetime.now(timezone.utc)

    asset = db.query(Asset).filter(Asset.id == loan.asset_id).first()
    if asset:
        asset.current_status = "borrowed"
    
    db.commit()
    db.refresh(loan)
    
    return loan


def return_loan(
    db: Session,
    loan_id: uuid.UUID,
    user_id: uuid.UUID,
    is_admin: bool = False,
    notes: Optional[str] = None,
) -> Borrow:
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")
    
    if not is_admin and str(loan.user_id) != str(user_id):
        raise ValidationException("You can only return your own loans")
    
    if loan.loan_status == LoanStatus.BORROWED.value:
        LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.RETURNED.value)
    elif loan.loan_status == LoanStatus.OVERDUE.value:
        LoanStatusValidator.validate_transition(loan.loan_status, LoanStatus.RETURNED.value)
    else:
        raise LoanStatusTransitionError(f"Cannot return loan with status {loan.loan_status}")
    
    loan.loan_status = LoanStatus.RETURNED.value
    loan.returned_at = datetime.now(timezone.utc)
    loan.status_changed_at = datetime.now(timezone.utc)
    if notes:
        loan.notes = notes
    
    asset = db.query(Asset).filter(Asset.id == loan.asset_id).first()
    if asset:
        asset.current_status = "available"
    
    db.commit()
    db.refresh(loan)
    
    return loan


def check_overdue_loans(db: Session) -> list[Borrow]:
    now = datetime.now(timezone.utc)
    
    overdue_loans = db.query(Borrow).filter(
        and_(
            Borrow.loan_status == LoanStatus.BORROWED.value,
            Borrow.due_date.isnot(None),
            Borrow.due_date < now
        )
    ).all()
    
    updated_loans = []
    for loan in overdue_loans:
        loan.loan_status = LoanStatus.OVERDUE.value
        loan.status_changed_at = now
        updated_loans.append(loan)
    
    db.commit()
    
    return updated_loans


def get_user_loans(
    db: Session,
    user_id: uuid.UUID,
    status: Optional[str] = None,
) -> list[Borrow]:
    query = db.query(Borrow).filter(Borrow.user_id == user_id)
    
    if status:
        query = query.filter(Borrow.loan_status == status)
    
    return query.order_by(Borrow.created_at.desc()).all()


def get_all_loans(
    db: Session,
    status: Optional[str] = None,
    asset_id: Optional[uuid.UUID] = None,
) -> list[Borrow]:
    query = db.query(Borrow)
    
    if status:
        query = query.filter(Borrow.loan_status == status)
    
    if asset_id:
        query = query.filter(Borrow.asset_id == asset_id)
    
    return query.order_by(Borrow.created_at.desc()).all()


def get_loan_by_id(
    db: Session,
    loan_id: uuid.UUID,
) -> Borrow:
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")
    return loan


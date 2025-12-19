from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.api.deps import get_db, get_current_active_user, require_permission_dependency
from app.core.permissions import Permission, RolePermission
from app.models.user import User
from app.models.enums import LoanStatus
from app.schemas.borrow import (
    LoanCreate,
    LoanUpdate,
    LoanStatusUpdate,
    LoanResponse,
    LoanWithAsset,
)
from app.schemas.auth import BaseResponse
from app.services.borrow_service import (
    create_loan_request,
    approve_loan,
    reject_loan,
    start_borrowing,
    return_loan,
    get_user_loans,
    get_all_loans,
    get_loan_by_id,
    check_overdue_loans,
    LoanStatusTransitionError,
)
from app.utils.audit import log_loan_action, get_client_ip
from app.utils.exceptions import ValidationException, NotFoundException

router = APIRouter(prefix="/loans", tags=["Loans"])


def get_user_friendly_error_message(error: Exception) -> str:
    """Convert technical error messages to user-friendly messages"""
    error_str = str(error).lower()
    
    if "database" in error_str or "sql" in error_str or "psycopg" in error_str:
        return "Database error occurred. Please contact administrator."
    elif "connection" in error_str or "timeout" in error_str:
        return "Connection error. Please try again later."
    elif "not found" in error_str:
        return "The requested resource was not found."
    elif "permission" in error_str or "access" in error_str:
        return "You don't have permission to perform this action."
    elif "status" in error_str and "transition" in error_str:
        return str(error)
    elif "validation" in error_str:
        return "Invalid data provided. Please check your input."
    else:
        return "An error occurred. Please try again later."

@router.post("", status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_data: LoanCreate,
    request: Request,
    current_user: User = Depends(require_permission_dependency(Permission.CREATE_LOAN)),
    db: Session = Depends(get_db),
):
    """Create loan request (status: PENDING)"""
    try:
        loan = create_loan_request(
            db=db,
            user_id=current_user.id,
            asset_id=loan_data.asset_id,
            due_date=loan_data.due_date,
            notes=loan_data.notes,
        )
        
        log_loan_action(
            db=db,
            user=current_user,
            action="create",
            loan_id=loan.id,
            ip_address=get_client_ip(request),
        )
        
        return BaseResponse(
            status=201,
            message="Loan request created successfully",
            data=LoanResponse.model_validate(loan).model_dump()
        )
    except ValidationException as e:
        raise
    except Exception as e:
        raise ValidationException(get_user_friendly_error_message(e))


@router.get("", status_code=status.HTTP_200_OK)
def list_loans(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        is_admin = RolePermission.has_permission(current_user, Permission.MANAGE_LOANS)
        
        if is_admin:
            loans = get_all_loans(db, status=status_filter)
        else:
            loans = get_user_loans(db, current_user.id, status=status_filter)
        
        if not loans or len(loans) == 0:
            raise NotFoundException("Loan")
        
        return BaseResponse(
            status=200,
            message="Loans retrieved successfully",
            data=[LoanResponse.model_validate(loan).model_dump() for loan in loans]
        )
    except NotFoundException:
        raise
    except Exception as e:
        raise ValidationException(get_user_friendly_error_message(e))


@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
def get_loan(
    loan_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    loan = get_loan_by_id(db, loan_id)
    
    is_admin = RolePermission.has_permission(current_user, Permission.MANAGE_LOANS)
    if not is_admin and str(loan.user_id) != str(current_user.id):
        from app.core.permissions import PermissionDeniedException
        raise PermissionDeniedException("You can only access your own loans")
    
    return BaseResponse(
        status=200,
        message="Loan retrieved successfully",
        data=LoanResponse.model_validate(loan).model_dump()
    )


@router.post("/{loan_id}/approve", status_code=status.HTTP_200_OK)
def approve_loan_request(
    loan_id: uuid.UUID,
    request: Request,
    status_data: Optional[LoanStatusUpdate] = None,
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_LOANS)),
    db: Session = Depends(get_db),
):
    try:
        loan = approve_loan(
            db=db,
            loan_id=loan_id,
            approver_id=current_user.id,
            notes=status_data.notes if status_data else None,
        )
        
        log_loan_action(
            db=db,
            user=current_user,
            action="approve",
            loan_id=loan.id,
            ip_address=get_client_ip(request),
        )
        
        return BaseResponse(
            status=200,
            message="Loan approved successfully",
            data=LoanResponse.model_validate(loan).model_dump()
        )
    except LoanStatusTransitionError as e:
        raise ValidationException(get_user_friendly_error_message(e))


@router.post("/{loan_id}/reject", status_code=status.HTTP_200_OK)
def reject_loan_request(
    loan_id: uuid.UUID,
    request: Request,
    status_data: Optional[LoanStatusUpdate] = None,
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_LOANS)),
    db: Session = Depends(get_db),
):
    try:
        loan = reject_loan(
            db=db,
            loan_id=loan_id,
            approver_id=current_user.id,
            notes=status_data.notes if status_data else None,
        )
        
        log_loan_action(
            db=db,
            user=current_user,
            action="reject",
            loan_id=loan.id,
            ip_address=get_client_ip(request),
        )
        
        return BaseResponse(
            status=200,
            message="Loan rejected successfully",
            data=LoanResponse.model_validate(loan).model_dump()
        )
    except LoanStatusTransitionError as e:
        raise ValidationException(get_user_friendly_error_message(e))


@router.post("/{loan_id}/start", status_code=status.HTTP_200_OK)
def start_borrowing_asset(
    loan_id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Start borrowing (APPROVED -> BORROWED) - Owner only"""
    try:
        loan = start_borrowing(
            db=db,
            loan_id=loan_id,
            user_id=current_user.id,
        )
        
        log_loan_action(
            db=db,
            user=current_user,
            action="start_borrowing",
            loan_id=loan.id,
            ip_address=get_client_ip(request),
        )
        
        return BaseResponse(
            status=200,
            message="Borrowing started successfully",
            data=LoanResponse.model_validate(loan).model_dump()
        )
    except LoanStatusTransitionError as e:
        raise ValidationException(get_user_friendly_error_message(e))
    except ValidationException as e:
        raise


@router.post("/{loan_id}/return", status_code=status.HTTP_200_OK)
def return_borrowed_asset(
    loan_id: uuid.UUID,
    request: Request,
    status_data: Optional[LoanStatusUpdate] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        is_admin = RolePermission.has_permission(current_user, Permission.MANAGE_LOANS)
        
        loan = return_loan(
            db=db,
            loan_id=loan_id,
            user_id=current_user.id,
            is_admin=is_admin,
            notes=status_data.notes if status_data else None,
        )
        
        log_loan_action(
            db=db,
            user=current_user,
            action="return",
            loan_id=loan.id,
            ip_address=get_client_ip(request),
        )
        
        return BaseResponse(
            status=200,
            message="Asset returned successfully",
            data=LoanResponse.model_validate(loan).model_dump()
        )
    except LoanStatusTransitionError as e:
        raise ValidationException(get_user_friendly_error_message(e))
    except ValidationException as e:
        raise


@router.post("/check-overdue", status_code=status.HTTP_200_OK)
def check_overdue(
    current_user: User = Depends(require_permission_dependency(Permission.MANAGE_LOANS)),
    db: Session = Depends(get_db),
):
    overdue_loans = check_overdue_loans(db)
    
    return BaseResponse(
        status=200,
        message=f"Found {len(overdue_loans)} overdue loans",
        data=[LoanResponse.model_validate(loan).model_dump() for loan in overdue_loans]
    )

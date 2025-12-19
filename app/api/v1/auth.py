from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.auth_service import authenticate_user, refresh_access_token
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    TokenData,
    RefreshTokenRequest,
    BaseResponse,
)
from app.schemas.user import UserResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    tokens = authenticate_user(db, data.email, data.password)
    
    return TokenResponse(
        status=200,
        message="Login successful",
        data=TokenData(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer"
        )
    )

@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    tokens = refresh_access_token(db, data.refresh_token)
    
    return TokenResponse(
        status=200,
        message="Token refreshed successfully",
        data=TokenData(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer"
        )
    )

@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        status=200,
        message="User profile retrieved successfully",
        data=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            is_active=current_user.is_active,
            role_id=current_user.role_id,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
        ).model_dump()
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        status=200,
        message="Logout successful",
        data=None
    )
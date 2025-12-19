from pydantic import BaseModel, EmailStr
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    status: int
    message: str
    data: Optional[T] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "message": "Success",
                "data": None
            }
        }

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenResponse(BaseResponse[TokenData]):
    status: int = 200
    message: str = "Login successful"
    data: Optional[TokenData] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }

class RefreshTokenRequest(BaseModel):
    refresh_token: str

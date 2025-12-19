from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict


class BaseAPIException(HTTPException):
    """Base exception class for API errors"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Dict[str, Any] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class InvalidCredentialsException(BaseAPIException):
    """Exception for invalid login credentials"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserException(BaseAPIException):
    """Exception for inactive user"""
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="INACTIVE_USER",
        )


class NotFoundException(BaseAPIException):
    """Exception for resource not found"""
    def __init__(self, resource: str = "Resource", detail: str = None):
        detail = detail or f"{resource} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ValidationException(BaseAPIException):
    """Exception for validation errors"""
    def __init__(self, detail: str = "Validation error", errors: Dict = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )
        self.errors = errors


def create_error_response(
    status_code: int,
    detail: str,
    error_code: str = None,
    errors: Dict = None,
) -> JSONResponse:
    """Create a standardized error response"""
    content = {
        "status": status_code,
        "message": detail,
        "data": None
    }
    
    if errors:
        content["errors"] = errors
    
    return JSONResponse(
        status_code=status_code,
        content=content,
    )


from typing import Any, Optional
from fastapi.responses import JSONResponse


def create_success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> JSONResponse:
    content = {
        "status": status_code,
        "message": message,
        "data": data,
    }
    
    return JSONResponse(
        status_code=status_code,
        content=content,
    )


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> dict:
    return {
        "status": status_code,
        "message": message,
        "data": data,
    }

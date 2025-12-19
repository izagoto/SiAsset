from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, assets, borrows, users
from app.utils.exceptions import (
    BaseAPIException,
    create_error_response,
)
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cyber Asset Management",
    description="API for managing cyber assets, users, and borrows",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if "components" in openapi_schema and "securitySchemes" in openapi_schema["components"]:
        if "BearerAuth" in openapi_schema["components"]["securitySchemes"]:
            openapi_schema["components"]["securitySchemes"]["BearerAuth"]["description"] = (
                "Masukkan token JWT kamu di sini. Contoh: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    logger.warning(
        f"API Exception: {exc.error_code} - {exc.detail}",
        extra={"path": request.url.path, "method": request.method}
    )
    return create_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_code=exc.error_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    json_error = False
    
    for error in exc.errors():
        loc = error["loc"]
        error_type = error.get("type", "")
        error_msg = error.get("msg", "")
        
        if error_type == "json_invalid":
            json_error = True
            detail = "Invalid JSON format. Please ensure your request body is valid JSON and Content-Type header is set to 'application/json'."
            logger.warning(
                f"JSON Parse Error: {error_msg}",
                extra={"path": request.url.path, "method": request.method}
            )
            return create_error_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail,
                error_code="VALIDATION_ERROR",
            )
        
        field_parts = []
        for part in loc:
            if part != "body":
                if isinstance(part, (int, str)):
                    field_parts.append(str(part))
        
        field = ".".join(field_parts) if field_parts else "body"
        errors[field] = error_msg
    
    logger.warning(
        f"Validation Error: {errors}",
        extra={"path": request.url.path, "method": request.method}
    )
    
    error_messages = [f"{field}: {msg}" for field, msg in errors.items()]
    detail = "Validation error" if len(error_messages) > 1 else error_messages[0] if error_messages else "Validation error"
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail,
        error_code="VALIDATION_ERROR",
        errors=errors if len(errors) > 1 else None,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    
    error_message = "Internal server error"
    error_type = type(exc).__name__
    
    if "database" in str(exc).lower() or "sql" in str(exc).lower() or "psycopg" in str(exc).lower():
        error_message = "Database error occurred. Please try again later."
    elif "connection" in str(exc).lower() or "timeout" in str(exc).lower():
        error_message = "Connection error. Please try again later."
    elif "validation" in str(exc).lower():
        error_message = "Invalid data provided. Please check your input."
    elif "permission" in str(exc).lower() or "access" in str(exc).lower():
        error_message = "You don't have permission to perform this action."
    elif "not found" in str(exc).lower():
        error_message = "The requested resource was not found."
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_message,
        error_code="INTERNAL_SERVER_ERROR",
    )

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

app.include_router(assets.router, prefix="/api/v1")
app.include_router(borrows.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

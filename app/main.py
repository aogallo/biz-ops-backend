import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)
from app.core.logging_config import setup_logging
from app.infrastructure.database import create_db_and_tables, engine
from app.routes import user_routes, vendor_routes
from app.schemas.common import ErrorResponse, HealthResponse

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting up Business Operations API...")
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Business Operations API...")
    engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    description="Business Operations Backend API with FastAPI and PostgreSQL",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(f"Application error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message, "error_code": exc.error_code, **exc.details},
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found exceptions."""
    logger.warning(f"Resource not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(AuthenticationError)
async def authentication_exception_handler(request: Request, exc: AuthenticationError):
    """Handle authentication exceptions."""
    logger.warning(f"Authentication failed: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    """Handle authorization exceptions."""
    logger.warning(f"Authorization failed: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "error_code": "VALIDATION_ERROR"},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred", "error_code": "DATABASE_ERROR"},
    )


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the API status, version, and database connection status.
    """
    # Check database connection
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.API_VERSION,
        "database": db_status,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check endpoint.
    
    Returns comprehensive health information about the API and its dependencies.
    """
    return await health_check()


# Include routers
app.include_router(router=user_routes.router)
app.include_router(router=vendor_routes.router)


# Log registered routes on startup
@app.on_event("startup")
async def log_routes():
    """Log all registered routes."""
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"  {', '.join(route.methods)} {route.path}")
    logger.info(f"API Documentation available at: /docs")
    logger.info(f"ReDoc Documentation available at: /redoc")

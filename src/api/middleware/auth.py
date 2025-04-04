from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.services.auth_service import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app, auth_service: AuthService, exclude_paths: list = None):
        super().__init__(app)
        self.auth_service = auth_service
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/users", "/token"]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and apply authentication"""
        # Skip authentication for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.replace("Bearer ", "")
        
        # Validate token
        payload = await self.auth_service.validate_token(token)
        if not payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Add user info to request state
        request.state.user = payload
        
        # Process the request
        return await call_next(request)
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings

#from backend.config.settings import settings
from utils.auth import FirebaseAuthManager


PUBLIC_PATHS = [
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ----------------------------
        # DEV MODE (AUTH BYPASS)
        # ----------------------------
        if settings.DEV_MODE:
            request.state.user_id = "dev_user"
            return await call_next(request)

        # ----------------------------
        # PUBLIC PATHS (NO AUTH)
        # ----------------------------
        for path in PUBLIC_PATHS:
            if request.url.path.startswith(path):
                return await call_next(request)

        # ----------------------------
        # AUTH HEADER CHECK
        # ----------------------------
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"},
            )

        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid Authorization format"},
            )

        # ----------------------------
        # TOKEN VALIDATION
        # ----------------------------
        token = auth_header.replace("Bearer ", "")
        decoded = FirebaseAuthManager.verify_id_token(token)

        if not decoded:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        # ----------------------------
        # AUTH SUCCESS
        # ----------------------------
        request.state.user = decoded
        request.state.user_id = decoded.get("uid")

        return await call_next(request)
from fastapi import Request, HTTPException, status

def auth_middleware(request: Request):
    user = getattr(request.state, "user", None)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    return user

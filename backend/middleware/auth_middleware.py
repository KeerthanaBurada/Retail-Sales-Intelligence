"""
Authentication middleware - FastAPI dependency for protecting routes.

Extracts the Bearer token from the Authorization header, validates it,
and returns the authenticated User object for use in route handlers.
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from services.auth_service import verify_token

# Points to the login endpoint so Swagger UI knows where to send credentials
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that extracts and validates the JWT from the request.

    Usage in a route:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            ...

    Raises 401 if the token is invalid/expired or the user no longer exists.
    """
    try:
        payload = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

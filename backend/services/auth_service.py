"""
Authentication service - handles password hashing and JWT token management.

Uses bcrypt for password hashing (industry standard, resistant to brute-force)
and python-jose for JWT encoding/decoding.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Bcrypt context - 'auto' deprecation means it will automatically upgrade
# hashes if a stronger scheme is added later
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with an expiration claim.

    The token payload includes whatever data is passed in (typically user id
    and email) plus an 'exp' claim set to ACCESS_TOKEN_EXPIRE_MINUTES from now.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Returns the token payload dict on success.
    Raises ValueError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {e}")

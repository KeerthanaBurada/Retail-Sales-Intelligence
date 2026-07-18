"""User-related request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str
    name: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class UserResponse(BaseModel):
    """Schema for returning user data (excludes password)."""
    id: int
    email: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"

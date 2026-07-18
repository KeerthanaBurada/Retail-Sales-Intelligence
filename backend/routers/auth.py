from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from services.auth_service import hash_password, verify_password, create_access_token
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix='/api/auth', tags=['Authentication'])


@router.post('/register', response_model=TokenResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return an access token."""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, detail='Email already registered')

    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={'sub': str(new_user.id)})
    return TokenResponse(access_token=token, token_type='bearer')


@router.post('/login', response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return an access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(401, detail='Invalid email or password')

    token = create_access_token(data={'sub': str(user.id)})
    return TokenResponse(access_token=token, token_type='bearer')


@router.get('/profile', response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return UserResponse.model_validate(current_user)

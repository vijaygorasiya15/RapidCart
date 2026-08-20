from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.auth import RefreshRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import (
    authenticate_user,
    create_refresh_token_for_user,
    register_user,
    revoke_refresh_token,
    verify_refresh_token,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

"""
This is a FastAPI helper class that handles the standard OAuth2 login form.

It expects the login request to contain:
username=someone@example.com
password=123456
"""

from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        user = register_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token_for_user(db, user.id)
    return Token(access_token=access_token, refresh_token=refresh_token)
"""
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

There are two dependencies here.

First:
form_data: OAuth2PasswordRequestForm = Depends()

This tells FastAPI:
"Get the login form data from the incoming request and give me an OAuth2PasswordRequestForm object."

Second:
Depends() tells FastAPI:
"Don't expect me to manually create this object. You create it using this dependency and pass it into my function."
"""

@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    db_token = verify_refresh_token(db, payload.refresh_token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = db_token.user
    revoke_refresh_token(db, db_token)  # rotation: old token dies here

    new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    new_refresh_token = create_refresh_token_for_user(db, user.id)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    db_token = verify_refresh_token(db, payload.refresh_token)
    if db_token:
        revoke_refresh_token(db, db_token)
    return None
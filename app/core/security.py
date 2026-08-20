import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from jose import JWTError, jwt

"""
python-jose is being used to work with JWTs.

jwt gives you functions like:

jwt.encode()
jwt.decode()

JWTError is an exception that can occur when a JWT is invalid, expired, incorrectly signed, etc.
"""

from passlib.context import CryptContext

"""
This imports Passlib's CryptContext.
Passlib is used for password hashing and verification.
"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""
Configure Passlib to use bcrypt.
schemes=["bcrypt"]
You're telling Passlib:
Use the bcrypt algorithm for hashing passwords.
"""


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
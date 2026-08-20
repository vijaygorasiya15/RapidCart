from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: int | None = None
    role: str | None = None

"""
TokenData — internal shape used when we decode a JWT back into its claims (not exposed directly to clients).
"""
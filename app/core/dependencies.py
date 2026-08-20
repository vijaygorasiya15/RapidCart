from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import RoleEnum, User
from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi import status as ws_status
from fastapi.security import OAuth2PasswordBearer

"""
OAuth2PasswordBearer is a FastAPI security utility.
Its job here is to: Look for an access token in the request's Authorization header.

For example, the client sends:
Authorization: Bearer eyJhbGciOiJIUzI1Ni...

OAuth2PasswordBearer extracts:
eyJhbGciOiJIUzI1Ni... <—the actual token, removing Bearer.
"""

from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
"""
Here you're creating a reusable security dependency.

The important part is:
tokenUrl="/auth/login"
This tells FastAPI: "The endpoint where a user obtains their token is /auth/login."

OAuth2PasswordBearer does NOT validate your JWT itself. 
It mainly extracts the Bearer token from the request.
"""

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user

"""
* means: Accept any number of role arguments and collect them into a tuple.
"""
def require_role(*allowed_roles: RoleEnum):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Operation not permitted for role '{current_user.role.value}'")
        return current_user
    return role_checker

"""
401 → Who are you? / Invalid authentication
403 → I know who you are, but you're not allowed / FORBIDDEN
"""


async def get_current_user_ws(websocket: WebSocket, db: Session) -> User:
    token = websocket.query_params.get("token")
    if not token:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION, reason="Missing token")

    payload = decode_access_token(token)
    if payload is None:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise WebSocketException(code=ws_status.WS_1008_POLICY_VIOLATION, reason="User not found")

    return user
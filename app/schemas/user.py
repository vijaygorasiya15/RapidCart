from app.models.user import RoleEnum
from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.BUYER


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)

"""
model_config = ConfigDict(from_attributes=True)

This tells Pydantic: "I am allowed to create this Pydantic schema from an object's attributes, not only from a dictionary."

This is especially important with SQLAlchemy.

Your database gives you a SQLAlchemy object like:

user = User(
    id=1,
    email="abc@gmail.com",
    role=RoleEnum.BUYER
)

That's an object, not a dictionary.

Without from_attributes=True, Pydantic mainly expects something like:

{
    "id": 1,
    "email": "abc@gmail.com",
    "role": "buyer"
}

With:

model_config = ConfigDict(from_attributes=True)

Pydantic can read:

user.id
user.email
user.role

and convert the SQLAlchemy object into your UserResponse.
"""